#!/usr/bin/env python3

import json
import os
import subprocess
import time
from pathlib import Path


def test_tdd_workflow_with_collection_error():
    """Test complete TDD workflow with pytest collection error"""
    
    # Create a test directory
    test_dir = Path("test_tdd_workflow")
    test_dir.mkdir(exist_ok=True)
    
    # Change to test directory
    original_dir = os.getcwd()
    os.chdir(test_dir)
    
    try:
        # Step 1: Write a test that imports non-existent module
        test_file = Path("test_calculator.py")
        test_file.write_text("""
from calculator import add

def test_add():
    assert add(2, 3) == 5
""")
        
        # Step 2: Run pytest - should fail with collection error (RED phase)
        result = subprocess.run(
            ["uv", "run", "pytest", "test_calculator.py", "-v"],
            capture_output=True,
            text=True
        )
        
        print(f"Pytest exit code: {result.returncode}")
        print(f"Pytest stdout:\n{result.stdout}")
        
        # Should see collection error  
        assert result.returncode != 0
        assert "Test results captured for TDD validation:" in result.stdout
        assert "Errors: 1" in result.stdout
        
        # Check test.json was created - it might be in parent directory due to pytest rootdir
        test_json = Path(".claude/adk-validator/data/test.json")
        if not test_json.exists():
            # Check parent directory
            parent_test_json = Path("../.claude/adk-validator/data/test.json")
            if parent_test_json.exists():
                print(f"test.json found in parent directory: {parent_test_json.absolute()}")
                test_json = parent_test_json
            else:
                # List all test.json files
                import subprocess
                result = subprocess.run(["find", "..", "-name", "test.json", "-type", "f"], 
                                     capture_output=True, text=True)
                print(f"Found test.json files:\n{result.stdout}")
                assert False, f"test.json not found at {test_json.absolute()}"
        
        with open(test_json) as f:
            data = json.load(f)
            test_results = data["test_results"]
            print(f"Test results: {json.dumps(test_results, indent=2)}")
            
            assert test_results["errors"] == 1
            assert test_results["status"] == "failed"
            assert test_results["total_tests"] == 1
        
        # Wait a moment to ensure file is written
        time.sleep(0.1)
        
        # Step 3: Write implementation - should be allowed (GREEN phase)
        impl_json = {
            "tool_name": "Write",
            "tool_input": {
                "file_path": "calculator.py",
                "content": "def add(a, b):\n    return a + b"
            }
        }
        
        # Run validator from the same directory where pytest ran
        result = subprocess.run(
            ["uv", "run", "python", "-m", "claude_code_adk_validator"],
            input=json.dumps(impl_json),
            capture_output=True,
            text=True,
            cwd=os.getcwd()  # Explicitly set working directory
        )
        
        print(f"Validator exit code: {result.returncode}")
        print(f"Validator stderr:\n{result.stderr}")
        
        # Should allow implementation
        assert result.returncode == 0, "TDD validator should allow GREEN phase after collection error"
        
        # Step 4: Run tests again - should pass (verify GREEN)
        result = subprocess.run(
            ["uv", "run", "pytest", "test_calculator.py", "-v"],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0, "Tests should pass after implementation"
        assert "1 passed" in result.stdout
        
        print("✓ TDD workflow with collection error works correctly!")
        
    finally:
        # Clean up
        os.chdir(original_dir)
        subprocess.run(["rm", "-rf", str(test_dir)], check=False)


if __name__ == "__main__":
    test_tdd_workflow_with_collection_error()
