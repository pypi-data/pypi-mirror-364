#!/usr/bin/env python3
"""Basic test to verify processor setup is working"""

import asyncio
import os
import json


def test_processor_imports():
    """Test that we can import our processors"""
    try:
        from claude_code_adk_validator.streaming_processors import (
            ValidationProcessor,
            SecurityValidationProcessor,
            TDDValidationProcessor,
            FileCategorizationProcessor,
            ValidationPipelineBuilder,
        )
        print("✓ All processors imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False


def test_processor_creation():
    """Test that processors can be instantiated"""
    try:
        from claude_code_adk_validator.streaming_processors import (
            ValidationProcessor,
            SecurityValidationProcessor,
            TDDValidationProcessor,
            FileCategorizationProcessor,
            ValidationPipelineBuilder,
        )
        
        # Test instantiation
        val_proc = ValidationProcessor()
        sec_proc = SecurityValidationProcessor()
        tdd_proc = TDDValidationProcessor()
        file_proc = FileCategorizationProcessor()
        builder = ValidationPipelineBuilder()
        
        print("✓ All processors instantiated successfully")
        return True
    except Exception as e:
        print(f"✗ Instantiation failed: {e}")
        return False


def test_processor_attributes():
    """Test that processors have expected attributes"""
    try:
        from claude_code_adk_validator.streaming_processors import (
            SecurityValidationProcessor,
            TDDValidationProcessor,
        )
        
        sec_proc = SecurityValidationProcessor()
        tdd_proc = TDDValidationProcessor()
        
        # Check attributes
        assert hasattr(sec_proc, 'processor_type')
        assert sec_proc.processor_type == 'security'
        
        assert hasattr(tdd_proc, 'processor_type')
        assert tdd_proc.processor_type == 'tdd'
        
        print("✓ Processors have expected attributes")
        return True
    except AssertionError as e:
        print(f"✗ Attribute check failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False


async def test_basic_validation_flow():
    """Test basic validation flow without genai-processors specifics"""
    try:
        from claude_code_adk_validator.security_validator import SecurityValidator
        from claude_code_adk_validator.tdd_validator import TDDValidator
        
        # Create validators
        sec_validator = SecurityValidator()
        tdd_validator = TDDValidator()
        
        # Test basic bash command validation
        result = await sec_validator.perform_quick_validation(
            "Bash", 
            {"command": "ls -la"}
        )
        assert result["approved"] is True
        print("✓ Safe bash command allowed")
        
        # Test dangerous command
        result = await sec_validator.perform_quick_validation(
            "Bash",
            {"command": "rm -rf /"}
        )
        assert result["approved"] is False
        print("✓ Dangerous bash command blocked")
        
        # Test grep enforcement
        result = await sec_validator.perform_quick_validation(
            "Bash",
            {"command": "grep pattern file.txt"}
        )
        assert result["approved"] is False
        print("✓ Grep command blocked (use rg)")
        
        # Test eval command (should be blocked now)
        result = await sec_validator.perform_quick_validation(
            "Bash",
            {"command": "echo 'test' && eval \"echo $USER\""}
        )
        assert result["approved"] is False
        print("✓ Eval command blocked")
        
        # Test base64 piping to shell
        result = await sec_validator.perform_quick_validation(
            "Bash",
            {"command": "echo 'ZWNobyBoZWxsbw==' | base64 -d | sh"}
        )
        assert result["approved"] is False
        print("✓ Base64 piping to shell blocked")
        
        # Test file operation with subprocess shell=True
        result = await sec_validator.perform_quick_validation(
            "Write",
            {
                "file_path": "app.py",
                "content": "import subprocess\nsubprocess.run(cmd, shell=True)"
            }
        )
        assert result["approved"] is False
        print("✓ Dynamic code execution with shell=True blocked")
        
        return True
        
    except AssertionError as e:
        print(f"✗ Validation test failed")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("Testing Processor Setup...")
    print("=" * 60)
    
    tests = [
        ("Import Test", test_processor_imports),
        ("Creation Test", test_processor_creation),
        ("Attribute Test", test_processor_attributes),
    ]
    
    passed = 0
    for test_name, test_func in tests:
        print(f"\\nRunning {test_name}...")
        if test_func():
            passed += 1
    
    # Run async test
    print(f"\\nRunning Basic Validation Flow Test...")
    if asyncio.run(test_basic_validation_flow()):
        passed += 1
    
    total = len(tests) + 1
    print(f"\\n{'=' * 60}")
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All processor tests passed!")
        return 0
    else:
        print(f"❌ {total - passed} tests failed")
        return 1


if __name__ == "__main__":
    exit(main())
