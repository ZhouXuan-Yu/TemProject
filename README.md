# TemProject

> 面向大型商业项目的轻量 Claude Code / Coding Agent 工程模板。
>
> 目标不是把 Agent 基础设施做得越复杂越好，而是让 Claude Code 形成真正可感知的 **执行 → 验证 → 修复 → 再验证 → 完成** 闭环，同时保留可持续上下文、长期项目记忆、代码结构理解、安全约束和低运行开销。

[![Agent Infrastructure](https://github.com/ZhouXuan-Yu/TemProject/actions/workflows/agent-infra.yml/badge.svg)](https://github.com/ZhouXuan-Yu/TemProject/actions/workflows/agent-infra.yml)

## 项目定位

TemProject 用于承载需要长期使用 Claude Code 开发的大型项目。v4 的核心不再是“让 Agent 记住更多”，而是让 Agent **不要在任务尚未验收时停下来**，并在跨会话、跨阶段、多人协作和大型代码库中持续知道：

- 当前项目做到哪里；
- 当前最重要的任务是什么；
- 哪些技术/业务决定已经确认；
- 哪些经验经过验证，可以复用；
- 哪些只是本次会话产生的运行证据；
- 当前代码真实结构是什么；
- 哪些危险操作必须阻止或请求人工确认；
- 当前任务是否真的完成、验证是否发生在最后一次代码修改之后；
- 验证失败后下一轮应该修什么，而不是直接返回“已完成”。

最终原则是：**Execution Loop 负责把任务做完；源码负责实现真相；Curated Memory 负责项目真相；Runtime 只负责证据；MCP 负责加速理解。Memory 是辅助，不再是运行时中心。**

---

## 核心设计

```text
Claude Code
  ├─ CLAUDE.md + .claude/rules/
  │    └─ Agent 工作原则、项目规则、安全边界
  │
  ├─ SessionStart
  │    └─ 注入有限的 MEMORY + TASKS
  │
  ├─ UserPromptSubmit
  │    ├─ 捕获高价值 correction / decision / task / knowledge
  │    └─ 检索少量相关 Curated Memory
  │
  ├─ PreToolUse[Bash]
  │    └─ deny / ask / allow 安全分层
  │
  ├─ PostToolUse[state-changing tools]
  │    └─ 记录有限运行证据，不保存完整编辑正文
  │
  ├─ Stop(command)
  │    ├─ 增量构建 Memory Promotion Queue
  │    └─ 检查最后一次代码修改后是否有验证、验证是否通过
  │
  ├─ Stop(prompt)
  │    └─ 对照用户原始需求做语义验收；未完成则 block 并继续
  │
  └─ codebase-memory-mcp（可选）
       └─ 代码符号 / 调用链 / 路由 / 依赖 / 影响分析

Curated Truth
  ├─ .memory/MEMORY.md
  ├─ .memory/TASKS.md
  ├─ .memory/DECISIONS.md
  ├─ .memory/LEARNING.md
  └─ docs/wiki/

Runtime Evidence（不提交 Git）
  └─ .memory/runtime/
       ├─ candidates.jsonl
       ├─ observations.jsonl
       ├─ promotion-queue.jsonl
       ├─ promotion-decisions.jsonl
       └─ bounded state / cursor files
```

详细架构见 [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)。

---

## 为什么这样设计

### 0. Execution-first：不是“写完代码”，而是“通过验收”

v3 实际使用反馈暴露了一个核心问题：Memory、MCP、Hook 和规则都存在，但 Claude 仍然可以在“已经修改文件、还没有验证”时直接结束，所以用户很难感受到生产力提升。

v4 把主链改成：

```text
Understand
  ↓
Plan
  ↓
Execute
  ↓
Verify
  ↓
失败？ ── yes ──> Repair ──> Re-verify
  │
  no
  ↓
Semantic Acceptance
  ↓
完成？ ── no ──> Continue
  │
  yes
  ↓
Finish
```

Stop 阶段现在有两层 Gate：

1. **Deterministic Gate**：代码发生修改后，最后一次有效代码修改之后必须出现相关 test/build/lint/typecheck/smoke 验证；验证失败就阻止结束。
2. **Semantic Gate**：即使测试通过，也要检查用户原始请求中的交付内容是否真的完成。

Claude Code 官方当前也把 Stop Hook 用于 completeness validation，并提供原生 `/goal <condition>` 在多个 turn 间持续工作直到目标满足。更长时间的 PRD/多任务/并行 worktree 则更适合 Ralph/Ralphy 这类 outer orchestrator。

详细说明见 [`docs/AUTONOMOUS_EXECUTION.md`](docs/AUTONOMOUS_EXECUTION.md)。


### 1. Context Engineering，而不是无限堆上下文

当前 Coding Agent 的主流方向已经从“把所有聊天历史塞给模型”逐步转向 **显式管理 Context Window**：项目状态、当前任务、长期知识、工具结果和检索内容应该拥有不同生命周期。

TemProject 因此只在启动时注入有限项目状态，并在用户提交 Prompt 时最多检索少量高相关记忆，避免上下文不断膨胀。

参考方向：

- [humanlayer/12-factor-agents](https://github.com/humanlayer/12-factor-agents)
- [langchain-ai/langgraph](https://github.com/langchain-ai/langgraph)

### 2. Runtime State 与 Durable Memory 分离

工具调用、普通聊天、临时观察都不应该自动变成长期项目事实。TemProject 将运行数据与长期知识拆开：

```text
Runtime Event
   ↓
Candidate
   ↓
Promotion Queue
   ↓
Review
   ↓
Curated Truth
```

这种思路与当前 Agent Memory 中的 consolidation / lifecycle 方向一致。

参考方向：

- [langchain-ai/langmem](https://github.com/langchain-ai/langmem)
- [mem0ai/mem0](https://github.com/mem0ai/mem0)
- [letta-ai/letta](https://github.com/letta-ai/letta)
- [coleam00/claude-memory-compiler](https://github.com/coleam00/claude-memory-compiler)

### 3. Memory Promotion，而不是自动覆盖事实

TemProject 不允许 Hook 根据一次对话自动重写 `MEMORY.md`、`DECISIONS.md` 或 Wiki。

高价值信息先成为 Candidate，再经过 confidence/priority triage、冲突提示和 review。新的决定如果替代旧决定，使用 `supersedes` 保留历史，而不是删除旧事实。

这使项目在长期迭代中具备更好的审计性，也能避免 Agent 把一次错误理解永久写进知识库。

### 4. Code Graph 与 Project Memory 分工

项目使用 [`codebase-memory-mcp`](https://github.com/0ctacity/codebase-memory-mcp) 作为可选代码结构 intelligence 层，用于：

- symbols / functions / classes；
- call graph；
- HTTP routes；
- dependencies；
- structural discovery；
- impact analysis。

但它不是业务知识库，也不是最终实现真相。MCP 索引如果与当前源码冲突，以当前源码为准。

### 5. Coding Agent 走“Agent + Workspace/Tools”方向

现代 Coding Agent 越来越强调 Agent 推理与实际执行环境的边界，而不是让模型本身承担所有状态和系统职责。TemProject 因此把源码、Memory、MCP、Hook、安全规则拆成独立职责。

参考方向：

- [OpenHands/OpenHands](https://github.com/OpenHands/OpenHands)
- [OpenHands/software-agent-sdk](https://github.com/OpenHands/software-agent-sdk)
- [SWE-agent/SWE-agent](https://github.com/SWE-agent/SWE-agent)
- [michaelshimeles/ralphy](https://github.com/michaelshimeles/ralphy)
- [allierays/agentic-loop](https://github.com/allierays/agentic-loop)

### 6. Observability / Eval 保持可插拔，而不是默认变重

当前 Agent/LLM Observability 与 Evaluation 已经形成比较成熟的独立工具生态，包括：

- [Langfuse](https://github.com/langfuse/langfuse) — tracing、eval、datasets、metrics、OpenTelemetry integration；
- [Arize Phoenix](https://github.com/Arize-ai/phoenix) — AI observability 与 evaluation；
- [OpenLIT](https://github.com/openlit/openlit) — OpenTelemetry-native AI observability；
- [DeepEval](https://github.com/confident-ai/deepeval) — LLM/Agent evaluation；
- [Promptfoo](https://github.com/promptfoo/promptfoo) — Agent/RAG/prompt eval、CI/CD、red-team。

TemProject **当前不默认集成这些平台**。原因是这个仓库首先是 Coding Agent 项目模板，而不是独立 Agent Runtime 平台。只有实际项目出现模型调用链、线上 tracing、评测数据集、成本分析或安全 red-team 需求时，再按照 Research-First 原则选择相应工具。

完整调研记录见 [`docs/AGENT_RESEARCH.md`](docs/AGENT_RESEARCH.md)。

---

## 项目目录

```text
TemProject/
├─ CLAUDE.md                    # Agent 总原则，保持短小
├─ .mcp.json                    # codebase-memory-mcp 项目配置
├─ .claude/
│  ├─ settings.json             # Claude Code Hooks
│  ├─ hooks/
│  │  ├─ session-start.py
│  │  ├─ user-prompt.py
│  │  ├─ pre-tool.py
│  │  ├─ post-tool.py
│  │  ├─ stop.py
│  │  ├─ memory_engine.py
│  │  ├─ promotion_engine.py
│  │  └─ memoryctl.py
│  └─ rules/
│     ├─ security.md
│     ├─ database.md
│     ├─ git.md
│     ├─ testing.md
│     ├─ frontend.md
│     ├─ backend.md
│     ├─ code-intelligence.md
│     └─ research-first.md
├─ .memory/
│  ├─ MEMORY.md                 # 当前项目状态
│  ├─ TASKS.md                  # 当前任务和下一步
│  ├─ DECISIONS.md              # ADR / 已确认决定
│  ├─ LEARNING.md               # 可复用经验
│  ├─ config.json               # Memory v3 运行配置
│  └─ README.md                 # Memory 机制说明
├─ docs/
│  ├─ ARCHITECTURE.md
│  ├─ AGENT_RESEARCH.md
│  ├─ CODEBASE_MEMORY_MCP.md
│  └─ wiki/                     # 稳定业务/领域知识
├─ tests/agent/                 # Agent 基建回归测试
└─ .github/workflows/
   └─ agent-infra.yml           # Python compile + tests
```

---

## Source of Truth 约定

| 内容 | 权威来源 |
| --- | --- |
| 当前代码真实实现 | Source files |
| 预期系统架构 | `docs/ARCHITECTURE.md` |
| 当前项目状态 | `.memory/MEMORY.md` |
| 当前任务 | `.memory/TASKS.md` |
| 已确认技术/业务决定 | `.memory/DECISIONS.md` |
| 稳定业务知识 | `docs/wiki/` |
| 已验证经验 | `.memory/LEARNING.md` |
| Agent 生态调研依据 | `docs/AGENT_RESEARCH.md` |
| 代码结构图谱 | `codebase-memory-mcp`，仅辅助 |
| Runtime observations | 非权威证据 |

---

## Memory 策略

TemProject v4 仍然保持 v3 的小而快 Memory 设计，但 Memory 现在明确属于 Execution Loop 的辅助层：

```json
{
  "retrieval": {
    "max_results": 2,
    "max_chars": 2500,
    "min_token_overlap": 2
  },
  "runtime": {
    "max_record_chars": 4000,
    "max_observation_chars": 1600,
    "max_file_bytes": 1048576,
    "dedupe_cache_size": 512
  },
  "promotion": {
    "batch_size": 25,
    "min_queue_confidence": 0.45
  }
}
```

普通 Prompt 不会自动进入长期记忆。只有 correction、明确 decision、task 和稳定 knowledge 等高信号信息才可能成为 Candidate。

Tool Result 不直接转化为长期记忆；Write/Edit 不保存完整正文；Promotion 使用增量 cursor，不在每次 Stop 时全量扫描历史文件。

---

## 安全策略

`PreToolUse[Bash]` 使用 Claude Code 支持的权限决策模型：

```text
allow  → 正常执行
ask    → 高风险但可能合理，要求用户确认
deny   → 灾难性或明显不可接受操作
```

例如 force push、`git reset --hard`、DROP/TRUNCATE 等属于需要确认的高风险操作；删除根目录、格式化磁盘一类灾难性操作直接拒绝。

规则目标不是让 Agent 什么都不能做，而是让高风险动作具备清晰的人机确认边界。

---

## 快速开始

### 1. 获取项目

```bash
git clone https://github.com/ZhouXuan-Yu/TemProject.git
cd TemProject
```

如果已经克隆：

```bash
git pull
```

### 2. 验证 Agent 基础设施

需要 Python 3.11+：

```bash
python -m unittest discover -s tests/agent -p "test_*.py"
```

再执行健康检查：

```bash
python .claude/hooks/memoryctl.py doctor
```

`codebase-memory-mcp` 未安装时可能显示 WARN，但不会阻塞普通 Claude Code 使用。

### 3. 可选安装 codebase-memory-mcp

按上游 [`0ctacity/codebase-memory-mcp`](https://github.com/0ctacity/codebase-memory-mcp) 的当前安装方式完成安装，并确保：

```bash
codebase-memory-mcp --help
```

可以正常执行。

项目已经通过 `.mcp.json` 注册：

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

### 4. 启动 Claude Code

```bash
claude
```

进入后执行：

```text
/mcp
```

确认 `codebase-memory-mcp` 已连接，然后就可以开始实际项目开发。

### 5. 测试自动完成闭环

给 Claude 一个真实的小型代码修改任务。不要主动提醒它跑测试。

预期行为：

```text
Claude 修改代码
→ 尝试结束
→ Stop Gate 发现没有验证
→ 自动继续
→ 执行相关 test/build/lint/typecheck
→ 如果失败，修复
→ 再验证
→ 语义验收
→ 最终返回
```

对于更明确的多轮目标，可使用 Claude Code 当前原生能力：

```text
/goal 修复登录问题，原始复现不再出现，相关测试通过，并且用户要求的行为全部完成
```

避免使用“做到完美”之类主观目标。

---

## Memory Review CLI

```bash
# 构建/更新 Review Queue
python .claude/hooks/memoryctl.py build

# 查看待审核 Candidate
python .claude/hooks/memoryctl.py queue

# 批准
python .claude/hooks/memoryctl.py approve <fingerprint>

# 拒绝
python .claude/hooks/memoryctl.py reject <fingerprint>

# 新决定替代历史决定
python .claude/hooks/memoryctl.py supersede <fingerprint> --supersedes ADR-XXX

# 导出待应用草稿
python .claude/hooks/memoryctl.py export

# 健康检查
python .claude/hooks/memoryctl.py doctor
```

批准与真正修改 Curated Markdown 是两个独立步骤，避免自动化系统静默修改项目事实。

---

## CI / 回归保护

`.github/workflows/agent-infra.yml` 会在 Agent 基建发生变化时自动执行：

```text
Python compile
      ↓
Agent infrastructure tests
```

当前基线使用 Python 3.11，主要防止 Hook、Memory、Promotion、安全和效率策略在后续修改中发生回退。

---

## Research-First 原则

本项目的 Agent 基础设施不鼓励“凭感觉继续加功能”。涉及以下内容的重大修改前，应先检查当前官方文档与活跃 GitHub 项目：

- Agent architecture；
- Memory / Context Engineering；
- MCP；
- RAG；
- orchestration / workflow；
- tool/model routing；
- permissions / security；
- observability；
- evaluation；
- deployment；
- foundational dependencies。

调研结果需要说明：**看了什么、当前主流是什么、采用什么、不采用什么、为什么。**

这也是本仓库能够长期跟随 Agent 生态变化，而不是快速变成一套过时自定义框架的核心机制。

---

## 当前跟随的主流方向（2026-09）

TemProject 当前主要跟随以下趋势：

1. **Execution Loop > Memory-first**：真正的价值来自实现、验证、修复、再验证和可判定完成；Memory 负责辅助连续性。
2. **Verification as Gate**：代码改动后没有验证，或者验证失败时，不允许直接声明完成。
3. **Semantic + Deterministic Acceptance**：测试证明机器可验证部分，Stop verifier 对照原始需求检查交付完整性。
4. **Inner Loop + Outer Orchestrator 分层**：Stop/`/goal` 负责 session 内闭环，Ralph/Ralphy 类工具负责长时间 PRD、多任务、并行 worktree。
5. **Context Engineering > 无限聊天历史**：显式控制进入模型的状态、知识和工具上下文。
6. **Runtime State 与 Durable Memory 分层**：短期执行状态不等于长期知识。
7. **Memory Consolidation / Promotion**：先采集，再筛选和审核，而不是每轮自动重写长期记忆。
8. **Append / Supersede > Destructive Rewrite**：长期项目更重视审计和历史演进。
9. **MCP / Tooling 可插拔**：代码图谱、检索和外部服务不能成为单点依赖。
10. **Coding Agent + Workspace / Execution Boundary**：Agent 推理、代码执行和环境能力职责分离。
11. **Narrow Hooks + Deterministic Guardrails**：Hook 做明确、可测试的事情，不演变成第二套应用平台。
12. **OTel-compatible Observability**：真正进入 Agent Runtime/生产调用后，再接专业 tracing/eval 系统。
13. **Evaluation as CI**：能够确定性验证的基础设施优先使用自动测试和 CI，而不是所有问题都调用另一个 LLM 判断。
14. **Research-First Evolution**：生态变化快，基础架构决策优先以当前 upstream/官方实现为依据。

---

## 主要参考项目

- [anthropics/claude-code](https://github.com/anthropics/claude-code)
- [humanlayer/12-factor-agents](https://github.com/humanlayer/12-factor-agents)
- [langchain-ai/langgraph](https://github.com/langchain-ai/langgraph)
- [langchain-ai/langmem](https://github.com/langchain-ai/langmem)
- [mem0ai/mem0](https://github.com/mem0ai/mem0)
- [letta-ai/letta](https://github.com/letta-ai/letta)
- [OpenHands/OpenHands](https://github.com/OpenHands/OpenHands)
- [OpenHands/software-agent-sdk](https://github.com/OpenHands/software-agent-sdk)
- [SWE-agent/SWE-agent](https://github.com/SWE-agent/SWE-agent)
- [coleam00/claude-memory-compiler](https://github.com/coleam00/claude-memory-compiler)
- [0ctacity/codebase-memory-mcp](https://github.com/0ctacity/codebase-memory-mcp)
- [langfuse/langfuse](https://github.com/langfuse/langfuse)
- [Arize-ai/phoenix](https://github.com/Arize-ai/phoenix)
- [openlit/openlit](https://github.com/openlit/openlit)
- [confident-ai/deepeval](https://github.com/confident-ai/deepeval)
- [promptfoo/promptfoo](https://github.com/promptfoo/promptfoo)

> 这些项目用于架构方向与工程模式参考。TemProject 并不试图复制或捆绑全部方案，而是只吸收符合当前 Coding Agent 模板目标的部分。

---

## 适用场景

适合：长期商业项目、多人协作项目、较大代码库、需要 Claude Code 跨会话持续工作的项目、需要明确技术决策和项目知识沉淀的项目。

不适合把它当作独立 Agent SaaS、完整 LLM Observability 平台、向量数据库产品或自动化项目管理系统。真正出现这些需求时，应优先接入成熟的专业方案，而不是继续把所有能力塞进本模板。

---

## 当前状态

Agent Infrastructure v4 已根据真实使用反馈从 Memory-first 调整为 **Execution-first**。当前重点不是继续增加基础设施，而是验证自动完成闭环是否真的改善日常开发：未验证不能结束、失败自动修复、通过后再做语义验收。

后续任何重要升级继续遵循：

```text
真实需求
  ↓
GitHub / Official Research
  ↓
主流方案比较
  ↓
项目约束判断
  ↓
ADR / Research Ledger
  ↓
最小实现
  ↓
Tests / CI
```
