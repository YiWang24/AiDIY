---
slug: ai-daily-digest-2026-08-26
title: "AI Daily Digest: OpenAI 自研芯片能效反超 Nvidia、Mechanical Turk 谢幕、GRPO 有了新对手 - 2026/08/26"
authors: [yiwang]
tags: [ai, daily-digest, agents, llm]
---

<!--truncate-->

今天的头条属于硬件与基础设施：SemiAnalysis 拿到 OpenAI 首款自研推理芯片 Jalapeño 的完整数据——700W 功耗跑出 13.4 PFLOPs，能效比达到 Nvidia 的 1.5-1.9 倍；Apple 同日发布首款 2nm M6 与四芯 M5 Ultra，端侧 512GB 统一内存让本地跑 200B+ 模型成为可能。软件侧，运营 21 年的 Mechanical Turk 宣布 9 月底关闭，"人工的人工智能"被真正的人工智能替代。学术前沿上，BPCO 证明精心设计的 Critic 可以用单次采样匹敌 GRPO，RENDER 则揭示记忆评测中"喂给模型什么形态"与"检索到什么"同样重要。

## SemiAnalysis 深度解析 Jalapeño：OpenAI 自研芯片能效反超 Nvidia

OpenAI 与 Broadcom 合作的首款定制推理芯片 Jalapeño，16 个月就在 TSMC N3P 完成流片。SemiAnalysis 的深度分析给出关键数字：B0 版本在 700W 功耗下实现 13.4 PFLOPs 的 MXFP4 算力（Nvidia Rubin 需要 900-1150W），搭配 15.4TB/s 的 HBM4；实际推理中 DeepSeek R1 单用户吞吐超 700 tok/s，GPT-OSS 约 1400 tok/s。OpenAI 自测显示，在 GPT-OSS、DeepSeek R1、Kimi K2.5 1T 三组负载上，Jalapeño 的每瓦特工作量是 Nvidia 芯片的 1.5-1.9 倍。

这意味着自研推理芯片的叙事从"降低成本"升级为"性能反超"。当超大规模厂商能用不到两年时间流片出能效领先的推理芯片，Nvidia 的护城河就需要重新评估——芯片设计能力正在向云厂商扩散。

> 来源：[SemiAnalysis](https://newsletter.semianalysis.com/p/openai-jalapeno-better-than-nvidia)（2026-08-26）

## Apple M6 进入 2nm 时代，M5 Ultra 拥抱四芯封装

Apple 发布首款 2 纳米芯片 M6：12 核 CPU、12 核 GPU、双 16 核 Neural Engine、最高 32GB 统一内存（170GB/s），峰值 GPU AI 算力比 M5 高约 30%。更重磅的是 M5 Ultra——Apple 首款四 die 封装的 M 系列芯片，最高 36 核 CPU、80 核 GPU、512GB 统一内存、1.2TB/s 带宽，AI GPU 算力达到 M3 Ultra 的 4.5 倍。Mac mini 899 美元起，Mac Studio 5499 美元起。

对端侧 Agent 而言这是实质性的硬件基座跃升：512GB 统一内存加 1.2TB/s 带宽，意味着在桌面设备上本地运行 200B+ 参数级模型不再需要妥协。端侧推理能力正在快速逼近数据中心推理机。

> 来源：[Apple Newsroom](https://www.apple.com/newsroom/2026/08/apple-introduces-m6-and-m5-ultra-for-a-big-leap-in-performance-and-ai-compute/)（2026-08-26）

## Mechanical Turk 谢幕：从"人工的人工智能"到真正的人工智能

AWS 通知用户将于 9 月 30 日关闭运营 21 年的 Mechanical Turk——Bezos 曾把它称为"人工的人工智能"（artificial artificial intelligence）。平台 7 月 30 日起停收新客户，此前早已被 Scale AI、Mercor、Prolific 等 AI 原生数据标注商边缘化。更讽刺的是，2023 年的一项研究发现大量 MTurk 工人已经在悄悄用 LLM 完成任务，"人类判断"的前提早已被动摇。

从人机回圈到模型在环，数据标注行业用自己的谢幕完成了范式转移的注脚。

> 来源：[CNBC](https://www.cnbc.com/2026/08/25/amazon-service-that-jeff-bezos-called-artificial-ai-is-shutting-down.html)（2026-08-25）

## Skild S1：单条视频教会机器人做 10 分钟长程任务

Skild AI 发布机器人基础模型 S1：无需微调，从单条人类视频演示就能学会最长 10 分钟的操作任务。在相同 10 万小时训练规模下，S1 对未见任务的成功率为 66%，而语言提示的 VLA 基线只有 9%。演示涵盖煎松饼、手冲咖啡、盆栽移栽和成套件组装。Sequoia 的 Alfred Lin 称之为"游戏规则改变者"。

在 VLA（视觉-语言-动作）路线之外，视频模仿正在成为更具样本效率的具身智能范式。

> 来源：[Skild AI](https://www.skild.ai/blogs/s1)（2026-08-26）

## 安全视角：NemoClaw 漏洞与 Agent 基础设施的攻击面

Oasis Security 披露 CVE-2026-65105：NVIDIA 的 NemoClaw 工具将 Ollama 绑定到 0.0.0.0:11434 且无鉴权，DNS 重绑定攻击可让单个恶意网页通过 /api/create 重写模型的 chat template，向每条系统消息追加攻击者文本并跨会话持久化，API 调用方完全无感。v0.0.35 已修复 macOS/Linux，Windows/WSL 版仍未修复。

同日还有一条基础设施新闻：Accel 领投 Keenable 2600 万美元种子轮，为 AI Agent 构建覆盖 1000 亿+ 文档的独立检索库——在 X 关停 Nitter、平台收紧反爬限制的背景下，面向 Agent 的搜索基础设施正在成为新的卡位点。

> 来源：[The Hacker News](https://thehackernews.com/2026/08/a-malicious-webpage-could-poison-your.html)（2026-08-26）
>
> 来源：[TechCrunch](https://techcrunch.com/2026/08/25/accel-backed-keenable-is-indexing-the-web-for-ai-agents/)（2026-08-25）

## ChatGPT Work 浏览器学会登录网站并支持 Webhook 触发任务

OpenAI 8 月 25 日更新 ChatGPT：Work 浏览器现在可以进入需要登录的网站（仅限 Plus/Pro，关键操作前需用户确认），Plus/Pro 用户可以从 Gmail、Slack、GitHub 的 webhook 触发定时任务，任务共享和最多 3 个并行定时任务向免费用户开放，并集成了密码管理器与安全凭据处理。

Agent 浏览器从"只读网页"进化到"带凭据操作"，凭据安全随之成为 Agent 浏览器的核心工程问题。

> 来源：[OpenAI Help](https://help.openai.com/en/articles/6825453-chatgpt-release-notes)（2026-08-25）

## 学术前沿：RL 后训练、记忆评测与代码过程监督

### BPCO：精心设计的 Critic 可靠替代 GRPO（arXiv:2608.23566）

GRPO 靠每提示采样多条响应绕开 critic 训练，但标准 critic 配方常不稳定。BPCO 组合 DPPO、限制到奖励区间的价值预测、Monte Carlo 价值目标、未归一化策略优势与长度自适应 GAE；由于 critic 仅在训练期使用，还可以用策略看不到的参考答案或评分 rubric 作条件。在 1.5B 到 30B-A3B MoE 模型的数学推理任务上，BPCO 稳定超越强 critic 基线，单响应采样即匹敌或超越组相对基线——RL 后训练中采样预算与性能的两难有了新解。

### RENDER：记忆评测必须控制"读者侧证据形态"（arXiv:2608.23568）

同一段对话历史可以被渲染为记忆条目、摘要、类型化记录或原始摘录，但记忆/RAG 评测常把回答模型的输入当作实现细节。RENDER 固定对话、只改变读者侧产物，在 500 道 LongMemEval 题上发现：匹配预算的解析包比近期截断原始对话高 42.4-72.6 分；三个在形式化账本包上得 0 分的模型，从自然语言条目读出同样事实的正确率达 45.4-53.4%。"喂给模型什么形态的证据"与"检索到什么"同样重要。

### STEP-KTODER：单元测试做代码生成的过程监督（arXiv:2608.23632）

代码生成缺少过程监督，根源是"步"没有标准定义。STEP-KTODER 把步定义为多函数程序中的模块级函数，用自动生成的单元测试打二元正确性标签，将函数级过程监督与整程序结果反馈结合为 stepwise KTO，在 HumanEval(+)/MBPP(+)/BigCodeBench/LiveCodeBench 上超越 outcome-only KTO 与 DPO（已被 EMNLP 2026 Findings 接收）。关键发现：执行标签必不可少——LLM-as-judge 会系统性高估函数失败率、污染正例标签。

### ESQ-Bench：企业级 Oracle 场景撕开 NL2SQL 精度幻觉（arXiv:2608.23569）

Spider/BIRD 上执行准确率超 89% 的 NL2SQL 模型，遇上真实企业库就露馅。ESQ-Bench 用 6 个完整 schema（465 表、164682 行）、三档复杂度、550 组金标准问答对评估：GPT-4o 的执行匹配率随层级单调下滑（79.8→60.3→57.2%），且通过执行检查的查询中 73-99% 存在静默语义偏差——跑通了但结果是错的。Claude Sonnet 4.6 各层级全面领先，本地 Llama 3.2 全库仅 13.3%。

> 来源：[arXiv:2608.23566](https://arxiv.org/abs/2608.23566)；[arXiv:2608.23568](https://arxiv.org/abs/2608.23568)；[arXiv:2608.23632](https://arxiv.org/abs/2608.23632)；[arXiv:2608.23569](https://arxiv.org/abs/2608.23569)（2026-08）

## 知识库更新

本次更新涉及以下文档：

- **AI Agents / Frontier** (`docs/ai/agents/10-frontier.mdx`): 新增 11 条前沿趋势（#598-608）——Jalapeño 能效反超、Apple M6/M5 Ultra、Mechanical Turk 关闭、Skild S1、NemoClaw CVE、ChatGPT Work 浏览器升级、Keenable 融资，以及 BPCO、RENDER、STEP-KTODER、ESQ-Bench 四篇论文；并修复了 #597 条目末尾粘连的列表分隔符

---

*本文由 AiDIY 每日知识更新工作流自动生成，数据来源包括 aiweekly、arXiv、SemiAnalysis、Apple Newsroom 等。*
