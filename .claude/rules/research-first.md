# Research-First Engineering Rule

This project uses a research-first approach for Agent infrastructure and foundational architecture.

Before making a material design decision involving Agent architecture, memory, context engineering, RAG, MCP, orchestration, workflow engines, model/tool routing, permissions, security, observability, evaluation, deployment, or a new foundational dependency:

1. Check current official documentation and active GitHub repositories first.
2. Prefer upstream/official projects, active maintenance, production-oriented designs, and clearly documented boundaries.
3. Treat stars and forks as adoption signals only, never as proof of technical correctness.
4. Compare at least the relevant established pattern and the proposed local design.
5. Record meaningful research in `docs/AGENT_RESEARCH.md` before or alongside implementation.
6. Record what is adopted, what is rejected, and why.
7. Reuse established patterns when they fit; deviate only when project constraints justify it.
8. Never copy code blindly. Check license, security implications, maintenance status, and compatibility first.

For code-agent work, current source code remains the final implementation truth. For business rules, curated project documentation remains authoritative.

This rule is mandatory for Agent-platform evolution. It is not required for trivial localized fixes that do not introduce or change architecture.
