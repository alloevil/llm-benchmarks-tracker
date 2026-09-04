# 模型 Benchmark 详细介绍

## 目录

- [MMLU](#mmlu)
- [MMLU-Pro](#mmlu-pro)
- [HumanEval](#humaneval)
- [HumanEval+](#humaneval-1)
- [MBPP](#mbpp)
- [GSM8K](#gsm8k)
- [MATH](#math)
- [GPQA](#gpqa)
- [IFEval](#ifeval)
- [BigBench-Hard](#bigbench-hard)
- [TruthfulQA](#truthfulqa)
- [HellaSwag](#hellaswag)
- [WinoGrande](#winogrande)
- [DROP](#drop)
- [TriviaQA](#triviaqa)

---

## MMLU

**Massive Multitask Language Understanding** (2020)

- **论文**: https://arxiv.org/abs/2009.03300
- **作者**: Dan Hendrycks, Collin Burns, Steven Basart, Andy Zou, Mantas Mazeika, Dawn Song, Jacob Steinhardt (UC Berkeley)
- **题量**: 15,908 道多选题

### 测试什么

MMLU 覆盖 57 个学科，从初中到研究生级别：

| 类别 | 学科举例 |
|------|----------|
| STEM | 数学、物理、化学、生物、计算机科学 |
| 人文 | 历史、哲学、法律 |
| 社商 | 经济学、心理学、商业 |
| 其他 | 医学、护理、全球文化 |

### 为什么重要

MMLU 是最广泛使用的 LLM 知识基准。它能快速判断一个模型的"知识面"是否足够广。但随着模型越来越强，MMLU 逐渐饱和（top 模型 ~90%），区分度下降。

### 局限

- 纯选择题，不测试生成能力
- 部分题目有歧义或错误（后有 MMLU-Redux 修复）
- 不测试推理深度

---

## MMLU-Pro

**MMLU-Pro: A More Robust and Challenging Multi-Task Language Understanding Benchmark** (2024)

- **论文**: https://arxiv.org/abs/2406.01574
- **作者**: Yubo Wang 等 (TIGER-AI-Lab)
- **题量**: 12,032 道

### 测试什么

MMLU 的加强版：
- 10 个选项（MMLU 为 4 个），降低猜测概率
- 移除简单/有歧义题目
- 增加需要复杂推理的题目
- 减少模型对 prompt 格式的敏感性

### 为什么重要

MMLU 逐渐饱和后，MMLU-Pro 成为更有效的区分工具。当前最强模型在 MMLU-Pro 上 ~78%，仍有明显提升空间。

---

## HumanEval

**Evaluating Large Language Models Trained on Code** (2021)

- **论文**: https://arxiv.org/abs/2107.03374
- **作者**: Mark Chen 等 (OpenAI)
- **题量**: 164 道

### 测试什么

从函数签名和 docstring 生成 Python 实现代码。使用 pass@k 指标：生成 k 个候选，至少有一个通过所有测试用例的概率。

### 为什么重要

代码能力是 LLM 最实用的能力之一。HumanEval 是代码生成的标准基准。但题目相对简单（多为算法题），与真实编程场景有差距。

### 局限

- 题目较少（164 道）
- 以算法题为主，缺乏真实工程场景
- 测试用例不够充分（后有 HumanEval+ 补充）

---

## HumanEval+

**HumanEval+: Deeper Evaluation of Language Model Coding Capabilities** (2023)

- **论文**: https://arxiv.org/abs/2309.09117
- **题量**: 164 道（80x 测试用例）

### 测试什么

HumanEval 的增强版，将测试用例从平均 ~8 个增加到 ~774 个，大幅减少假阳性。

---

## MBPP

**Mostly Basic Python Programming** (2021)

- **论文**: https://arxiv.org/abs/2108.07732
- **作者**: Jacob Austin 等 (Google)
- **题量**: 974 道

### 测试什么

入门级 Python 编程题，比 HumanEval 更简单，适合测试基础编程能力。

---

## GSM8K

**Grade School Math 8K** (2021)

- **论文**: https://arxiv.org/abs/2110.14168
- **作者**: Karl Cobbe 等 (OpenAI)
- **题量**: 8,500 道

### 测试什么

小学数学应用题，需要 2-8 步推理。例如：

> "Janet's ducks lay 16 eggs per day. She eats three for breakfast every morning and bakes muffins for her friends every day with four. She sells the remainder at the farmers' market daily for $2 per egg. How much in dollars does she make every day at the farmers' market?"

### 为什么重要

GSM8K 是测试"基础数学推理"的标准基准。它的难度在于需要正确的多步推理链，而非单步计算。Chain-of-Thought (CoT) 在 GSM8K 上首次展现出巨大优势。

### 局限

- 难度较低，当前模型 ~97%
- 不涉及高等数学

---

## MATH

**Measuring Mathematical Problem Solving** (2021)

- **论文**: https://arxiv.org/abs/2103.03874
- **作者**: Dan Hendrycks 等 (UC Berkeley)
- **题量**: 12,500 道

### 测试什么

竞赛级数学题，涵盖 7 个领域、5 个难度级别：

| 级别 | 描述 |
|------|------|
| Level 1 | 简单竞赛题 |
| Level 2-3 | 中等难度 |
| Level 4-5 | AIME 级难题 |

7 个领域：初级代数、中级代数、计数与概率、几何、中级数论、预微积分、线性代数

### 为什么重要

MATH 是数学推理能力的标准基准。o3 推理模型的出现使 MATH 分数从 ~50% 跃升到 ~95%，是 AI 能力跃迁最明显的指标之一。

---

## GPQA

**Graduate-Level Google-Proof Q&A** (2023)

- **论文**: https://arxiv.org/abs/2311.12022
- **作者**: David Rein 等 (NYU)
- **题量**: 448 道

### 测试什么

研究生级科学问题（物理、化学、生物），设计为"Google-Proof"——即使有搜索引擎，非专家正确率仅 ~34%。

### 为什么重要

GPQA 测试的是真正的深度理解，不是表面知识。领域专家 ~81%，非专家+搜索 ~34%，这个差距说明题目确实需要专业知识。

---

## IFEval

**Instruction Following Evaluation** (2023)

- **论文**: https://arxiv.org/abs/2311.07911
- **作者**: Jeffrey Zhou 等 (Google)
- **题量**: 541 条

### 测试什么

带可验证约束的指令，例如：
- "回答必须包含关键词 X"
- "回答不超过 100 字"
- "必须以 JSON 格式输出"

测试模型是否能严格遵循格式、长度、关键词等约束。

---

## BigBench-Hard

**BIG-Bench Hard** (2022)

- **论文**: https://arxiv.org/abs/2304.05128
- **题量**: 6,511 道（23 个任务）

### 测试什么

从 BIG-Bench 的 204 个任务中筛选出 23 个最难任务（人类表现 >90% 但模型 <50% 的任务），包括逻辑推理、因果判断、多步算术等。

---

## TruthfulQA

**Measuring How Models Mimic Human Falsehoods** (2021)

- **论文**: https://arxiv.org/abs/2109.07958
- **作者**: Stephanie Lin, Jacob Hilton, Owain Evans (Oxford)
- **题量**: 817 道

### 测试什么

817 个问题，覆盖 38 个类别（健康、法律、金融、政治等），测试模型是否会重复人类常见谬误。

### 为什么重要

大模型容易自信地输出错误信息（hallucination）。TruthfulQA 专门测试这个问题。注意：TruthfulQA 的评分较复杂，不是简单的"正确率"。

---

## HellaSwag

**Can a Machine Really Finish Your Sentence?** (2019)

- **论文**: https://arxiv.org/abs/1905.07830
- **题量**: 10,000 道

### 测试什么

句子补全任务：给出一段描述，从 4 个选项中选择最合理的延续。错误选项通过 Adversarial Filtering 生成，对人类简单但对模型有挑战。

---

## WinoGrande

**WinoGrande: An Adversarial Winograd Schema Challenge at Scale** (2019)

- **论文**: https://arxiv.org/abs/1907.10641
- **题量**: 44,000 道

### 测试什么

Winograd Schema 问题的大规模版本。需要常识推理来消歧代词指代。

---

## DROP

**Discrete Reasoning Over Paragraphs** (2019)

- **论文**: https://arxiv.org/abs/1903.00161
- **题量**: 96,000+

### 测试什么

阅读理解问题，但需要离散推理（加减、计数、排序、集合运算等），不是简单的抽取式回答。

---

## TriviaQA

**TriviaQA: A Large Scale Distantly Supervised Challenge Dataset** (2017)

- **论文**: https://arxiv.org/abs/1705.03551
- **题量**: 95,000+

### 测试什么

开放域问答，来自 Wikipedia 和网络搜索结果。难度较低，主要测试知识覆盖面。
