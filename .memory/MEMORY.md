# Project Memory

> Current project state only. Do not use this file as a chronological diary.

## Project Phase

Claude Code agent infrastructure v1 implementation.

## Current Objective

Validate the Hook lifecycle locally, then connect the intended external semantic-memory provider through the provider adapter.

## Completed

- Project memory architecture defined.
- CLAUDE.md initialized.
- Project rule files created.
- Claude Code Hook configuration created.
- SessionStart loads current project state and active tasks.
- UserPromptSubmit classifies prompts and performs local curated-memory retrieval.
- PreToolUse contains destructive-command protection.
- PostToolUse records bounded, sanitized observations.
- Runtime candidate-memory capture implemented.
- Runtime deduplication implemented.
- Runtime file rotation/archive implemented.
- Secret/token redaction implemented.
- Memory provider abstraction implemented with local fallback.
- Memory engine policy documented in `.memory/config.json` and `.memory/README.md`.

## In Progress

- Local Claude Code runtime validation
- External semantic-memory provider identification and integration
- Candidate-to-curated-memory promotion workflow

## Current Blockers

- The exact `cobase-memory` / `cobase-memeroy` project intended for integration has not yet been identified. Public search results for `cobase` point to an unrelated JavaScript data-storage package, so no external provider has been wired yet.

## Recently Confirmed

- Curated Markdown remains the source of truth.
- Runtime observations are not authoritative memory.
- External semantic memory is a retrieval layer, not a replacement for project truth.
- Hooks must fall back safely if an external memory provider is unavailable.
- Curated Markdown must not be silently rewritten from raw tool observations.

## Next

1. Pull the repository locally.
2. Start Claude Code inside the repository.
3. Validate SessionStart, UserPromptSubmit, PreToolUse, PostToolUse, PreCompact, Stop and SessionEnd payloads.
4. Confirm `.memory/runtime/` files are generated and ignored by Git.
5. Test a safe destructive-command simulation and confirm PreToolUse blocking behavior.
6. Provide or identify the exact external memory repository/provider.
7. Implement its provider adapter and semantic retrieval.
