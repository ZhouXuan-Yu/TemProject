# Project Tasks

## Current Task

Validate Agent infrastructure v4 execution-first completion loop in real Claude Code usage.

## Why v4 exists

Real use of v3 showed that memory/context/safety improvements were not enough: Claude could still stop after writing code without completing verification or repairing failures. v4 moves the primary value surface to autonomous task completion.

## Acceptance Criteria

- [x] Current Claude Code Stop/`/goal` behavior researched.
- [x] SWE-agent and Ralph/Ralphy-style execution loops reviewed.
- [x] Execution lifecycle defined: Understand → Plan → Execute → Verify → Repair → Re-verify → Finish.
- [x] Deterministic Stop completion gate implemented.
- [x] Code changes require verification after the latest meaningful edit.
- [x] Failed latest verification blocks stopping and requests repair.
- [x] Semantic Stop verifier added against the original user request.
- [x] Documentation-only changes exempted from code-test requirement.
- [x] `.claude/rules/execution-loop.md` added.
- [x] `docs/AUTONOMOUS_EXECUTION.md` added.
- [x] ADR-006 records execution-first autonomy.
- [x] Completion-gate tests added.
- [x] GitHub Actions passes on the v4 completion-gate commits, including failed-Bash evidence capture.
- [ ] Pull v4 locally.
- [ ] Confirm an implementation task automatically continues when no verification was run.
- [ ] Confirm a failing test causes repair/re-test rather than a final answer.
- [ ] Confirm successful verification plus semantic completion allows normal finish.
- [ ] Confirm informational/no-edit questions do not get trapped in a completion loop.
- [ ] Confirm genuine external blockers return a clear blocker/unverified report.

## Local acceptance scenarios

### Scenario A — missing verification

Ask Claude to make a small code change and do not mention tests. Expected: when Claude tries to finish after editing, Stop blocks it and it automatically runs a relevant verification.

### Scenario B — failing verification

Use a small change where the first test can fail. Expected: Claude receives the failure, repairs the implementation, reruns verification, and only then finishes.

### Scenario C — documentation only

Ask for a README/document edit. Expected: no forced code test from the deterministic gate; semantic completion still applies.

### Scenario D — informational task

Ask a code explanation question with no repository modification. Expected: answer normally with no loop.

## Autonomy modes

- Default: automatic inner Stop acceptance/repair loop.
- Stronger session objective: native Claude Code `/goal <condition>`.
- Long AFK PRD/multi-task/parallel work: optional outer orchestrator such as Ralphy/Ralph.

## After Acceptance

Do not add more Memory/observability infrastructure unless a real project need appears. The next iterations should be driven by completion failures observed in real work: false positives, missed verification commands, loop quality, blocker handling, and semantic acceptance quality.
