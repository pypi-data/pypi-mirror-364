#!/usr/bin/env python3

import re
import json
from typing import Optional, Dict, Any, List
from pydantic import BaseModel

try:
    from google import genai
except ImportError:
    genai = None

from .tdd_prompts import (
    TDDCorePrompt,
    EditAnalysisPrompt,
    WriteAnalysisPrompt,
    MultiEditAnalysisPrompt,
    TDDContextFormatter,
)
from .config import GEMINI_MODEL
from .streaming_processors import (
    TDDValidationProcessor,
    FileCategorizationProcessor,
    ProcessorPart,
    extract_json_from_part,
)


class TDDValidationResponse(BaseModel):
    """TDD-specific validation response model"""

    approved: bool
    violation_type: Optional[str] = (
        None  # "multiple_tests", "over_implementation", "premature_implementation"
    )
    test_count: Optional[int] = None
    affected_files: List[str] = []
    tdd_phase: str = "unknown"  # "red", "green", "refactor", "unknown"
    reason: str = ""
    suggestions: List[str] = []
    detailed_analysis: Optional[str] = None


class FileCategorizationResponse(BaseModel):
    """Response model for file categorization"""

    category: str  # "structural", "config", "docs", "data", "test", "implementation"
    reason: str
    requires_tdd: bool


class TDDValidator:
    """
    TDDValidator enforces Test-Driven Development principles through:
    - Operation-specific validation (Edit, Write, MultiEdit)
    - Red-Green-Refactor cycle enforcement
    - New test count detection
    - Over-implementation prevention
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.client = genai.Client(api_key=api_key) if api_key and genai else None
        self.model_name = GEMINI_MODEL
        self.processor = TDDValidationProcessor(api_key)
        self.file_categorization_processor = FileCategorizationProcessor(api_key)

    def _is_minimal_init_file(self, file_path: str, content: str) -> bool:
        """Check if __init__.py file is minimal (structural)"""
        if not file_path.endswith("__init__.py"):
            return False

        # Empty file is structural
        if not content.strip():
            return True

        # Simple imports only (no logic)
        lines = [line.strip() for line in content.split("\n") if line.strip()]

        # Check if all lines are comments, imports, or simple assignments
        for line in lines:
            if line.startswith("#"):  # Comment
                continue
            if line.startswith(
                ("import ", "from ", "__version__", "__author__", "__email__")
            ):
                continue
            if line.startswith("__all__") and "=" in line:  # Simple __all__ definition
                continue
            # If we find any other code, it's implementation
            return False

        return True

    def _is_config_file(self, file_path: str) -> bool:
        """Check if file is a configuration file"""
        import os

        config_extensions = {".ini", ".toml", ".yaml", ".yml", ".json", ".cfg", ".conf"}
        config_names = {
            "setup.py",
            "pyproject.toml",
            "requirements.txt",
            "Dockerfile",
            "Makefile",
        }

        ext = os.path.splitext(file_path)[1].lower()
        name = os.path.basename(file_path)

        return ext in config_extensions or name in config_names

    def _has_implementation_logic(self, content: str) -> bool:
        """Check if content contains actual implementation logic"""
        if not content.strip():
            return False

        lines = [line.strip() for line in content.split("\n") if line.strip()]

        for line in lines:
            # Skip comments and docstrings
            if line.startswith("#") or line.startswith('"""') or line.startswith("'''"):
                continue
            # Skip simple imports and metadata
            if line.startswith(
                ("import ", "from ", "__version__", "__author__", "__email__")
            ):
                continue
            # Skip simple variable assignments (like __all__)
            if any(
                line.startswith(var)
                for var in ["__all__", "__version__", "__author__", "__email__"]
            ):
                continue
            # If we find function/class definitions or other logic, it's implementation
            if any(
                keyword in line
                for keyword in [
                    "def ",
                    "class ",
                    "if ",
                    "for ",
                    "while ",
                    "try:",
                    "except",
                ]
            ):
                return True

        return False

    async def categorize_file(self, file_path: str, content: str = "") -> dict:
        """
        Smart categorization for TDD validation logic.

        Distinguishes between structural files (no tests required) and
        implementation files (tests required) based on research into
        TDD best practices and pytest documentation.

        Returns dict with:
            category: 'structural', 'config', 'test', 'implementation'
            requires_tdd: bool
            reason: str
        """
        if not self.api_key or not self.client:
            # Enhanced fallback categorization with smart classification
            import os

            if not file_path:
                return {
                    "category": "unknown",
                    "requires_tdd": False,
                    "reason": "No file path provided",
                }

            basename = os.path.basename(file_path)
            ext = os.path.splitext(file_path)[1].lower()

            # Check for test files first
            if any(
                pattern in file_path.lower()
                for pattern in ["test", "spec", "_test.", ".test.", "tests/"]
            ):
                return {
                    "category": "test",
                    "requires_tdd": False,
                    "reason": "Test file",
                }

            # Check for configuration files
            if self._is_config_file(file_path):
                return {
                    "category": "config",
                    "requires_tdd": False,
                    "reason": "Configuration file",
                }

            # Check for documentation
            if ext in [".md", ".rst", ".txt"] or "README" in basename:
                return {
                    "category": "docs",
                    "requires_tdd": False,
                    "reason": "Documentation file",
                }

            # Check for generated files (never need tests)
            generated_patterns = [
                ".generated.",
                ".g.",
                "_pb.",
                ".pb.",
                "autogen_",
                ".freezed.",
                ".gen.",
                "_generated.",
                ".min.",
                ".bundle.",
            ]
            if any(pattern in basename.lower() for pattern in generated_patterns):
                return {
                    "category": "structural",
                    "requires_tdd": False,
                    "reason": "Generated/compiled file - no tests needed",
                }

            # Check for lock files
            lock_files = {
                "package-lock.json",
                "yarn.lock",
                "pnpm-lock.yaml",
                "Gemfile.lock",
                "Cargo.lock",
                "go.sum",
                "go.mod",
                "poetry.lock",
                "Pipfile.lock",
                "composer.lock",
            }
            if basename in lock_files:
                return {
                    "category": "data",
                    "requires_tdd": False,
                    "reason": "Dependency lock file",
                }

            # Check for migration files
            if "migration" in file_path.lower() or "/migrate/" in file_path:
                return {
                    "category": "data",
                    "requires_tdd": False,
                    "reason": "Database migration file",
                }

            # Check for schema/definition files
            schema_extensions = {".proto", ".graphql", ".sql", ".avsc", ".xsd", ".wsdl"}
            if ext in schema_extensions:
                return {
                    "category": "data",
                    "requires_tdd": False,
                    "reason": "Schema definition file",
                }

            # Check for known structural files by name
            structural_files = {
                "__init__.py",
                "__main__.py",
                "conftest.py",
                "_version.py",
                "version.py",
                "constants.py",
                "index.js",
                "index.ts",
                "mod.rs",
                "lib.rs",
                "main.rs",
                "package-info.java",
                "doc.go",
                "urls.py",
                "apps.py",
            }

            if basename in structural_files:
                # Verify it's actually structural by content
                if not self._has_implementation_logic(content):
                    return {
                        "category": "structural",
                        "requires_tdd": False,
                        "reason": f"Structural file: {basename}",
                    }

            # Check for code files
            code_extensions = [
                ".py",
                ".js",
                ".ts",
                ".java",
                ".go",
                ".rs",
                ".dart",
                ".rb",
                ".php",
            ]
            if ext in code_extensions:
                if self._has_implementation_logic(content):
                    return {
                        "category": "implementation",
                        "requires_tdd": True,
                        "reason": "Code file with implementation logic",
                    }
                else:
                    return {
                        "category": "structural",
                        "requires_tdd": False,
                        "reason": "Code file without implementation logic",
                    }

            # Default to data file
            return {
                "category": "data",
                "requires_tdd": False,
                "reason": "Non-code file",
            }

        prompt = f"""Analyze this file and categorize it for TDD (Test-Driven Development) validation purposes.

FILE PATH: {file_path}
CONTENT PREVIEW (first 500 chars): {content[:500] if content else "No content provided"}

Categories:
- 'structural': Organizational/structural files (no business logic) - NO TDD REQUIRED
- 'config': Configuration files - NO TDD REQUIRED
- 'docs': Documentation files - NO TDD REQUIRED
- 'data': Data/resource files - NO TDD REQUIRED
- 'test': Test files - TDD REQUIRED (must follow ONE TEST RULE)
- 'implementation': Implementation code with business logic - TDD REQUIRED

## STRUCTURAL FILES ACROSS LANGUAGES
Recognize these patterns as structural (NO TDD required):

**Python:**
- __init__.py: Package markers (empty or just imports/exports)
- __main__.py: Entry points with minimal logic
- conftest.py: pytest configuration
- _version.py, version.py: Version metadata only
- constants.py: Only constant declarations

**JavaScript/TypeScript:**
- index.js/index.ts: Barrel files (re-exports only)
- index.d.ts, types.ts: Type definitions without logic
- constants.js/ts: Only constant declarations
- Re-export files that aggregate imports

**Go:**
- doc.go: Package documentation
- Simple main.go with just main() calling other packages

**Rust:**
- mod.rs, lib.rs: Module organization (pub mod, use statements)
- main.rs: Entry point with minimal logic

**Dart/Flutter:**
- barrel files that just export other files
- generated files (*.g.dart, *.freezed.dart, *.gen.dart)
- part files that are fragments of a library

**Java:**
- package-info.java: Package documentation
- Generated files (*.generated.java, *_Generated.java)

**Cross-Language Patterns:**
- Generated/compiled files: *.generated.*, *.g.*, *_pb.go, *.pb.*, autogen_*
- Migration files: *_migration.*, migrations/*, db/migrate/*
- Schema files: *.proto, *.graphql, *.sql (DDL only), openapi.yaml
- Lock files: package-lock.json, yarn.lock, Gemfile.lock, Cargo.lock, go.sum
- Build artifacts: dist/*, build/*, target/*, *.min.js, *.bundle.js
- Test fixtures: fixtures/*, __fixtures__/*, testdata/*, *.fixture.*
- Mock data: mocks/*, __mocks__/*, *.mock.*, mock_*.json

**Framework Files:**
- Django: urls.py (URL routing), apps.py (app config)
- React: index.js that just renders App
- Express: Simple route files that wire endpoints

## CONTENT ANALYSIS RULES
A file is STRUCTURAL if it contains ONLY:
- Import/export statements
- Constant declarations (no computed values)
- Type/interface definitions (TypeScript)
- Module declarations (mod, pub mod in Rust)
- Simple variable assignments (__version__ = "1.0.0")
- Comments and documentation

A file is IMPLEMENTATION if it contains:
- Function/method definitions with logic (def, function, fn)
- Class definitions with methods
- Control flow (if, for, while, switch)
- Business logic or algorithms
- State management
- API endpoints with logic
- Database operations

A file is TEST if it contains:
- Test functions (def test_*, func Test*, @Test)
- Test classes or suites
- Test assertions and expectations
- TDD VALIDATION REQUIRED: Test files must follow ONE TEST RULE (single test only)

## EDGE CASES
- Entry points (main.py, index.js) with minimal wiring → structural
- Files with a single function that just calls others → structural
- Config files that compute values dynamically → implementation
- Type files with validation logic → implementation

Analyze the file holistically considering naming, location, and content."""

        try:
            # Create categorization request
            request = {"prompt": prompt}
            request_part = ProcessorPart(json.dumps(request))

            # Process through file categorization processor
            result = {}
            async for response_part in self.file_categorization_processor.call(
                request_part
            ):
                json_data = extract_json_from_part(response_part)
                if json_data:
                    result.update(json_data)

            if result and "error" not in result:
                return {
                    "category": result.get("category", "unknown"),
                    "requires_tdd": result.get("requires_tdd", False),
                    "reason": result.get("reason", ""),
                }
            else:
                # Fallback on error
                return {
                    "category": "unknown",
                    "requires_tdd": False,
                    "reason": "Categorization failed",
                }

        except Exception:
            # Fallback on error - use smart categorization logic
            import os

            if not file_path:
                return {
                    "category": "unknown",
                    "requires_tdd": False,
                    "reason": "No file path provided",
                }

            basename = os.path.basename(file_path)
            ext = os.path.splitext(file_path)[1].lower()

            # Check for test files first (most important for TDD)
            if any(
                pattern in file_path.lower()
                for pattern in ["test", "spec", "_test.", ".test.", "tests/"]
            ):
                return {
                    "category": "test",
                    "requires_tdd": True,  # Test files need TDD validation (one test rule)
                    "reason": "Test file (LLM categorization failed, using fallback)",
                }

            # Check for configuration files
            if self._is_config_file(file_path):
                return {
                    "category": "config",
                    "requires_tdd": False,
                    "reason": "Configuration file (LLM categorization failed, using fallback)",
                }

            # Check for documentation
            if ext in [".md", ".rst", ".txt"] or "README" in basename:
                return {
                    "category": "docs",
                    "requires_tdd": False,
                    "reason": "Documentation file (LLM categorization failed, using fallback)",
                }

            # Check for code files
            code_extensions = [
                ".py",
                ".js",
                ".ts",
                ".java",
                ".go",
                ".rs",
                ".dart",
                ".rb",
                ".php",
            ]
            if ext in code_extensions:
                if self._has_implementation_logic(content):
                    return {
                        "category": "implementation",
                        "requires_tdd": True,
                        "reason": "Code file with implementation logic (LLM categorization failed, using fallback)",
                    }
                else:
                    return {
                        "category": "structural",
                        "requires_tdd": False,
                        "reason": "Code file without implementation logic (LLM categorization failed, using fallback)",
                    }

            # Default fallback
            return {
                "category": "implementation",
                "requires_tdd": True,
                "reason": "Categorization failed, assuming implementation",
            }

    async def validate(
        self,
        tool_name: str,
        tool_input: dict,
        context: str,
        tdd_context: Dict[str, Any],
    ) -> dict:
        """
        Main TDD validation entry point.

        Args:
            tool_name: The Claude tool being executed
            tool_input: The tool's input parameters
            context: Conversation context
            tdd_context: TDD-specific context (test results, todos, modifications)

        Returns:
            TDDValidationResponse dict with TDD compliance status
        """

        # Skip TDD validation if no API key
        if not self.api_key:
            return {
                "approved": True,
                "reason": "TDD validation service unavailable",
                "tdd_phase": "unknown",
            }

        # Check file categorization for file-based operations
        if tool_name in ["Write", "Edit", "MultiEdit", "Update"]:
            file_path = tool_input.get("file_path", "")
            content = (
                tool_input.get("content", "")
                if tool_name in ["Write", "Update"]
                else ""
            )

            # Get file category using LLM
            categorization = await self.categorize_file(file_path, content)

            # Skip TDD validation for non-implementation files
            if not categorization.get("requires_tdd", True):
                return {
                    "approved": True,
                    "reason": f"TDD validation not required for {categorization.get('category', 'unknown')} files: {categorization.get('reason', '')}",
                    "tdd_phase": "not_applicable",
                    "file_category": categorization.get("category"),
                }

        # Route to operation-specific validation
        try:
            if tool_name == "Edit":
                return await self.validate_edit_operation(tool_input, tdd_context)
            elif tool_name == "Write":
                return await self.validate_write_operation(tool_input, tdd_context)
            elif tool_name == "MultiEdit":
                return await self.validate_multi_edit_operation(tool_input, tdd_context)
            elif tool_name == "Update":
                # Update has special handling to diff against existing content
                return await self.validate_update_operation(tool_input, tdd_context)
            else:
                # Other operations (Bash, etc.) don't need TDD validation
                return {
                    "approved": True,
                    "reason": f"{tool_name} operation doesn't require TDD validation",
                    "tdd_phase": "unknown",
                }

        except Exception as e:
            # Fail-safe: allow operation if TDD validation fails
            return {
                "approved": True,
                "reason": f"TDD validation service error: {str(e)}",
                "tdd_phase": "unknown",
            }

    async def validate_edit_operation(
        self, tool_input: dict, tdd_context: Dict[str, Any]
    ) -> dict:
        """Validate Edit operations for TDD compliance"""

        file_path = tool_input.get("file_path", "")
        old_content = tool_input.get("old_string", "")
        new_content = tool_input.get("new_string", "")

        # Build TDD analysis prompt
        prompt = self.build_edit_validation_prompt(
            old_content, new_content, file_path, tdd_context
        )

        return await self.execute_tdd_validation(prompt, [file_path])

    async def validate_write_operation(
        self, tool_input: dict, tdd_context: Dict[str, Any]
    ) -> dict:
        """Validate Write operations for TDD compliance"""

        file_path = tool_input.get("file_path", "")
        content = tool_input.get("content", "")

        # Pre-validation: Check test count for test files (ONE test rule)
        if self.detect_test_files(file_path, content):
            test_functions = self.extract_test_functions(content)
            test_count = len(test_functions)

            if test_count > 1:
                return {
                    "approved": False,
                    "violation_type": "multiple_tests",
                    "test_count": test_count,
                    "tdd_phase": "red",
                    "reason": f"TDD: Multiple tests ({test_count}) detected in single Write operation. The ONE test rule requires writing only one test at a time to follow Red-Green-Refactor cycle properly.",
                    "suggestions": [
                        "Split into separate Write operations, one test at a time",
                        "Write first test, run it (RED phase), implement code (GREEN phase), then write next test",
                        "Follow TDD discipline: one test → implementation → refactor → repeat",
                    ],
                    "detailed_analysis": f"Found {test_count} test functions: {', '.join(test_functions)}. TDD methodology requires writing one failing test at a time to maintain focused development and proper test coverage.",
                }
        else:
            # Pre-validation: Check if implementation file has corresponding tests
            # Only check for non-trivial implementation files
            if self._has_implementation_logic(content):
                # Check if there are recent test results or test files in context
                test_results = tdd_context.get("test_results")
                has_failing_tests = bool(test_results and test_results.get("failures"))

                # Simple heuristic: implementation files should only be written after tests
                # Check if context is empty or has no meaningful test data
                # Note: test_results might be None even if the key exists
                if not tdd_context or tdd_context.get("test_results") is None:
                    # No test context or no test results - block implementation
                    return {
                        "approved": False,
                        "violation_type": "premature_implementation",
                        "tdd_phase": "red",
                        "reason": "TDD: Writing implementation without failing tests. TDD requires writing a failing test first (Red phase) before implementation.",
                        "suggestions": [
                            "Write a failing test first that describes the desired behavior",
                            "Run the test to confirm it fails (Red phase)",
                            "Only then implement the minimal code to make the test pass (Green phase)",
                            "Follow TDD cycle: Red → Green → Refactor",
                        ],
                        "detailed_analysis": "Implementation file detected without evidence of failing tests. TDD discipline requires test-first development to ensure all code is tested and necessary.",
                    }
                elif not has_failing_tests:
                    # Has test results but no failures - also block
                    return {
                        "approved": False,
                        "violation_type": "premature_implementation",
                        "tdd_phase": "red",
                        "reason": "TDD: Writing implementation without failing tests. All tests are passing - write a failing test first.",
                        "suggestions": [
                            "Write a failing test for the new functionality",
                            "Ensure the test fails before implementing",
                            "Only implement enough code to make the test pass",
                        ],
                        "detailed_analysis": "Test results show all tests passing. TDD requires a failing test before implementation.",
                    }

        # Build TDD analysis prompt
        prompt = self.build_write_validation_prompt(file_path, content, tdd_context)

        return await self.execute_tdd_validation(prompt, [file_path])

    async def validate_multi_edit_operation(
        self, tool_input: dict, tdd_context: Dict[str, Any]
    ) -> dict:
        """Validate MultiEdit operations for TDD compliance"""

        edits = tool_input.get("edits", [])
        file_path = tool_input.get("file_path", "")

        # Build TDD analysis prompt for multiple edits
        prompt = self.build_multi_edit_validation_prompt(edits, file_path, tdd_context)

        return await self.execute_tdd_validation(prompt, [file_path])

    def build_edit_validation_prompt(
        self,
        old_content: str,
        new_content: str,
        file_path: str,
        tdd_context: Dict[str, Any],
    ) -> str:
        """Build validation prompt for Edit operations"""

        tdd_principles = TDDCorePrompt.get_tdd_principles()
        edit_analysis = EditAnalysisPrompt.get_analysis_prompt(
            old_content, new_content, file_path
        )
        context_info = TDDContextFormatter.format_tdd_context(tdd_context)

        return f"""You are a TDD compliance validator. Analyze this Edit operation for Test-Driven Development violations.

{tdd_principles}

{edit_analysis}

{context_info}

## VALIDATION REQUIREMENTS

Your task is to determine if this Edit operation violates TDD principles. Focus on:

1. **New Test Count**: How many completely new tests are being added?
2. **Implementation Scope**: Is the implementation minimal and test-driven?
3. **TDD Phase Compliance**: Does this follow Red-Green-Refactor properly?
4. **Over-implementation**: Are features being added beyond test requirements?

## DECISION FRAMEWORK

**APPROVE** if:
- Zero or one new test being added
- Implementation is minimal and addresses specific test failures
- Changes follow Red-Green-Refactor discipline
- No premature optimization or over-engineering

**BLOCK** if:
- Multiple new tests being added in single operation
- Over-implementation beyond current test requirements
- Implementation without corresponding test failures
- Features added that aren't tested

## RESPONSE FORMAT

Provide structured TDD validation response with:
- **approved**: boolean decision
- **violation_type**: specific TDD violation if any
- **test_count**: number of new tests detected
- **tdd_phase**: current phase (red/green/refactor)
- **reason**: clear explanation of decision
- **suggestions**: actionable TDD improvements
- **detailed_analysis**: comprehensive TDD assessment

Analyze thoroughly and enforce TDD discipline to maintain code quality and test coverage."""

    def build_write_validation_prompt(
        self, file_path: str, content: str, tdd_context: Dict[str, Any]
    ) -> str:
        """Build validation prompt for Write operations"""

        tdd_principles = TDDCorePrompt.get_tdd_principles()
        write_analysis = WriteAnalysisPrompt.get_analysis_prompt(file_path, content)
        context_info = TDDContextFormatter.format_tdd_context(tdd_context)

        return f"""You are a TDD compliance validator. Analyze this Write operation for Test-Driven Development violations.

{tdd_principles}

{write_analysis}

{context_info}

## VALIDATION REQUIREMENTS

Your task is to determine if this Write operation violates TDD principles. Focus on:

1. **File Type**: Is this a test file or implementation file?
2. **Test Count**: If test file, count how many NEW test functions are being added (CRITICAL: only ONE allowed)
3. **Test Coverage**: For implementation files, are there corresponding tests?
4. **Implementation Justification**: Is implementation driven by test failures?
5. **Scope Assessment**: Is implementation minimal and focused?

## DECISION FRAMEWORK

**APPROVE** if:
- Writing test files with ONLY ONE new test at a time
- Writing minimal implementation to address specific test failures
- Creating infrastructure/setup code that supports testing
- Implementation scope matches test requirements

**BLOCK** if:
- Writing multiple tests in a single operation (even in test files)
- Creating implementation files without corresponding tests
- Over-implementing beyond current test requirements
- Writing speculative code not driven by test failures
- Implementing multiple features without adequate test coverage

## RESPONSE FORMAT

Provide structured TDD validation response focusing on file creation compliance with TDD workflow."""

    def build_multi_edit_validation_prompt(
        self, edits: List[Dict[str, Any]], file_path: str, tdd_context: Dict[str, Any]
    ) -> str:
        """Build validation prompt for MultiEdit operations"""

        tdd_principles = TDDCorePrompt.get_tdd_principles()
        multi_edit_analysis = MultiEditAnalysisPrompt.get_analysis_prompt(edits)
        context_info = TDDContextFormatter.format_tdd_context(tdd_context)

        return f"""You are a TDD compliance validator. Analyze this MultiEdit operation for Test-Driven Development violations.

{tdd_principles}

{multi_edit_analysis}

{context_info}

## VALIDATION REQUIREMENTS

Your task is to determine if this MultiEdit operation violates TDD principles. Focus on:

1. **Cumulative New Tests**: Total new tests across ALL edits
2. **Sequential Implementation**: Is each edit minimal and justified?
3. **Scope Coherence**: Do all edits work toward single test goal?
4. **Progressive Compliance**: Does each edit maintain TDD discipline?

## CRITICAL RULE

**CUMULATIVE NEW TEST COUNT** across all edits must not exceed 1. This is the most important check for MultiEdit operations.

## DECISION FRAMEWORK

**APPROVE** if:
- Total new tests across all edits ≤ 1
- Each edit contributes to minimal implementation
- Sequential changes maintain test-driven approach
- No over-implementation or feature sprawl

**BLOCK** if:
- Total new tests across all edits > 1
- Edits implement features beyond test requirements
- Sequential changes show scope creep or over-engineering
- MultiEdit is being used to circumvent single-test rule

## RESPONSE FORMAT

Provide structured TDD validation response with special attention to cumulative effects of multiple edits."""

    async def execute_tdd_validation(
        self, prompt: str, affected_files: List[str]
    ) -> dict:
        """Execute TDD validation using Gemini with structured response"""

        try:
            # Create validation request
            request = {"prompt": prompt}
            request_part = ProcessorPart(json.dumps(request))

            # Process through TDD validation processor
            result = {}
            async for response_part in self.processor.call(request_part):
                json_data = extract_json_from_part(response_part)
                if json_data:
                    result.update(json_data)

            if result and "error" not in result:
                return {
                    "approved": result.get("approved", False),
                    "violation_type": result.get("violation_type"),
                    "test_count": result.get("test_count"),
                    "affected_files": result.get("affected_files", affected_files),
                    "tdd_phase": result.get("tdd_phase", "unknown"),
                    "reason": result.get("reason", ""),
                    "suggestions": result.get("suggestions", []),
                    "detailed_analysis": result.get("detailed_analysis"),
                }
            else:
                # Handle error case
                return {
                    "approved": True,
                    "reason": result.get("error", "TDD validation service error"),
                    "tdd_phase": "unknown",
                    "affected_files": affected_files,
                }

        except Exception as e:
            # Fail-safe: allow operation if TDD validation fails
            return {
                "approved": True,
                "reason": f"TDD validation service error: {str(e)}",
                "tdd_phase": "unknown",
                "affected_files": affected_files,
            }

    def detect_test_files(self, file_path: str, content: str = "") -> bool:
        """Detect if a file is a test file based on path and content"""

        # Path-based detection
        test_path_patterns = [
            r"test.*\.py$",
            r".*_test\.py$",
            r".*\.test\.py$",
            r"test.*\.js$",
            r".*\.test\.js$",
            r".*\.spec\.js$",
            r"test.*\.go$",
            r".*_test\.go$",
            r"Test.*\.java$",
            r".*Test\.java$",
            r"/tests?/",
            r"\\tests?\\",
        ]

        for pattern in test_path_patterns:
            if re.search(pattern, file_path, re.IGNORECASE):
                return True

        # Content-based detection
        if content:
            test_content_patterns = [
                r"def test_",
                r"class Test",
                r"import unittest",
                r"test\(",
                r"describe\(",
                r"it\(",
                r"expect\(",
                r"func Test",
                r"@Test",
                r"@pytest",
            ]

            for pattern in test_content_patterns:
                if re.search(pattern, content):
                    return True

        return False

    def count_new_tests(self, old_content: str, new_content: str) -> int:
        """Count new test functions added (character-by-character comparison)"""

        # Extract test functions from both contents
        old_tests = self.extract_test_functions(old_content)
        new_tests = self.extract_test_functions(new_content)

        # Count tests that exist in new but not in old
        new_test_count = 0
        for test in new_tests:
            if test not in old_tests:
                new_test_count += 1

        return new_test_count

    def extract_test_functions(self, content: str) -> List[str]:
        """Extract test function names from code content"""

        test_patterns = [
            r"def (test_\w+)",  # Python test functions
            r"def (should_\w+)",  # Python BDD-style tests
            r'test\s*\(\s*[\'"]([^\'"]+)[\'"]',  # JavaScript test()
            r'it\s*\(\s*[\'"]([^\'"]+)[\'"]',  # JavaScript it()
            r"func (Test\w+)",  # Go test functions
            r"@Test\s+\w+\s+(\w+)",  # Java test methods
        ]

        test_functions = []
        for pattern in test_patterns:
            matches = re.findall(pattern, content, re.MULTILINE)
            test_functions.extend(matches)

        return test_functions

    async def validate_update_operation(
        self, tool_input: dict, tdd_context: Dict[str, Any]
    ) -> dict:
        """
        Validate Update operations for TDD compliance.

        Update operations replace entire file content, so we need to:
        1. Read the existing file content
        2. Compare old vs new to count only genuinely new tests
        3. Apply the same TDD rules but only for new additions
        """

        file_path = tool_input.get("file_path", "")
        new_content = tool_input.get("content", "")

        # Try to read existing file content
        import os

        old_content = ""
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    old_content = f.read()
            except Exception:
                # If we can't read the file, treat it as a new file (Write operation)
                return await self.validate_write_operation(tool_input, tdd_context)
        else:
            # File doesn't exist, treat as Write operation
            return await self.validate_write_operation(tool_input, tdd_context)

        # For test files, check new test count
        if self.detect_test_files(file_path, new_content):
            old_tests = self.extract_test_functions(old_content)
            new_tests = self.extract_test_functions(new_content)

            # Count only genuinely new tests
            genuinely_new_tests = [t for t in new_tests if t not in old_tests]
            new_test_count = len(genuinely_new_tests)

            if new_test_count > 1:
                return {
                    "approved": False,
                    "violation_type": "multiple_tests",
                    "test_count": new_test_count,
                    "tdd_phase": "red",
                    "reason": f"TDD: Multiple new tests ({new_test_count}) detected in Update operation. The ONE test rule requires adding only one new test at a time.",
                    "suggestions": [
                        f"You're adding {new_test_count} new tests: {', '.join(genuinely_new_tests)}",
                        "Add only the first new test, commit, then add the next test in a separate Update",
                        "Follow TDD discipline: one test → implementation → refactor → repeat",
                    ],
                    "detailed_analysis": f"Existing tests: {len(old_tests)}, Total tests after update: {len(new_tests)}, New tests being added: {new_test_count}. TDD requires incremental test development.",
                }
        else:
            # Pre-validation: Check if implementation file update has corresponding tests
            # Only check for non-trivial implementation files
            if self._has_implementation_logic(new_content):
                # Check if there are recent test results or test files in context
                test_results = tdd_context.get("test_results")
                has_failing_tests = bool(test_results and test_results.get("failures"))

                # Simple heuristic: implementation updates should only happen after tests
                # Check if context is empty or has no meaningful test data
                # Note: test_results might be None even if the key exists
                if not tdd_context or tdd_context.get("test_results") is None:
                    # No test context or no test results - block implementation
                    return {
                        "approved": False,
                        "violation_type": "premature_implementation",
                        "tdd_phase": "red",
                        "reason": "TDD: Updating implementation without failing tests. TDD requires writing a failing test first (Red phase) before implementation.",
                        "suggestions": [
                            "Write a failing test first that describes the desired behavior",
                            "Run the test to confirm it fails (Red phase)",
                            "Only then update the implementation to make the test pass (Green phase)",
                            "Follow TDD cycle: Red → Green → Refactor",
                        ],
                        "detailed_analysis": "Implementation update detected without evidence of failing tests. TDD discipline requires test-first development to ensure all changes are tested and necessary.",
                    }
                elif not has_failing_tests:
                    # Has test results but no failures - also block
                    return {
                        "approved": False,
                        "violation_type": "premature_implementation",
                        "tdd_phase": "red",
                        "reason": "TDD: Updating implementation without failing tests. All tests are passing - write a failing test first.",
                        "suggestions": [
                            "Write a failing test for the new functionality",
                            "Ensure the test fails before implementing",
                            "Only then update the implementation",
                        ],
                        "detailed_analysis": "Test results show all tests passing. TDD requires a failing test before implementation updates.",
                    }

        # Build TDD analysis prompt for Update operations
        prompt = self.build_update_validation_prompt(
            file_path, old_content, new_content, tdd_context
        )

        return await self.execute_tdd_validation(prompt, [file_path])

    def build_update_validation_prompt(
        self,
        file_path: str,
        old_content: str,
        new_content: str,
        tdd_context: Dict[str, Any],
    ) -> str:
        """Build validation prompt specifically for Update operations"""

        tdd_principles = TDDCorePrompt.get_tdd_principles()
        context_info = TDDContextFormatter.format_tdd_context(tdd_context)

        return f"""You are a TDD compliance validator. Analyze this Update operation for Test-Driven Development violations.

{tdd_principles}

## UPDATE OPERATION ANALYSIS

File Path: {file_path}

PREVIOUS CONTENT (first 1000 chars):
{old_content[:1000]}

NEW CONTENT (first 1000 chars):  
{new_content[:1000]}

{context_info}

## CRITICAL: UPDATE OPERATION RULES

Update operations REPLACE the entire file content. You must:
1. Compare old vs new content to identify what's actually changing
2. Count only GENUINELY NEW tests (not existing tests)
3. Apply TDD rules only to the NET changes, not the entire file
4. Recognize test modification/evolution as valid TDD practice

## TEST MODIFICATION VS ADDITION

**Test Modification (ALLOWED during Red phase):**
- Changing test implementation but keeping same function name
- Renaming test function (e.g., test_login → test_login_redirects)
- Replacing one test with another (removing old, adding new = net zero)
- Simplifying complex test into focused one

**Test Addition (ONE at a time):**
- Net increase in test count must be ≤ 1
- Count = (new total tests) - (old total tests)
- If count > 1, this is adding multiple tests → BLOCK

## VALIDATION REQUIREMENTS

Focus on:
1. **NET Test Change**: (new test count) - (old test count) ≤ 1
2. **Test Evolution**: Is this refining existing test or adding new behavior?
3. **Implementation Justification**: If adding implementation, is it test-driven?
4. **Change Purpose**: Red phase refinement vs new feature addition

## DECISION FRAMEWORK

**APPROVE** if:
- Adding only ONE new test (net increase = 1)
- Modifying/renaming existing tests (net increase = 0)
- Replacing one test with another (net increase = 0)
- Adding minimal implementation for existing failing tests
- Refactoring while keeping tests green

**BLOCK** if:
- Adding multiple new tests (net increase > 1)
- Adding implementation without test justification
- Over-implementing beyond test requirements

Remember: The file may already contain tests. Only new additions count toward the one-test limit."""
