# Project Memory

> Current project state only. Do not use this file as a chronological diary.

## Project Phase

Claude Code agent infrastructure v2: research-first architecture + reviewed memory promotion + codebase intelligence.

## Current Objective

Validate the complete Hook/MCP/Promotion lifecycle in a real local Claude Code session, then move to Agent observability/evaluation after another current GitHub ecosystem review.

## Completed

- Project memory architecture defined.
- CLAUDE.md initialized with code-intelligence and Research-First protocols.
- Project rule files created.
- `.claude/rules/research-first.md` enforces current GitHub/official research before material Agent-platform changes.
- `docs/AGENT_RESEARCH.md` records the initial Agent ecosystem research ledger and adoption rationale.
- Claude Code Hook configuration created.
- SessionStart loads current project state and active tasks.
- UserPromptSubmit classifies prompts and performs local curated-memory retrieval.
- PreToolUse contains destructive-command protection.
- PostToolUse records bounded, sanitized observations.
- Runtime candidate-memory capture implemented.
- Runtime deduplication implemented.
- Runtime file rotation/archive implemented.
- Secret/token redaction implemented.
- Memory provider abstraction implemented with local fallback.
- Memory engine policy upgraded to v2.
- Reviewed Promotion Engine implemented in `.claude/hooks/promotion_engine.py`.
- Promotion confidence/priority scoring implemented as triage only.
- Possible conflict marking implemented without automatic conflict resolution.
- Append-oriented promotion review audit implemented.
- Explicit supersession links implemented; old history is not silently deleted.
- `.claude/hooks/memoryctl.py` provides build/queue/approve/reject/supersede/export review commands.
- Stop Hook derives promotion queue entries in fail-open mode without modifying curated truth.
- Standard-library promotion smoke tests added under `tests/agent/test_promotion_engine.py`.
- `codebase-memory-mcp` identified as the structural code-intelligence MCP.
- Project-level `.mcp.json` created using the `codebase-memory-mcp` executable from PATH.
- `.claude/rules/code-intelligence.md` created.
- `docs/CODEBASE_MEMORY_MCP.md` created.
- Local `.codebase-memory/` indexes are ignored by Git.
- ADR-002 records code-intelligence boundaries.
- ADR-003 records research-first Agent engineering.
- ADR-004 records reviewed append-oriented memory promotion.

## In Progress

- Local Claude Code runtime validation
- Local installation/availability of `codebase-memory-mcp`
- Code graph indexing validation
- Local execution of the new promotion-engine smoke tests
- Validation of review queue thresholds against real project usage

## Current Blockers

- Runtime verification requires the local development machine to have the `codebase-memory-mcp` executable installed and available on PATH.
- Hook behavior still needs to be validated against the locally installed Claude Code version.
- The current isolated automation environment cannot reach github.com by DNS, so repository tests could not be executed there after push; the test suite is committed for local execution instead.

## Recently Confirmed

- Material Agent architecture changes must first review current GitHub/official solutions and record adoption rationale.
- Context, runtime state, durable project memory, structural code intelligence, and exact source code have separate responsibilities.
- `codebase-memory-mcp` is used for structural code discovery, call chains, routes, dependencies, and impact analysis.
- Curated Markdown remains the source of truth for project state, decisions, lessons, and business/domain knowledge.
- Current source files remain the final source of truth for exact implementation.
- MCP failure must not block normal development.
- Runtime observations and candidates are not authoritative memory.
- Promotion confidence is a review-priority signal, not authority.
- Curated Markdown must not be silently rewritten from raw tool observations.
- Corrections/conflicting decisions are reviewed and linked through supersession rather than destructive overwrite.

## Next

1. Pull the repository locally.
2. Run `python -m unittest discover -s tests/agent -p "test_*.py"`.
3. Run `python .claude/hooks/memoryctl.py build` and `python .claude/hooks/memoryctl.py queue`.
4. Install `codebase-memory-mcp` and ensure the executable is available on PATH.
5. Start Claude Code inside the repository and run `/mcp`.
6. Confirm `codebase-memory-mcp` is connected and exposes its code-intelligence tools.
7. Index the repository and test structural queries.
8. Validate SessionStart, UserPromptSubmit, PreToolUse, PostToolUse, PreCompact, Stop and SessionEnd payloads.
9. Confirm `.memory/runtime/` queue/audit files are generated and ignored by Git.
10. Research current Agent observability/evaluation approaches on GitHub before designing the next platform layer.
