# Project Memory

The memory system is deliberately small. Its purpose is to preserve useful project truth across Agent sessions without turning every conversation/tool call into long-term knowledge.

## Curated truth

- `MEMORY.md` — current project state
- `TASKS.md` — active work
- `DECISIONS.md` — accepted ADRs/decisions
- `LEARNING.md` — reusable lessons from verified failures
- `docs/wiki/` — stable domain/business facts

## Runtime evidence

`.memory/runtime/` is local and ignored by Git. It may contain candidates, bounded tool observations, promotion queues, review decisions, and small cursor/dedupe state.

Runtime evidence is never authoritative.

## Capture policy

- Ordinary user prompts are not stored as candidates.
- High-signal corrections, decisions, tasks, and knowledge statements may become candidates.
- Tool results do not become long-term-memory candidates.
- Only state-changing tool classes are observed, and full edit/write contents are not persisted.

## Promotion policy

```text
high-signal candidate
  -> incremental queue
  -> confidence/priority triage
  -> optional related-context/conflict marker
  -> explicit approve/reject/supersede
  -> explicit curated-memory application
```

The engine never silently rewrites curated Markdown. Superseded decisions remain in history.

## Commands

```bash
python .claude/hooks/memoryctl.py doctor
python .claude/hooks/memoryctl.py build
python .claude/hooks/memoryctl.py queue
python .claude/hooks/memoryctl.py approve <fingerprint>
python .claude/hooks/memoryctl.py reject <fingerprint>
python .claude/hooks/memoryctl.py supersede <fingerprint> --supersedes ADR-XXX
python .claude/hooks/memoryctl.py export
```

`codebase-memory-mcp` is optional structural code intelligence. It is not a memory truth store and its absence must not block development.
