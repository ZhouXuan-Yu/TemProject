# Project Memory Engine

This directory separates durable project truth from noisy runtime memory.

## Source of Truth

Curated files are reviewed project knowledge and may be committed to Git:

- `MEMORY.md` — current project state
- `TASKS.md` — active work and priorities
- `LEARNING.md` — reusable lessons from verified failures
- `DECISIONS.md` — accepted decisions / ADRs
- `config.json` — memory-engine policy

Stable domain knowledge lives under `docs/wiki/`, while architecture lives in `docs/ARCHITECTURE.md`.

## Runtime Layer

`.memory/runtime/` is generated locally by hooks and is ignored by Git.

Typical files:

- `candidates.jsonl` — append-oriented candidate memory events
- `observations.jsonl` — sanitized tool observations
- `promotion-queue.jsonl` — derived review queue
- `promotion-decisions.jsonl` — append-only approval/rejection/supersession audit trail
- `promotion-state.json` — idempotency state for queue building
- `promotion-draft.md` — optional non-authoritative application draft
- `seen.json` — bounded deduplication state
- `session.jsonl` — session lifecycle checkpoints

Runtime information must not be treated as authoritative project truth.

## Promotion Architecture

The promotion path intentionally separates capture, consolidation, review, and application:

```text
User / Tool / Session events
        ↓
  candidates.jsonl
        ↓
 deterministic triage
        ↓
 promotion-queue.jsonl
        ↓
 explicit review action
        ↓
promotion-decisions.jsonl
        ↓
 explicit application only
        ↓
Curated Markdown Source of Truth
```

### Why this design

- Raw events are noisy and should not become project truth automatically.
- Confidence is a triage signal, not authority.
- Corrections and new decisions may conflict with older truth, so they require review.
- Historical decisions should be superseded, not silently deleted.
- Review decisions need an audit trail.
- Hooks must stay fail-open and must not make normal development dependent on the memory subsystem.

This follows the broader Agent-memory direction of separating hot-path state from longer-lived memory and performing consolidation outside the immediate reasoning path.

## Promotion Policy

| Candidate | Proposed destination | Default behavior |
| --- | --- | --- |
| Current implementation/state change | `MEMORY.md` | Queue for review |
| Work item / priority | `TASKS.md` | Queue for review |
| Confirmed mistake + reusable prevention | `LEARNING.md` | Queue for review when explicitly classified |
| Explicit accepted decision | `DECISIONS.md` | High-priority review |
| Stable domain fact | `docs/wiki/` | Review required |
| Temporary observation | Runtime only | Do not promote |

`auto_write_curated_markdown` is intentionally `false`.

The engine does not automatically resolve semantic conflicts. A correction or new decision with related curated context is marked `possible` conflict and requires review.

Supersession is represented as a relationship instead of deletion:

```text
new decision --supersedes--> old decision
```

## Review CLI

Build the queue manually:

```bash
python .claude/hooks/memoryctl.py build
```

List pending candidates:

```bash
python .claude/hooks/memoryctl.py queue
```

Approve a candidate without changing curated Markdown:

```bash
python .claude/hooks/memoryctl.py approve <fingerprint> --target .memory/DECISIONS.md --note "confirmed by project owner"
```

Reject a candidate:

```bash
python .claude/hooks/memoryctl.py reject <fingerprint> --note "temporary discussion only"
```

Record supersession:

```bash
python .claude/hooks/memoryctl.py supersede <fingerprint> --supersedes ADR-003 --target .memory/DECISIONS.md
```

Render explicitly approved records into a draft:

```bash
python .claude/hooks/memoryctl.py export
```

The generated draft still does **not** modify authoritative project files. Application remains an explicit operation until the workflow is validated in real project usage.

## Stop Hook

`Stop` calls the queue builder in fail-open mode. It only derives review items from new candidates. If queue generation fails, Claude Code continues normally.

## Retrieval

`UserPromptSubmit` performs lightweight lexical retrieval against curated project memory and injects only the most relevant chunks into the current turn.

The current provider is `local`. Provider selection is isolated in `.claude/hooks/memory_provider.py` so a semantic/vector memory backend can be added later without changing all hooks.

## Security

Before runtime content is written:

- known secret/token patterns are redacted
- records are truncated
- duplicate records are dropped
- runtime files are rotated at a bounded size

Do not store credentials, patient/private data, secrets, or production dumps in project memory.

## Future Semantic Provider Contract

A provider only needs to implement:

```python
class MemoryProvider:
    def search(self, query: str, limit: int = 4) -> str:
        ...

    def remember(self, record: dict) -> bool:
        ...
```

If an external provider is unavailable, hooks must fail open to the local curated-memory provider rather than breaking normal development.

## Research Requirement

Material changes to this memory architecture must first follow `.claude/rules/research-first.md` and update `docs/AGENT_RESEARCH.md` with the relevant current GitHub/official ecosystem review.
