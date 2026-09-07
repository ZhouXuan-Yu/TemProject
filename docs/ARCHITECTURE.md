# Agent Infrastructure Architecture

```text
Claude Code
  ├─ CLAUDE.md + .claude/rules/      compact operating policy
  ├─ SessionStart                    inject bounded current state/tasks
  ├─ UserPromptSubmit                high-signal candidate capture + bounded retrieval
  ├─ PreToolUse[Bash]                destructive-operation guard
  ├─ PostToolUse[state-changing]     bounded runtime observation only
  ├─ Stop                            incremental promotion-queue build
  └─ codebase-memory-mcp             optional structural code intelligence

Curated truth
  ├─ .memory/MEMORY.md
  ├─ .memory/TASKS.md
  ├─ .memory/DECISIONS.md
  ├─ .memory/LEARNING.md
  └─ docs/wiki/

Runtime evidence (.memory/runtime/, ignored by Git)
  ├─ candidates.jsonl
  ├─ observations.jsonl
  ├─ promotion-queue.jsonl
  ├─ promotion-decisions.jsonl
  └─ small bounded state files
```

## Design Rules

- Current source code is exact implementation truth.
- Curated Markdown is reviewed project/domain truth.
- Runtime logs are bounded, non-authoritative evidence.
- Promotion is incremental and reviewed; confidence only prioritizes review.
- No external observability, vector database, or LLM-eval service is required by default.
- Optional services must be replaceable and fail open to ordinary repository inspection.
