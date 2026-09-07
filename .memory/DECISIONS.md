# Architecture & Business Decision Records

---

## ADR-001 Agent Memory Architecture

**Status:** Accepted

**Date:** 2026-08-22

### Context

The project requires long-term AI-assisted development across many Claude Code sessions.

### Decision

Separate persistent agent information into:

- CLAUDE.md — working principles
- MEMORY.md — current state
- TASKS.md — active work
- LEARNING.md — reusable lessons
- DECISIONS.md — accepted decisions
- Wiki — stable knowledge
- ARCHITECTURE.md — system architecture

### Reason

Different categories have different lifecycles and should not be mixed into a single memory file.

### Consequences

Hooks and external memory systems should classify information before writing it.

---

## ADR-002 Codebase Intelligence via codebase-memory-mcp

**Status:** Accepted

**Date:** 2026-09-07

### Context

Large commercial projects require efficient structural code discovery across functions, classes, call chains, routes, dependencies, and module boundaries. Markdown project memory is not suitable for continuously representing the live repository structure.

### Decision

Use `codebase-memory-mcp` as the optional structural code-intelligence layer for Claude Code.

Responsibilities are separated as follows:

- curated Markdown memory stores project state, accepted decisions, reusable lessons, and stable domain knowledge
- `codebase-memory-mcp` stores and queries structural code relationships
- current source files remain the final source of truth for exact implementation

### Constraints

- MCP availability must not become a hard dependency for development.
- Stale graph results must not override current source code.
- Local `.codebase-memory/` indexes are not committed by default.
- Machine-specific binary paths must not be committed to the shared project configuration.

### Consequences

Claude should prefer codebase-memory-mcp for structural discovery and impact analysis, then verify relevant source files before editing.
