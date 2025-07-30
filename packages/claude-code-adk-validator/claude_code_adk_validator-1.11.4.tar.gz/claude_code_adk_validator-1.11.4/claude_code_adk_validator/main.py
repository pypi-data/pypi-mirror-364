#!/usr/bin/env python3
"""
Main entry point for Claude Code ADK-Inspired Validator.

This module provides the command-line interface for the validator,
allowing it to be used with uvx and as a console script.
"""

import asyncio
import sys
import json
import os
import argparse
import subprocess
from pathlib import Path

from .hybrid_validator import HybridValidator
from .config import DEFAULT_HOOK_TIMEOUT
from .test_reporters import store_manual_test_results


def _is_uv_project() -> bool:
    """Check if current directory is a uv project."""
    cwd = Path.cwd()
    return (cwd / "pyproject.toml").exists() and (
        (cwd / "uv.lock").exists() or _has_uv_command()
    )


def _has_uv_command() -> bool:
    """Check if uv command is available."""
    try:
        subprocess.run(["uv", "--version"], capture_output=True, check=True, timeout=5)
        return True
    except (
        subprocess.CalledProcessError,
        FileNotFoundError,
        subprocess.TimeoutExpired,
    ):
        return False


def _install_package_as_dev_dependency() -> tuple[bool, str]:
    """Install package as dev dependency in uv project."""
    try:
        result = subprocess.run(
            ["uv", "add", "--dev", "claude-code-adk-validator"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            return True, "Package installed successfully as dev dependency"
        else:
            return False, f"Installation failed: {result.stderr.strip()}"
    except subprocess.TimeoutExpired:
        return False, "Installation timed out"
    except FileNotFoundError:
        return False, "uv command not found"
    except Exception as e:
        return False, f"Installation error: {str(e)}"


def setup_claude_hooks(
    validator_command: str = "uvx claude-code-adk-validator",
) -> None:
    """Setup Claude Code hooks configuration."""
    claude_dir = Path.cwd() / ".claude"
    settings_file = claude_dir / "settings.local.json"

    # Create .claude directory if it doesn't exist
    claude_dir.mkdir(exist_ok=True)

    # Hook configuration
    hook_config = {
        "hooks": {
            "PreToolUse": [
                {
                    "matcher": "Write|Edit|Bash|MultiEdit|Update|TodoWrite",
                    "hooks": [
                        {
                            "type": "command",
                            "command": validator_command,
                            "timeout": DEFAULT_HOOK_TIMEOUT,
                        }
                    ],
                }
            ]
        }
    }

    # Merge with existing configuration if present
    if settings_file.exists():
        try:
            with open(settings_file, "r") as f:
                existing_config = json.load(f)

            # Merge configurations
            if "hooks" in existing_config:
                existing_config["hooks"].update(hook_config["hooks"])
            else:
                existing_config.update(hook_config)

            hook_config = existing_config
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not read existing configuration: {e}")
            print("Creating new configuration...")

    # Write configuration
    try:
        with open(settings_file, "w") as f:
            json.dump(hook_config, f, indent=2)

        print("SUCCESS: Claude Code hooks configured successfully!")
        print(f"Configuration written to: {settings_file}")
        print(f"Hook command: {validator_command}")

        # Try to setup pytest plugin integration
        pytest_setup_success = False
        if _is_uv_project():
            print("\nDetected uv project - setting up pytest plugin integration...")
            install_success, install_message = _install_package_as_dev_dependency()

            if install_success:
                print(f"SUCCESS: {install_message}")
                print("SUCCESS: Pytest plugin integration ready!")
                pytest_setup_success = True
            else:
                print(f"WARNING: {install_message}")
                print("Manual setup required for pytest plugin:")
                print("   uv add --dev claude-code-adk-validator")
        else:
            print("\nFor pytest plugin integration in non-uv projects:")
            print("   pip install claude-code-adk-validator")
            print("   # or add to your requirements-dev.txt / pyproject.toml")

        # Provide usage instructions
        print("\nSetup Complete!")
        print("Claude Code hooks: Ready")
        if pytest_setup_success:
            print("Pytest plugin: Ready (run 'pytest' to auto-capture test results)")
        else:
            print("Pytest plugin: Manual installation needed")

        # Check for API key
        if not os.environ.get("GEMINI_API_KEY"):
            print(
                "\nWARNING: Don't forget to set your GEMINI_API_KEY environment variable:"
            )
            print("   export GEMINI_API_KEY='your_gemini_api_key'")

    except IOError as e:
        print(f"ERROR: Error writing configuration: {e}")
        sys.exit(1)


def validate_hook_input() -> None:
    """Main validation function for Claude Code hooks."""
    try:
        # Read hook input from stdin
        stdin_input = sys.stdin.read()
        hook_input = json.loads(stdin_input)
    except json.JSONDecodeError:
        print("Invalid JSON input", file=sys.stderr)
        sys.exit(0)

    # Check for API key
    api_key = os.environ.get("GEMINI_API_KEY")

    # Check if running in CI environment
    is_ci = os.environ.get("CI") == "true" or os.environ.get("GITHUB_ACTIONS") == "true"

    if not api_key:
        if is_ci:
            # In CI, continue with degraded mode silently
            api_key = None
        else:
            # In local development, block operations
            print(
                "ERROR: GEMINI_API_KEY not configured - blocking operations",
                file=sys.stderr,
            )
            print(
                "Set GEMINI_API_KEY environment variable to enable validation",
                file=sys.stderr,
            )
            sys.exit(2)

    # Initialize hybrid validator and get detailed validation result
    validator = HybridValidator(api_key)
    tool_name = hook_input.get("tool_name", "")
    tool_input = hook_input.get("tool_input", {})
    transcript_path = hook_input.get("transcript_path", "")

    try:
        # Extract conversation context using security validator's method
        context = validator.security_validator.extract_conversation_context(
            transcript_path
        )
        validation_result = asyncio.run(
            validator.validate_tool_use(tool_name, tool_input, context)
        )
        validator.security_validator.cleanup_uploaded_files()

        # Get approval status
        is_approved = validation_result.get("approved", False)

        if not is_approved:
            # Show actionable suggestions first if blocked
            reason = validation_result.get("reason", "Operation blocked")
            print(f"ERROR: {reason}", file=sys.stderr)

            if validation_result.get("suggestions"):
                print("", file=sys.stderr)  # Empty line for readability
                for suggestion in validation_result.get("suggestions", []):
                    print(f"→ {suggestion}", file=sys.stderr)

            # Consolidate additional details into a single section
            details = []

            # Collect all analysis information
            if validation_result.get("detailed_analysis"):
                details.append(validation_result.get("detailed_analysis"))

            if validation_result.get("performance_analysis"):
                details.append(validation_result.get("performance_analysis"))

            if validation_result.get("code_quality_analysis"):
                details.append(validation_result.get("code_quality_analysis"))

            # Show consolidated details if any
            if details:
                print("\nDetails:", file=sys.stderr)
                for detail in details:
                    print(f"• {detail}", file=sys.stderr)

            # Show severity breakdown in a simpler format
            if validation_result.get("severity_breakdown"):
                breakdown = validation_result.get("severity_breakdown")
                if breakdown:
                    issues = []
                    if hasattr(breakdown, "BLOCK") and breakdown.BLOCK:
                        issues.extend(breakdown.BLOCK)
                    elif isinstance(breakdown, dict) and breakdown.get("BLOCK"):
                        issues.extend(breakdown["BLOCK"])

                    if issues:
                        print("\nSpecific issues:", file=sys.stderr)
                        for issue in issues:
                            print(f"• {issue}", file=sys.stderr)

            # Show file-specific issues if present
            if validation_result.get("file_analysis"):
                file_analysis = validation_result.get("file_analysis")

                file_issues = []
                if file_analysis and file_analysis.get("security_issues"):
                    file_issues.extend(file_analysis.get("security_issues", []))
                if file_analysis and file_analysis.get("code_quality_concerns"):
                    file_issues.extend(file_analysis.get("code_quality_concerns", []))

                if file_issues:
                    print("\nFile issues found:", file=sys.stderr)
                    for issue in file_issues:
                        print(f"• {issue}", file=sys.stderr)

                # Show recommendations if different from main suggestions
                if file_analysis and file_analysis.get("recommendations"):
                    recs = file_analysis.get("recommendations", [])
                    main_suggestions = validation_result.get("suggestions", [])
                    unique_recs = [r for r in recs if r not in main_suggestions]
                    if unique_recs:
                        print("\nAdditional recommendations:", file=sys.stderr)
                        for rec in unique_recs:
                            print(f"→ {rec}", file=sys.stderr)

        # Don't print full context or raw response - too verbose and not for human readability

        # Simple exit without decorative formatting
        if not is_approved:
            sys.exit(2)
        else:
            sys.exit(0)

    except Exception as e:
        print(f"VALIDATION ERROR: {e}", file=sys.stderr)
        validator.security_validator.cleanup_uploaded_files()
        sys.exit(1)


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Claude Code Hybrid Security + TDD Validation Hooks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Setup Claude Code hooks configuration
  uvx claude-code-adk-validator --setup

  # Run as validation hook (used by Claude Code)
  uvx claude-code-adk-validator < hook_input.json

  # Show version information
  uvx claude-code-adk-validator --version

  # List supported languages for test capture
  uvx claude-code-adk-validator --list-languages

  # Capture test results for TDD validation
  npm test --json | uvx claude-code-adk-validator --capture-test-results typescript
  go test -json ./... | uvx claude-code-adk-validator --capture-test-results go
  cargo test --message-format json | uvx claude-code-adk-validator --capture-test-results rust
        """,
    )

    parser.add_argument(
        "--setup", action="store_true", help="Setup Claude Code hooks configuration"
    )

    parser.add_argument(
        "--version", action="store_true", help="Show version information"
    )

    parser.add_argument(
        "--validator-command",
        default="uvx claude-code-adk-validator",
        help="Command to use in hook configuration (default: uvx claude-code-adk-validator)",
    )

    parser.add_argument(
        "--capture-test-results",
        metavar="LANGUAGE",
        choices=["python", "typescript", "javascript", "go", "rust", "dart", "flutter"],
        help="Capture test results from stdin for specified language",
    )

    parser.add_argument(
        "--list-languages",
        action="store_true",
        help="List supported languages for test result capture",
    )

    # Parse arguments
    args = parser.parse_args()

    if args.version:
        from . import __version__

        print(f"claude-code-adk-validator {__version__}")
        print("Hybrid security + TDD validation for Claude Code tool execution")
        print("Using Google Gemini with sequential validation pipeline")
        return

    if args.setup:
        print("Setting up Claude Code hooks...")
        setup_claude_hooks(args.validator_command)
        return

    if args.list_languages:
        print("Supported languages for test result capture:")
        print("  - python      (pytest)")
        print("  - typescript  (jest, vitest)")
        print("  - javascript  (jest, vitest)")
        print("  - go          (go test)")
        print("  - rust        (cargo test)")
        print("  - dart        (dart test)")
        print("  - flutter     (flutter test)")
        print("\nUsage examples:")
        print(
            "  npm test --json | uvx claude-code-adk-validator --capture-test-results typescript"
        )
        print(
            "  go test -json ./... | uvx claude-code-adk-validator --capture-test-results go"
        )
        print(
            "  cargo test --message-format json | uvx claude-code-adk-validator --capture-test-results rust"
        )
        return

    if args.capture_test_results:
        # Read test output from stdin
        try:
            test_output = sys.stdin.read()
            if not test_output.strip():
                print("Error: No test output provided via stdin", file=sys.stderr)
                sys.exit(1)

            success = store_manual_test_results(test_output, args.capture_test_results)
            if success:
                print(f"SUCCESS: Test results captured for {args.capture_test_results}")
                sys.exit(0)
            else:
                print(
                    f"ERROR: Failed to capture test results for {args.capture_test_results}",
                    file=sys.stderr,
                )
                sys.exit(1)

        except Exception as e:
            print(f"ERROR: Error capturing test results: {e}", file=sys.stderr)
            sys.exit(1)

    # Default behavior: run as validation hook
    validate_hook_input()


if __name__ == "__main__":
    main()
