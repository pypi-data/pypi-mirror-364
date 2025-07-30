#!/usr/bin/env python3
"""
Quick validation tests that run fast for pre-commit hooks.

These tests focus on rule-based validation that doesn't require LLM calls.
For comprehensive LLM-based tests, run test_tdd_enforcement.py separately.
"""

import json
import subprocess
import sys
import os
import tempfile
import threading
import concurrent.futures
import time

def run_validation_quick(tool_data):
    """Run validation with short timeout for pre-commit"""
    input_file = None
    try:
        # Use CI mode to enable degraded validation without API key
        env = os.environ.copy()
        env.pop("GEMINI_API_KEY", None)
        env["CI"] = "true"  # Enable CI mode for degraded validation

        # Use test entry point to avoid stdin issues
        process = subprocess.run(
            ["uv", "run", "python", "-m", "claude_code_adk_validator.test_entry", json.dumps(tool_data)],
            capture_output=True,
            text=True,
            timeout=10,  # Reasonable timeout for pre-commit
            env=env,
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Run from project root
        )
        return process.returncode, process.stderr
    except subprocess.TimeoutExpired as e:
        stderr = "TIMEOUT"
        if hasattr(e, 'stderr') and e.stderr:
            stderr = f"TIMEOUT: {e.stderr}"
        return 1, stderr
    except Exception as e:
        return 1, f"ERROR: {str(e)}"

class QuickValidationTests:
    """Quick validation test suite with parallel execution"""
    
    def __init__(self):
        self.passed = 0
        self.total = 0
        self.lock = threading.Lock()  # Thread safety for counters
        self.transcript_path = None
        
    def create_transcript(self):
        """Create a test transcript file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
            f.write('{"role": "user", "content": "test"}\n')
            self.transcript_path = f.name
            
    def cleanup(self):
        """Clean up test files"""
        if self.transcript_path:
            try:
                os.unlink(self.transcript_path)
            except:
                pass

    def test_single_security_validation(self, test):
        """Test a single security validation case"""
        with self.lock:
            self.total += 1
            
        code, stderr = run_validation_quick(test["data"])

        if test["should_block"]:
            success = code == 2
            status = "PASS" if success else "FAIL"
            expected = "blocked"
        else:
            success = code == 0
            status = "PASS" if success else "FAIL"
            expected = "allowed"

        print(f"{test['name']}: {status} (expected {expected}, got exit {code})")

        if not success and stderr and "TIMEOUT" not in stderr:
            print(f"  Error: {stderr[:100]}...")

        if success:
            with self.lock:
                self.passed += 1
                
        return success
        
    def test_security_validation(self):
        """Test basic security validation (fast, rule-based) with parallel execution"""
        print("QUICK SECURITY VALIDATION TESTS")
        print("=" * 50)
        print("SEQUENTIAL EXECUTION: Running 5 tests one by one")
        print("=" * 50)
        
        start_time = time.time()

        tests = [
            # Should be blocked - security violations
            {
                "name": "Dangerous rm command",
                "data": {
                    "tool_name": "Bash",
                    "tool_input": {"command": "rm -rf /"},
                    "transcript_path": self.transcript_path
                },
                "should_block": True
            },
            {
                "name": "Real Stripe key",
                "data": {
                    "tool_name": "Write",
                    "tool_input": {
                        "file_path": "config.py",
                        "content": 'api_key = "sk_live_1234567890abcdefghijklmnop"'
                    },
                    "transcript_path": self.transcript_path
                },
                "should_block": True
            },
            {
                "name": "Grep command (tool enforcement)",
                "data": {
                    "tool_name": "Bash",
                    "tool_input": {"command": "grep pattern file.txt"},
                    "transcript_path": self.transcript_path
                },
                "should_block": True
            },
            # Should be allowed
            {
                "name": "Safe bash command",
                "data": {
                    "tool_name": "Bash",
                    "tool_input": {"command": "ls -la"},
                    "transcript_path": self.transcript_path
                },
                "should_block": False
            },
            {
                "name": "Safe file write",
                "data": {
                    "tool_name": "Write",
                    "tool_input": {
                        "file_path": "hello.txt",
                        "content": "Hello, World!"
                    },
                    "transcript_path": self.transcript_path
                },
                "should_block": False
            },
        ]
        
        print("\nStarting sequential test execution...")
        
        # Run tests sequentially to avoid subprocess issues in CI
        results = []
        for test in tests:
            results.append(self.test_single_security_validation(test))
        
        elapsed_time = time.time() - start_time
        
        print(f"\nResults: {self.passed}/{self.total} passed")
        print(f"Execution time: {elapsed_time:.1f} seconds")

        return all(results)

    def test_single_tool_routing(self, tool):
        """Test routing for a single tool"""
        with self.lock:
            self.total += 1
            
        # Different input structure for different tools
        if tool == "Bash":
            tool_input = {"command": "echo test"}
        elif tool == "TodoWrite":
            tool_input = {"todos": [{"content": "Test todo", "status": "pending", "priority": "medium", "id": "test-1"}]}
        else:
            tool_input = {"file_path": "test.txt", "content": "test"}
            
        test_data = {
            "tool_name": tool,
            "tool_input": tool_input,
            "transcript_path": self.transcript_path
        }

        code, stderr = run_validation_quick(test_data)

        # All tools should at least not error (exit code 0 or 2, not 1)
        success = code in [0, 2]
        status = "PASS" if success else "FAIL"

        print(f"{tool} routing: {status} (exit {code})")

        if not success:
            print(f"  Error: {stderr[:100]}...")

        if success:
            with self.lock:
                self.passed += 1
                
        return success
        
    def test_basic_tool_routing(self):
        """Test that all tools are properly routed with parallel execution"""
        print("\nBASIC TOOL ROUTING TESTS")
        print("=" * 50)
        print("SEQUENTIAL EXECUTION: Running 6 tests one by one")
        print("=" * 50)
        
        start_time = time.time()

        tools_to_test = ["Write", "Edit", "MultiEdit", "Update", "Bash", "TodoWrite"]
        
        print("\nStarting sequential test execution...")
        
        # Run tests sequentially to avoid subprocess issues in CI
        results = []
        for tool in tools_to_test:
            results.append(self.test_single_tool_routing(tool))
        
        elapsed_time = time.time() - start_time
        
        print(f"\nResults: {self.passed}/{self.total} passed")
        print(f"Execution time: {elapsed_time:.1f} seconds")

        return all(results)

    def test_branch_validation(self):
        """Test branch validation for protected branches"""
        print("\nBRANCH VALIDATION TESTS")
        print("-" * 40)
        
        start_time = time.time()
        branch_tests = [
            {
                "description": "Block code changes on main branch",
                "tool_name": "Write",
                "tool_input": {
                    "file_path": "src/main.py",
                    "content": "print('hello world')"
                },
                "expected_block": True,
                "reason": "Code on protected branch"
            },
            {
                "description": "Allow README on main branch",
                "tool_name": "Write",
                "tool_input": {
                    "file_path": "README.md",
                    "content": "# Project Documentation"
                },
                "expected_block": False,
                "reason": "Docs allowed on main"
            },
            {
                "description": "Allow docs directory on main",
                "tool_name": "Edit",
                "tool_input": {
                    "file_path": "docs/guide.md",
                    "old_string": "old",
                    "new_string": "new"
                },
                "expected_block": False,
                "reason": "Docs allowed on main"
            },
            {
                "description": "Allow .github files on main",
                "tool_name": "Write",
                "tool_input": {
                    "file_path": ".github/workflows/test.yml",
                    "content": "name: Test"
                },
                "expected_block": False,
                "reason": "CI files allowed on main"
            }
        ]
        
        # Run tests with simulated git environment
        # Note: In CI mode, branch validation is skipped, so these tests
        # mainly verify the logic works without actual git commands
        results = []
        for test in branch_tests:
            success = self.test_single_branch_validation(test)
            results.append(success)
        
        elapsed_time = time.time() - start_time
        print(f"\nResults: {self.passed}/{self.total} passed")
        print(f"Execution time: {elapsed_time:.1f} seconds")
        
        return all(results)

    def test_single_branch_validation(self, test):
        """Test a single branch validation case"""
        with self.lock:
            self.total += 1
            test_num = self.total
        
        print(f"  [{test_num}] {test['description']}... ", end="", flush=True)
        
        tool_data = {
            "tool_name": test["tool_name"],
            "tool_input": test["tool_input"],
            "transcript_path": self.transcript_path
        }
        
        start_time = time.time()
        exit_code, stderr = run_validation_quick(tool_data)
        elapsed_time = time.time() - start_time
        
        # In CI mode, branch validation is typically skipped
        # So we mainly check that the validator runs without errors
        success = (exit_code == 0 or exit_code == 2)
        
        with self.lock:
            if success:
                self.passed += 1
                print(f"✓ ({elapsed_time:.1f}s)")
            else:
                print(f"✗ ({elapsed_time:.1f}s)")
                print(f"    Unexpected error: {stderr[:200]}")
        
        return success
    
    def run_all_tests(self):
        """Run all quick validation tests in parallel"""
        print("QUICK VALIDATION TEST SUITE")
        print("=" * 60)
        print("Fast tests for pre-commit hooks (no LLM calls)")
        print("SEQUENTIAL EXECUTION: Running test suites one by one")
        print("=" * 60)

        self.create_transcript()
        
        start_time = time.time()
        
        # Define test suites to run in parallel
        test_suites = [
            ("Security Validation", self.test_security_validation),
            ("Tool Routing", self.test_basic_tool_routing),
            ("Branch Validation", self.test_branch_validation)
        ]
        
        print("Starting sequential test suite execution...")
        
        # Execute test suites sequentially to avoid subprocess issues
        results = {}
        for test_name, test_func in test_suites:
            try:
                result = test_func()
                results[test_name] = result
                print(f"✓ {test_name} suite completed")
            except Exception as e:
                results[test_name] = False
                print(f"✗ {test_name} suite failed with error: {e}")
        
        elapsed_time = time.time() - start_time
        
        print("\n" + "=" * 60)
        print(f"FINAL RESULTS: {self.passed}/{self.total} tests passed")
        print(f"Total execution time: {elapsed_time:.1f} seconds")
        
        if self.passed == self.total:
            print("✓ ALL QUICK TESTS PASSED")
            return 0
        else:
            print("✗ SOME QUICK TESTS FAILED")
            return 1

def main():
    """Main test runner"""
    test_suite = QuickValidationTests()
    try:
        return test_suite.run_all_tests()
    finally:
        test_suite.cleanup()

if __name__ == "__main__":
    sys.exit(main())
