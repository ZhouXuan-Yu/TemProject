# Agent Engineering Research Ledger

This document records external research that materially influences the project's Agent architecture. It is intentionally concise: the goal is to preserve design rationale, not mirror external documentation.

## Research Policy

For foundational Agent changes, review current official documentation and active GitHub projects before implementation. Evaluate maintenance activity, adoption, architecture, license, operational fit, and failure modes. Stars/forks are signals only.

Record:

- research date and topic
- upstream projects reviewed
- mainstream patterns observed
- what this project adopts
- what this project rejects or postpones
- why

---

## 2026-09-07 — Agent Memory, Context Engineering, and Coding-Agent Architecture

### Projects reviewed

#### anthropics/claude-code

Role in landscape: primary host/runtime for this project. Relevant patterns include project instructions, hooks, MCP integration, tool execution, and codebase-aware terminal workflows.

Repository: https://github.com/anthropics/claude-code

#### humanlayer/12-factor-agents

Role in landscape: production-oriented Agent engineering principles. A central pattern is explicit ownership of the context window: prompts, RAG, tool history, state, and memory are deliberately composed rather than treated as one undifferentiated transcript.

Repository: https://github.com/humanlayer/12-factor-agents

#### langchain-ai/langgraph

Role in landscape: durable Agent orchestration. Its architecture separates thread/checkpoint state from longer-lived memory and emphasizes resumable/durable execution.

Repository: https://github.com/langchain-ai/langgraph

#### langchain-ai/langmem

Role in landscape: Agent memory management. Relevant pattern: memory can be managed in the hot path while extraction/consolidation can also run as a background process rather than blocking every Agent turn.

Repository: https://github.com/langchain-ai/langmem

#### mem0ai/mem0

Role in landscape: production-oriented memory layer. Relevant direction: additive fact capture, temporal metadata, entity-aware/multi-signal retrieval, and explicit memory lifecycle rather than a single mutable summary blob.

Repository: https://github.com/mem0ai/mem0

#### letta-ai/letta

Role in landscape: stateful Agents with persistent memory and identity. Relevant pattern: Agent state and memory are first-class platform concerns, not just prompt text.

Repository: https://github.com/letta-ai/letta

#### OpenHands/software-agent-sdk and OpenHands

Role in landscape: modular software-engineering Agent runtime. Relevant direction: separate Agent logic from workspaces/execution infrastructure and support durable/isolated environments.

Repositories:
- https://github.com/OpenHands/software-agent-sdk
- https://github.com/OpenHands/OpenHands

#### SWE-agent/SWE-agent

Role in landscape: issue-to-patch software engineering Agent. Useful as a reference for constrained coding workflows and executable task environments.

Repository: https://github.com/SWE-agent/SWE-agent

#### coleam00/claude-memory-compiler

Role in landscape: Claude Code-specific memory compilation. It uses hooks to capture sessions and a later compilation/extraction phase to organize decisions and lessons into structured knowledge instead of writing every raw event directly into long-term memory.

Repository: https://github.com/coleam00/claude-memory-compiler

#### 0ctacity/codebase-memory-mcp

Role in landscape: persistent structural code intelligence through MCP, including graph/vector/full-text/cross-repository search. It is new and therefore remains an optional acceleration layer, never a project source of truth.

Repository: https://github.com/0ctacity/codebase-memory-mcp

### Mainstream patterns observed

1. **Context engineering is explicit.** Current state, retrieved knowledge, tool history, instructions, and long-term memory should have distinct responsibilities.
2. **Short-lived execution state and durable memory are separate.** Session/thread checkpoints are not the same thing as cross-session knowledge.
3. **Long-term memory benefits from consolidation.** Raw events are captured first; higher-quality knowledge is extracted or promoted later.
4. **Authoritative memory should not be silently destructively rewritten.** Additive history, temporal metadata, review, and supersession are safer for production systems.
5. **Human review remains valuable for consequential truth.** Architecture decisions, business facts, and corrections should have an auditable approval path.
6. **Coding Agents increasingly separate reasoning from execution/workspaces.** Code intelligence and isolated workspaces are supporting services rather than the sole Agent brain.
7. **MCP/tool boundaries should be optional and replaceable.** External intelligence services must fail safely without preventing ordinary repository work.

### Adopted for TemProject

- Keep curated Markdown as reviewed project truth.
- Keep runtime observations/candidates append-oriented and non-authoritative.
- Build a derived Promotion Queue instead of letting hooks rewrite curated truth directly.
- Add confidence/priority scoring only as triage signals, not as automatic authority.
- Mark possible conflicts and require review rather than asking a heuristic classifier to resolve them automatically.
- Represent replacement decisions with explicit supersession links; preserve historical records.
- Build review decisions as an append-only audit trail.
- Continue using `codebase-memory-mcp` only for structural code intelligence, with source files as exact implementation truth.
- Preserve a provider boundary so later semantic memory systems can be swapped in.

### Rejected or postponed

- **Automatic LLM rewriting of MEMORY/WIKI/DECISIONS on every turn:** rejected because it creates silent truth drift and weak auditability.
- **Using a vector database as the only source of truth:** rejected; retrieval storage and authoritative project records have different responsibilities.
- **Treating codebase-memory-mcp as authoritative:** rejected; its index may be stale and it is a relatively new dependency.
- **Automatic conflict resolution:** postponed until we have evaluation data. Initial implementation only marks possible conflicts.
- **Automatic application of approved candidates to curated Markdown:** postponed until the review queue is validated locally. Approval and application remain separate operations in v1.

### Resulting design

```text
Runtime Events
    ↓ append
candidates.jsonl
    ↓ deterministic scoring/classification
Promotion Queue
    ↓ human/agent review action
promotion-decisions.jsonl
    ↓ explicit application only
Curated Truth
(MEMORY / TASKS / LEARNING / DECISIONS / WIKI)

Old truth is not silently deleted:
new record ──supersedes──> old record
```

This research snapshot should be revisited before major changes to the Agent platform rather than treated as permanently current.
