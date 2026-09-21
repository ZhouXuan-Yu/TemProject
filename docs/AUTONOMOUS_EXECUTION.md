# Autonomous Execution

TemProject uses three levels of autonomy. They solve different problems and should not be confused.

## Level 1 — Default inner completion loop

This is always active through project Stop hooks.

For code-changing tasks:

```text
Understand
  ↓
Plan
  ↓
Execute
  ↓
Verify
  ↓
Pass? ── yes ──> Semantic acceptance check ── pass ──> Finish
  │
  no
  ↓
Repair
  ↓
Re-verify
  └─────────────── loop
```

The deterministic Stop gate reads bounded runtime observations for the current session. Successful state-changing tools are captured through `PostToolUse`; non-zero Bash failures are captured separately through `PostToolUseFailure`, so a failed verification becomes explicit repair-loop evidence instead of being guessed from output text.

It blocks stopping when:

- a code file was changed;
- no recognized verification command ran after the latest code edit; or
- the latest recognized verification failed.

A second semantic Stop prompt checks whether the user's actual requested outcome was materially completed.

This is the normal mode for everyday Claude Code work.

## Level 2 — Claude Code native /goal

Claude Code currently provides a session-scoped goal loop:

```text
/goal <objective completion condition>
```

After each turn a small evaluator checks the goal. If the condition is not satisfied, Claude starts another turn instead of returning control.

Use this when the user wants a clear multi-turn objective, for example:

```text
/goal the authentication bug is fixed, the reproduction passes, relevant tests pass, and no requested behavior is missing
```

Keep the condition objective. Do not use vague goals such as "make it perfect".

For long or uncertain work, include a bounded escape condition in the goal wording and monitor token/time cost.

Current limitation: /goal is session-scoped and user-invoked. The model cannot reliably create or modify its own native goal in the general case, so TemProject does not depend on it for baseline behavior.

## Level 3 — Outer AFK orchestrator

A Stop hook is not a full task scheduler.

When the work is:

- a PRD with many independent stories;
- hours-long AFK execution;
- branch/worktree-per-task;
- parallel agents;
- repeated retries across separate Claude processes;
- auto-commit / PR creation;
- browser-driven end-to-end flows across many tasks;

prefer a dedicated outer orchestrator.

Current GitHub references include:

- `michaelshimeles/ralphy` — autonomous coding loop with project test/lint/build commands, retry controls, task lists, worktrees, parallel execution and Claude Code support;
- `allierays/agentic-loop` — PRD validation plus implement → code-check → failure feedback → retry flow;
- Ralph-style loops generally — fresh or bounded iterations driven by explicit task state rather than one ever-growing conversation.

TemProject intentionally does not copy those schedulers into the Hook layer.

## Verification commands recognized by the default gate

The baseline recognizes common verification families including:

- pytest / unittest
- npm/pnpm/yarn/bun test, lint, build, check, typecheck
- tsc / eslint / vitest / jest
- ruff / mypy / pyright
- go test
- cargo test/check/clippy
- Maven / Gradle test/check/build
- dotnet test/build
- phpunit
- git diff --check
- Python compileall

The semantic gate still decides whether that evidence is relevant to the requested outcome.

## External blockers

The loop should stop instead of spinning when the remaining work depends on something the agent cannot resolve, such as:

- unavailable credentials;
- a third-party service outage;
- missing user-only business information;
- required hardware/environment not accessible to the agent;
- an explicit approval boundary.

The final response must then state:

1. what is complete;
2. what was verified;
3. the exact blocker;
4. what remains unverified;
5. the next action needed from the user or environment.

## Design principle

**Autonomy is not "never stop". Autonomy is continuing while further agent action can objectively improve the task, and stopping with evidence when the outcome is complete or genuinely blocked.**
