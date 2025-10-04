# PTY MCP Documentation

Welcome to the PTY MCP Server documentation!

## Quick Links

- **[Main README](../README.md)** - Quick start and overview
- **[Architecture](./architecture/README.md)** - Design principles and DDD
- **[API Reference](./api/)** - All 37 tools documented
- **[Development Guide](./development/)** - Contributing guidelines

---

## Documentation Structure

### 📐 Architecture
Understand the design principles and patterns used in PTY MCP.

- **[Overview](./architecture/README.md)** - Domain-Driven Design and layer separation
- **[Dependency Injection](./architecture/dependency-injection.md)** - 100% DI implementation
- **[ADR Index](./architecture/adr/)** - Architecture Decision Records

### ✨ Features
In-depth documentation of specific features and capabilities.

- **[Tmux Integration](./features/tmux-integration.md)** - Multi-session management
- **[Session Management](./features/)** - PTY, process, socket, serial sessions
- **[Project Environments](./features/)** - Dynamic project context

### 📚 API Reference
Complete reference for all tools and interfaces.

- **[Tools Reference](./api/)** - All 37 tools with examples
- **[SessionManager API](./api/)** - Core session management
- **[Plugin Development](./api/)** - Creating new tools

### 🛠️ Development
Guidelines for contributing to PTY MCP.

- **[Setup Guide](./development/)** - Development environment
- **[Testing Guide](../tests/README.md)** - Writing and running tests
- **[Contributing](./development/)** - Pull request process

---

## Finding What You Need

### I want to...

**Understand the architecture:**
→ Start with [Architecture Overview](./architecture/README.md)

**Learn about a specific feature:**
→ Check [Features](./features/) directory

**Use a specific tool:**
→ See [API Reference](./api/) (coming soon)

**Contribute code:**
→ Read [Development Guide](./development/) and [Testing Guide](../tests/README.md)

**Understand a design decision:**
→ Browse [Architecture Decision Records](./architecture/adr/)

---

## Documentation Standards

### For Contributors

When adding documentation:

1. **Architecture docs** → `architecture/` (design decisions, patterns)
2. **Feature docs** → `features/` (user-facing capabilities)
3. **API docs** → `api/` (tool reference, interfaces)
4. **Development docs** → `development/` (contributing guidelines)

### Format

- Use Markdown (.md)
- Include code examples
- Link to related docs
- Update this index when adding new docs

---

## External Resources

- **[MCP Protocol Specification](https://modelcontextprotocol.io/docs)**
- **[Python DDD Resources](https://github.com/ddd-crew)**
- **[Dependency Injection Patterns](https://martinfowler.com/articles/injection.html)**

---

## Need Help?

- 📋 Check [Issues](https://github.com/Sundeepg98/pty-mcp-server/issues)
- 💬 Start a [Discussion](https://github.com/Sundeepg98/pty-mcp-server/discussions)
- 📧 Email: sundeepg8@gmail.com
