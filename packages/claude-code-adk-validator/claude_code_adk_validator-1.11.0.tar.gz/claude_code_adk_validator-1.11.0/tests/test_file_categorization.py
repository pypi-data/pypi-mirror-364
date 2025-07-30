#!/usr/bin/env python3
"""
File categorization tests for TDD validation.

This test suite verifies that the file categorization system correctly
identifies which files require TDD validation and which don't.

Run with: uv run python tests/test_file_categorization.py
"""

import sys
import os
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from claude_code_adk_validator.tdd_validator import TDDValidator

class FileCategorizationTests:
    """Test suite for file categorization logic"""

    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY")
        self.validator = TDDValidator(self.api_key)
        self.passed = 0
        self.total = 0

    def assert_category(self, file_path, content, expected_category, expected_requires_tdd):
        """Assert that file is categorized correctly"""
        self.total += 1
        
        try:
            result = self.validator.categorize_file(file_path, content)
            category = result.get("category")
            requires_tdd = result.get("requires_tdd")
            reason = result.get("reason", "")
            
            print(f"\nTesting: {file_path}")
            print(f"Content preview: {content[:50]}..." if content else "Empty file")
            print(f"Expected: {expected_category}, requires_tdd={expected_requires_tdd}")
            print(f"Actual: {category}, requires_tdd={requires_tdd}")
            print(f"Reason: {reason}")
            
            if category == expected_category and requires_tdd == expected_requires_tdd:
                print("✓ PASSED")
                self.passed += 1
                return True
            else:
                print("✗ FAILED")
                return False
                
        except Exception as e:
            print(f"\nTesting: {file_path}")
            print(f"✗ ERROR: {e}")
            return False

    def test_implementation_files(self):
        """Test that implementation files are correctly categorized"""
        test_cases = [
            ("calculator.py", "def add(a, b):\n    return a + b", "implementation", True),
            ("utils.py", "def helper():\n    pass", "implementation", True),
            ("main.py", "if __name__ == '__main__':\n    main()", "implementation", True),
            ("service.py", "class UserService:\n    def create_user(self):\n        pass", "implementation", True),
        ]
        
        results = []
        for file_path, content, expected_category, expected_requires_tdd in test_cases:
            result = self.assert_category(file_path, content, expected_category, expected_requires_tdd)
            results.append(result)
        
        return all(results)

    def test_test_files(self):
        """Test that test files are correctly categorized"""
        test_cases = [
            ("test_calculator.py", "def test_add():\n    assert True", "test", False),
            ("test_utils.py", "import pytest\n\ndef test_helper():\n    pass", "test", False),
            ("tests/test_main.py", "def test_main():\n    pass", "test", False),
            ("spec_calculator.py", "def spec_add():\n    pass", "test", False),
        ]
        
        results = []
        for file_path, content, expected_category, expected_requires_tdd in test_cases:
            result = self.assert_category(file_path, content, expected_category, expected_requires_tdd)
            results.append(result)
        
        return all(results)

    def test_structural_files(self):
        """Test that structural files are correctly categorized"""
        test_cases = [
            ("__init__.py", "", "structural", False),
            ("__init__.py", "from .module import function", "structural", False),
            ("__main__.py", "from .cli import main\n\nif __name__ == '__main__':\n    main()", "structural", False),
            ("conftest.py", "import pytest", "structural", False),
            ("constants.py", "API_VERSION = '1.0'\nDATABASE_URL = 'sqlite:///app.db'", "structural", False),
        ]
        
        results = []
        for file_path, content, expected_category, expected_requires_tdd in test_cases:
            result = self.assert_category(file_path, content, expected_category, expected_requires_tdd)
            results.append(result)
        
        return all(results)

    def test_config_files(self):
        """Test that configuration files are correctly categorized"""
        test_cases = [
            ("setup.py", "from setuptools import setup", "config", False),
            ("pyproject.toml", "[tool.pytest]", "config", False),
            ("requirements.txt", "pytest==7.0.0", "config", False),
            ("Dockerfile", "FROM python:3.11", "config", False),
            ("config.json", '{"debug": true}', "config", False),
        ]
        
        results = []
        for file_path, content, expected_category, expected_requires_tdd in test_cases:
            result = self.assert_category(file_path, content, expected_category, expected_requires_tdd)
            results.append(result)
        
        return all(results)

    def test_documentation_files(self):
        """Test that documentation files are correctly categorized"""
        test_cases = [
            ("README.md", "# Project Title", "docs", False),
            ("CHANGELOG.md", "## Version 1.0.0", "docs", False),
            ("docs/api.rst", "API Documentation", "docs", False),
            ("guide.txt", "User guide content", "docs", False),
        ]
        
        results = []
        for file_path, content, expected_category, expected_requires_tdd in test_cases:
            result = self.assert_category(file_path, content, expected_category, expected_requires_tdd)
            results.append(result)
        
        return all(results)

    def test_edge_cases(self):
        """Test edge cases and complex scenarios"""
        test_cases = [
            # Empty implementation file should still require tests if it will have logic
            ("calculator.py", "", "structural", False),  # Empty files are structural
            
            # __init__.py with actual logic should require tests
            ("__init__.py", "def factory():\n    return SomeClass()", "implementation", True),
            
            # Configuration with computed values might be implementation
            ("settings.py", "DATABASE_URL = os.environ.get('DB_URL', 'sqlite:///default.db')", "implementation", True),
        ]
        
        results = []
        for file_path, content, expected_category, expected_requires_tdd in test_cases:
            result = self.assert_category(file_path, content, expected_category, expected_requires_tdd)
            results.append(result)
        
        return all(results)

    def test_fallback_behavior(self):
        """Test behavior when API is unavailable"""
        # Test with no API key
        validator_no_api = TDDValidator(api_key=None)
        
        print(f"\nTesting fallback behavior (no API key):")
        result = validator_no_api.categorize_file("calculator.py", "def add(a, b):\n    return a + b")
        
        print(f"Result: {result}")
        
        # Should fall back to safe defaults
        if result.get("category") in ["implementation", "structural"] and isinstance(result.get("requires_tdd"), bool):
            print("✓ PASSED - Fallback behavior works")
            self.passed += 1
        else:
            print("✗ FAILED - Fallback behavior broken")
        
        self.total += 1
        return True

    def run_all_tests(self):
        """Run all categorization tests"""
        print("FILE CATEGORIZATION TEST SUITE")
        print("=" * 80)
        print("Verifying TDD file categorization logic")
        if not self.api_key:
            print("WARNING: No GEMINI_API_KEY - testing fallback behavior only")
        print("=" * 80)

        tests = [
            ("Implementation Files", self.test_implementation_files),
            ("Test Files", self.test_test_files),
            ("Structural Files", self.test_structural_files),
            ("Config Files", self.test_config_files),
            ("Documentation Files", self.test_documentation_files),
            ("Edge Cases", self.test_edge_cases),
            ("Fallback Behavior", self.test_fallback_behavior),
        ]

        for test_name, test_func in tests:
            print(f"\n{'='*60}")
            print(f"TESTING: {test_name}")
            print('='*60)
            
            try:
                test_func()
            except Exception as e:
                print(f"✗ TEST SUITE ERROR: {e}")
                self.total += 1

        print(f"\n{'=' * 80}")
        print(f"FINAL RESULTS: {self.passed}/{self.total} categorization tests passed")
        
        if self.passed == self.total:
            print("🎉 ALL TESTS PASSED - File categorization is working correctly!")
            return 0
        else:
            print("❌ SOME TESTS FAILED - File categorization has issues!")
            failure_rate = (self.total - self.passed) / self.total * 100
            print(f"   Failure rate: {failure_rate:.1f}%")
            return 1

def main():
    """Main test runner"""
    test_suite = FileCategorizationTests()
    return test_suite.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())
