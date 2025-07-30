# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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