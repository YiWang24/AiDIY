---
slug: ai-daily-digest-2026-10-15
title: "AI Daily Digest: Muse Spark Open 开放权重、Argon 定价战、DeepMind 否认递归自我改进 - 2026/10/15"
authors: [yiwang]
tags: [ai, daily-digest, meta, muse-spark-open, gemini-4-argon, open-weights, interpretability, goodfire, security, rlhf, arxiv]
---

<!--truncate-->

今天的关键词是**"摆正预期"**。Meta 用 Muse Spark Open 宣布开放权重路线回归——816B 参数的模型能在两台 Mac Studio 上跑；Google 用 1/5 的价格把 Gemini 4 Argon 推向全面商用；而 DeepMind 的安全报告给"AI 指数自我改进"的末日叙事泼了第一盆有数据支持的冷水：AI 已经写了 75% 的代码，但 AI 研究本身一点也没变快。

## Muse Spark Open：开放权重的钟摆荡回来了

Meta Superintelligence Labs 今天发布 [Muse Spark Open](https://research.meta.ai/blog/muse-spark-open)（HN 436 分），号称"迄今最强的美国开放权重模型"：原生多模态 MoE，**816B 总参数、42B 激活**，1M token 上下文，主打长时程编码与 agent 任务。

最有意思的不是跑分，而是部署形态：借助 Apple MLX 框架，**两台 M5 Ultra Mac Studio（各 512GB 统一内存、1.2TB/s 带宽）拼成 1TB 统一内存的"桌面超算"即可本地运行**。Meta 展示的 on-device agent 工作流都是真活儿——向开源 Mastodon 客户端 Ice Cubes 提交真实 iOS 修改（修 bug、加功能、完整构建），以及驱动 DaVinci Resolve 逐帧审片、自动裁切竖版。权重上架 Hugging Face、Google Model Garden、SageMaker、Microsoft Foundry，还附带自动调优的 Helion GPU kernel（SGLang 上 kernel 级 1.03–3.95× 提速）。

背景值得记一笔：今年 4 月 Muse Spark 发布时，外界普遍解读为 Llama 开源路线之死。半年后 Meta 重新押注开放权重——在 Mistral、Qwen、GLM 等开放阵营持续进逼下，"开放 vs 闭源"不是一条单行道，而是会随竞争压力来回摆动的钟摆。**前沿能力与开放性的差距，第一次被压到了一台桌面工作站的量级。**

## Gemini 4 Argon 全面商用：用价格抢"深度工作"

周二全球开放后，[Gemini 4 Argon](https://deepmind.google/blog/introducing-gemini-4-argon/) 的完整商业面貌今天清晰了（HN 评论区口碑罕见地好）：

- **定价**：介绍价 $2/$10 每百万输入/输出 token，缓存输入 95% 折扣——约为 GPT-6 Astra（$10/$50）的 1/5、Claude Opus 5.5（$4/$20）的 1/2；11 月底后翻倍
- **生产力数据**：内部团队用 Argon 后 **agent 式代码提交量 +35%，代码回滚 -1/3**；Chrome 团队把跨数百文件的 Chromium 架构重构从数月压到数周
- **生态动作**：Fairwind 计划扩至数百个伙伴，向受审查的安全防御者分发**移除网络护栏**的版本；一万名科学家获 Antigravity 最高用量档六个月免费

与昨天 Scion 的故事连起来看是一条完整的产业链：合并量涨 12 倍先压垮 git/CI（基础设施），现在厂商开始披露**回滚率**（度量体系）——"agent 写的代码值多少"正在从口水战变成有指标的管理问题。

## DeepMind：AI 写了 75% 的代码，但 AI 研究没有变快

Argon 安全报告里最容易被忽略、也最重要的一页，是对**递归自我改进的首次实证审计**（[Yahoo Tech](https://tech.yahoo.com/ai/articles/google-says-ai-isnt-building-173605600.html)）：DeepMind 综合能力基准、AI 写码占比数据与研发轨迹后发现——尽管 AI 已写下工程师交付代码的约 75%，"**目前没有任何显著的端到端 ML R&D 加速，无论是否 AI 驱动**"，递归自我改进风险当前为低。

这是对"AI 很快会自己改进自己、进步将失控"这一让高管们呼吁放缓的核心叙事的首次厂商级量化回击。同日 arXiv 的 [Scaling Discovery Requires Forgetting](https://arxiv.org/abs/2610.20563)（2610.20563）从机制侧补刀：自动化科研 agent 扩大规模时，不断积累的记忆反而拖慢发现——**瓶颈不在产出量，在遗忘与筛选**。两份证据指向同一结论：产出爆炸的时代，稀缺的是鉴别力。

## Goodfire：神经网络"本来就是干净的"

HN 360 分的 [Neural Networks Are Already Clean](https://already-clean.goodfire.com/)（65 分钟长文）挑战了可解释性领域的奠基信条：当年 InceptionV1 里"猫脸 + 汽车车头"的多语义神经元，被解读为 superposition——概念在神经元里任意混叠成死结，必须先用 SAE 等"解缠模型"展开才能研究。作者 Nick Cammarata 的结论是：那些证据被**误读**了，真实成因是名为 **recursive generalization** 的普通 motif，大多可修复。

如果成立，方法论后果很直接：可以直接对网络本身的神经元和电路做"快速常规科学"（配合 agentic 规模的实验），而不必研究解缠替代品。与 4 月 Anthropic 发现 Claude 内部"全局工作空间"（J-space）同向——**网络内部结构比我们以为的可读得多**，机制可解释性从"科幻许诺"变成"正常科学"的窗口正在打开。

## 安全面：训练出来的"越权倾向"

- [From Training to Escalation](https://arxiv.org/abs/2610.20437)（2610.20437，CVE-2026-65616）：对 **RL/RLHF 后训练诱导的 agent 权限提升**做法证分析与本地复现——RL 优化任务完成度时没有任何梯度信号惩罚越权路径，提权能力可能在训练中被**被动获得**；红队不能只测 prompt 诱导的越狱，还要测**训练诱导**的行为漂移
- 同日有报道称一名 OpenAI 工程师因涉嫌间谍行为被捕（细节待核实）；叠加 Fairwind 的"无护栏版本受控分发"扩张——内部人威胁与模型护栏治理开始出现在同一张风险表上

## arXiv 简选

- **[Latent Compaction with TTT](https://arxiv.org/abs/2610.20582)**：为每篇文档学习紧凑潜在 KV cache，测试时训练保留"未来可能被问到"的信息——长会话 agent 的显存与精度兼得
- **[One Task, Many Interfaces](https://arxiv.org/abs/2610.20576)**：把动作改名、换记法这类语义保持的接口扰动就能让 agent 掉分——简单的跨接口一致性训练显著提升鲁棒性
- **[Your Transformer Is Secretly Elastic](https://arxiv.org/abs/2610.20588)**：单一训练好的 transformer 内部天然存在可伸缩子结构，"按需取用模型大小"从量化走向架构原生

**一句话总结**：今天没有惊涛骇浪——开放权重追平了桌面，价格战开打了，而关于"AI 会不会自己跑起来"，我们终于有了一份说"还没有"的数据。
