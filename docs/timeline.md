# LLM Benchmark 时间线

## 2017

| 类型 | 名称 | 说明 |
|------|------|------|
| Model | TriviaQA | 开放域问答基准 |

## 2019

| 类型 | 名称 | 说明 |
|------|------|------|
| Model | ARC-AGI | François Chollet 发布抽象推理基准 |
| Model | HellaSwag | 常识推理（Adversarial Filtering） |
| Model | WinoGrande | 大规模代词消歧 |
| Model | DROP | 离散推理阅读理解 |

## 2020

| 类型 | 名称 | 说明 |
|------|------|------|
| Model | MMLU | 57 学科多选题，成为标准知识基准 |
| Harness | lm-eval-harness | EleutherAI 发布评测框架 |

## 2021

| 类型 | 名称 | 说明 |
|------|------|------|
| Model | HumanEval | OpenAI 代码生成基准 |
| Model | GSM8K | OpenAI 小学数学推理 |
| Model | MATH | UC Berkeley 竞赛级数学 |
| Model | TruthfulQA | Oxford 真实性测试 |

## 2022

| 类型 | 名称 | 说明 |
|------|------|------|
| Model | BigBench-Hard | 从 BIG-Bench 筛选的 23 个最难任务 |

## 2023 — Agent 元年

这是 LLM 评测的分水岭。Agent 评测框架首次大规模出现，标志着行业从"模型能做什么"转向"模型能完成什么任务"。

| 类型 | 名称 | 说明 |
|------|------|------|
| Model | GPQA | 研究生级 Google-Proof 问答 |
| Model | IFEval | 指令遵循评估 |
| Agent | SWE-bench | 真实 GitHub Issue 修复 |
| Agent | WebArena | 真实网站环境操作 |
| Agent | GAIA | 通用 AI 助手基准 |
| Agent | AgentBench | 8 环境 Agent 综合测试 |
| Harness | HELM | 斯坦福全面评测框架 |
| Harness | OpenCompass | 上海 AI Lab 中文评测平台 |
| Harness | Chatbot Arena | LMSYS 人类偏好盲评 |
| Harness | Open LLM Leaderboard | HF 开源模型排行榜 |

## 2024 — Agent 精细化

Agent 评测从"能用"走向"好用"，细分场景和验证标准出现。

| 类型 | 名称 | 说明 |
|------|------|------|
| Model | MMLU-Pro | MMLU 加强版，10 选项 |
| Agent | SWE-bench Verified | 人工验证子集（500 题） |
| Agent | VisualWebArena | 视觉网页操作 |
| Agent | OSWorld | 真实操作系统操作 |
| Agent | τ-bench | 工具使用 + 规则遵循 |
| Agent | MLE-bench | Kaggle ML 工程 |
| Agent | SimpleQA | 简单事实问答 |
| Harness | Inspect AI | UK AISI Agent 评测框架 |

## 2025

| 类型 | 名称 | 说明 |
|------|------|------|
| Model | ARC-AGI-2 | 抽象推理加强版 |
| Agent | BrowseComp | 网页浏览理解 |

## 2026

| 类型 | 名称 | 说明 |
|------|------|------|
| Agent | ARC-AGI-3 | **首个交互式推理基准**，所有 AI < 1%，人类 100% |

---

## 趋势观察

1. **2019-2021**: 静态基准的黄金期（MMLU、HumanEval、GSM8K）
2. **2022**: 静态基准逐渐饱和
3. **2023**: Agent 评测元年（SWE-bench、WebArena、GAIA）
4. **2024**: Agent 评测精细化（更真实的环境、更严格的验证）
5. **2025-2026**: 交互式评测出现（ARC-AGI-3），测试"学习能力"而非"已有能力"
