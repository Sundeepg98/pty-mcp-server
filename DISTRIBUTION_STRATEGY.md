# PTY MCP Server - Distribution Strategy Recommendation

## Executive Summary
**Recommendation:** Use the SAME repository with proper versioning and multiple distribution channels.

---

## Current Situation
- **v3.1.0**: Original source version (had dangerous exec tool)
- **v4.0.0**: Refactored package version (31 secure tools)
- **Working Package**: `pty-mcp-server` installable via `uv tool install`

---

## Distribution Options Analysis

### Option 1: New Repository (NOT Recommended ❌)
**Pros:**
- Clean slate for package version
- No legacy code confusion

**Cons:**
- Splits community and contributions
- Loses GitHub stars, issues, history
- Maintenance overhead (2 repos)
- Confuses users about which to use
- Harder to track evolution

### Option 2: Same Repository (RECOMMENDED ✅)
**Pros:**
- Single source of truth
- Preserves project history
- Easier maintenance
- Clear upgrade path
- Better for SEO/discovery

**Cons:**
- Need clear version separation

---

## Recommended Implementation Plan

### 1. Repository Structure
```
pty-mcp-python/
├── README.md                 # Clear installation instructions
├── pyproject.toml           # Package configuration
├── LICENSE
├── CHANGELOG.md             # Version history
├── .github/
│   └── workflows/
│       ├── test.yml         # CI testing
│       └── publish.yml      # PyPI publishing
├── pty_mcp_server/          # Package source (v4.0.0+)
│   ├── __init__.py
│   ├── server.py
│   ├── core/
│   ├── lib/
│   └── plugins/
├── legacy/                   # Old source version (optional)
│   └── v3.1.0/              # Archive of old version
└── docs/
    ├── installation.md
    ├── migration.md         # v3 → v4 guide
    └── api.md
```

### 2. Distribution Channels

#### Primary: PyPI (Professional) 🎯
```bash
# Users can install with:
pip install pty-mcp-server
# or
uv tool install pty-mcp-server
```

**Steps:**
1. Register package name on PyPI
2. Set up API tokens
3. Configure GitHub Actions for auto-publish
4. Maintain semantic versioning

#### Secondary: GitHub Releases
```bash
# Direct from GitHub:
uv tool install git+https://github.com/yourusername/pty-mcp-python@v4.0.0
```

#### Development: Direct from source
```bash
# For developers:
git clone https://github.com/yourusername/pty-mcp-python
cd pty-mcp-python
uv tool install --from .
```

---

## Version Management Strategy

### Branching Model
```
main           → Latest stable (v4.x.x)
develop        → Development branch
legacy/v3      → Old source version (archived)
feature/*      → New features
release/v*     → Release preparation
```

### Version Tags
- `v3.1.0` - Last source-only version
- `v4.0.0` - First package version
- `v4.1.0` - Future updates

### Semantic Versioning
- **Major (4.x.x)**: Breaking changes
- **Minor (x.1.x)**: New features, backward compatible
- **Patch (x.x.1)**: Bug fixes

---

## Migration Documentation

### README.md Updates
```markdown
# PTY MCP Server

A Model Context Protocol server for PTY, process, network, and serial operations.

## Installation

### Quick Install (Recommended)
```bash
# Via PyPI
pip install pty-mcp-server

# Or using uv
uv tool install pty-mcp-server
```

### From Source
```bash
git clone https://github.com/yourusername/pty-mcp-python
cd pty-mcp-python
uv tool install --from .
```

### Legacy Version (v3.x)
⚠️ The legacy source version is deprecated. See [migration guide](docs/migration.md).

## What's New in v4.0.0
- ✅ Proper Python package structure
- ✅ Removed dangerous `exec` tool
- ✅ XDG-compliant configuration
- ✅ 31 secure tools
- ✅ PyPI distribution
```

---

## Publishing Workflow

### Initial PyPI Setup
```bash
# 1. Create PyPI account
# 2. Generate API token
# 3. Test on TestPyPI first
python -m build
twine upload --repository testpypi dist/*

# 4. Publish to PyPI
twine upload dist/*
```

### GitHub Actions (`.github/workflows/publish.yml`)
```yaml
name: Publish to PyPI
on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Build and publish
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
        run: |
          pip install build twine
          python -m build
          twine upload dist/*
```

---

## Timeline

### Phase 1: Repository Preparation (Day 1)
- [x] Clean up repository structure
- [ ] Move old source to `legacy/` folder
- [ ] Update README with clear instructions
- [ ] Add CHANGELOG.md

### Phase 2: PyPI Setup (Day 2)
- [ ] Register `pty-mcp-server` on PyPI
- [ ] Test on TestPyPI
- [ ] Set up GitHub Actions
- [ ] First official release (v4.0.0)

### Phase 3: Documentation (Day 3)
- [ ] Migration guide (v3 → v4)
- [ ] API documentation
- [ ] Example usage
- [ ] MCP integration guide

### Phase 4: Promotion
- [ ] Update MCP server lists
- [ ] Announce on relevant forums
- [ ] Create GitHub release

---

## Package Metadata (pyproject.toml)

```toml
[project]
name = "pty-mcp-server"
version = "4.0.0"
description = "Model Context Protocol server for PTY, process, network, and serial communication"
authors = [{name = "Your Name", email = "your.email@example.com"}]
license = {text = "MIT"}
readme = "README.md"
homepage = "https://github.com/yourusername/pty-mcp-python"
repository = "https://github.com/yourusername/pty-mcp-python"
keywords = ["mcp", "pty", "terminal", "ssh", "serial", "claude"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Software Development :: Libraries",
    "Topic :: System :: Terminals"
]
```

---

## Decision Summary

### Use SAME Repository Because:
1. **Continuity**: Preserves project history and community
2. **Discoverability**: Better SEO, existing stars/watchers
3. **Simplicity**: One repo to maintain
4. **Clear Path**: Users can see evolution from v3 to v4

### Distribution via PyPI Because:
1. **Standard**: Python community expectation
2. **Easy**: `pip install pty-mcp-server`
3. **Professional**: Shows maturity
4. **Automated**: CI/CD for releases

### Next Steps:
1. Decide on PyPI package name (suggest keeping `pty-mcp-server`)
2. Clean up repository structure
3. Register on PyPI
4. Set up automated publishing
5. Release v4.0.0 officially

---

## Questions to Resolve

1. **GitHub username/organization?** Need this for URLs
2. **PyPI account ready?** Need to register package name
3. **Keep legacy code visible?** Archive in `legacy/` folder?
4. **Documentation hosting?** GitHub Pages or just README?

---

This approach gives you the best of both worlds: professional package distribution while maintaining project continuity.