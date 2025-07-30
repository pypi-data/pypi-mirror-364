#!/usr/bin/env python3

import sys
import os
import threading
import concurrent.futures
import time

# Add the package to Python path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from claude_code_adk_validator.file_categorization import FileContextAnalyzer

class FileCategorizationTests:
    """File categorization test suite with parallel execution"""
    
    def __init__(self):
        self.passed = 0
        self.total = 0
        self.lock = threading.Lock()  # Thread safety for counters
        
    def test_single_categorization(self, test_case):
        """Test a single file categorization case"""
        with self.lock:
            self.total += 1
            
        print(f"\n--- {test_case['name']} ---")
        
        result = FileContextAnalyzer.categorize_file(
            test_case['file_path'], 
            test_case['content']
        )
        
        # Check categorization results
        category_ok = result.get('category') == test_case['expected_category']
        is_test_ok = result.get('is_test_file') == test_case['expected_is_test']
        strict_security_ok = result.get('requires_strict_security') == test_case['expected_strict_security']
        
        print(f"Path: {test_case['file_path']}")
        print(f"Expected: category={test_case['expected_category']}, is_test={test_case['expected_is_test']}, strict_security={test_case['expected_strict_security']}")
        print(f"Got:      category={result.get('category')}, is_test={result.get('is_test_file')}, strict_security={result.get('requires_strict_security')}")
        print(f"Reason: {result.get('reason')}")
        
        if category_ok and is_test_ok and strict_security_ok:
            print("✓ PASSED")
            with self.lock:
                self.passed += 1
            return True
        else:
            print("✗ FAILED")
            if not category_ok:
                print(f"  Category mismatch: expected {test_case['expected_category']}, got {result.get('category')}")
            if not is_test_ok:
                print(f"  is_test_file mismatch: expected {test_case['expected_is_test']}, got {result.get('is_test_file')}")
            if not strict_security_ok:
                print(f"  requires_strict_security mismatch: expected {test_case['expected_strict_security']}, got {result.get('requires_strict_security')}")
            return False
    
    def test_file_categorization(self):
        """Test FileContextAnalyzer categorization logic with parallel execution"""
        print("Testing FileContextAnalyzer categorization")
        print("=" * 50)
        print("PARALLEL EXECUTION: Running 10 tests concurrently")
        print("=" * 50)
        
        start_time = time.time()

        test_cases = [
        # Test files
        {
            "name": "Test file by path - tests/conftest.py",
            "file_path": "tests/conftest.py",
            "content": "import pytest\n@pytest.fixture\ndef test_data():\n    return 'test'",
            "expected_category": "test",
            "expected_is_test": True,
            "expected_strict_security": False
        },
        {
            "name": "Test file by content - test_auth.py", 
            "file_path": "test_auth.py",
            "content": "def test_login():\n    assert True\n\ndef test_logout():\n    assert True",
            "expected_category": "test",
            "expected_is_test": True,
            "expected_strict_security": False
        },
        
        # Configuration files
        {
            "name": "Config file - .env.example",
            "file_path": ".env.example", 
            "content": "DATABASE_URL=postgres://localhost\nAPI_KEY=your_key_here",
            "expected_category": "config",
            "expected_is_test": False,
            "expected_strict_security": False
        },
        {
            "name": "Config file - pyproject.toml",
            "file_path": "pyproject.toml",
            "content": "[tool.pytest]\ntestpaths = ['tests']",
            "expected_category": "config", 
            "expected_is_test": False,
            "expected_strict_security": False
        },
        
        # Documentation files
        {
            "name": "Documentation - README.md",
            "file_path": "README.md",
            "content": "# My Project\n\nExample usage:\n```python\napi_key = 'your-key-here'\n```",
            "expected_category": "docs",
            "expected_is_test": False,
            "expected_strict_security": False
        },
        
        # Structural files
        {
            "name": "Structural file - __init__.py (empty)",
            "file_path": "src/__init__.py",
            "content": "",
            "expected_category": "structural",
            "expected_is_test": False,
            "expected_strict_security": False
        },
        {
            "name": "Structural file - __init__.py (imports only)",
            "file_path": "package/__init__.py", 
            "content": "from .module import function\nfrom .utils import helper\n\n__version__ = '1.0.0'",
            "expected_category": "structural",
            "expected_is_test": False,
            "expected_strict_security": False
        },
        
        # Implementation files (should require strict security)
        {
            "name": "Implementation file - app.py",
            "file_path": "src/app.py",
            "content": "def process_payment(amount):\n    if amount > 0:\n        return charge_card(amount)\n    return False",
            "expected_category": "implementation",
            "expected_is_test": False,
            "expected_strict_security": True
        },
        {
            "name": "Implementation file - server.py",
            "file_path": "server.py",
            "content": "from flask import Flask\n\napp = Flask(__name__)\n\n@app.route('/')\ndef home():\n    return 'Hello World'",
            "expected_category": "implementation",
            "expected_is_test": False,
            "expected_strict_security": True
        },
        
        # Data files
        {
            "name": "Lock file - package-lock.json",
            "file_path": "package-lock.json",
            "content": '{"name": "project", "lockfileVersion": 1}',
            "expected_category": "data",  # Lock files are categorized as data
            "expected_is_test": False,
            "expected_strict_security": False
        },
        {
            "name": "Schema file - schema.sql",
            "file_path": "db/schema.sql", 
            "content": "CREATE TABLE users (id INT PRIMARY KEY);",
            "expected_category": "data",
            "expected_is_test": False,
            "expected_strict_security": False
        }
        ]
        
        print(f"\nStarting parallel test execution...")
        
        # Run tests in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(self.test_single_categorization, test_cases))
        
        elapsed_time = time.time() - start_time
        
        print(f"\n{'=' * 50}")
        print(f"File Categorization Test Results: {self.passed}/{self.total} passed")
        print(f"Total execution time: {elapsed_time:.1f} seconds")
        
        return self.passed == self.total

    def test_test_secret_patterns(self):
        """Test the test secret patterns functionality"""
        print("\n\nTesting test secret patterns")
        print("=" * 50)
        
        with self.lock:
            self.total += 1
        
        patterns = FileContextAnalyzer.get_test_secret_patterns()
        
        print("Test secret patterns:")
        for pattern in patterns:
            print(f"  - {pattern}")
        
        # Test that expected patterns are present
        expected_patterns = ["test[_-]", "mock[_-]", "dummy[_-]", "fake[_-]", "example[_-]"]
        
        missing_patterns = []
        for expected in expected_patterns:
            if expected not in patterns:
                missing_patterns.append(expected)
        
        if missing_patterns:
            print(f"✗ FAILED - Missing patterns: {missing_patterns}")
            return False
        else:
            print("✓ PASSED - All expected patterns present")
            with self.lock:
                self.passed += 1
            return True
    
    def run_all_tests(self):
        """Run all file categorization tests in parallel"""
        print("Testing File Context Analysis for Context-Aware Validation")
        print("=" * 60)
        print("PARALLEL EXECUTION: Running test suites concurrently")
        print("=" * 60)
        
        start_time = time.time()
        
        # Define test suites to run in parallel
        test_suites = [
            ("File Categorization", self.test_file_categorization),
            ("Test Secret Patterns", self.test_test_secret_patterns)
        ]
        
        print("Starting parallel test suite execution...")
        
        # Execute test suites in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            future_to_test = {executor.submit(test_func): test_name
                            for test_name, test_func in test_suites}
            
            results = {}
            for future in concurrent.futures.as_completed(future_to_test):
                test_name = future_to_test[future]
                try:
                    result = future.result()
                    results[test_name] = result
                    print(f"✓ {test_name} suite completed")
                except Exception as e:
                    results[test_name] = False
                    print(f"✗ {test_name} suite failed with error: {e}")
        
        elapsed_time = time.time() - start_time
        
        print(f"\n{'=' * 60}")
        print(f"FINAL RESULTS: {self.passed}/{self.total} tests passed")
        print(f"Total execution time: {elapsed_time:.1f} seconds")
        
        if self.passed == self.total:
            print("All file context analysis tests PASSED!")
            print("FileContextAnalyzer is working correctly for context-aware validation")
            return 0
        else:
            print("Some file context analysis tests FAILED!")
            return 1

def main():
    """Main test runner"""
    test_suite = FileCategorizationTests()
    return test_suite.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())
