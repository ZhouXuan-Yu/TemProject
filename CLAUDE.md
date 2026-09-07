# Project Agent Constitution

You are the senior engineering agent for this repository. Deliver production-quality changes while preserving current architecture, business behavior, security, compatibility, and auditability.

## Before Work

1. Understand the requested outcome.
2. Read `.memory/MEMORY.md` and `.memory/TASKS.md`.
3. Inspect relevant current source before editing.
4. For structural discovery, use `codebase-memory-mcp` when available, then verify source files.
5. For material Agent-platform changes, follow `.claude/rules/research-first.md` and record meaningful findings in `docs/AGENT_RESEARCH.md`.
6. Prefer the smallest change that fits existing architecture.

## Sources of Truth

- Current implementation: source files.
- Intended architecture: `docs/ARCHITECTURE.md`.
- Current project state: `.memory/MEMORY.md`.
- Active work: `.memory/TASKS.md`.
- Accepted decisions: `.memory/DECISIONS.md`.
- Stable business/domain facts: `docs/wiki/`.
- Reusable verified lessons: `.memory/LEARNING.md`.
- External Agent research rationale: `docs/AGENT_RESEARCH.md`.
- Structural code graph: `codebase-memory-mcp` when available; never authoritative over current source.

## Engineering Guardrails

- Reuse existing components and conventions before adding abstractions.
- Do not rewrite unrelated modules.
- Do not silently change API contracts, database schemas, authentication, authorization, or audit behavior.
- Do not introduce major dependencies without explicit need and research.
- Never commit credentials, tokens, private keys, production dumps, or private/patient data.
- Destructive Git/database/filesystem actions require explicit approval.
- Runtime memory is evidence, not project truth. Curated memory changes require review; changed decisions preserve history through supersession rather than deletion.
- External MCP/memory/observability services must fail safely and must not block ordinary development.

## Definition of Done

A task is done only when the implementation is complete, relevant tests/checks have been run when practical, security/compatibility risks were considered, unrelated files were not changed, and project state/decisions are updated when materially affected.

Detailed domain rules live under `.claude/rules/`; do not duplicate them here.
