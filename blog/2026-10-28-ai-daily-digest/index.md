---
slug: ai-daily-digest-2026-10-28
title: "AI Daily Digest: Gemini 4 Carbon 分级放量、1.7B 端侧模型赢了 9B、RAG 学会说\"我不知道\" - 2026/10/28"
authors: [yiwang]
tags: [ai, daily-digest, google, gemini-4-carbon, frontier-model, staged-rollout, fairwind, cybersecurity, liquid-ai, lfm3, on-device, nvidia, nemotron, speech, asr, rtx-spark, cursor, agent-sdk, rag, calibration, conformal, arxiv, hn]
---

<!--truncate-->

今天的主题是"门槛"的三种重新定义：Google 用分级放量重新定义了前沿模型的发布门槛，Liquid AI 用 1.7B 参数重新定义了端侧 agent 的能力门槛，RAG 研究用"拒答"重新定义了可靠性的门槛。三条线看起来互不相干，其实都在回答同一个问题——**当模型能力足够强之后，限制它的应该是什么**。

## Gemini 4 Carbon：跑分第一，但你暂时用不上

今天最大的新闻毫无疑问是 Google 发布 Gemini 4 Carbon（HN 436 分）——距 Argon 全面可用仅 15 天，节奏快得让整个行业侧目。Artificial Analysis Intelligence Index v5 上 Carbon 得 59 分，在 52 个模型中排第一，领先 Claude Opus 5.5（max）的 58 和 GPT-6 Astra（max）的 57，比自家 Argon 的 50 高出 9 分。

能力主打两个方向。**网络安全**：SEC-bench Pro 88.2%（找漏洞）、ExploitGym 54.8%（判断可利用性）、Collinear CWE-bench 71.0%（修根因）。**长时程任务**：Google 内部团队报告 Carbon 可以连续工作数天，走进死胡同后自主回溯换路线——这正好接上昨天我们讨论的"常驻 proactive agent"趋势：模型的能力边界正在从"一次对话"扩展到"一段工期"。

但比跑分更值得注意的是发布方式：Carbon **先开放给部分网络防御者**，再通过 Fairwind Program 扩展到更多受信伙伴，开发者与企业"尽快、无日期"，并且参与了美国政府的自愿性发布前测试。这一套流程和 Argon 一模一样。换句话说，**"分级放量"已经从权宜之计固化为 Google 的标准操作**：跑分可以公布第一，权重和 API 却按信任等级逐级解锁。介绍期价格 $2/$10 每百万 token（之后 $4/$20），cached input 打 95% 折扣——价格战的白热化昨天聊过，今天不重复。

## 1.7B 打 9B：端侧 agent 的"越小越强"

Liquid AI 昨天发布的 LFM3 家族给"小模型"这个词注入了新含义：六个 ~2B 参数的开源权重端侧模型——文本、视觉、音频、omni 各一个，加两个 decision 模型——全部从同一个 LFM3-1.7B-Base 骨干分出。最能打的数据点：LFM3-1.7B 文本模型在 WebArena-Verified 上得 38.42，**超过 Qwen3.5-9B 的 28.94 和 Qwen3.5-4B 的 21.92**。4-bit 量化下整个模型约 1GB，256K 上下文窗口，单 GPU 就能微调，day-zero 支持 NVIDIA 刚扩展的 RTX Spark 笔记本阵营。

当然要保留一句：这些数字全部是 Liquid AI 自报的，且大模型在 agentic coding 和知识任务上仍然占优。但趋势是清晰的——**端侧模型的竞争已经从"聊天质量"转移到"agent 执行力"**。收件箱分诊、日程管理、工单路由这类本地工作流，正在成为 2B 级模型的精准战场。

同日 NVIDIA 也在语音一侧补了一刀：Nemotron 3.5 Transcribe，30B 总参、约 4B 激活的开源权重语音模型，40 语言转写、HF Open ASR 榜 5.33% WER 居开源权重第一，单块 RTX PRO 6000 三分钟处理 100 小时音频，还配套放出了 46 万小时、48 语言的 Granary v2 数据集。加上 Cursor 发布 Agent SDK（编码 agent 能力平台化为可编程 SDK）、Anthropic 公开 Claude 加速药物研发的早期进展（HN 307 分）——agent 生态今天在"端侧、工具链、科学场景"三个方向同时推进。

## RAG 学会说"我不知道"

arXiv 今天的收获集中在 RAG 可靠性，而且方向惊人地一致：**从"答得更好"转向"知道自己不该答"**。

- **CalibraRL**（[2610.35142](https://arxiv.org/abs/2610.35142)）：用置信度校准的强化学习缓解 RAG 幻觉，训练信号显式区分"证据充分却答错"和"证据不足被迫猜"——RL 从优化答案走向优化"答案与证据的关系"
- **SpectRAG**（[2610.36991](https://arxiv.org/abs/2610.36991)）：为多跳 RAG 建带权重的 chunk 图，在给定 token 预算内做上下文选择——"检索多少"从固定 top-k 变成预算约束优化问题
- **Adaptive Retrieval, Selective Answers**（[2610.34872](https://arxiv.org/abs/2610.34872)）：把 conformal factuality 引入 agentic RAG，检索不足时追加检索或直接拒答

和上周的 RAG-Stress（误导性证据会把模型本来对的答案带偏）放在一起看，RAG 输出护栏的版图才算完整：一边管"被坏证据带偏"，一边管"没证据硬答"。生产系统的下一个 KPI 可能不是准确率，而是**拒答率与答案翻转率的联合分布**。

agent 一侧也有两篇值得记下：**Concordat**（[2610.37461](https://arxiv.org/abs/2610.37461)）把分布式系统的会话类型论搬进 LLM agent 通信，协议从提示词约定升级为可静态检查的契约；**TeamGym**（[2610.37571](https://arxiv.org/abs/2610.37571)）则首次为"分布式信息下的团队决策"提供评测环境——每个 agent 只持有一部分信息，考的是协作而非单点。多 agent 系统正在补自己缺的那门"分布式系统 101"课。

## 小结

三件事指向同一个转折：行业的主要矛盾正在从"模型不够强"转移到"如何在受控的条件下使用强大的模型"。Google 选择按信任分级放量，端侧阵营选择把能力塞进 1GB，RAG 研究者选择教模型承认无知。**能力的过剩，正在把工程约束推向舞台中央**——这大概是今天所有新闻放在一起读时，最值得记住的一句话。
