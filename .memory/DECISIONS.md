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
