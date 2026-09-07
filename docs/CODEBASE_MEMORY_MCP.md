# codebase-memory-mcp Integration

This project uses `codebase-memory-mcp` as an optional structural code-intelligence layer for Claude Code.

## Responsibilities

`codebase-memory-mcp` is responsible for repository structure and code relationships such as:

- functions and classes
- symbols and modules
- call chains
- routes and service relationships
- architecture discovery
- impact analysis

It does **not** replace the project's curated memory.

Project responsibilities remain separated:

- `CLAUDE.md` — agent working constitution
- `.memory/MEMORY.md` — current project state
- `.memory/TASKS.md` — active work
- `.memory/LEARNING.md` — reusable engineering lessons
- `.memory/DECISIONS.md` — accepted decisions
- `docs/wiki/` — stable business/domain knowledge
- `docs/ARCHITECTURE.md` — architecture source of truth
- `codebase-memory-mcp` — structural code graph and code discovery

## Installation

Install the `codebase-memory-mcp` executable for your operating system and ensure the executable is available on `PATH`.

The repository-level `.mcp.json` launches:

```json
{
  "mcpServers": {
    "codebase-memory-mcp": {
      "command": "codebase-memory-mcp",
      "args": []
    }
  }
}
```

This intentionally avoids an absolute machine-specific path.

If the executable is not on `PATH`, use a personal/local MCP override rather than committing your absolute path to the repository.

## Claude Code verification

After installation:

1. Open the repository in a terminal.
2. Start Claude Code.
3. Run `/mcp`.
4. Confirm `codebase-memory-mcp` is connected.
5. Ask Claude to inspect repository architecture using the MCP code graph.

If MCP is unavailable, normal Claude Code work must still continue using Grep, Glob, Read, and the project documentation.

## Index lifecycle

The code graph may become stale after major changes.

Re-index when:

- a large refactor has completed
- modules are moved or renamed
- API/service boundaries change
- graph results disagree with current source code

The local generated `.codebase-memory/` directory is intentionally ignored by Git by default. Each developer or environment may rebuild its own index.

## Usage policy

Use codebase memory before broad file-by-file exploration when the question is structural, for example:

- "what calls this function?"
- "which modules depend on this service?"
- "what routes reach this code?"
- "what breaks if this interface changes?"
- "where is this symbol used across the codebase?"

Use normal source reading to confirm exact implementation details before editing.

## Failure policy

The MCP integration is an enhancement, not a hard dependency.

If it fails:

1. Do not stop development.
2. Fall back to normal source inspection.
3. Record recurring integration failures in `.memory/LEARNING.md` only if they reveal a reusable lesson.
4. Do not modify business truth merely because the code index is stale or unavailable.
