# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.4.0] - 2025-07-26

### Added
- Full Python 3.10+ support now that aceiot-models 0.3.3 supports it
- Multi-version Python testing infrastructure with tox (3.10, 3.11, 3.12, 3.13)
- GitHub Actions CI/CD workflow for automated testing across all Python versions
- Pre-commit hooks for code quality checks
- CONTRIBUTING.md with development and testing guidelines
- Automated release workflow with testing

### Changed
- Updated requires-python from >=3.13 to >=3.10
- Fixed datetime.UTC usage for Python 3.10 compatibility (using timezone.utc)
- Updated development dependencies to include tox and pre-commit
- Enhanced CI/CD pipeline infrastructure for multi-version testing
- Updated aceiot-models dependency to 0.3.3

### Fixed
- Removed local path override for aceiot-models dependency
- Fixed CI/CD workflows to use uv run for all commands
- Updated test to match new APIClient._request method name
- Resolved variable shadowing in deploy function
- Fixed missing Any import in volttron_commands
- Resolved all pyright type checking errors

## [0.3.2] - 2025-07-26

### Changed
- Code formatting improvements for consistency
- Minor code style updates to comply with project standards

## [0.3.1] - 2025-07-25

### Fixed
- Addressed all ruff linting issues (trailing whitespace, formatting)
- Fixed pyright type checking errors
- Resolved undefined variable issues in volttron commands
- Fixed type annotations for better type safety
- Updated error handling tests to match new client/gateway fallback logic

### Changed
- Improved variable initialization to prevent runtime errors
- Enhanced type safety with proper type guards

## [0.3.0] - 2025-07-25

### Added
- Integration with aceiot-models API client library, removing duplicate code
- `--keep-archive` flag for volttron upload-agent command to retain temporary archives
- Default CSV output for site timeseries command with format `<site>-<start>-<end>.csv`
- Support for both client and gateway names in volttron commands
- Comprehensive error handling with detailed API error messages
- Test coverage for volttron commands and error scenarios

### Changed
- Volttron commands now accept either client or gateway names consistently
- Site timeseries command now uses efficient `get_site_timeseries` API endpoint
- Temporary archives are created in current directory instead of system temp
- Archive names include timestamp for better tracking
- File extension in default filenames now matches the specified format

### Fixed
- Blank error messages in REPL mode when gateway context is missing
- Directory upload for volttron agents now properly creates archives
- Error handling in REPL mode now shows proper error messages

### Removed
- Custom API client implementation (replaced with aceiot-models)
- Batch-size parameter from site timeseries command (no longer needed)

## [0.2.0] - Previous Release

### Added
- Initial Volttron agent deployment support
- REPL mode for interactive command execution
- Site timeseries export functionality