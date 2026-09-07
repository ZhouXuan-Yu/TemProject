# Project Memory

> Current project state only. Do not use this file as a chronological diary.

## Project Phase

Claude Code agent infrastructure v1 + codebase intelligence integration.

## Current Objective

Validate the Hook lifecycle and `codebase-memory-mcp` connection in a real local Claude Code session, then implement candidate-to-curated-memory promotion.

## Completed

- Project memory architecture defined.
- CLAUDE.md initialized and updated with code-intelligence protocol.
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
- `codebase-memory-mcp` identified as the structural code-intelligence MCP.
- Project-level `.mcp.json` created using the `codebase-memory-mcp` executable from PATH.
- `.claude/rules/code-intelligence.md` created.
- `docs/CODEBASE_MEMORY_MCP.md` created.
- Local `.codebase-memory/` indexes are ignored by Git.
- ADR-002 records the separation between curated project memory, code graph memory, and source-code truth.

## In Progress

- Local Claude Code runtime validation
- Local installation/availability of `codebase-memory-mcp`
- Code graph indexing validation
- Candidate-to-curated-memory promotion workflow

## Current Blockers

- Runtime verification requires the local development machine to have the `codebase-memory-mcp` executable installed and available on PATH.
- Hook behavior still needs to be validated against the locally installed Claude Code version.

## Recently Confirmed

- `codebase-memory-mcp` is used for structural code discovery, call chains, routes, dependencies, and impact analysis.
- Curated Markdown remains the source of truth for project state, decisions, lessons, and business/domain knowledge.
- Current source files remain the final source of truth for exact implementation.
- MCP failure must not block normal development.
- Runtime observations are not authoritative memory.
- Curated Markdown must not be silently rewritten from raw tool observations.

## Next

1. Pull the repository locally.
2. Install `codebase-memory-mcp` and ensure the executable is available on PATH.
3. Start Claude Code inside the repository and run `/mcp`.
4. Confirm `codebase-memory-mcp` is connected and exposes its code-intelligence tools.
5. Index the repository and test structural queries.
6. Validate SessionStart, UserPromptSubmit, PreToolUse, PostToolUse, PreCompact, Stop and SessionEnd payloads.
7. Confirm `.memory/runtime/` files are generated and ignored by Git.
8. Implement reviewed candidate-to-curated-memory promotion and superseded-decision handling.
