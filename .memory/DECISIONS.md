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

---

## ADR-003 Research-First Agent Engineering

**Status:** Accepted

**Date:** 2026-09-07

### Context

The Agent ecosystem changes quickly. Memory, context engineering, MCP, orchestration, evaluation, workspaces, and coding-agent patterns can materially evolve within months. Designing these layers only from prior experience risks rebuilding solved problems or following stale practices.

### Decision

Material Agent-platform changes must begin with current official documentation and GitHub ecosystem research.

Research is recorded in `docs/AGENT_RESEARCH.md` and should capture:

- upstream projects reviewed
- mainstream patterns observed
- what is adopted
- what is rejected or postponed
- project-specific reasons

### Constraints

- Stars/forks are adoption signals, not proof of technical correctness.
- External code must not be copied without license/security/compatibility review.
- Research is mandatory for foundational Agent architecture changes, not trivial localized fixes.
- Current project constraints may justify deviations, but the reason must be explicit.

### Consequences

Agent architecture decisions become traceable to current ecosystem evidence rather than relying only on model memory or individual preference.

---

## ADR-004 Reviewed Append-Oriented Memory Promotion

**Status:** Accepted

**Date:** 2026-09-07

### Context

Raw conversations and tool observations are noisy. Automatically rewriting authoritative Markdown from every Agent turn creates truth drift, loses history, makes conflict resolution opaque, and weakens auditability.

Current Agent-memory projects increasingly separate runtime state from durable memory and use later extraction/consolidation steps. The project also needs corrections and changed decisions to preserve historical context instead of deleting old records.

### Decision

Adopt a reviewed promotion pipeline:

```text
runtime event
  -> candidate
  -> deterministic triage/confidence
  -> promotion queue
  -> explicit review decision
  -> explicit application to curated truth
```

Runtime candidates and review decisions are append-oriented audit records. Confidence is used only to prioritize review.

### Conflict Policy

- A heuristic may mark a `possible` conflict but must not resolve it automatically.
- Corrections and new decisions with related existing memory require review.
- Replacements use an explicit `supersedes` relationship.
- Old historical records are retained rather than silently deleted.

### Authority Policy

The promotion engine does not directly modify `MEMORY.md`, `TASKS.md`, `LEARNING.md`, `DECISIONS.md`, or `docs/wiki/`.

An approval and its eventual application are separate operations. This separation remains until the workflow is validated with real project use and evaluation data.

### Consequences

The memory system favors auditability and correctness over maximum automatic recall. It may temporarily miss some low-value memories, but it avoids silently converting weak observations into project truth.
