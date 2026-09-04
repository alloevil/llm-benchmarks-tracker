# Harness（评测框架）详细介绍

## 什么是 Harness？

Harness（评测框架）是运行 Benchmark 的标准化工具。它提供：
- 统一的模型 API 接口
- 数据加载和预处理
- 结果计算和统计
- 排行榜生成

一个好的 Harness 应该：
- 支持多种模型后端
- 结果可复现
- 易于扩展新任务

---

## 目录

- [EleutherAI lm-eval-harness](#eleutherai-lm-eval-harness)
- [OpenAI Evals](#openai-evals)
- [HELM](#helm)
- [OpenCompass](#opencompass)
- [Chatbot Arena](#chatbot-arena)
- [Open LLM Leaderboard](#open-llm-leaderboard)
- [ModelScope 评测](#modelscope-评测)
- [Inspect AI](#inspect-ai)

---

## EleutherAI lm-eval-harness

- **维护者**: EleutherAI
- **仓库**: https://github.com/EleutherAI/lm-evaluation-harness
- **首次发布**: 2020

### 特点

最广泛使用的 LLM 评测框架，支持 400+ benchmark。

**优势**：
- 支持 HuggingFace、vLLM、Anthropic、OpenAI、Claude 等多种后端
- 任务定义简洁（YAML 配置）
- 支持分布式评估
- 结果缓存，避免重复计算

**使用方式**：
```bash
lm_eval --model hf --model_args pretrained=gpt2 --tasks mmlu,hellaswag
```

### 为什么选它

如果你只想用一个框架评估所有主流 benchmark，lm-eval 是首选。

---

## OpenAI Evals

- **维护者**: OpenAI
- **仓库**: https://github.com/openai/evals
- **首次发布**: 2023

### 特点

OpenAI 的开源评测框架，核心是 Registry 机制。

**优势**：
- 自定义 eval 非常方便
- 社区贡献的 eval 库
- 与 OpenAI API 深度集成

**使用方式**：
```bash
oaieval gpt-3.5-turbo match-fuzzy
```

---

## HELM

**Holistic Evaluation of Language Models**

- **维护者**: Stanford CRFM
- **网站**: https://crfm.stanford.edu/helm
- **首次发布**: 2023

### 特点

斯坦福的全面评测框架，强调"全面性"。

**优势**：
- 覆盖 42+ 场景、29+ 指标
- 每个场景都有标准化的 prompt 模板
- 透明的评估报告
- 强调可复现性

**局限**：配置复杂，运行较慢。

---

## OpenCompass

- **维护者**: 上海 AI Lab
- **网站**: https://opencompass.org.cn
- **首次发布**: 2023

### 特点

中文大模型评测平台。

**优势**：
- 中文评测最完善（C-Eval, CMMLU 等）
- 支持 100+ 数据集
- 提供完整排行榜
- 社区活跃

---

## Chatbot Arena

- **维护者**: LMSYS
- **网站**: https://chat.lmsys.org
- **首次发布**: 2023

### 特点

基于人类偏好的盲评平台。

**机制**：
1. 用户提问
2. 两个匿名模型同时回答
3. 用户投票选择更好的回答
4. 使用 Elo/Bradley-Terry 系统计算排名

**为什么重要**：这是目前最大规模的人类偏好评测，被认为是最接近"真实使用体验"的排名。

---

## Open LLM Leaderboard

- **维护者**: Hugging Face
- **网站**: https://huggingface.co/spaces/open-llm-leaderboard
- **首次发布**: 2023

### 特点

开源模型的标准排行榜。

**评测集**（v2）：
- ARC-Challenge
- HellaSwag
- MMLU-Pro
- TruthfulQA
- Winogrande
- GSM8K

---

## ModelScope 评测

- **维护者**: 魔搭社区（阿里）
- **网站**: https://modelscope.cn
- **首次发布**: 2023

### 特点

中文评测生态完善，与 ModelScope 模型库深度集成。

---

## Inspect AI

- **维护者**: UK AISI（英国 AI 安全研究所）
- **仓库**: https://github.com/UKGovernmentBEIS/inspect_ai
- **首次发布**: 2024

### 特点

特别适合 Agent 评测的框架。

**核心概念**：
- **Solver**: 问题解决策略
- **Tool**: Agent 可使用的工具
- **Scorer**: 评分函数

**为什么选它**：如果你要评测 Agent 而非简单的 LLM，Inspect AI 是最佳选择。

---

## 如何选择？

| 需求 | 推荐 |
|------|------|
| 评估主流 benchmark | lm-eval-harness |
| 中文模型评测 | OpenCompass |
| 人类偏好排名 | Chatbot Arena |
| Agent 评测 | Inspect AI |
| 全面评估+报告 | HELM |
| 自定义 eval | OpenAI Evals |
