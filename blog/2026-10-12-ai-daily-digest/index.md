---
slug: ai-daily-digest-2026-10-12
title: "AI Daily Digest: Muse Wonder 发布、AlphaProof Nexus 登 Science、被量化的「差距」 - 2026/10/12"
authors: [yiwang]
tags: [ai, daily-digest, meta, muse-wonder, alphaproof, lean, formal-verification, karpathy, coding-agents, rsi, world-model, agent-security, evaluation-variance, quantization, arxiv]
---

<!--truncate-->

今天的关键词是**"差距"**。Karpathy 说人们对 LLM 能力的共同认知差距正在拉大（HN 641 分，本周最高）；Ars Technica 追问 AI coding agent 生成了更多代码却没产出更多软件；而 DeepMind 的 AlphaProof Nexus 用 Lean 形式化验证把"AI 数学证明可信不可信"的差距彻底抹平——同一天 Meta 发布了号称最强的 agent 模型 Muse Wonder。差距既是问题，也是所有竞争的轴线。

## AlphaProof Nexus：AI 数学从"像证明"到"是证明"

DeepMind 的 [AlphaProof Nexus](https://aitoolherald.com/articles/google-deepmind-s-alphaproof-nexus-solves-open-math-problems/) 成果登上 *Science*：自主解出 353 个尝试中的 **9 个开放 Erdős 问题**（含两个悬置 56 年的难题）、44 个 OEIS 猜想，并推进了凸优化中的一个已知界。架构上是"LLM 推理 + Lean 编译器验证"的闭环：Gemini 3.1 Pro 生成证明草案，Lean 逐步形式化检查，编译错误回传引导下一轮修正；最难情形可调用 AlphaProof 的 RL 专用模块。

几个值得记住的数字与细节：

- **每题推理成本只有几百美元**——顶级数学研究能力的门槛从"国家级算力"降到"一个研究组的预算"
- 最简单的 agent 配置（LLM-编译器循环，无专用模块）就解出了全部 9 个 Erdős 问题——**模型越强，需要的 agent 架构越简单**，这个趋势比任何单个结果都重要
- 成功率仍然只有 ~2.5%，且集中在 Lean 库成熟的组合数论方向；Terence Tao 提醒整体成功率约 1-2%，别把"解决开放问题"脑补成"取代数学家"

对照 OpenAI 把数百个证明直接丢上 GitHub 绕过评审、遭 Tao 领衔的人类数学协会抵制——**"验证"与"发表"的程序正义正在成为 AI 科研的竞争轴**。这与上周 METR 统计审计是同一个故事：结论可信度本身成了稀缺品。

## Meta Muse Wonder：为 Agent 而生的前沿模型

Meta 今天发布 [Muse Wonder 与 Muse Wonder Full](https://about.fb.com/news/2026/10/introducing-muse-wonder-full/)，官方定位"迄今最强、面向个人与专业 **agentic 任务**"——从处理保险理赔、读懂租约到构建可运行的应用。Wonder 走 Meta Model API 与 Muse Code，Wonder Full 面向 Muse Code 订阅者，后续接入 Muse 助手。至此，OpenAI（dots）、Google（Gemini agent + Workspace 邮箱/日历身份）、Microsoft（Copilot）、Meta（Muse Wonder）全部把"长时程自主 coworker"当作主战场——**模型发布会的单位已经从 benchmark 变成了"agent 任务"**。

## HN：认知差距与产出差距

- [Karpathy：LLM 能力认知的差距正在拉大](https://twitter.com/karpathy/status/2109361546505966046)（641 分 / 932 评论）。重度使用者与轻度试用者对模型能力的判断分歧越来越大，这解释了为什么不同团队采用 coding agent 的收益天差地别——**能力认知决定任务分配与审核设计**。
- [AI coding agents generate more code, but not more software](https://arstechnica.com/ai/2026/10/ai-coding-agents-generate-more-code-but-not-more-software/)（Ars Technica）：代码产量大涨，交付软件没有同比例增加，产出被返工与膨胀吃掉。KPI 该从"生成量"换成**任务完成率 + 变更存活率**。
- Launch HN：[Agent37（YC F26）](https://news.ycombinator.com/item?id=50059096)做低成本 agent 沙箱——agent 基础设施的细分市场仍在快速长出新公司。

## arXiv：把"差距"变成研究对象

- **RSI-Anything**（[2610.13912](https://arxiv.org/abs/2610.13912)）：基于 JEPA 世界模型的递归自我改进框架，世界模型同时充当评估器与学习数据筛选器——上周"评估能力是 RSI 核心组件"的论断有了工程实现。配套的 **MC-EvoBench**（[2610.13829](https://arxiv.org/abs/2610.13829)）专门度量"记忆"与"可迁移能力"的差距——自我改进最常见的假阳性。
- **X-AgentRed**（[2610.13886](https://arxiv.org/abs/2610.13886)）：在演化的多服务生态中红队测试个人 Agent，挖掘"每步合规、组合致害"的累积风险——单步策略检查覆盖不了的盲区。
- **Same Query, Different Answer**（[2610.13823](https://arxiv.org/abs/2610.13823)）：即使温度为 0，语义查询系统的 run-to-run 方差也足以改变评测结论——**不报方差的 leaderboard 排名可能是噪声**。配套的 [When to Abstain](https://arxiv.org/abs/2610.13821) 把"弃权决策"当作可学习、可校准的能力。
- **推理效率**：[ReplaySSM](https://arxiv.org/abs/2610.13778) 缓存 SSM 输入而非状态、[DualQuant](https://arxiv.org/abs/2610.13767) 免校准权重+激活双 4-bit 量化——与 DwarfStar 的 2-bit 专家量化正交，低比特推理的最后几个瓶颈正被逐个拆掉。

## 一句话总结

今天的所有新闻都在量化某种差距：能力的差距（认知分歧）、产出的差距（代码 vs 软件）、可信度的差距（Lean 验证 vs 裸 GitHub 证明）、自我改进的差距（记忆 vs 能力）。**测量差距的工具，正在比缩小差距的模型更值钱。**
