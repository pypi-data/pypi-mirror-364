#!/usr/bin/env python3

import json
import subprocess
import sys
import os
import threading
import concurrent.futures
import time

class ValidationTests:
    """Basic validation test suite with parallel execution"""
    
    def __init__(self):
        self.passed = 0
        self.total = 0
        self.lock = threading.Lock()  # Thread safety for counters
        
    def test_validator(self, test_name, hook_input, expected_exit_code=0):
        """Test the ADK validator with sample input"""
        with self.lock:
            self.total += 1
            
        print(f"\n{'='*60}")
        print(f"TEST: {test_name}")
        print(f"Expected Exit Code: {expected_exit_code}")

        try:
            # Run the validator via package
            process = subprocess.run(
                [sys.executable, '-m', 'claude_code_adk_validator'],
                input=json.dumps(hook_input),
                text=True,
                capture_output=True,
                timeout=15
            )

            print(f"Exit Code: {process.returncode}")

            if process.returncode == expected_exit_code:
                print("✓ PASSED")
                with self.lock:
                    self.passed += 1
                return True
            else:
                print(f"✗ FAILED - Expected exit code {expected_exit_code}, got {process.returncode}")
                if process.stderr:
                    print(f"   Stderr: {process.stderr[:200]}...")
                return False

        except subprocess.TimeoutExpired:
            print("✗ FAILED - Timeout")
            return False
        except Exception as e:
            print(f"✗ FAILED - Error: {e}")
            return False
    
    def run_all_tests(self):
        """Run all validation tests in parallel"""
        print("Testing Google ADK-inspired Claude Code Validator")
        print("=" * 60)
        print("PARALLEL EXECUTION: Running 7 tests concurrently")
        print("=" * 60)
        
        start_time = time.time()

        # Test 1: Safe file write (should pass)
        safe_write = {
            "session_id": "test123",
            "transcript_path": "/tmp/nonexistent.jsonl",
            "hook_event_name": "PreToolUse",
            "tool_name": "Write",
            "tool_input": {
                "file_path": "README.md",
                "content": "# Test Project\n\nHello, world!"
            }
        }

        # Test 2: Dangerous bash command (should be blocked)
        dangerous_bash = {
            "session_id": "test123",
            "transcript_path": "/tmp/nonexistent.jsonl",
            "hook_event_name": "PreToolUse",
            "tool_name": "Bash",
            "tool_input": {
                "command": "rm -rf /"
            }
        }

        # Test 3: File with real secrets (should be blocked)
        sensitive_file = {
            "session_id": "test123",
            "transcript_path": "/tmp/nonexistent.jsonl",
            "hook_event_name": "PreToolUse",
            "tool_name": "Write",
            "tool_input": {
                "file_path": ".env",
                "content": "api_key = \"sk_live_1234567890abcdefghijklmnop\"\npassword = \"realLongPasswordValue123456\""
            }
        }

        # Test 4: Safe bash command (should pass)
        safe_bash = {
            "session_id": "test123",
            "transcript_path": "/tmp/nonexistent.jsonl",
            "hook_event_name": "PreToolUse",
            "tool_name": "Bash",
            "tool_input": {
                "command": "ls -la"
            }
        }

        # Test 5: Grep command (should suggest ripgrep)
        grep_command = {
            "session_id": "test123",
            "transcript_path": "/tmp/nonexistent.jsonl",
            "hook_event_name": "PreToolUse",
            "tool_name": "Bash",
            "tool_input": {
                "command": "grep pattern file.txt"
            }
        }

        # Test 6: Find command (should suggest ripgrep alternative)
        find_command = {
            "session_id": "test123",
            "transcript_path": "/tmp/nonexistent.jsonl",
            "hook_event_name": "PreToolUse",
            "tool_name": "Bash",
            "tool_input": {
                "command": "find . -name '*.py'"
            }
        }

        # Test 7: Python command (should suggest uv run python)
        python_command = {
            "session_id": "test123",
            "transcript_path": "/tmp/nonexistent.jsonl",
            "hook_event_name": "PreToolUse",
            "tool_name": "Bash",
            "tool_input": {
                "command": "python script.py"
            }
        }

        # Check if we have API key for adjusting test expectations
        has_api_key = bool(os.environ.get("GEMINI_API_KEY"))

        # Run tests
        # Note: All tests should pass consistently
        # Real secrets are always blocked in fast validation tier
        tests = [
            ("Safe file write", safe_write, 0),
            ("Dangerous bash command", dangerous_bash, 2),
            ("File with potential sensitive content", sensitive_file, 2),
            ("Safe bash command", safe_bash, 0),
            ("Grep command (should be blocked, suggest rg)", grep_command, 2),
            ("Find command (should be blocked, suggest rg)", find_command, 2),
            ("Python command (should be blocked, suggest uv)", python_command, 2)
        ]

        print(f"\nStarting parallel test execution...")
        
        # Run tests in parallel
        def run_single_test(test_data):
            test_name, hook_input, expected_exit = test_data
            return self.test_validator(test_name, hook_input, expected_exit)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=7) as executor:
            results = list(executor.map(run_single_test, tests))
        
        elapsed_time = time.time() - start_time

        print(f"\n{'=' * 60}")
        print(f"Test Results: {self.passed}/{self.total} passed")
        print(f"Total execution time: {elapsed_time:.1f} seconds")

        if self.passed == self.total:
            print("✓ All tests passed!")
            return 0
        else:
            print("✗ Some tests failed")
            return 1

def main():
    """Main test runner"""
    test_suite = ValidationTests()
    return test_suite.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())
