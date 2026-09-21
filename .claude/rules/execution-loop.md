# Execution Loop Rule

This project is execution-first. Memory, MCP, and research support delivery; they do not replace delivery.

## Required lifecycle

For implementation/fix/refactor/configuration/deployment/file-changing work:

1. **Understand** — restate the concrete requested outcome internally and identify observable acceptance evidence.
2. **Plan** — choose the smallest viable sequence of changes and checks.
3. **Execute** — make focused changes using existing architecture.
4. **Verify** — after the latest meaningful code change, run the smallest relevant test/build/lint/typecheck/smoke check.
5. **Repair** — if verification fails, inspect the failure, change the implementation or approach, and retry.
6. **Re-verify** — rerun the relevant check after each repair.
7. **Finish** — stop only when requested deliverables are complete and verification supports the result.

## Acceptance evidence

Valid evidence may include, depending on the project:

- targeted unit/integration tests
- build/compile success
- lint/typecheck/static analysis
- API or CLI smoke test
- browser/UI flow verification
- deployment/health check
- direct reproduction of the original bug followed by a passing reproduction after the fix

Documentation-only changes do not require a code test, but should still be checked for internal consistency when practical.

## Failure behavior

- Do not repeat the same failed command without changing something relevant.
- Do not hide or reinterpret a failing check as success.
- Prefer targeted verification first; expand to broader regression checks when risk warrants it.
- If an external blocker prevents further progress, stop looping and report exactly what is blocked, what was verified, and what remains unverified.
- Never pursue subjective perfection as an endless completion condition.

## Completion enforcement

The Stop stage has two gates:

1. deterministic gate: code-changing work must have verification evidence after the latest meaningful edit;
2. semantic gate: the original user request must be materially satisfied.

If either gate can be resolved by more agent work, Claude should continue automatically instead of returning a premature final answer.

## Longer autonomous work

Claude Code currently provides native `/goal <condition>`, which keeps a session working across turns until a small evaluator judges the condition satisfied. Use it for an explicit session-level end condition when stronger autonomy is wanted.

For long AFK task lists, PRDs, retries, parallel worktrees, or many independent stories, prefer a dedicated outer orchestrator such as Ralphy/Ralph rather than turning project hooks into an unbounded scheduler.

Keep completion conditions objective and bounded.
