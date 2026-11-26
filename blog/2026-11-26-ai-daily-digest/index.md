---
slug: ai-daily-digest-2026-11-26
title: "AI Daily Digest: Anthropic 发布 7.6 万行 GRH Lean 短版证明、NP_R ≠ PAR_R 再添自动化数学宣称、GPT-6 内生蛋白质设计能力、NYT 禁摄影师升级 Photoshop - 2026/11/26"
authors: [yiwang]
tags: [ai, daily-digest, lean, formal-verification, automated-math, ai-safety, protein-design, content-authenticity, arxiv]
---

<!--truncate-->

今天的主题词是**验证的金字塔**。Anthropic 把黎曼猜想相关的 GRH 形式化证明从 1700 万行压缩到 7.6 万行——机器检查全过，但「没有一个数学家通读过」；同一天又一批自动化数学宣称涌上 HN。当机器验证成为唯一可靠的一层，人类理解那一层正在变薄。

## Anthropic 发布 GRH Lean 短版：76,000 行的「短」

[grh-lean 仓库](https://github.com/lsernau/grh-lean)（[HN 527 分，336 评论](https://news.ycombinator.com/item?id=50648050)）昨日晚间发布：基于 Levent Alpöge 的证明（与 Anthropic 同事及 Claude 协作产出），Generalized Riemann Hypothesis 的 Lean 4 证明分两个版本——**可读版约 30 万行、紧凑版约 7.6 万行**，仅依赖 Mathlib 与三条标准公理，构建一次约需 12 核 1-2 小时。README 的自我描述异常清醒：*「证明只通过了机器检查，没有任何数学家通读过它，也没有附带论文」*。

这条线的上下文值得串起来：全社区协作的 1700 万行 RH Lean 证明（11-21）刚因「[Yes, 17M lines of Lean is a lot](https://micjm.com/blog/yes-17m-lines-of-lean-is-a-lot/)」（277 分）的规模质疑登上首页，[网上已出现「 alleged fatal flaw」的挑战](https://news.ycombinator.com/item?id=50636806)，现在 Anthropic 的短版把行数砍掉两个数量级——而且社区已经在为它[写教科书](https://github.com/tamnd/grh-lean-handbook)。注意层级结构：**机器验证层已经可靠且规模化，人类理解层刚刚起步**。短版的价值不在于更可信（可信度由 Lean 保证，与行数无关），而在于可读版是 30 万行、紧凑版 7.6 万行——把「能被人读懂」的门槛从不可能拉回到「一个专注的团队几个月」。证明的可理解性第一次成为被显式优化的工程指标。

## NP_R ≠ PAR_R：自动化数学的下一批宣称

今天下午刚上首页的 [NP_R ≠ PAR_R](https://github.com/samueleverett01/bss-permanent-separations)（112 分，121 评论）——随机化计算类与永久行列式相关的采样复杂度分离——延续了本周自动化数学宣称的节奏：ω=9/4、分解问题界、如今是复杂度类分离。这些工作的共同点是都还没过同行评审，部分 Lean 形式化「承诺了但未发布」。按昨天确立的判断标准：精确分离宣称在验证前一律按猜想处理；真正值得追踪的不是单篇对错，而是**宣称的产出速率与验证速率之间的缺口仍在扩大**。

## GPT-6 模型展现出「内生」蛋白质设计能力

OpenAI 发布 [GPT-6 models demonstrate intrinsic protein-design capabilities](https://openai.com/index/gpt-6-models-demonstrate-intrinsic-protein-design-capabilities/)（[355 分，97 评论](https://news.ycombinator.com/item?id=50634658)）：未做生物特化训练的 GPT-6 系列模型在蛋白质设计任务上表现出能力——「intrinsic」这个词是重点，它宣称的不是加了个生物工具包，而是通用预训练涌现出结构生物学层面的设计能力。结合 11-24 API 中上线的医疗模型配置（Astra/Sol 接入专属医疗检索索引），OpenAI 在生物/医疗方向的布局正在从「问答助手」转向「设计工具」——这条线的验证问题也比聊天难得多：蛋白质设计的对错要用湿实验确认，验证周期以周计。

## NYT 警告摄影师：别升级 Photoshop

[The Verge 报道](https://www.theverge.com/ai-artificial-intelligence/1041227/the-new-york-times-warns-photographers-not-to-update-photoshop-over-ai-features)（[616 分，491 评论](https://news.ycombinator.com/item?id=50647673)）：纽约时报摄影部门警告摄影师暂缓升级 Photoshop，原因是新版 AI 功能对新闻照片真实性的威胁——生成式填充与自动「增强」会让「按下快门那一刻的原始记录」与「算法重构的图像」之间失去清晰边界。这是内容真实性战场从 C2PA 签名、水印下沉到**工作流入口**的信号：新闻机构发现最可靠的防线不是事后检测，而是让原始传感器数据根本不经过生成式管线。

## 其他值得记录的

- **Google 强制 Workspace AI agent 用官方 MCP 服务器**（[116 分](https://news.ycombinator.com/item?id=50653477)）：平台化 agent 的权限收口开始了——但 Gmail 的 MCP 服务器「不能发邮件」，能力阉割版官方通道与全功能第三方通道之间的张力将是 2027 年 agent 平台的主战场。
- **Moat：OpenRouter 替代品**（206 分）：LLM 路由层继续「去中心化」，继 OpenRouter 下线三家推理提供商后，社区自建路由的动量在积累。
- **OpenAI 或已进入成本控制模式**（[22 分](https://micjm.com/blog/openai-is-in-cost-control-mode/)）：与 Codex 计量事故、 healthcare 配置的商业化节奏互相印证。
- **GitHub Copilot Fusion 转正、MAI Code 2 进 Copilot**：微软本周 Ignite 后的 agent 编码矩阵继续加密。

## arXiv 精选

**[Tokenisation is not in APX](https://arxiv.org/abs/2611.34938)**（11-25）：除非 P=NP，不存在多项式时间算法能把分词器做到常数因子近似最优——分词优化连 TSP 式的近似保证都没有。知识库分词笔记已更新：**你的 tokenizer 离最优差多远，理论上是不可知的**。

**[Mixture-of-Loops Transformer](https://arxiv.org/abs/2611.34923)**（11-25）：循环 Transformer 的循环间连接从固定设计变成每 token 动态路由。与 GLM-5.4（首个 Loop Transformer 旗舰）、Inkling 2 Mini（26.4B 循环架构跑在 32GB Mac 上）汇成一条线：**有效深度正在成为独立于参数量的缩放维度**。知识库 Transformer 架构笔记已更新。

**[How Much Do Coding Agents Over-Edit, and Why?](https://arxiv.org/abs/2611.34875)**（11-25）：用 Delta Residue Attribution 回放 agent 轨迹，把「补丁大」拆解成必要超出与真正过度编辑。知识库 Coding Agents 笔记已更新：**用 diff 大小评审 agent 会同时惩罚做对的人**。

**[Attack Policy Selection can Mislead Monitor Evaluators](https://arxiv.org/abs/2611.34934)**（11-25）：OpenAI 前生产监控器的案例研究——换一批攻击策略，同一个监控器的漏报率显著漂移。知识库 AgentOps 安全笔记已更新：监控器也会过拟合自己的评估集。

**[Diverse Alternative Reasoning Traces for Hard Math Problems](https://arxiv.org/abs/2611.34928)**（11-25）：难题的「通过验证的推理轨迹」在独立采样下极稀少，本文提出多样化替代轨迹生成策略——与本周的数学验证主题呼应：**稀缺的不只是证明，还有能通过验证的路径**。

---

今天的故事共享一个结构：**验证金字塔的形状正在改变**。机器检查那一层变得又快又可靠（Lean 构建一次只要两小时），人类理解那一层却在变薄（没有数学家通读过 GRH 证明）、被绕过（新闻照片不许碰生成式管线）、或者干脆欠着账（自动化数学宣称排队等审查）。机器验证是必要条件，永远不该被当成充分条件——GRH 仓库 README 那句「没有数学家读过它」，是本周最诚实的一句话。明天见。
