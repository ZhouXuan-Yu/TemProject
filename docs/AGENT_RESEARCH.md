# Agent Engineering Research Ledger

Record only ecosystem research that materially changes this project's Agent architecture. The goal is design rationale, not a mirror of upstream documentation.

## Research Policy

For foundational Agent changes, check current official documentation and active GitHub repositories. Prefer upstream projects and current implementation evidence; treat popularity as an adoption signal, not proof. Record what is adopted, rejected, or postponed and why.

---

## 2026-09-07 — Memory, Context Engineering, and Coding-Agent Architecture

### Projects reviewed

- `anthropics/claude-code` — primary host/runtime; project instructions, hooks, MCP, tools.
- `humanlayer/12-factor-agents` — explicit ownership of context composition.
- `langchain-ai/langgraph` — durable/thread state separated from longer-lived memory.
- `langchain-ai/langmem` — hot-path memory plus later consolidation.
- `mem0ai/mem0` — production-oriented persistent memory lifecycle.
- `letta-ai/letta` — stateful Agents with first-class persistent memory.
- `OpenHands/software-agent-sdk` — modular coding-Agent runtime/workspace separation.
- `SWE-agent/SWE-agent` — constrained issue-to-patch coding workflows.
- `coleam00/claude-memory-compiler` — Claude Code session capture followed by later memory compilation.
- `0ctacity/codebase-memory-mcp` — graph/vector/full-text structural code intelligence through MCP.

### Adopted

- Explicit separation between runtime context, durable project truth, structural code intelligence, and current source.
- Append/review promotion rather than automatic LLM rewriting of authoritative Markdown.
- Supersession links instead of destructive historical replacement.
- Optional MCP acceleration with source verification and fail-open fallback.

### Rejected/postponed

- Vector DB as project source of truth.
- Automatic conflict resolution.
- Automatic per-turn rewriting of MEMORY/WIKI/DECISIONS.
- Treating codebase-memory-mcp as authoritative.

---

## 2026-09-07 — Final Runtime Weight, Observability, and Evaluation

### GitHub projects and official implementation reviewed

- `anthropics/claude-code` — current Hook examples confirm matcher expressions such as `Edit|Write|MultiEdit|NotebookEdit`; current Hook schema supports `permissionDecision: allow|deny|ask`.
- `langfuse/langfuse` — active open-source AI engineering platform covering observability, evals, datasets, metrics, and OpenTelemetry integration.
- `Arize-ai/phoenix` — active AI observability and evaluation platform.
- `openlit/openlit` — OpenTelemetry-native AI observability/evaluation platform.
- `confident-ai/deepeval` — dedicated LLM evaluation framework.
- `promptfoo/promptfoo` — prompt/Agent/RAG evaluation, CI/CD, red-team and vulnerability testing.

### Mainstream patterns observed

1. Production Agent/LLM observability is increasingly treated as a dedicated tracing/evaluation concern rather than hand-written logs inside business code.
2. Interoperable/OpenTelemetry-compatible tracing is a strong integration direction in current observability platforms.
3. Evaluation and red-team tooling is most useful when there is an owned model/prompt/Agent runtime plus datasets or repeatable scenarios.
4. Coding-Agent host hooks should stay narrowly matched and deterministic; they should not become a second application platform by default.
5. Deterministic CI tests are still the appropriate first evaluation layer for infrastructure whose behavior can be asserted without calling an LLM.

### Audit findings in TemProject v2

- `CLAUDE.md` duplicated detailed Research-First and Code-Intelligence rules already stored under `.claude/rules/`.
- UserPromptSubmit stored every ordinary prompt as a candidate even though observations never reached promotion.
- PostToolUse ran for all tools, persisted large input/response payloads, and duplicated high-value tool results into candidates that typically scored below the promotion threshold.
- Candidate dedupe rewrote a large global `seen.json` on ordinary tool observations.
- Stop rebuilt the promotion queue by rereading the entire candidate file each turn.
- PreCompact and SessionEnd logs had no downstream consumer.
- `memory_provider.py` had one real implementation and no current external backend.
- v2 config contained policy fields not consumed by code.
- PreToolUse said some actions required approval but always returned `deny`, making approval impossible.

### Adopted for v3

- Compact `CLAUDE.md`; detailed rules remain in specialized files.
- High-signal-only candidate capture.
- PostToolUse matcher narrowed to state-changing tool classes.
- Tool observations store path/command/status/error summaries, not edit/write bodies.
- No tool-result memory candidates.
- Small candidate-only dedupe cache.
- Incremental promotion cursor.
- Bounded retrieval: two results and a small context budget with a relevance floor.
- Remove unused provider and lifecycle logging hooks.
- Tiered safety: catastrophic `deny`, recoverable high-risk `ask`.
- On-demand local doctor + deterministic GitHub Actions tests.
- No Langfuse/Phoenix/OpenLIT/DeepEval/Promptfoo dependency in the baseline template.

### Deferred trigger

Revisit production tracing/evaluation only when a concrete project embeds its own model/Agent runtime, has real trace/eval requirements, or accumulated failure cases that deterministic infrastructure tests cannot cover.
