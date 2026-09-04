<div align="center">

# LLM Benchmarks Tracker

**有来源、经 schema 校验的 LLM 与 Agent 评测基准目录。**

[**English**](README.md) · [**浏览网站**](https://alloevil.github.io/llm-benchmarks-tracker/zh/) · [**JSON API**](https://alloevil.github.io/llm-benchmarks-tracker/api/v1/index.json) · [**提交分数**](https://github.com/alloevil/llm-benchmarks-tracker/issues/new?template=result.yml) · [**更新日志**](CHANGELOG.md)

[![CI](https://github.com/alloevil/llm-benchmarks-tracker/actions/workflows/ci.yml/badge.svg)](https://github.com/alloevil/llm-benchmarks-tracker/actions/workflows/ci.yml)
[![Pages](https://github.com/alloevil/llm-benchmarks-tracker/actions/workflows/pages.yml/badge.svg)](https://alloevil.github.io/llm-benchmarks-tracker/zh/)
[![Release](https://img.shields.io/github/v/release/alloevil/llm-benchmarks-tracker)](https://github.com/alloevil/llm-benchmarks-tracker/releases)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

</div>

对每个基准记录：它测什么、是否仍能区分前沿系统（`status`）、测试集暴露程度（`contamination_risk`）、有出处的人类基线（若存在），以及最高分由谁、在什么条件下报告。

<!-- gen:stats -->
**31** 个模型基准 · **23** 个 Agent 基准 · **18** 个评测方 · **250** 条有来源的结果 · 更新于 2026-09-04
<!-- /gen:stats -->

**为什么再做一个列表？** 多数基准页面照搬厂商幻灯片上的数字，没有出处。这里每一行结果都带有来源 URL、来源类型（官方榜单 / 论文 / 独立复现 / 厂商自报 / 聚合站）、访问日期和评测条件（工具、推理强度、scaffold、pass@k）。没有来源的数字不收录。

## 模型基准

对模型本身做静态的「提示—回答」打分。「最高分」是结果账本中的最佳一行，不是模型排名；各行条件不同。按发布时间倒序。

<!-- gen:model -->
| Benchmark | 发布 | 领域 | 状态 | 最高分 | 系统 | 来源 |
|---|---|---|---|---|---|---|
| [BenchCAD](https://benchcad.com/leaderboard) | 2026-05 | multimodal, code, reasoning | active | 0.843 | Claude Fable 5.1 (max, Python tools) | [厂商自报](https://benchcad.com/leaderboard) |
| [AA-Omniscience](https://artificialanalysis.ai/evaluations/omniscience) | 2025-11 | knowledge, factuality | active | 44 | GPT-6 Astra (high) | [独立复现](https://artificialanalysis.ai/evaluations/omniscience) |
| [GDPval](https://openai.com/index/gdpval/) | 2025-09 | general-assistant, knowledge, instruction-following | active | 74.1% | GPT-5.2 Pro | [厂商自报](https://openai.com/index/introducing-gpt-5-2/) |
| [HealthBench](https://openai.com/index/healthbench/) | 2025-05 | knowledge, safety, instruction-following | active | 59.9% | o3 | [论文](https://arxiv.org/abs/2505.08775) |
| [ARC-AGI-2](https://arcprize.org/leaderboard) | 2025-03 | reasoning | saturating | 95% | GPT-6 Astra (Max) | [官方榜单](https://arcprize.org/leaderboard) |
| [ScreenSpot-Pro](https://gui-agent.github.io/grounding-leaderboard/) | 2025-01 | computer-use, multimodal | saturating | 92.7% | GPT-6 Astra | [厂商自报](https://openai.com/index/gpt-6-astra/) |
| [Humanity's Last Exam](https://lastexam.ai/) | 2025-01 | knowledge, reasoning, science, math, multimodal | active | 65% | Claude Fable 5.1 (with tools) | [厂商自报](https://www.anthropic.com/claude-fable-and-mythos-5-1) |
| [Aider Polyglot](https://aider.chat/docs/leaderboards/) | 2024-12 | code, instruction-following | saturating | 88% | gpt-5 (high) | [官方榜单](https://aider.chat/docs/leaderboards/) |
| [SimpleQA](https://openai.com/index/introducing-simpleqa/) | 2024-11 | factuality, knowledge | active | 62.5% | gpt-4.5-preview-2025-02-27 | [厂商自报](https://github.com/openai/simple-evals) |
| [FrontierMath](https://epoch.ai/benchmarks/frontiermath-tiers-1-3-v2) | 2024-11 | math, reasoning, research | saturating | 93.7% | gpt-6-astra (max) | [独立复现](https://epoch.ai/benchmarks/frontiermath-tiers-1-3-v2) |
| [MMMU-Pro](https://mmmu-benchmark.github.io/#leaderboard) | 2024-09 | multimodal, knowledge, reasoning | active | 86.9% | Chance Vision 1.5 | [厂商自报](https://mmmu-benchmark.github.io/) |
| [MMLU-Pro](https://huggingface.co/spaces/TIGER-Lab/MMLU-Pro) | 2024-06 | knowledge, reasoning | saturating | 91% | Gemini 3.1 Pro (High) | [独立复现](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro) |
| [RULER](https://github.com/NVIDIA/RULER) | 2024-04 | long-context | saturating | 95.1% | Jamba-1.5-large | [官方榜单](https://github.com/NVIDIA/RULER) |
| [LiveCodeBench](https://livecodebench.github.io/leaderboard.html) | 2024-03 | code, reasoning | active | 93.5% | DeepSeek-V4-Pro (Think Max) | [厂商自报](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro) |
| [BFCL](https://gorilla.cs.berkeley.edu/leaderboard.html) | 2024-02 | tool-use | active | 77.47% | Claude-Opus-4-5-20251101 (FC) | [官方榜单](https://gorilla.cs.berkeley.edu/leaderboard.html) |
| [MMMU](https://mmmu-benchmark.github.io/#leaderboard) | 2023-11 | multimodal, knowledge, reasoning | saturating | 85.4% | GPT-5.1 | [厂商自报](https://mmmu-benchmark.github.io/) |
| [IFEval](https://github.com/google-research/google-research/tree/master/instruction_following_eval) | 2023-11 | instruction-following | saturating | 95% | Qwen3.5-27B | [厂商自报](https://huggingface.co/Qwen/Qwen3.5-27B) |
| [GPQA Diamond](https://github.com/idavidrein/gpqa) | 2023-11 | science, reasoning, knowledge | saturating | 96% | GPT-6 Astra | [聚合站](https://benchlm.ai/benchmarks/gpqa-diamond) |
| [LMArena Text](https://lmarena.ai/leaderboard/text) | 2023-05 | human-preference, general-assistant | active | 1466 | gemini-2.5-pro | [官方榜单](https://huggingface.co/spaces/lmarena-ai/arena-leaderboard) |
| *已饱和或退役 —— 不再用于比较前沿系统。所示分数为最后一次报告值，不是榜首。* | | | | | | |
| [AIME 2025](https://matharena.ai/) | 2025-02 | math, reasoning | saturated | 最后报告 100% | GPT-5.2 (high) | [独立复现](https://matharena.ai/) |
| [BIG-Bench Hard](https://github.com/suzgunmirac/BIG-Bench-Hard) | 2022-10 | reasoning | saturated | 最后报告 87.5% | DeepSeek-V4-Pro-Base | [厂商自报](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro) |
| [GSM8K](https://github.com/openai/grade-school-math) | 2021-10 | math, reasoning | saturated | 最后报告 92.6% | DeepSeek-V4-Pro-Base | [厂商自报](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro) |
| [TruthfulQA](https://github.com/sylinrl/TruthfulQA) | 2021-09 | factuality, safety | saturated | 最后报告 58% | GPT-3-175B (helpful prompt) | [论文](https://arxiv.org/abs/2109.07958) |
| [MBPP](https://github.com/google-research/google-research/tree/master/mbpp) | 2021-08 | code | saturated | 最后报告 88.6% | Llama 3.1 405B Instruct | [厂商自报](https://huggingface.co/meta-llama/Llama-3.1-70B-Instruct) |
| [HumanEval](https://github.com/openai/human-eval) | 2021-07 | code | saturated | 最后报告 76.8% | DeepSeek-V4-Pro-Base | [厂商自报](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro) |
| [MATH](https://epoch.ai/benchmarks/math-level-5) | 2021-03 | math, reasoning | saturated | 最后报告 98.1% | o3-high | [厂商自报](https://github.com/openai/simple-evals) |
| [MMLU](https://github.com/hendrycks/test) | 2020-09 | knowledge, reasoning | saturated | 最后报告 90.1% | DeepSeek-V4-Pro-Base | [厂商自报](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro) |
| [ARC-AGI-1](https://arcprize.org/leaderboard) | 2019-11 | reasoning | saturated | 最后报告 98.5% | GPT-6 Astra (XHigh) | [官方榜单](https://arcprize.org/leaderboard) |
| [WinoGrande](https://winogrande.allenai.org/) | 2019-07 | commonsense, reasoning | saturated | 最后报告 81.5% | DeepSeek-V4-Pro-Base | [厂商自报](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro) |
| [HellaSwag](https://rowanzellers.com/hellaswag/) | 2019-05 | commonsense | saturated | 最后报告 88% | DeepSeek-V4-Pro-Base | [厂商自报](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro) |
| [DROP](https://github.com/allenai/allennlp-reading-comprehension) | 2019-03 | reasoning, knowledge | saturated | 最后报告 88.7% | DeepSeek-V4-Pro-Base | [厂商自报](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro) |
<!-- /gen:model -->

## Agent 基准

交互式环境：系统执行动作、调用工具，按任务完成度打分。scaffold 与预算能让分数相差几十个点；比较前先看 `conditions`。按发布时间倒序。

<!-- gen:agent -->
| Benchmark | 发布 | 领域 | 状态 | 最高分 | 系统 | 来源 |
|---|---|---|---|---|---|---|
| [OSWorld 2.0](https://osworld-v2.xlang.ai/) | 2026-06 | computer-use, multimodal, tool-use | active | 41.7% | Claude Fable 5.1 | [厂商自报](https://www.anthropic.com/claude-fable-and-mythos-5-1) |
| [AutomationBench](https://zapier.com/benchmarks) | 2026-04 | tool-use, general-assistant, instruction-following | active | 50.3% | Claude Opus 5 (max) | [官方榜单](https://github.com/zapier/AutomationBench) |
| [ARC-AGI-3](https://arcprize.org/leaderboard) | 2026-03 | reasoning, tool-use | saturating | 99.9% | GPT-6 Astra (high) | [官方榜单](https://arcprize.org/blog/astra) |
| [Terminal-Bench](https://www.tbench.ai/leaderboard) | 2026-01 | software-engineering, code, tool-use, ml-engineering | active | 64.6% | GPT-6 Astra | [厂商自报](https://openai.com/index/gpt-6-astra/) |
| [DeepSearchQA](https://www.kaggle.com/benchmarks/google/dsqa/leaderboard) | 2025-12 | web, research, factuality, tool-use | active | 95% | Claude Opus 5 | [聚合站](https://benchlm.ai/benchmarks/deepsearchqa) |
| [Tool Decathlon (Toolathlon)](https://toolathlon.xyz/docs/leaderboard) | 2025-10 | tool-use, general-assistant, software-engineering | active | 78.4% | GLM 5.3 Flash (max) | [官方榜单](https://toolathlon.xyz/docs/leaderboard) |
| [SWE-Bench Pro](https://labs.scale.com/leaderboard/swe_bench_pro_public) | 2025-09 | software-engineering, code, tool-use | active | 61.5% | Muse Spark 1.1 | [官方榜单](https://labs.scale.com/leaderboard/swe_bench_pro_public) |
| [tau2-bench](https://taubench.com/leaderboard?benchmark=core) | 2025-06 | tool-use, instruction-following, general-assistant | active | 87.9% | Qwen3.5-397B-A17B | [官方榜单](https://taubench.com) |
| [FieldWorkArena](https://en-documents.research.global.fujitsu.com/fieldworkarena/) | 2025-05 | multimodal, general-assistant, safety, reasoning | active | 52% | GPT-5.2 (2025-12-11) | [论文](https://arxiv.org/abs/2505.19662) |
| [PaperBench](https://github.com/openai/frontier-evals/tree/main/project/paperbench) | 2025-04 | research, ml-engineering, code, tool-use | active | 43.4% | IterativeAgent o1-high | [官方榜单](https://github.com/openai/frontier-evals/tree/main/project/paperbench) |
| [BrowseComp](https://openai.com/index/browsecomp/) | 2025-04 | web, tool-use, factuality, reasoning | saturating | 92.2% | GPT-5.6 Sol | [聚合站](https://benchlm.ai/benchmarks/browsecomp) |
| [SWE-bench Multilingual](https://www.swebench.com/#multilingual) | 2025-03 | software-engineering, code, tool-use | active | 72.7% | Gemini 3 Flash | [官方榜单](https://www.swebench.com/#multilingual) |
| [MLE-bench](https://github.com/openai/mle-bench) | 2024-10 | ml-engineering, code, tool-use | active | 64.44% | Famou-Agent 2.0 + Gemini-3-Pro-Preview | [官方榜单](https://github.com/openai/mle-bench) |
| [SWE-bench Verified](https://www.swebench.com/#verified) | 2024-08 | software-engineering, code, tool-use | saturating | 96% | Claude Opus 5 | [聚合站](https://benchlm.ai/benchmarks/swe-bench-verified) |
| [OSWorld](https://os-world.github.io) | 2024-04 | computer-use, multimodal, tool-use | active | 90.19% | Intelligence-Indeed Agent | [官方榜单](https://os-world.github.io) |
| [VisualWebArena](https://docs.google.com/spreadsheets/d/1M801lEpBbKSNwP-vDBkC_pF7LdyGU1f_ufZb_NWNBZQ/edit?gid=2044883967#gid=2044883967) | 2024-01 | web, multimodal, computer-use | active | 54% | Gemini 2.5 Flash (SGV) | [官方榜单](https://docs.google.com/spreadsheets/d/1M801lEpBbKSNwP-vDBkC_pF7LdyGU1f_ufZb_NWNBZQ/edit?gid=2044883967#gid=2044883967) |
| [GAIA](https://huggingface.co/spaces/gaia-benchmark/leaderboard) | 2023-11 | general-assistant, tool-use, web, reasoning, multimodal | saturating | 93.36% | CustomGPT.ai Research Lab v44 | [官方榜单](https://huggingface.co/spaces/gaia-benchmark/leaderboard) |
| [WebArena](https://docs.google.com/spreadsheets/d/1M801lEpBbKSNwP-vDBkC_pF7LdyGU1f_ufZb_NWNBZQ/edit?usp=sharing) | 2023-07 | web, tool-use, computer-use | active | 74.3% | WebTactix + Deepseek v3.2 | [官方榜单](https://docs.google.com/spreadsheets/d/1M801lEpBbKSNwP-vDBkC_pF7LdyGU1f_ufZb_NWNBZQ/edit?usp=sharing) |
| *已饱和或退役 —— 不再用于比较前沿系统。所示分数为最后一次报告值，不是榜首。* | | | | | | |
| [Cybench](https://cybench.github.io/#leaderboard_title) | 2024-08 | safety, code, tool-use | saturated | 最后报告 96% | Claude Opus 4.7 | [厂商自报](https://cybench.github.io) |
| [tau-bench](https://github.com/sierra-research/tau-bench) | 2024-06 | tool-use, instruction-following, general-assistant | retired | 最后报告 69.2% | TC (claude-3-5-sonnet-20241022), retail | [官方榜单](https://github.com/sierra-research/tau-bench) |
| [AndroidWorld](https://docs.google.com/spreadsheets/d/1cchzP9dlTZ3WXQTfYNhh3avxoLipqHN75v1Tb86uhHo/edit?gid=0#gid=0) | 2024-05 | computer-use, multimodal, tool-use | saturated | 最后报告 85.3% | Qwen3.8 Max | [聚合站](https://benchlm.ai/benchmarks/androidworld) |
| [SWE-bench](https://www.swebench.com/#test) | 2023-10 | software-engineering, code, tool-use | saturated | 最后报告 52.62% | Sonar Foundation Agent + Claude 4.5 Opus | [官方榜单](https://www.swebench.com/#test) |
| [AgentBench](https://docs.google.com/spreadsheets/d/e/2PACX-1vRR3Wl7wsCgHpwUw1_eUXW_fptAPLL3FkhnW_rua0O1Ji_GIVrpTjY5LaKAhwO-WeARjnY_KNw0SYNJ/pubhtml) | 2023-08 | tool-use, reasoning, web, code | retired | 最后报告 3.11 | claude-3 opus | [论文](https://arxiv.org/abs/2308.03688) |
<!-- /gen:agent -->

## 评测方

你自己运行的框架、维护者运营的榜单、独立复现模型的机构，以及转载已报告数字的聚合站。独立性很重要：同一模型的厂商自报分数通常高于独立复现。

<!-- gen:evaluators -->
| 评测方 | 类型 | 维护者 | 方法 | 状态 |
|---|---|---|---|---|
| [DeepEval](https://deepeval.com) | framework | Confident AI | self-run | active |
| [EvalScope](https://evalscope.readthedocs.io/en/latest/) | framework | ModelScope (Alibaba) | self-run | active |
| [HELM](https://crfm.stanford.edu/helm/) | framework | Stanford CRFM | self-run | archived |
| [Inspect AI](https://inspect.aisi.org.uk/) | framework | UK AI Security Institute | self-run | active |
| [Lighteval](https://huggingface.co/docs/lighteval/en/index) | framework | Hugging Face | self-run | active |
| [LM Evaluation Harness](https://github.com/EleutherAI/lm-evaluation-harness) | framework | EleutherAI | self-run | active |
| [OpenAI Evals](https://platform.openai.com/docs/guides/evals) | framework | OpenAI | self-run | archived |
| [OpenCompass](https://opencompass.org.cn/) | framework | Shanghai AI Laboratory (OpenCompass team) | self-run | active |
| [Holistic Agent Leaderboard (HAL)](https://hal.cs.princeton.edu) | leaderboard | Princeton University (SAgE team) | self-run | active |
| [LiveBench](https://livebench.ai) | leaderboard | LiveBench team (Abacus.AI, NYU and collaborators) | self-run | active |
| [LMArena](https://lmarena.ai) | leaderboard | Arena (LMArena, spun out of LMSYS / UC Berkeley) | crowdsourced | active |
| [Open LLM Leaderboard](https://huggingface.co/spaces/open-llm-leaderboard/open_llm_leaderboard) | leaderboard | Hugging Face | submission | archived |
| [SWE-rebench](https://swe-rebench.com) | leaderboard | Nebius | self-run | active |
| [Artificial Analysis](https://artificialanalysis.ai) | independent-evaluator | Artificial Analysis | self-run | active |
| [Epoch AI Benchmarking Hub](https://epoch.ai/benchmarks) | independent-evaluator | Epoch AI | self-run | active |
| [Scale SEAL Leaderboards](https://scale.com/leaderboard) | independent-evaluator | Scale AI (SEAL Research Lab) | self-run | active |
| [Vals AI](https://www.vals.ai) | independent-evaluator | Vals AI | self-run | active |
| [BenchLM](https://benchlm.ai) | aggregator | BenchLM.ai (independent, maintained by @glevd) | collected | active |
<!-- /gen:evaluators -->

## 时间线

<!-- gen:timeline -->
- **2019** — ARC-AGI-1, DROP, HellaSwag, WinoGrande
- **2020** — MMLU
- **2021** — GSM8K, HumanEval, LM Evaluation Harness (framework), MATH, MBPP, TruthfulQA
- **2022** — BIG-Bench Hard, HELM (framework)
- **2023** — AgentBench, DeepEval (framework), GAIA, GPQA Diamond, IFEval, LMArena (leaderboard), LMArena Text, MMMU, Open LLM Leaderboard (leaderboard), OpenAI Evals (framework), OpenCompass (framework), SWE-bench, WebArena
- **2024** — Aider Polyglot, AndroidWorld, Artificial Analysis (independent-evaluator), BFCL, Cybench, Epoch AI Benchmarking Hub (independent-evaluator), EvalScope (framework), FrontierMath, Inspect AI (framework), Lighteval (framework), LiveBench (leaderboard), LiveCodeBench, MLE-bench, MMLU-Pro, MMMU-Pro, OSWorld, RULER, Scale SEAL Leaderboards (independent-evaluator), SimpleQA, SWE-bench Verified, tau-bench, Vals AI (independent-evaluator), VisualWebArena
- **2025** — AA-Omniscience, AIME 2025, ARC-AGI-2, BenchLM (aggregator), BrowseComp, DeepSearchQA, FieldWorkArena, GDPval, HealthBench, Holistic Agent Leaderboard (HAL) (leaderboard), Humanity's Last Exam, PaperBench, ScreenSpot-Pro, SWE-bench Multilingual, SWE-Bench Pro, SWE-rebench (leaderboard), tau2-bench, Tool Decathlon (Toolathlon)
- **2026** — ARC-AGI-3, AutomationBench, BenchCAD, OSWorld 2.0, Terminal-Bench
<!-- /gen:timeline -->

## 数据模型

```
data/
  benchmarks/<id>.json     每个基准一个文件            schema/benchmark.schema.json
  results/<id>.json        只追加的分数账本            schema/results.schema.json
  evaluators/<id>.json     框架 / 榜单 / 独立评测方     schema/evaluator.schema.json
```

关键字段：

| 字段 | 含义 |
|---|---|
| `layer` | `model`（静态打分）或 `agent`（交互环境） |
| `status` | `active` 仍能区分前沿系统 · `saturating` 距上限或人类基线约 5 分以内 · `saturated` 已无区分度 · `retired` 维护者已停止 |
| `contamination_risk` | `low` 滚动更新 / 私有测试集 · `medium` 公开但有缓解措施 · `high` 公开、静态、被广泛抓取 |
| `description_zh` | `description` 的中文翻译；名称与指标保留原文 |
| `human_baseline` | 仅当存在有出处的实测数字时填写 |
| `results[].source.kind` | `official-leaderboard` · `paper` · `independent-evaluation` · `developer-report` · `aggregator` |
| `results[].conditions` | `split`、`tools`、`reasoning_effort`、`scaffold`、`pass_k`、`shots`、`cost_usd_per_task`、`notes` —— 不知道的键不填，绝不猜 |

结果账本只追加：新分数是新的一行，绝不修改旧行。`scripts/dataset.py::Dataset.sota()` 按 `metric.higher_is_better` 选出最佳行。

## 参与贡献

见 [CONTRIBUTING.md](CONTRIBUTING.md)（英文）。简版：编辑或新增 `data/` 下的 JSON，运行 `python scripts/validate.py && python scripts/build.py`，提交 PR。CI 会拒绝 schema 违规、悬空引用、无来源的行，以及过期的 README 表格。

## 许可

代码与数据以 [MIT 许可](LICENSE) 发布。基准名称、论文与分数归各自作者所有；每个条目均链接至原处。
