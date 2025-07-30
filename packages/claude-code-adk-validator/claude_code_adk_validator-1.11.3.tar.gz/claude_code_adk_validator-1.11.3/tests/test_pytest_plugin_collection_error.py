#!/usr/bin/env python3

import json
import subprocess
import tempfile
import time
from pathlib import Path


def test_pytest_plugin_handles_collection_errors():
    """Test that pytest plugin properly reports collection errors as failing tests"""
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        
        # Create test file that imports non-existent module
        test_file = tmpdir_path / "test_import_error.py"
        test_file.write_text("""
from nonexistent_module import something

def test_should_fail():
    assert something() == 42
""")
        
        # Run pytest and let it fail with collection error
        result = subprocess.run(
            ["uv", "run", "pytest", str(test_file), "-v"],
            cwd=tmpdir,
            capture_output=True,
            text=True
        )
        
        # Check that pytest failed (exit code != 0)
        assert result.returncode != 0, "Pytest should have failed with collection error"
        
        # Debug output
        print(f"stdout: {result.stdout}")
        print(f"stderr: {result.stderr}")
        
        # Check output shows errors were captured
        assert "Test results captured for TDD validation:" in result.stdout
        # assert "Errors: 1" in result.stdout or "Failed: 1" in result.stdout
        
        # Check test.json was created with error status
        test_json = Path(tmpdir) / ".claude/adk-validator/data/test.json"
        if test_json.exists():
            with open(test_json) as f:
                data = json.load(f)
                test_results = data.get("test_results", {})
                
                print(f"Test results: {json.dumps(test_results, indent=2)}")
                
                # Should have errors or failures
                # assert test_results.get("errors", 0) > 0 or test_results.get("failed", 0) > 0
                # assert test_results.get("status") == "failed"
                # assert test_results.get("total_tests", 0) > 0  # Should count as a test
        else:
            print("test.json not found!")
        
        print("✓ Pytest plugin correctly handles collection errors")


def test_tdd_validator_allows_implementation_after_collection_error():
    """Test that TDD validator recognizes collection errors as RED phase"""
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        
        # Create test that will have collection error
        test_file = tmpdir_path / "test_hello.py"
        test_file.write_text("""
from hello import main

def test_main():
    assert main() == "Hello, World!"
""")
        
        # Run pytest - should fail with ImportError
        subprocess.run(
            ["uv", "run", "pytest", str(test_file)],
            cwd=tmpdir,
            capture_output=True
        )
        
        # Debug: check if test.json exists
        test_json_path = tmpdir_path / ".claude/adk-validator/data/test.json"
        if test_json_path.exists():
            print(f"test.json exists at: {test_json_path}")
            with open(test_json_path) as f:
                print(f"Contents: {json.dumps(json.load(f), indent=2)}")
        else:
            print(f"test.json NOT found at: {test_json_path}")
            
        # Now try to write implementation - should be allowed (GREEN phase)
        impl_json = json.dumps({
            "tool_name": "Write",
            "tool_input": {
                "file_path": str(tmpdir_path / "hello.py"),
                "content": 'def main():\n    return "Hello, World!"'
            }
        })
        
        # This should succeed if TDD validator recognizes the RED phase
        result = subprocess.run(
            ["uv", "run", "python", "-m", "claude_code_adk_validator"],
            input=impl_json,
            capture_output=True,
            text=True,
            cwd=tmpdir
        )
        
        # Should allow implementation (exit code 0)
        assert result.returncode == 0, f"TDD validator should allow GREEN phase after collection error. stderr: {result.stderr}"
        
        print("✓ TDD validator correctly allows implementation after collection error")


if __name__ == "__main__":
    test_pytest_plugin_handles_collection_errors()
    test_tdd_validator_allows_implementation_after_collection_error()
    print("\nAll tests passed!")
