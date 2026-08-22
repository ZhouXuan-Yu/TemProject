# Project Tasks

## Current Task

Validate Claude Code agent infrastructure and prepare semantic-memory integration.

### Acceptance Criteria

- [x] CLAUDE.md created
- [x] Project rules created
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
- [ ] Verify hook execution in a real local Claude Code session
- [ ] Verify destructive-operation blocking in a real local session
- [ ] Verify MEMORY/TASKS context injection
- [ ] Verify relevant-memory retrieval on UserPromptSubmit
- [ ] Connect the intended external semantic-memory provider

## P0

- [ ] Clone/pull the repository locally and run Claude Code
- [ ] Validate all Hook event payloads against the installed Claude Code version
- [ ] Validate security guard behavior with safe test commands
- [ ] Confirm runtime files are generated under `.memory/runtime/`

## P1

- [ ] Identify the exact external memory project/provider to integrate
- [ ] Implement semantic provider adapter
- [ ] Add semantic retrieval fallback/health checks
- [ ] Add reviewed promotion workflow from candidates to curated Markdown

## P2

- [ ] Add memory confidence scoring
- [ ] Add stale-memory/superseded-decision handling
- [ ] Add candidate review tooling
- [ ] Add observability metrics for retrieval hit rate and memory growth
