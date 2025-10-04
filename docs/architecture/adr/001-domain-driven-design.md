# ADR-001: Adopt Domain-Driven Design Architecture

**Status:** Accepted
**Date:** 2024-01-15
**Deciders:** Architecture Team

---

## Context

PTY MCP Server needed a sustainable architecture to manage:
- Multiple session types (PTY, process, socket, serial, tmux)
- 37 tools across 6 categories
- Plugin-based extensibility
- Test isolation and maintainability
- Clear separation of concerns

Without architectural guidance, the codebase risked becoming:
- Tightly coupled (hard to test)
- Difficult to extend (new features break existing code)
- Unclear ownership (business logic mixed with infrastructure)
- Hard to understand (no clear layer boundaries)

## Decision

We adopt **Domain-Driven Design (DDD)** with the following layer structure:

### 1. Domain Layer (`core/`)
**Purpose:** Business logic and domain entities
**Contains:**
- `core/manager.py` - SessionManager (domain service)
- `core/sessions/` - Session entities (PTY, process, socket, serial, tmux)

**Rules:**
- NO external dependencies (infrastructure concerns)
- Pure business logic
- Domain entities encapsulate state
- Domain services coordinate entities

### 2. Application Layer (`lib/`)
**Purpose:** Use cases and application services
**Contains:**
- `lib/registry.py` - ToolRegistry (application service)
- `lib/base.py` - BaseTool interface
- `lib/env_manager.py` - Environment management
- `lib/config.py` - Configuration management

**Rules:**
- Orchestrate domain services
- Implement use cases
- Handle application-level concerns
- Depend on domain layer only

### 3. Interface Layer (`plugins/`)
**Purpose:** Tool implementations (adapters)
**Contains:**
- `plugins/terminal/` - 8 tools
- `plugins/process/` - 6 tools
- `plugins/network/` - 6 tools
- `plugins/serial/` - 5 tools
- `plugins/system/` - 6 tools
- `plugins/tmux/` - 6 tools

**Rules:**
- Adapt domain services to tool interface
- User-facing implementations
- Input validation and sanitization
- Output formatting (MCP protocol)

### 4. Infrastructure (Implicit - to be extracted)
**Currently scattered in:**
- `server.py` - MCP protocol adapter
- Session classes - External process/socket management
- `lib/config.py` - File I/O operations

**Future:** Extract to `infrastructure/` directory

## Dependency Flow

```
User Request (MCP)
    ↓
server.py (Infrastructure)
    ↓
SessionManager (Domain Service)
    ↓ injected into
ToolRegistry (Application Service)
    ↓ discovers and instantiates
Tool Implementations (Interface Layer)
    ↓ use
SessionManager methods
    ↓ manage
Domain Entities (Sessions)
    ↓ interact with
External Systems (tmux, ssh, sockets, etc.)
```

**Critical Rule:** Dependencies point INWARD toward the domain.

## Consequences

### Positive

✅ **Testability**
- Domain logic isolated from infrastructure
- Can test business rules without external dependencies
- Mocking is straightforward

✅ **Extensibility**
- New tools added without modifying core
- Plugin architecture naturally fits DDD
- Domain services stable as tools evolve

✅ **Clarity**
- Clear layer boundaries
- Explicit dependencies
- Easy to locate code by responsibility

✅ **Maintainability**
- Changes localized to specific layers
- Domain logic protected from infrastructure changes
- Easier onboarding for new developers

### Negative

⚠️ **Initial Complexity**
- More files and directories
- Requires understanding of DDD concepts
- Need to educate contributors

⚠️ **Potential Over-Engineering**
- Simple features might feel over-structured
- Risk of "architecture astronaut" syndrome
- Must balance purity with pragmatism

### Mitigations

1. **Comprehensive Documentation**
   - This ADR
   - Architecture overview (docs/architecture/README.md)
   - Dependency injection guide

2. **Pragmatic Application**
   - Keep domain layer focused
   - Don't create layers just for purity
   - Refactor when complexity justifies it

3. **Clear Examples**
   - Tmux integration as reference implementation
   - Test suite demonstrates DDD benefits
   - Code reviews enforce patterns

## Compliance Status

**Current Grade: B+ (Very Good)**

✅ **Strengths:**
- 100% Dependency Injection (constructor-based)
- Clear layer separation (core/lib/plugins)
- Plugin architecture aligns with DDD
- Domain entities well-defined
- SessionManager as domain service

⚠️ **Areas for Improvement:**
- Infrastructure layer needs extraction
- "lib" naming could be clearer (consider "application")
- Test organization improved (addressed separately)
- Documentation scattered (addressed by this ADR)

## Related Decisions

- **[ADR-002](./002-tmux-integration.md)** - Tmux multi-session integration
- **Dependency Injection** - See [dependency-injection.md](../dependency-injection.md)

## References

- [Domain-Driven Design (Eric Evans)](https://martinfowler.com/bliki/DomainDrivenDesign.html)
- [Clean Architecture (Uncle Bob)](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Hexagonal Architecture](https://alistair.cockburn.us/hexagonal-architecture/)

---

**Review Date:** 2024-07-15 (6 months)
**Reviewers:** Architecture team, core contributors
