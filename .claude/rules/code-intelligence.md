# Code Intelligence Rules

`codebase-memory-mcp` is the preferred structural code-discovery layer for this project.

## Use it for

- locating symbols, functions, classes, routes, and modules
- understanding inbound and outbound call chains
- impact analysis before changing shared code
- tracing cross-module and cross-service relationships
- architecture discovery in unfamiliar areas
- dead-code and dependency analysis when relevant

## Retrieval order

1. For current project status, read `.memory/MEMORY.md` and `.memory/TASKS.md`.
2. For accepted project decisions, consult `.memory/DECISIONS.md`.
3. For stable business facts, consult `docs/wiki/`.
4. For code structure and relationships, prefer `codebase-memory-mcp`.
5. Use Grep/Glob/Read to verify exact implementation details and source text.

## Important constraints

- The code graph is an index of the repository, not the source of truth for business policy.
- Always verify exact code before editing critical logic.
- Do not let stale index results override current source files.
- Re-index after substantial refactors when graph results appear stale.
- MCP unavailability must not block development; fall back to normal repository inspection.
- Never treat graph analysis as permission to bypass architecture, security, or database rules.
