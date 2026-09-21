# Project Memory

> Current project state only. Do not use this file as a chronological diary.

## Project Phase

Agent infrastructure v4: execution-first autonomous completion with bounded memory/context support.

## Current Objective

Validate that everyday Claude Code tasks now produce a visible productivity improvement: the agent should keep working through missing/failed verification and stop only after objective evidence plus semantic acceptance, or a genuine external blocker.

## Core Runtime

- `CLAUDE.md` defines an execution contract.
- `.claude/rules/execution-loop.md` defines Verify/Repair/Re-verify behavior.
- SessionStart injects bounded current state/tasks.
- UserPromptSubmit provides bounded curated-memory retrieval and high-signal candidates.
- PreToolUse applies deny/ask safety boundaries.
- PostToolUse stores bounded state-changing evidence.
- Stop command hook performs deterministic post-edit verification gating.
- Stop prompt hook performs semantic completion gating against the original user request.
- Memory promotion remains incremental and reviewed.
- `codebase-memory-mcp` remains optional structural intelligence.

## Important Correction from v3

The previous architecture over-invested in memory governance relative to execution control. In real use, this did not create a noticeable completion improvement because Stop never enforced task acceptance.

v4 therefore treats Memory as support infrastructure and the execution loop as the primary user-value path.

## Autonomy Model

1. **Inner loop (default):** Stop hooks automatically keep Claude working when verification is missing/failed or the user request is incomplete.
2. **Native `/goal` (optional):** stronger explicit session-level objective loop in current Claude Code.
3. **Outer orchestrator (optional):** Ralphy/Ralph-style tools for long AFK PRDs, retries, worktrees, parallel agents and multi-task scheduling.

## Completion Policy

For code-changing work, "done" requires relevant verification after the latest meaningful code edit.

A failure means repair and re-verify while the agent can still act.

A genuine external blocker may end the loop, but the final response must identify what is complete, what was verified, the exact blocker, and what remains unverified.

## Current Validation Status

- v4 implementation committed to GitHub.
- New completion-gate regression tests committed.
- Remote GitHub Actions result for the v4 changes still needs confirmation.
- Real local Claude Code behavior still needs user acceptance testing.

## Next

1. Confirm GitHub Actions passes.
2. Pull latest `main` locally.
3. Run `python -m unittest discover -s tests/agent -p "test_*.py"`.
4. Test missing-verification auto-continuation.
5. Test failing-test repair loop.
6. Test documentation-only and informational tasks.
7. Use native `/goal` for one larger objective and compare the experience.
8. Only after real usage, tune verification detection or semantic gate wording.
