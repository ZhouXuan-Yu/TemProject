# Project Tasks

## Current Task

Final local acceptance of Agent infrastructure v3.

## Acceptance Criteria

- [x] Current GitHub Agent observability/evaluation ecosystem reviewed.
- [x] Duplicate rules and unused abstractions audited.
- [x] `CLAUDE.md` reduced to a compact constitution.
- [x] Ordinary prompts no longer create memory candidates.
- [x] PostToolUse narrowed to state-changing tool classes.
- [x] Write/Edit bodies are not stored in runtime observations.
- [x] Tool results no longer create promotion candidates.
- [x] Promotion queue uses incremental candidate cursor processing.
- [x] Retrieval context budget reduced and relevance floor added.
- [x] Safety guard split into `deny` vs `ask` using Claude Code's supported permission decisions.
- [x] Unused memory provider abstraction removed.
- [x] PreCompact and SessionEnd logging hooks removed.
- [x] Functional config reduced to v3.
- [x] `memoryctl.py doctor` added.
- [x] GitHub Actions Agent-infra regression workflow added.
- [x] Isolated compile + 10 unit/integration tests pass.
- [ ] Pull final version on local development machine.
- [ ] Run the test suite locally.
- [ ] Run `memoryctl.py doctor` locally.
- [ ] Verify Claude Code SessionStart/UserPromptSubmit/PreToolUse/PostToolUse/Stop hooks.
- [ ] Verify `/mcp` connection and repository indexing.
- [ ] Confirm runtime files stay bounded during real usage.

## After Acceptance

Do not add more Agent-platform infrastructure by default. Add a new layer only when a real project requirement appears and after the Research-First protocol.

Optional future trigger: when the repository embeds its own LLM/Agent execution runtime, reevaluate OpenTelemetry-compatible tracing (for example Langfuse/Phoenix/OpenLIT) and dedicated eval/red-team tooling (for example DeepEval/Promptfoo) against actual requirements.
