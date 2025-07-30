#!/usr/bin/env python3

import json
import subprocess
import sys
import os
import threading
import concurrent.futures
import time

class ContextAwareValidationTests:
    """Context-aware validation test suite with parallel execution"""
    
    def __init__(self):
        self.passed = 0
        self.total = 0
        self.lock = threading.Lock()  # Thread safety for counters
        
    def test_validator(self, test_name, hook_input, expected_exit_code=0, should_contain_in_stderr=None):
        """Test the ADK validator with sample input"""
        with self.lock:
            self.total += 1
            
        print(f"\n{'='*60}")
        print(f"TEST: {test_name}")
        print(f"Expected Exit Code: {expected_exit_code}")
        
        try:
            process = subprocess.run(
                [sys.executable, '-m', 'claude_code_adk_validator'],
                input=json.dumps(hook_input),
                text=True,
                capture_output=True,
                timeout=30  # Longer timeout for LLM analysis
            )

            print(f"Exit Code: {process.returncode}")

            # Check exit code
            exit_code_ok = process.returncode == expected_exit_code
            
            # Check stderr content if specified
            stderr_content_ok = True
            if should_contain_in_stderr:
                stderr_content_ok = should_contain_in_stderr.lower() in process.stderr.lower()

            test_passed = exit_code_ok and stderr_content_ok
            
            if test_passed:
                print("✓ PASSED")
                with self.lock:
                    self.passed += 1
            else:
                print("✗ FAILED")
                if not exit_code_ok:
                    print(f"   Expected exit code {expected_exit_code}, got {process.returncode}")
                if not stderr_content_ok:
                    print(f"   Expected stderr to contain '{should_contain_in_stderr}'")
                if process.stderr:
                    print(f"   Stderr: {process.stderr[:200]}...")

            return test_passed

        except subprocess.TimeoutExpired:
            print("✗ FAILED - Timeout")
            return False
        except Exception as e:
            print(f"✗ FAILED - Error: {e}")
            return False
    
    def run_all_tests(self):
        """Run all context-aware validation tests in parallel"""
        print("Testing Context-Aware Security Validation (Issue #29)")
        print("=" * 60)
        print("PARALLEL EXECUTION: Running 8 tests concurrently")
        print("=" * 60)

        # Check if we have API key for LLM tests
        has_api_key = bool(os.environ.get("GEMINI_API_KEY"))
        if not has_api_key:
            print("WARNING: No GEMINI_API_KEY found. LLM-based tests will use fallback validation.")
        
        start_time = time.time()
        
        # Test 1: Test file with test fixtures (should be ALLOWED)
        # This was the core issue - test files being blocked for legitimate test secrets
        test_conftest_with_fixtures = {
        "session_id": "test123",
        "transcript_path": "/tmp/nonexistent.jsonl", 
        "hook_event_name": "PreToolUse",
        "tool_name": "Write",
        "tool_input": {
            "file_path": "tests/conftest.py",
            "content": '''import pytest
from jose import jwt

@pytest.fixture
def test_jwt_secret():
    return "test-secret-key"

@pytest.fixture  
def mock_jwt_token():
    payload = {"user_id": 123, "username": "testuser"}
    return jwt.encode(payload, "test-secret-key", algorithm="HS256")

@pytest.fixture
def mock_api_key():
    return "test_api_key_12345"

@pytest.fixture
def dummy_database_url():
    return "postgresql://test:test123@localhost:5432/testdb"
'''
        }
    }

    # Test 2: Production file with test-like secret (should be BLOCKED)
    # Even if it looks like test, production files should be strict
    production_with_test_secret = {
        "session_id": "test123",
        "transcript_path": "/tmp/nonexistent.jsonl",
        "hook_event_name": "PreToolUse", 
        "tool_name": "Write",
        "tool_input": {
            "file_path": "src/app.py",
            "content": '''import os
from flask import Flask

app = Flask(__name__)

# This looks like test but in production file should be blocked
API_KEY = "test-secret-key"
JWT_SECRET = "test-jwt-secret-123"

@app.route("/")
def hello():
    return "Hello World"
'''
        }
    }

    # Test 3: Production file with real secrets (should be BLOCKED)
    production_with_real_secrets = {
        "session_id": "test123", 
        "transcript_path": "/tmp/nonexistent.jsonl",
        "hook_event_name": "PreToolUse",
        "tool_name": "Write",
        "tool_input": {
            "file_path": "src/config.py",
            "content": '''
# Real production secrets that should always be blocked
STRIPE_SECRET_KEY = "sk_live_1234567890abcdefghijklmnop"
AWS_ACCESS_KEY_ID = "AKIA1234567890ABCDEF"
GITHUB_TOKEN = "ghp_1234567890abcdefghijklmnopqrstuvwxyz"
DATABASE_PASSWORD = "RealP@ssw0rd!2024Secure"
'''
        }
    }

    # Test 4: Test file with obvious production secret (should be BLOCKED) 
    # Even test files should block obvious production secrets
    test_with_real_secret = {
        "session_id": "test123",
        "transcript_path": "/tmp/nonexistent.jsonl",
        "hook_event_name": "PreToolUse",
        "tool_name": "Write", 
        "tool_input": {
            "file_path": "tests/test_payment.py",
            "content": '''import pytest

def test_payment_processing():
    # This real Stripe key should be blocked even in test files
    stripe_key = "sk_live_1234567890abcdefghijklmnop"
    assert process_payment(stripe_key) == "success"
'''
        }
    }

    # Test 5: Config file with placeholder values (should be ALLOWED)
    # Config files should have minimal validation for placeholder values
    config_with_placeholders = {
        "session_id": "test123",
        "transcript_path": "/tmp/nonexistent.jsonl", 
        "hook_event_name": "PreToolUse",
        "tool_name": "Write",
        "tool_input": {
            "file_path": ".env.example",
            "content": '''# Example environment variables
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
API_KEY=your_api_key_here
SECRET_KEY=your_secret_key_here
STRIPE_KEY=sk_test_your_stripe_test_key
JWT_SECRET=your_jwt_secret_here
'''
        }
    }

    # Test 6: Documentation file with example secrets (should be ALLOWED)
    docs_with_examples = {
        "session_id": "test123",
        "transcript_path": "/tmp/nonexistent.jsonl",
        "hook_event_name": "PreToolUse", 
        "tool_name": "Write",
        "tool_input": {
            "file_path": "README.md",
            "content": '''# API Configuration

Set these environment variables:

```bash
export API_KEY="your-api-key-here"
export SECRET_KEY="example-secret-key-123"
export DATABASE_URL="postgresql://user:pass@localhost/db"
```

For testing, use:

```python
test_api_key = "test-api-key-12345"
mock_secret = "mock-secret-for-testing"
```
'''
        }
    }

    # Test 7: Test file with mixed secrets (some test, some real)
    # Should catch the real ones while allowing test fixtures
    test_with_mixed_secrets = {
        "session_id": "test123",
        "transcript_path": "/tmp/nonexistent.jsonl",
        "hook_event_name": "PreToolUse",
        "tool_name": "Write",
        "tool_input": {
            "file_path": "tests/test_auth.py",
            "content": '''import pytest

class TestAuthentication:
    def test_jwt_encoding(self):
        # These test fixtures should be allowed
        test_secret = "test-jwt-secret"
        mock_key = "mock-api-key-12345"
        
        # But this real AWS key should be blocked
        aws_key = "AKIA1234567890ABCDEF"
        
        token = encode_jwt({"user": "test"}, test_secret)
        assert decode_jwt(token, test_secret)["user"] == "test"
'''
        }
    }

    # Test 8: Ambiguous JWT token in test context
    # LLM should recognize this as a test fixture
    test_with_jwt_token = {
        "session_id": "test123", 
        "transcript_path": "/tmp/nonexistent.jsonl",
        "hook_event_name": "PreToolUse",
        "tool_name": "Write",
        "tool_input": {
            "file_path": "tests/fixtures/auth_tokens.py", 
            "content": '''# Test JWT tokens for authentication testing

# This should be recognized as a test fixture
TEST_JWT_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IlRlc3QgVXNlciIsImlhdCI6MTUxNjIzOTAyMn0.qdrr2_a7Sd80gmCWjnDomO4NjqAqjLjqMFAqr5Nf7n8"

# Mock API response for testing
MOCK_AUTH_RESPONSE = {
    "access_token": "test_access_token_12345",
    "refresh_token": "test_refresh_token_67890", 
    "expires_in": 3600
}
'''
        }
    }

        # Define test cases with expected outcomes
        tests = [
            # Core issue: test files with test fixtures should be ALLOWED
            ("Test file with legitimate test fixtures (CORE ISSUE)", test_conftest_with_fixtures, 0),
            
            # Production files should maintain strict validation
            ("Production file with test-like secrets (should block)", production_with_test_secret, 2),
            ("Production file with real secrets (should block)", production_with_real_secrets, 2),
            
            # Test files should still block obvious production secrets
            ("Test file with real production secret (should block)", test_with_real_secret, 2),
            
            # Config and docs should have minimal validation
            ("Config file with placeholders (should allow)", config_with_placeholders, 0),
            ("Documentation with examples (should allow)", docs_with_examples, 0),
            
            # Mixed content scenarios
            ("Test file with mixed secrets (should block real ones)", test_with_mixed_secrets, 2),
            
            # LLM intelligence tests (if API key available)
            ("JWT token in test context (should allow)", test_with_jwt_token, 0 if has_api_key else 0),
        ]

        # Add additional LLM-specific tests if API key is available
        if has_api_key:
            print(f"\nAPI key detected - including LLM intelligence tests")
        else:
            print(f"\nNo API key - using rule-based validation only")

        print(f"\nStarting parallel test execution...")
        
        # Run tests in parallel
        def run_single_test(test_data):
            test_name, hook_input, expected_exit = test_data
            return self.test_validator(test_name, hook_input, expected_exit)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            results = list(executor.map(run_single_test, tests))
        
        elapsed_time = time.time() - start_time
        
        print(f"\n{'=' * 60}")
        print(f"Context-Aware Validation Test Results: {self.passed}/{self.total} passed")
        print(f"Total execution time: {elapsed_time:.1f} seconds")

        if self.passed == self.total:
            print("✓ All context-aware validation tests passed!")
            print("✓ Issue #29 RESOLVED: Test files can now use legitimate test fixtures")
            return 0
        else:
            print("✗ Some context-aware validation tests failed")
            print("✗ Issue #29 may not be fully resolved")
            return 1

def main():
    """Main test runner"""
    test_suite = ContextAwareValidationTests()
    return test_suite.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())
