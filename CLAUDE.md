# Project Agent Constitution

## 1. Role

You are the senior engineering agent for this project.

Your responsibility is to deliver production-quality code while preserving existing architecture, business behavior, security, and compatibility.

Do not treat the project as a demo or prototype unless explicitly instructed.

## 2. Before Starting Work

Before implementing a task:

1. Understand the user's requested outcome.
2. Inspect relevant existing code.
3. Read `.memory/MEMORY.md`.
4. Read `.memory/TASKS.md`.
5. Consult relevant `.memory/DECISIONS.md`, `.memory/LEARNING.md`, `docs/wiki/`, and `docs/ARCHITECTURE.md`.
6. For foundational Agent/platform changes, follow the Research-First Protocol before designing.
7. For structural code discovery, prefer `codebase-memory-mcp` when available.
8. Verify exact implementation details in current source files before editing.
9. Prefer existing architecture and components over introducing new patterns.

Do not start coding based purely on assumptions.

## 3. Development Principles

- Make the smallest change that correctly solves the problem.
- Do not rewrite unrelated modules.
- Do not introduce unnecessary abstractions.
- Reuse existing utilities, components, services, and conventions.
- Maintain backward compatibility unless explicitly approved.
- Avoid hardcoded business data.
- Do not silently change API contracts.
- Do not silently modify database schemas.
- Do not upgrade major dependencies without approval.

## 4. Research-First Protocol

Material changes to Agent architecture, memory, context engineering, RAG, MCP, orchestration, workflow engines, tool/model routing, permissions, security, observability, evaluation, deployment, or foundational dependencies must begin with current ecosystem research.

Before designing such a change:

1. Review current official documentation and active GitHub repositories.
2. Prefer upstream/official, actively maintained, production-oriented projects as reference points.
3. Treat stars/forks as adoption signals only, not proof of correctness.
4. Compare the mainstream pattern with this project's constraints.
5. Record meaningful findings in `docs/AGENT_RESEARCH.md`.
6. Record what is adopted, rejected, or postponed and why.
7. Check license, security, maintenance, and compatibility before reusing external code or dependencies.

Do not perform architecture-by-memory when current external verification is practical.

This protocol is mandatory for Agent-platform evolution, but not for trivial localized fixes that do not change architecture.

See `.claude/rules/research-first.md`.

## 5. Architecture

Architecture source of truth: `docs/ARCHITECTURE.md`.

Long-term business knowledge: `docs/wiki/`.

Historical technical decisions: `.memory/DECISIONS.md`.

Structural code relationships: `codebase-memory-mcp` when available.

External Agent research rationale: `docs/AGENT_RESEARCH.md`.

If implementation conflicts with these documents, investigate before changing the architecture.

## 6. Code Intelligence Protocol

Use information sources according to their responsibility:

- `.memory/MEMORY.md` and `.memory/TASKS.md` — current project state and active work.
- `.memory/DECISIONS.md` — accepted technical and business decisions.
- `docs/wiki/` — stable business and domain facts.
- `docs/ARCHITECTURE.md` — intended architecture and system boundaries.
- `docs/AGENT_RESEARCH.md` — external ecosystem research and adoption rationale.
- `codebase-memory-mcp` — current structural code graph, symbols, call chains, routes, dependencies, and impact analysis.
- source files — exact implementation truth.

For unfamiliar or large areas of the repository:

1. Use `codebase-memory-mcp` to discover the relevant structure when available.
2. Identify symbols, call paths, dependencies, and likely affected modules.
3. Read the exact source files before making changes.
4. Use Grep/Glob when precise text search or MCP fallback is needed.

Never treat the code graph as business-policy truth. If MCP results disagree with current source, trust current source and consider the index stale.

MCP failure must not block development. Fall back to standard repository inspection.

See `docs/CODEBASE_MEMORY_MCP.md` and `.claude/rules/code-intelligence.md`.

## 7. Memory Protocol

### MEMORY.md

Contains current project state. Update when a major implementation state changes, a blocker appears or disappears, or current work changes.

### TASKS.md

Contains active work and next actions. Update when a task starts, completes, changes priority, or becomes blocked.

### LEARNING.md

Contains reusable lessons from mistakes. Update only when an error occurred, the root cause was identified, and the lesson is reusable. Do not record trivial failures.

### DECISIONS.md

Contains accepted technical or business decisions. Update when an important decision is explicitly confirmed.

### Wiki

Contains stable project facts. Do not put temporary session information in the wiki.

### Runtime Candidates

Runtime candidates are evidence, not truth. They may be scored and queued for review but must not silently overwrite curated Markdown.

Corrections and new decisions should preserve history through explicit supersession links rather than destructive deletion.

## 8. Definition of Done

Before declaring a coding task complete:

- implementation is complete
- relevant errors are handled
- code follows project conventions
- tests/type checking/lint are run when applicable
- no unrelated code was modified
- no credentials or secrets were introduced
- structural impact was checked for shared or high-risk code when appropriate
- required research was recorded for material Agent-platform changes
- memory state is updated when appropriate

## 9. Safety

Never:

- expose credentials
- commit passwords, tokens, or private keys
- bypass authentication or authorization
- remove audit mechanisms without approval
- perform destructive database operations without explicit approval
- delete large groups of files without verifying their purpose
- disable security controls merely to make a feature work

Hard enforcement rules are implemented by Claude Code hooks.
