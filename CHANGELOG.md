# Changelog

All notable changes to PTY MCP Server will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [4.0.0] - 2025-09-30

### Added
- Full Python package structure for pip/uv distribution
- XDG-compliant configuration paths  
- Package namespace imports (`pty_mcp_server.*`)
- Automated test suite
- PyPI distribution support
- Proper entry point: `pty-mcp-server` command
- Professional README for PyPI

### Changed
- Complete refactoring from source-based to package-based architecture
- Configuration paths now use XDG base directories
- All imports converted to package namespace
- Plugin loading now detects package vs source environment
- Switched from hatchling to setuptools build system
- Repository cleaned and organized for distribution

### Removed
- **BREAKING**: Removed dangerous `exec` tool (security concern)
- Removed sys.path manipulation from all modules
- Cleaned up duplicate source files (120+ duplicates)
- Removed backup directories
- Removed old refactoring scripts

### Fixed
- Plugin loading in packaged environment (was loading 0 tools)
- Import paths for all 31 tools
- Configuration class naming (PtyConfig → ProjectConfig)
- State persistence in package environment

### Security
- Removed exec tool that allowed arbitrary command execution without time limits
- All operations now properly sandboxed

## [3.1.0] - 2025-09-29

### Added
- Dynamic project-specific environment loading for exec commands
- Project .env file support
- Environment merging (system + project)

### Changed
- Exec commands now receive merged environment
- PTY/bash sessions maintain global environment (by design)

## [3.0.0] - 2025-09-29

### Major Architecture Refactoring
- **Perfect Dependency Injection (10/10 Score)**
  - Separated domain logic (/core) from infrastructure (/lib)
  - Config injected into core, never created by it
  - Removed all circular dependencies
  - Clean unidirectional dependency flow

### Structural Improvements
- **Split monolithic session_manager.py**
  - Was: 443 lines in one file
  - Now: Separated into focused modules
    - core/manager.py (87 lines)
    - core/sessions/pty.py (127 lines)
    - core/sessions/process.py (85 lines)
    - core/sessions/socket.py (70 lines)
    - core/sessions/serial.py (86 lines)

### Bug Fixes
- Fixed session cleanup on disconnect
- Fixed stale session detection
- Removed escape sequences from terminal output
- Fixed error message formatting

### Organization
- Renamed plugins/core to plugins/system (avoiding naming conflict)
- Created clean separation: /core (domain), /lib (utilities), /plugins (tools)
- Updated all imports to reflect new structure
- Comprehensive README with architecture documentation

### Tools
- All 32 tools working properly
- Categories: system (7), terminal (8), process (6), network (6), serial (5)

## [2.0.0] - 2025-09-28

### Added
- Plugin-based architecture
- Dynamic tool loading
- Registry system
- 32 tools across 5 categories

### Changed
- Modularized all tools into plugins
- Improved code organization

## [1.0.0] - 2025-09-27

### Added
- Initial release
- Basic PTY functionality  
- Process management
- Network tools
- Serial communication
- Monolithic structure