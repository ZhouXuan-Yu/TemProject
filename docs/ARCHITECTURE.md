# Agent Infrastructure Architecture

TemProject v4 is **execution-first**. Memory, MCP, and research are supporting services around the completion loop.

```text
User request
    ↓
Claude Code
    ↓
Understand → Plan → Execute
                    ↓
             state-changing tools
                    ↓
              PostToolUse evidence
                    ↓
                  Stop
        ┌───────────┴───────────┐
        ↓                       ↓
Deterministic gate        Semantic gate
(code changed?)          (request complete?)
        │                       │
        ├─ no verification ─────┤
        ├─ failed verification ─┤
        └─ incomplete outcome ──┤
                                ↓
                         decision: block
                                ↓
                     Repair / continue work
                                ↓
                         Re-verify / Stop
                                │
                           both pass
                                ↓
                              Finish
```

## Supporting layers

```text
CLAUDE.md + .claude/rules/
  └─ operating policy + execution contract

SessionStart
  └─ bounded current state/tasks

UserPromptSubmit
  ├─ bounded curated-memory retrieval
  └─ high-signal memory candidates only

PreToolUse[Bash]
  └─ catastrophic deny / recoverable high-risk ask

PostToolUse[state-changing]
  └─ bounded runtime evidence

Stop command hook
  ├─ incremental memory promotion
  └─ deterministic post-edit verification gate

Stop prompt hook
  └─ semantic completion gate against user outcome

codebase-memory-mcp
  └─ optional structural code intelligence
```

## Curated truth

- `.memory/MEMORY.md`
- `.memory/TASKS.md`
- `.memory/DECISIONS.md`
- `.memory/LEARNING.md`
- `docs/wiki/`

## Runtime evidence

`.memory/runtime/` is ignored by Git and bounded. It contains candidates, observations, promotion state, and review/audit records.

## Autonomy levels

1. **Default inner loop** — Stop hooks enforce verify/repair/re-verify before finish.
2. **Native Claude Code `/goal`** — optional session-level multi-turn objective loop.
3. **Outer orchestrator** — for long AFK PRDs, retries, parallel worktrees and many stories, use a dedicated tool such as Ralphy/Ralph instead of expanding project hooks into a scheduler.

See `docs/AUTONOMOUS_EXECUTION.md`.

## Design rules

- Current source code is exact implementation truth.
- Task completion requires evidence, not merely edits.
- Verification must happen after the latest meaningful code change.
- A failed verification means continue/repair, not "done with caveats" when the agent can still fix it.
- Curated Markdown is reviewed project/domain truth.
- Runtime logs are bounded, non-authoritative evidence.
- MCP accelerates code understanding but never overrides current source.
- Genuine external blockers end the loop with an explicit blocker/unverified report.
- No external observability, vector DB, or outer scheduler is required by default.
