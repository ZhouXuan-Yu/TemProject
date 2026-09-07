# Project Memory

> Current state only; not a chronological diary.

## Project Phase

Claude Code Agent infrastructure v3 — lean final candidate for local acceptance.

## Current Objective

Run the final v3 locally inside Claude Code, verify Hook payloads and `codebase-memory-mcp`, then use this repository as the reusable project baseline.

## Completed

- Research-first Agent engineering and GitHub research ledger.
- Compact `CLAUDE.md` with detailed rules delegated to `.claude/rules/`.
- Optional `codebase-memory-mcp` structural intelligence; current source remains implementation truth.
- Bounded SessionStart current-state injection.
- High-signal-only user memory candidate capture.
- Bounded lexical retrieval: 2 results / 2500 chars / relevance floor.
- Tiered Bash safety guard: catastrophic actions deny; recoverable high-risk actions ask for confirmation.
- PostToolUse restricted to state-changing tool classes and no longer stores Write/Edit bodies.
- Tool results no longer become long-term-memory candidates.
- Reviewed memory promotion with confidence/priority, possible-conflict marking, explicit review, and supersession history.
- Promotion queue changed from repeated full candidate scans to an incremental byte cursor.
- Candidate dedupe cache reduced and removed from ordinary tool observations.
- Unused `memory_provider.py`, PreCompact runtime logging, and SessionEnd runtime logging removed from the final design.
- Memory/runtime config reduced to settings that are actually used.
- On-demand `memoryctl.py doctor` added; no external observability service is required by default.
- GitHub Actions regression workflow added with Python compile + unit tests.
- Final isolated regression suite: 10 tests passed on 2026-09-07.
- First GitHub Actions `Agent Infrastructure` run completed successfully on the final code/test set.

## Current Blockers

- Local Claude Code Hook behavior still needs verification against the user's installed Claude Code version.
- `codebase-memory-mcp` must be installed and available on PATH for structural-intelligence tests; its absence does not block normal development.

## Confirmed Boundaries

- Source files = exact implementation truth.
- Curated Markdown = reviewed project/domain truth.
- Runtime logs/candidates = bounded evidence, never authority.
- `codebase-memory-mcp` = optional structural accelerator, never authority.
- External tracing/eval platforms are deferred until the project contains an actual embedded model/Agent runtime that benefits from them.

## Next

1. `git pull`
2. `python -m unittest discover -s tests/agent -p "test_*.py"`
3. `python .claude/hooks/memoryctl.py doctor`
4. Start Claude Code in the repository and verify hooks with safe test operations.
5. Run `/mcp`, verify `codebase-memory-mcp`, index the repository, and test structural queries.
6. Use the template in real project work; only add external observability/evaluation after real runtime needs appear.
