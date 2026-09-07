# Architecture & Business Decision Records

---

## ADR-001 Agent Memory Architecture

**Status:** Accepted  
**Date:** 2026-08-22

Separate persistent Agent information into `CLAUDE.md`, current state, tasks, lessons, decisions, stable wiki knowledge, and architecture documentation. Different information lifecycles must not be mixed into one memory blob.

---

## ADR-002 Codebase Intelligence via codebase-memory-mcp

**Status:** Accepted  
**Date:** 2026-09-07

Use `codebase-memory-mcp` as an optional structural code-intelligence layer for symbols, call chains, routes, dependencies, impact analysis, graph/vector/full-text search. Curated Markdown stores project/domain truth and current source files remain exact implementation truth. MCP failure or stale indexes must not block normal development or override source.

---

## ADR-003 Research-First Agent Engineering

**Status:** Accepted  
**Date:** 2026-09-07

Material Agent-platform changes must begin with current official documentation and active GitHub research. Record meaningful upstream references, adopted patterns, rejected/postponed alternatives, and project-specific reasons in `docs/AGENT_RESEARCH.md`.

---

## ADR-004 Reviewed Append-Oriented Memory Promotion

**Status:** Accepted  
**Date:** 2026-09-07

Runtime evidence does not directly rewrite curated truth. High-signal candidates enter a reviewed promotion pipeline with deterministic triage, possible conflict marking, explicit approve/reject/supersede decisions, and preserved history. Confidence prioritizes review only; it never grants authority.

---

## ADR-005 Lean Default Agent Runtime and Deferred External Observability

**Status:** Accepted  
**Date:** 2026-09-07

### Context

The v2 template accumulated several defensible but overlapping mechanisms: duplicated operating rules, all-tool PostToolUse logging, full tool-result candidate capture, repeated promotion scanning, lifecycle logs with no consumer, a single-implementation memory-provider abstraction, and policy fields not consumed by runtime code.

Current GitHub review also shows mature dedicated observability/evaluation platforms such as Langfuse, Arize Phoenix, OpenLIT, DeepEval, and Promptfoo. These are valuable when an application owns an LLM/Agent runtime, traces model/tool spans, maintains eval datasets, or needs red-team/regression programs. This repository is currently a Claude Code engineering-agent template, not an embedded LLM service.

### Decision

Adopt a lean default runtime:

- keep only SessionStart, UserPromptSubmit, PreToolUse[Bash], selected PostToolUse, and Stop hooks;
- capture user candidates only for high-signal correction/decision/task/knowledge prompts;
- keep tool observations bounded and never persist Write/Edit bodies;
- do not promote raw tool results into long-term-memory candidates;
- process new candidates incrementally with a byte cursor instead of rescanning the full candidate log;
- use a small bounded candidate dedupe cache; ordinary observations do not pay dedupe cost;
- keep local lexical retrieval tightly bounded and relevance-gated;
- remove unused provider/lifecycle abstractions until a real second implementation or consumer exists;
- use deterministic unit/integration tests plus GitHub Actions as the default evaluation layer;
- keep external observability/evaluation dependencies at zero by default.

### Observability Boundary

When a future project embeds a model/Agent runtime and requires production tracing, first evaluate OpenTelemetry-compatible approaches and mature platforms such as Langfuse, Phoenix, or OpenLIT. When model/prompt behavior requires scored regression, adversarial testing, or datasets, evaluate tools such as DeepEval or Promptfoo at that time.

### Safety Boundary

Claude Code officially supports `permissionDecision` values `allow`, `deny`, and `ask`. Catastrophic filesystem/formatting operations are denied; recoverable but destructive Git/database/file operations request confirmation instead of becoming permanently impossible.

### Consequences

The default template has fewer hook invocations, smaller context injection, smaller runtime logs, less repeated disk I/O, fewer unused files/config fields, and no platform service dependency. Advanced observability/evaluation remains an explicit future integration rather than baseline overhead.
