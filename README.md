# LLM Benchmarks Tracker 📊

> 系统化追踪 LLM 领域的评测基准——模型、Agent、Harness 三维度全覆盖

## 📋 目录

- [什么是 Benchmark？](#什么是-benchmark)
- [分类体系](#分类体系)
- [快速概览](#快速概览)
- [详细数据](#详细数据)
- [时间线](#时间线)
- [如何贡献](#如何贡献)

---

## 什么是 Benchmark？

Benchmark（基准测试）是评估 AI 系统能力的标准化测试集。它定义了一组任务和评分标准，使不同模型/系统之间的能力对比成为可能。

```
┌─────────────────────────────────────────────────────────┐
│                    LLM 评测生态                          │
│                                                         │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐           │
│  │  Harness   │──│ Benchmark │──│  Leaderboard│           │
│  │ (评测框架) │  │ (测试集)  │  │ (排行榜)   │           │
│  └───────────┘  └───────────┘  └───────────┘           │
│       │              │              │                   │
│  EleutherAI    MMLU, HumanEval   Chatbot Arena          │
│  lm-eval       SWE-bench, GAIA   Open LLM LB            │
└─────────────────────────────────────────────────────────┘
```

### 三者关系

| 层级 | 说明 | 类比 |
|------|------|------|
| **Model Benchmark** | 测试基础模型能力（知识、推理、代码） | 考试题目 |
| **Agent Benchmark** | 测试 Agent 在真实环境中完成任务的能力 | 实操考核 |
| **Harness** | 运行 Benchmark 的标准化评测框架 | 考试系统 |

---

## 分类体系

### 🧠 Model Benchmark — 模型能力测试

测试 LLM 本身的**静态能力**：知识问答、数学推理、代码生成、指令遵循等。

| Benchmark | 首发 | 测试维度 | 难度 |
|-----------|------|----------|------|
| MMLU | 2020 | 多学科知识 | ⭐⭐ |
| MMLU-Pro | 2024 | 多学科知识（加强版） | ⭐⭐⭐ |
| HumanEval | 2021 | 代码生成 | ⭐⭐ |
| GSM8K | 2021 | 小学数学推理 | ⭐⭐ |
| MATH | 2021 | 竞赛级数学 | ⭐⭐⭐⭐ |
| ARC-AGI | 2019 | 抽象推理 | ⭐⭐⭐ |
| ARC-AGI-2 | 2025 | 抽象推理（加强版） | ⭐⭐⭐⭐ |
| GPQA | 2023 | 研究生级问答 | ⭐⭐⭐⭐ |
| IFEval | 2023 | 指令遵循 | ⭐⭐ |
| BigBench-Hard | 2022 | 综合推理 | ⭐⭐⭐ |
| TruthfulQA | 2021 | 真实性 | ⭐⭐ |
| HellaSwag | 2019 | 常识推理 | ⭐ |
| WinoGrande | 2019 | 常识推理 | ⭐⭐ |
| DROP | 2019 | 阅读理解 | ⭐⭐ |
| TriviaQA | 2017 | 开放域问答 | ⭐ |

→ 详见 [docs/model-benchmarks.md](docs/model-benchmarks.md)

### 🤖 Agent Benchmark — 智能体能力测试

测试 Agent 在**交互式环境**中完成复杂任务的能力：编码、网页操作、工具使用等。

| Benchmark | 首发 | 测试维度 | 难度 |
|-----------|------|----------|------|
| SWE-bench | 2023 | 真实 GitHub Issue 修复 | ⭐⭐⭐⭐ |
| SWE-bench Verified | 2024 | SWE-bench 人工验证子集 | ⭐⭐⭐⭐ |
| WebArena | 2023 | 网页操作 | ⭐⭐⭐ |
| VisualWebArena | 2024 | 视觉网页操作 | ⭐⭐⭐⭐ |
| GAIA | 2023 | 通用 AI 助手 | ⭐⭐⭐⭐ |
| AgentBench | 2023 | 多环境 Agent | ⭐⭐⭐ |
| OSWorld | 2024 | 操作系统操作 | ⭐⭐⭐⭐ |
| τ-bench | 2024 | 工具使用 + 规则遵循 | ⭐⭐⭐ |
| MLE-bench | 2024 | Kaggle ML 工程 | ⭐⭐⭐⭐ |
| ARC-AGI-3 | 2026 | 交互式推理（首个） | ⭐⭐⭐⭐⭐ |
| BrowseComp | 2025 | 网页浏览理解 | ⭐⭐⭐ |
| SimpleQA | 2024 | 简单事实问答 | ⭐⭐ |

→ 详见 [docs/agent-benchmarks.md](docs/agent-benchmarks.md)

### ⚙️ Harness — 评测框架

提供标准化的评测流程、数据加载、结果计算、排行榜生成。

| Harness | 维护者 | 特点 |
|---------|--------|------|
| EleutherAI lm-eval | EleutherAI | 最广泛使用，支持 400+ benchmark |
| OpenAI Evals | OpenAI | 可自定义 eval，Registry 机制 |
| HELM | Stanford | 全面场景覆盖，多维度评估 |
| OpenCompass | 上海 AI Lab | 中文生态完善 |
| Chatbot Arena | LMSYS | 人类投票 ELO 排名 |
| Open LLM Leaderboard | Hugging Face | 开源模型标准排行 |
| ModelScope | 阿里 | 中文模型评测 |

→ 详见 [docs/harnesses.md](docs/harnesses.md)

---

## 快速概览

### 当前最强模型表现（2026-09）

> 数据来源：各官方排行榜 + Chatbot Arena

| Benchmark | 最高分 | 模型 | 人类基线 |
|-----------|--------|------|----------|
| MMLU | ~90% | GPT-5 / Claude 4 | ~89% |
| HumanEval | ~95% | Claude 4 Opus | - |
| MATH | ~95% | o3 | - |
| SWE-bench Verified | ~75% | Claude 4 Opus | - |
| ARC-AGI-2 | ~60% | o3 | ~95% |
| ARC-AGI-3 | <1% | 所有模型 | 100% |
| GPQA | ~75% | o3 | ~81% |

> ⚠️ 以上数据为近似值，请查阅各排行榜获取最新数据

---

## 详细数据

所有结构化数据存储在 `data/` 目录下：

- [model_benchmarks.json](data/model_benchmarks.json) — 模型基准测试数据
- [agent_benchmarks.json](data/agent_benchmarks.json) — Agent 基准测试数据
- [harnesses.json](data/harnesses.json) — 评测框架数据
- [timeline.json](data/timeline.json) — 时间线数据

每个 Benchmark 的详细介绍见 `docs/` 目录。

---

## 时间线

```
2017  TriviaQA
2019  HellaSwag ─── WinoGrande ─── DROP ─── ARC-AGI
2020  MMLU
2021  HumanEval ─── GSM8K ─── MATH ─── TruthfulQA
2022  BigBench-Hard
2023  GPQA ─── IFEval ─── SWE-bench ─── WebArena ─── GAIA ─── AgentBench ─── HELM
2024  MMLU-Pro ─── VisualWebArena ─── OSWorld ─── τ-bench ─── MLE-bench ─── SimpleQA ─── SWE-bench Verified
2025  ARC-AGI-2 ─── BrowseComp
2026  ARC-AGI-3（首个交互式推理基准）
```

→ 详见 [docs/timeline.md](docs/timeline.md)

---

## 项目结构

```
llm-benchmarks/
├── README.md                          # 本文件
├── data/
│   ├── model_benchmarks.json          # 模型 benchmark 结构化数据
│   ├── agent_benchmarks.json          # Agent benchmark 结构化数据
│   ├── harnesses.json                 # Harness 结构化数据
│   └── timeline.json                  # 时间线数据
├── docs/
│   ├── model-benchmarks.md            # 模型 benchmark 详细介绍
│   ├── agent-benchmarks.md            # Agent benchmark 详细介绍
│   ├── harnesses.md                   # Harness 详细介绍
│   └── timeline.md                    # 完整时间线
├── scripts/
│   └── validate.py                    # 数据校验脚本
└── .github/
    └── workflows/
        └── validate.yml               # CI: 数据格式校验
```

---

## 如何贡献

1. Fork 本仓库
2. 修改 `data/` 下的 JSON 文件
3. 运行 `python scripts/validate.py` 确认格式正确
4. 提交 PR

### 数据格式规范

每个 Benchmark 条目需包含：

```json
{
  "id": "benchmark-id",
  "name": "Benchmark Name",
  "year": 2024,
  "category": "model|agent",
  "description": "一句话描述",
  "paper": "论文链接",
  "website": "官网链接",
  "metrics": ["metric1", "metric2"],
  "difficulty": "easy|medium|hard|expert",
  "task_count": 100,
  "tags": ["tag1", "tag2"]
}
```

---

## License

MIT

## 引用

如果这个项目对你有帮助，请 Star ⭐ 支持！
