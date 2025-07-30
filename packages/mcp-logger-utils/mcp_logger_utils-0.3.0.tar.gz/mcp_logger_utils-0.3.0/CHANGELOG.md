# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.6] - 2025-07-24

### Added
- Added convenience logging methods to MCPLogger class: `debug()`, `info()`, `warning()`, `error()`
  - These methods provide direct access to logger levels without accessing the internal logger
  - Maintains consistent logging interface across MCP servers

### Changed
- Improved compatibility with self-contained MCP servers

## [0.2.5] - 2025-07-24

### Fixed
- Fixed `debug_tool` decorator to properly handle `asyncio.CancelledError`
  - CancelledError is now caught separately and always re-raised
  - Logs a warning when a tool is cancelled by the user
  - Prevents MCP server crashes when users interrupt tool calls

### Changed
- Added `import asyncio` to support CancelledError handling

## [0.2.4] - Previous Version

### Added
- Debug tools for MCP server development
- Automatic cache clearing functionality
- Robust JSON repair utilities