# Project Memory Engine

This directory separates durable project truth from noisy runtime memory.

## Source of Truth

Curated files are reviewed project knowledge and may be committed to Git:

- `MEMORY.md` — current project state
- `TASKS.md` — active work and priorities
- `LEARNING.md` — reusable lessons from verified failures
- `DECISIONS.md` — accepted decisions / ADRs
- `config.json` — memory-engine policy

Stable domain knowledge lives under `docs/wiki/`, while architecture lives in
`docs/ARCHITECTURE.md`.

## Runtime Layer

`.memory/runtime/` is generated locally by hooks and is ignored by Git.

Typical files:

- `candidates.jsonl` — candidate memories waiting for promotion
- `observations.jsonl` — sanitized tool observations
- `seen.json` — bounded deduplication state
- `session.jsonl` — session lifecycle checkpoints

Runtime information must not be treated as authoritative project truth.

## Promotion Policy

Runtime candidates are classified before promotion:

| Candidate | Destination | Review |
| --- | --- | --- |
| Current state change | `MEMORY.md` | Required for material changes |
| Work item / priority | `TASKS.md` | Required |
| Confirmed mistake + reusable prevention | `LEARNING.md` | Required |
| Explicit accepted decision | `DECISIONS.md` | Required |
| Stable domain fact | `docs/wiki/` | Required |
| Temporary observation | Runtime only | No promotion |

The default policy intentionally sets `auto_write_curated_markdown=false`.
Production project memory should prefer missing a low-value memory over silently
writing incorrect long-term truth.

## Retrieval

`UserPromptSubmit` performs lightweight lexical retrieval against curated
project memory and injects only the most relevant chunks into the current turn.

The current provider is `local`. Provider selection is isolated in
`.claude/hooks/memory_provider.py` so a semantic/vector memory backend can be
added later without changing all hooks.

## Security

Before runtime content is written:

- known secret/token patterns are redacted
- records are truncated
- duplicate records are dropped
- runtime files are rotated at a bounded size

Do not store credentials, patient/private data, secrets, or production dumps in
project memory.

## Future Semantic Provider Contract

A provider only needs to implement:

```python
class MemoryProvider:
    def search(self, query: str, limit: int = 4) -> str:
        ...

    def remember(self, record: dict) -> bool:
        ...
```

If an external provider is unavailable, hooks must fail open to the local
curated-memory provider rather than breaking normal development.
