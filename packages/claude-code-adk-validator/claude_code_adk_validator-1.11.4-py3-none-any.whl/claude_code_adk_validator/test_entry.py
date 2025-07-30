#!/usr/bin/env python3
"""Test entry point for quick validation tests"""
import asyncio
import sys
import json
import os


def main() -> None:
    """Entry point for tests that provides hook data via argument"""
    if len(sys.argv) < 2:
        print("Usage: test_entry.py <json_data>", file=sys.stderr)
        sys.exit(1)

    # Parse JSON from command line argument
    try:
        hook_input = json.loads(sys.argv[1])
    except json.JSONDecodeError:
        print("Invalid JSON input", file=sys.stderr)
        sys.exit(1)

    # Import and run validator
    from .hybrid_validator import HybridValidator

    # Check for API key
    api_key = os.environ.get("GEMINI_API_KEY")
    is_ci = os.environ.get("CI") == "true"

    if not api_key and not is_ci:
        print("ERROR: GEMINI_API_KEY not configured", file=sys.stderr)
        sys.exit(2)

    # Initialize validator
    validator = HybridValidator(api_key)

    # Extract tool info
    tool_name = hook_input.get("tool_name", "")
    tool_input = hook_input.get("tool_input", {})
    transcript_path = hook_input.get("transcript_path", "")

    # Extract context
    context = validator.security_validator.extract_conversation_context(transcript_path)

    # Run validation
    result = asyncio.run(validator.validate_tool_use(tool_name, tool_input, context))
    validator.security_validator.cleanup_uploaded_files()

    # Print result and exit
    if not result.get("approved", False):
        print(f"ERROR: {result.get('reason', 'Validation failed')}", file=sys.stderr)
        if result.get("suggestions"):
            for suggestion in result.get("suggestions", []):
                print(f"→ {suggestion}", file=sys.stderr)
        sys.exit(2)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
