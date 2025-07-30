# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.11.1] - 2025-07-25

### Fixed
- Version inconsistency where `__init__.py` had version 1.10.1 while `pyproject.toml` had 1.11.0
- This caused `uvx claude-code-adk-validator@latest --version` to incorrectly show 1.10.1

## [1.11.0] - 2025-07-25

### Changed
- Refactored to use genai-processors library for streaming LLM interactions (#45)
  - Replaced direct generate_content calls with processor pattern
  - Maintained parallel validation capability through asyncio.gather
  - Improved modularity and code organization

### Added
- New streaming_processors.py module with ValidationProcessor base class
- SecurityValidationProcessor and TDDValidationProcessor implementations
- FileCategorizationProcessor for streaming file categorization
- ParallelValidationPipeline for concurrent security and TDD validation
- extract_json_from_part helper for ProcessorPart compatibility

### Fixed
- All mypy type errors with proper async/await patterns
- ProcessorPart API compatibility issues
- Linting errors in streaming processor implementations

### Technical
- Added genai-processors>=0.1.0 dependency
- Updated all validators to use streaming processor pattern
- Improved type safety with proper async method signatures

## [1.10.1] - 2025-07-20

### Fixed
- Re-enabled pytest plugin entry point that was temporarily disabled (#43)
- `--setup` flag now properly installs pytest plugin for automatic test result capture
- Pytest can now discover and use the plugin after running `uvx claude-code-adk-validator --setup`

## [1.10.0] - 2025-07-26

### Added
- Explicit support for test modification during TDD Red phase (#41)
  - Tests can be refined, renamed, or replaced without violating TDD rules
  - Clear distinction between test modification (allowed) and multiple test addition (blocked)
- Three new test scenarios for test modification validation:
  - `test_update_modify_existing_test` - changing test implementation
  - `test_update_rename_test_function` - renaming test functions
  - `test_update_replace_test_with_different_one` - replacing tests
- Enhanced TDD validation prompts with "TEST EVOLUTION IN TDD" section
- Detailed documentation of practical TDD workflows in README

### Changed
- TDD prompts now explicitly allow test modifications with net zero change
- Update operation prompt includes "TEST MODIFICATION VS ADDITION" guidance
- ONE test rule clarified to apply to NET new tests, not modifications
- Validation focuses on net test count change: (new count) - (old count)

### Fixed
- Overly restrictive TDD validation that blocked legitimate test refinements
- LLM interpretation that confused test modification with rule violation
- Improved developer experience during iterative test development

## [1.9.0] - 2025-07-25

### Fixed
- CI test failure where 'Safe file write' test was blocked by branch validation on main branch
- PyPI publish failure due to incorrect version number in pyproject.toml (was 1.8.0, now 1.9.0)

### Added
- Branch validation for GitHub issue-based workflow enforcement (#37)
  - Detects current git branch and blocks code changes on protected branches (main, master, production)
  - Validates branch names follow issue-based pattern (e.g., 42-feature-name)
  - Checks if referenced GitHub issues exist using gh CLI
  - Provides helpful workflow suggestions for proper feature branch development
  - Allows documentation and configuration file changes on protected branches
- Branch context tracking in FileStorage for workflow continuity
- Branch information added to LLM prompts for context-aware security analysis
- Comprehensive test suite for branch validation functionality
- Configuration options for protected branches and issue workflow enforcement

### Changed
- SecurityValidator extended with minimal additions (~70 lines) instead of creating separate module
- LLM prompts now include branch and issue context for better security decisions
- Quick validation test suite includes branch validation tests

## [1.8.0] - 2025-07-25

### Fixed
- TDD validator incorrectly counting all tests as new in Update operations (#35)
  - Update operations now properly diff old vs new content to count only genuinely new tests
  - Added dedicated `validate_update_operation()` method to handle Update-specific logic
  - Fixed issue where legitimate updates adding one test were being blocked
- Quick validation tests timeout issue in CI mode
  - Created test_entry.py to handle subprocess tests without stdin
  - Fixed TodoWrite test data structure
  - Removed CI warning message that interfered with subprocess communication
  - Increased test timeouts from 5s to 10s for quick tests and 15s for comprehensive tests
  - Reduced parallel execution workers to improve test stability

### Added
- Comprehensive test coverage for Update operation TDD validation
- Test entry point for better subprocess testing reliability

### Changed
- Update operations now read existing file content for proper test counting
- Improved error messages for Update operations to show actual new test count

## [1.7.0] - 2025-07-21

### Added
- Template file support for HTML, Jinja2, and other template engines (fixes #33)
  - Automatic detection of template files by extension and directory patterns
  - Template-specific security validation focusing on XSS prevention
  - STRICT_TEMPLATE_VALIDATION config option for optional stricter checks
  - Templates skip code-level security analysis by default
- Template validation tests covering all major template engines
- Template-specific analysis prompts for Gemini LLM

### Fixed
- HTML templates being blocked for lacking server-side security headers
- Overly strict validation preventing legitimate template creation
- Templates incorrectly analyzed for SOLID principles and code quality

### Changed
- FileContextAnalyzer now includes template file categorization
- Security validator routes templates to template-specific validation
- File analysis prompts differentiate between code and template files

## [1.6.0] - 2025-07-21

### Fixed
- Documentation files being incorrectly analyzed as code (fixes #31)
  - File categorization now happens before file upload/analysis
  - Documentation files (.md, .rst, .txt) skip all security validation
  - Files >500 chars no longer trigger code analysis for docs
- CONTRIBUTING.md being blocked for containing example AWS keys

### Added
- Comprehensive test suite for documentation validation scenarios
- Specific handling for docs category in security validator

### Changed
- Security validation flow to check file type before expensive operations
- Documentation files now have dedicated validation path

## [1.5.0] - 2025-07-21

### Added
- Context-aware security validation for test files (fixes #29)
  - FileContextAnalyzer for intelligent file categorization
  - Test files can use test-, mock-, dummy-, fake- prefixed secrets
  - Production files maintain strict security validation
- Parallel test execution for all test files
  - 10x performance improvement (30-60s → 3-5s)
  - Thread-safe counter management with ThreadPoolExecutor
- Pre-PR documentation checks
  - Git hooks to check README.md and CLAUDE.md updates
  - Scripts for automated documentation validation
- Comprehensive test coverage for context-aware validation scenarios

### Changed
- Updated configuration to use gemini-2.5-pro for enhanced reasoning
- Security validator now distinguishes between test and production code
- LLM prompts now include file context for intelligent analysis

### Fixed
- Test files being blocked for legitimate test fixtures
- conftest.py can now contain test secrets for JWT testing

## [1.4.0] - 2025-07-20

### Added
- Update tool support in TDD validation for complete file replacements
- No-comments enforcement to promote self-evident code
- SOLID principles validation (SRP, OCP, LSP, ISP, DIP)
- Zen of Python compliance checking
- Comprehensive testing suite with parallel execution (~30 seconds)
- Pre-commit hooks for automated validation before commits
- Thread-safe parallel test execution
- Quick validation tests that run without LLM calls

### Changed
- Simplified all prompts by ~80% while maintaining functionality
- Removed all emojis from validation output
- Enhanced file categorization with better fallback logic
- Improved error messages to be more actionable

### Fixed
- Gemini API tool/JSON response format conflicts
- Multiple tests detection in Edit operations
- Debug statements removed for better performance

## [1.3.2] - 2025-07-19

### Added
- Comprehensive testing framework
- Pre-commit hook configuration
- Parallel test execution support

### Changed
- Refactored prompts to align with coding philosophy
- Enhanced TDD validation logic

## [1.3.1] - 2025-07-19

### Added
- Smart file classification for structural files (__init__.py, setup.py, etc.)
- Enhanced TDD validation scope refinement

### Fixed
- NoneType error in TDD validation
- File categorization for Python structural files

## [1.3.0] - 2025-07-19

### Added
- Automatic pytest plugin installation during --setup
- Enhanced setup process

### Fixed
- Issue #22: Automatic pytest plugin registration

## [1.2.1] - 2025-07-19

### Fixed
- GitHub Actions workflow permissions for release creation

## [1.2.0] - 2025-07-19

### Added
- Automatic test result capture for multiple languages
- Built-in pytest plugin for seamless integration
- Test reporters for Python, TypeScript/JavaScript, Go, Rust, Dart/Flutter
- CLI flags: --capture-test-results and --list-languages
- Simplified UX output with actionable-first design
- TodoWrite optimization (skips validation, persists context)

### Changed
- Optimized file categorization to use lighter gemini-2.5-flash model
- Improved output formatting (removed redundant headers)

### Fixed
- File storage context persistence
- Test result JSON format standardization

## [1.1.0] - 2025-07-18

### Added
- Hybrid Security + TDD validation system
- Modular architecture (security_validator.py, tdd_validator.py, hybrid_validator.py)
- Context persistence with FileStorage
- TDD enforcement with Red-Green-Refactor cycle
- Single test rule enforcement
- Operation-specific validation logic
- TodoWrite tool support

### Changed
- Split monolithic validator into specialized modules
- Added sequential validation pipeline

### Removed
- Fail-safe mode (operations now blocked without API key)

## [1.0.3] - 2025-07-17

### Added
- Enhanced secret detection with reduced false positives
- Word boundaries for pattern matching
- Placeholder exclusion for documentation
- Comprehensive stderr output with structured sections
- Full context processing (no truncation limits)
- Deep thinking analysis with 24576 token budget

### Fixed
- Gemini Files API integration
- Large file security analysis

## [1.0.0] - 2025-07-15

### Added
- Initial release with security validation
- Multi-tier validation system
- Google Gemini LLM integration
- Tool enforcement (grep→rg, find→rg, python→uv)
- PreToolUse hook support for Claude Code

[1.4.0]: https://github.com/jihunkim0/jk-hooks-gemini-challenge/compare/v1.3.2...v1.4.0
[1.3.2]: https://github.com/jihunkim0/jk-hooks-gemini-challenge/compare/v1.3.1...v1.3.2
[1.3.1]: https://github.com/jihunkim0/jk-hooks-gemini-challenge/compare/v1.3.0...v1.3.1
[1.3.0]: https://github.com/jihunkim0/jk-hooks-gemini-challenge/compare/v1.2.1...v1.3.0
[1.2.1]: https://github.com/jihunkim0/jk-hooks-gemini-challenge/compare/v1.2.0...v1.2.1
[1.2.0]: https://github.com/jihunkim0/jk-hooks-gemini-challenge/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/jihunkim0/jk-hooks-gemini-challenge/compare/v1.0.3...v1.1.0
[1.0.3]: https://github.com/jihunkim0/jk-hooks-gemini-challenge/compare/v1.0.0...v1.0.3
[1.0.0]: https://github.com/jihunkim0/jk-hooks-gemini-challenge/releases/tag/v1.0.0
