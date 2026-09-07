# Project Tasks

## Current Task

Validate Claude Code agent infrastructure v2: research-first workflow, reviewed memory promotion, and codebase-memory-mcp integration.

### Acceptance Criteria

- [x] CLAUDE.md created
- [x] Project rules created
- [x] Research-first Agent engineering rule added
- [x] Agent ecosystem research ledger added
- [x] SessionStart hook implemented
- [x] UserPromptSubmit hook implemented
- [x] PreToolUse protection implemented
- [x] PostToolUse observation implemented
- [x] PreCompact hook implemented
- [x] SessionEnd hook implemented
- [x] Runtime candidate capture implemented
- [x] Secret redaction implemented
- [x] Runtime deduplication implemented
- [x] Runtime rotation/archive implemented
- [x] Memory provider abstraction implemented
- [x] Reviewed Promotion Engine implemented
- [x] Promotion confidence/priority scoring implemented
- [x] Possible conflict marking implemented
- [x] Supersession audit relationship implemented
- [x] Candidate review CLI implemented
- [x] Promotion smoke tests committed
- [x] Stop Hook derives review queue without mutating curated Markdown
- [x] `codebase-memory-mcp` identified
- [x] Project-level `.mcp.json` created
- [x] Code-intelligence rules added
- [x] MCP integration documentation added
- [x] `.codebase-memory/` ignored by Git
- [ ] Execute promotion tests on the local development machine
- [ ] Verify MCP connection with `/mcp` in a real local Claude Code session
- [ ] Verify repository indexing and structural queries
- [ ] Verify hook execution in a real local Claude Code session
- [ ] Verify destructive-operation blocking in a real local session
- [ ] Verify MEMORY/TASKS context injection
- [ ] Verify relevant-memory retrieval on UserPromptSubmit
- [ ] Tune promotion thresholds from real project observations

## P0

- [ ] Pull the repository locally
- [ ] Run `python -m unittest discover -s tests/agent -p "test_*.py"`
- [ ] Run `python .claude/hooks/memoryctl.py build`
- [ ] Inspect `python .claude/hooks/memoryctl.py queue`
- [ ] Install `codebase-memory-mcp` and expose it on PATH
- [ ] Start Claude Code and verify `codebase-memory-mcp` via `/mcp`
- [ ] Index the repository and run structural discovery queries
- [ ] Validate all Hook event payloads against the installed Claude Code version
- [ ] Validate security guard behavior with safe test commands
- [ ] Confirm runtime files are generated under `.memory/runtime/`

## P1

- [ ] Validate approve/reject/supersede/export workflow against real candidates
- [ ] Decide when explicit approved promotion may be safely applied to curated Markdown
- [ ] Add stale/expiry metadata after reviewing real candidate behavior
- [ ] Decide whether to use the MCP project's optional Grep/Glob augmentation hook after local validation
- [ ] Add MCP health/fallback observability if needed

## P2

- [ ] Research current Agent observability/evaluation projects and practices on GitHub
- [ ] Design Agent trace/evaluation layer only after that research
- [ ] Add retrieval hit-rate and memory-growth observability
- [ ] Add promotion precision/acceptance metrics
- [ ] Add regression/evaluation cases for context and memory quality
