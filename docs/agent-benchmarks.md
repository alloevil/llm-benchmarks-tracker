# Agent Benchmark 详细介绍

## 目录

- [SWE-bench](#swe-bench)
- [SWE-bench Verified](#swe-bench-verified)
- [WebArena](#webarena)
- [VisualWebArena](#visualwebarena)
- [GAIA](#gaia)
- [AgentBench](#agentbench)
- [OSWorld](#osworld)
- [τ-bench](#τ-bench)
- [MLE-bench](#mle-bench)
- [ARC-AGI-3](#arc-agi-3)
- [BrowseComp](#browsecomp)
- [SimpleQA](#simpleqa)

---

## SWE-bench

**SWE-bench: Can Language Models Resolve Real-World GitHub Issues?** (2023)

- **论文**: https://arxiv.org/abs/2310.06770
- **作者**: Carlos E. Jimenez 等 (Princeton)
- **题量**: 2,294 个真实 Issue

### 测试什么

从 12 个知名 Python 开源项目（Django, Flask, scikit-learn, sympy 等）中收集的真实 GitHub Issue。Agent 需要：

1. 理解 Issue 描述
2. 定位相关代码文件
3. 生成正确的 patch
4. 通过项目的 CI 测试

### 为什么重要

SWE-bench 是衡量"AI 能否替代程序员"的最直接指标。它测试的不是简单的代码生成，而是：
- 理解复杂代码库
- 定位 bug
- 保持代码风格一致
- 不破坏已有功能

### 局限

- 仅限 Python 项目
- 主要是 bug fix，缺乏新功能开发
- 解法可能不唯一

---

## SWE-bench Verified

**SWE-bench Verified: Human-Validated Subset** (2024)

- **发布者**: OpenAI

### 测试什么

SWE-bench 的 500 题人工验证子集，确保：
- 问题描述清晰无歧义
- 测试用例正确
- 解法基本唯一

### 为什么重要

原始 SWE-bench 有噪声（部分题目描述不清、测试有 bug）。Verified 子集更可靠，是当前 SWE-bench 的标准评测集。

---

## WebArena

**WebArena: A Realistic Web Environment for Building Autonomous Agents** (2023)

- **论文**: https://arxiv.org/abs/2307.13854
- **作者**: Shuyan Zhou 等 (CMU)
- **题量**: 812 个任务

### 测试什么

在真实网站环境中（Reddit clone, GitLab, 在线商店, 地图, Wikipedia）完成任务：
- 信息检索（"找到某个帖子的评论数"）
- 表单提交（"创建一个 pull request"）
- 多步操作（"搜索商品并加入购物车"）

### 为什么重要

WebArena 不是模拟环境，而是部署了真实网站。Agent 需要理解网页结构、处理动态内容、正确使用各种 UI 元素。

---

## VisualWebArena

**VisualWebArena: Evaluating Multimodal Agents on Realistic Visual Web Tasks** (2024)

- **论文**: https://arxiv.org/abs/2401.13649
- **题量**: 910 个任务

### 测试什么

WebArena 的视觉扩展版。任务必须理解图像内容才能完成，例如：
- 识别网页中的图标
- 理解图表数据
- 在截图中定位元素

---

## GAIA

**GAIA: A Benchmark for General AI Assistants** (2023)

- **论文**: https://arxiv.org/abs/2311.12983
- **作者**: Grégoire Mialon 等 (Meta / Hugging Face)
- **题量**: 466 个问题

### 测试什么

真实世界问题，需要多步推理和工具使用。分 3 个级别：

| 级别 | 复杂度 | 示例 |
|------|--------|------|
| Level 1 | 简单 | 单次搜索+计算 |
| Level 2 | 中等 | 多步搜索+文件处理 |
| Level 3 | 困难 | 复杂推理链+多工具组合 |

### 为什么重要

GAIA 最接近"通用 AI 助手"的真实使用场景。问题看似简单（人类可以轻松解决），但需要 Agent 具备：
- 工具使用能力（搜索、计算、文件处理）
- 多步推理
- 信息综合

---

## AgentBench

**AgentBench: Evaluating LLMs as Agents** (2023)

- **论文**: https://arxiv.org/abs/2308.03688
- **作者**: Xiao Liu 等 (Tsinghua / Zhipu AI)
- **题量**: 2,000+

### 测试什么

8 个不同环境的 Agent 测试：

| 环境 | 任务类型 |
|------|----------|
| OS | 命令行操作 |
| DB | 数据库查询 |
| KG | 知识图谱推理 |
| Web Shopping | 网购 |
| Web Browsing | 网页浏览 |
| House Holding | 家居任务 |
| Card Game | 数字卡牌 |
| Coding | 编程 |

---

## OSWorld

**OSWorld: Benchmarking Multimodal Agents for Open-Ended Tasks in Real Computer Environments** (2024)

- **论文**: https://arxiv.org/abs/2404.07972
- **题量**: 369 个任务

### 测试什么

在真实操作系统（Ubuntu/Fedora/Windows/macOS）中完成开放式任务：
- 办公软件操作（编辑文档、制作幻灯片）
- 开发环境配置
- 系统管理
- 文件处理

### 为什么重要

OSWorld 是最接近"AI 使用电脑"的评测。Agent 需要操作真实的桌面环境，处理窗口、菜单、对话框等。

---

## τ-bench

**Tau-bench: A Benchmark for Tool-Agent-User Interaction** (2024)

- **论文**: https://arxiv.org/abs/2406.12045
- **作者**: Shunyu Yao 等 (Princeton / Sierra AI)
- **题量**: 300 个任务

### 测试什么

模拟客服场景，Agent 需要：
1. 与用户对话，理解需求
2. 调用 API 工具查询/修改数据
3. 严格遵循政策规则

### 为什么重要

τ-bench 测试的是"Agent + 工具 + 规则遵循"的组合能力，最接近真实的商业 Agent 使用场景。

---

## MLE-bench

**MLE-bench: Evaluating Machine Learning Agents on Machine Learning Engineering** (2024)

- **论文**: https://arxiv.org/abs/2410.07095
- **作者**: Jun Shern Chan 等 (OpenAI)
- **题量**: 75 个 Kaggle 竞赛

### 测试什么

75 个 Kaggle 竞赛，Agent 需要完成完整的 ML 工程流程：
- 数据探索
- 特征工程
- 模型训练
- 超参调优
- 提交结果

---

## ARC-AGI-3

**ARC-AGI-3: A New Challenge for Frontier Agentic Intelligence** (2026)

- **论文**: https://arxiv.org/abs/2603.24621
- **网站**: https://arcprize.org/arc-agi/3

### 测试什么

首个交互式推理基准。与前两代的静态题目不同，ARC-AGI-3 要求 Agent 在环境中通过试错来学习解决视觉推理任务。

### 为什么重要

- **第一个**测试 AI 是否能真正"学习"的基准
- 人类可以 100% 解决，但所有顶尖 AI 得分 < 1%
- 证明当前 AI 在通用推理上与人类差距巨大

---

## BrowseComp

**BrowseComp** (2025)

- **发布者**: OpenAI
- **题量**: 1,000 个问题

### 测试什么

需要深度浏览网页才能回答的问题，测试 Agent 的信息检索和综合能力。

---

## SimpleQA

**SimpleQA: Measuring Short-Form Factuality** (2024)

- **发布者**: OpenAI
- **题量**: 4,326 个问题

### 测试什么

简短事实性问题，有明确的唯一正确答案。测试模型的准确性和幻觉率。
