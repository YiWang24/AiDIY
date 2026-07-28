---
slug: ai-daily-digest-2026-07-28
title: "AI Daily Digest: MCP 最大修订落地、Amazon 战略收缩、Nvidia 布局 SSI - 2026/07/28"
authors: [yiwang]
tags: [ai, daily-digest, mcp, amazon, nvidia, ssi, kimi, stateless]
---

<!--truncate-->

今日 AI 领域呈现出基础设施、产业格局和技术架构三条主线交织的复杂画面。MCP 在诞生不到两年后迎来了最重大的无状态化修订，直接改变了 Agent 生态的部署范式；Amazon 在 Nova 模型线上按下"暂停键"，将全部赌注押向前沿研究团队；Nvidia 则通过投资 Ilya Sutskever 的 SSI，在 AI 芯片战争的棋盘上落下关键一子。与此同时，Kimi K3 的 Delta Attention 架构解析在技术社区引发热议，arXiv 上多篇 Agent 评估与架构论文也提供了新的理论视角。

## MCP 2026-07-28：自诞生以来最大规模修订

模型上下文协议（Model Context Protocol, MCP）维护团队于今日正式发布了 `2026-07-28` 版本规范，这标志着该协议自 2024 年末问世以来最重要的一次架构演进。

### 无状态协议核心

本次修订的核心变化是将协议传输层从有状态会话模型彻底转变为无状态模型。具体而言：

- **移除协议层会话**：取消了 `Mcp-Session-Id` 头和 `initialize`/`initialized` 握手流程
- **引入 `server/discover` RPC**：客户端通过每请求携带协议版本号进行能力协商，取代了之前的全局初始化握手
- **6 个 SEP 协同**：六份规范增强提案（Specification Enhancement Proposals）共同构成了这一无状态架构的技术基础

这意味着一个工具调用请求成为了完全自包含的：路由信息通过 HTTP 头部（`MCP-Protocol-Version`、`Mcp-Method`、`Mcp-Name`）传递，请求体包含所有业务参数。任何标准 HTTP 负载均衡器都可以直接分发这些请求，无需粘性路由或共享会话存储。

### 扩展框架与弃用策略

新规范同时引入了正式的扩展框架（Extensions），包括 MCP Apps（服务器端渲染 UI 扩展）和 Tasks（长时间运行任务的扩展）。授权机制更紧密地对齐 OAuth 和 OpenID Connect。旧的 HTTP+SSE 传输被标记为"已弃用"，Roots/Sampling/Logging 等功能也被纳入弃用范畴。

对于生产环境而言，这一修订的影响是深远的。此前，水平扩展 MCP 服务器需要复杂的共享会话存储和粘性路由配置，现在这一切都不再需要。微软 Azure App Service 团队已在技术博客中确认，新规范大幅简化了 MCP 服务在云平台上的部署复杂度。

> 来源：[MCP 2026-07-28 Release Candidate](https://blog.modelcontextprotocol.io/posts/2026-07-28-release-candidate)；[Microsoft 技术分析](https://techcommunity.microsoft.com/blog/appsonazureblog/mcp-just-went-stateless-—-what-the-2026-spec-changes-about-scaling-on-app-servic/4530222)（July 28, 2026）

## Amazon 战略收缩：Nova 模型全面降级

Amazon 正在进行一次深刻的 AI 战略转型。据 Business Insider 和 Reuters 报道，公司已决定停止主动开发大部分自研 Nova 系列 AI 模型。

### 被缩减的模型线

受影响的模型包括旗舰级 Nova Premier 和 Nova Omni 多模态模型、Reel 视频生成模型，以及 Canvas 图像生成器。这些模型不会被立即下线，而是进入"维持运转"（keep the lights on）模式——现有客户仍可使用，但不再获得功能更新或性能优化。

### Frontier Model Research 成为唯一焦点

Amazon 将工程团队和稀缺的计算资源集中到内部代号为 Frontier Model Research（FMR）的组织。该团队由加州大学伯克利分校教授 Pieter Abbeel 领导——他于 2024 年通过 Amazon 收购机器人初创公司 Covariant 而加入。FMR 已成为 Amazon AGI 组织内部的最高优先级项目，新旗舰基础模型预计在今年秋季的 re:Invent 大会上首次亮相。

与此同时，Amazon 于 2024 年成立的 AGI Lab（源自收购 Adept）已经关闭，伴随着 AGI 部门的一轮裁员。但 Amazon 并非退出 AI 竞赛：公司仍然是 Anthropic 和 OpenAI 的最大投资者之一，对这两家的投资合计可能超过 1000 亿美元。这种"自己造不如投资"的策略，与 Google、Microsoft 等竞争对手形成了鲜明对比。

> 来源：[Business Insider / Reuters](https://www.reuters.com/business/retail-consumer/amazon-winds-down-most-flagship-ai-models-strategy-overhaul-business-insider-2026-07-28)；[Trending Topics](https://www.trendingtopics.eu/amazon-scales-back-its-own-ai-models-to-focus-on-infra-openai-and-anthropic)（July 28, 2026）

## Nvidia 入股 SSI：Ilya Sutskever 的芯片选择

Nvidia 宣布向 Ilya Sutskever 创立的 Safe Superintelligence（SSI）投入一笔"巨额"资金。这笔交易的深层意义远超财务投资——它标志着 SSI 从 Google TPU 生态转向 Nvidia 的下一代 Vera Rubin GPU 平台，算力预计提升十倍。

### 从 TPU 到 GPU 的迁移

Sutskever 此前一直依赖 Google 的 TPU 芯片进行模型训练，这也延续了他在 OpenAI 时期的习惯（OpenAI 在与 Microsoft 合作前曾大量使用 Google 云服务）。转向 Nvidia 意味着 SSI 将深度绑定 Nvidia 的硬件路线图，包括最新的 Vera Rubin 平台。

对 Nvidia 而言，这笔投资具有双重战略价值：一方面锁定了 AI 领域最受关注的实验室之一作为长期客户，另一方面也在与 Google 的芯片竞争中取得了关键性胜利。Google 近年来一直在推广 TPU 作为 Nvidia GPU 的替代方案，SSI 的转向无疑削弱了这一努力。

SSI 成立于 2024 年，目标是实现"安全超级智能"的"直线冲刺"。公司融资约 20 亿美元，估值约 300 亿美元，投资方包括 Andreessen Horowitz、Sequoia Capital、DST Global 和 Greenoaks。Sutskever 表示研究方向聚焦于"人类大脑功能中被忽视的方面"。

> 来源：[The Decoder / Nvidia](https://the-decoder.com/)（July 28, 2026）；[MarketWatch](https://www.marketwatch.com/investing/stock/nvda)

## Kimi Delta Attention：社区深度解析走红

随着 Kimi K3 在昨天发布开源权重，技术社区对其核心架构 Kimi Delta Attention（KDA）的解析迅速走红。

Doubleword.ai 发表了一篇题为"你自己也能想出 Kimi Delta Attention"的技术博客，在 Hacker News 上获得了 229 分和 86 条评论。文章以直觉性的方式解释了 KDA 的设计动机——它并非凭空诞生的革命性架构，而是沿着已有的注意力机制研究脉络自然推导出的优化方向。

与此同时，知名 AI 研究者 Sebastian Raschka 也发布了 Kimi K3 架构的深度分析（HN 109 分），重点解读了 Stable LatentMoE 框架的设计：在 896 个专家中仅激活 16 个，配合 MXFP4 量化和 MXFP8 激活值，使得 2.8 万亿参数的模型在经济上变得可行。Raschka 的分析涵盖了从注意力层到 MoE 路由的完整架构图。

两篇解析共同揭示了一个关键事实：Kimi K3 的架构创新不在于单一突破，而在于多个已知优化技术的系统性整合。KDA 提供了高效的序列长度扩展基础，Attention Residuals（AttnRes）实现了跨深度的选择性表示检索，而 Stable LatentMoE 则保证了专家路由的稳定性。三者协同实现了约 2.5 倍的整体扩展效率提升。

> 来源：[Doubleword.ai](https://blog.doubleword.ai/you-could-have-come-up-with-kimi-delta-attention)；[Sebastian Raschka](https://sebastianraschka.com/blog/2026/kimi-k3-architecture-notes.html)；[arXiv:2510.26692](https://arxiv.org/abs/2510.26692)（July 28, 2026）

## Anthropic CEO 再谈开源风险

Anthropic CEO Dario Amodei 再次就开源 AI 模型的风险发出警告，同时坚称自己从未呼吁"禁止"开源。他的核心论点是：威权国家（如中国）可能利用开源模型追上美国的 AI 优势，且开源模型可能被用于生物武器或网络攻击。

然而批评者指出，Amodei 的警告时机耐人寻味——正值 Kimi K3 等开源模型在性能上逼近闭源前沿之际。将开源风险与国家安全绑定，客观上有利于保护 Anthropic 自身的商业模式免受更廉价开源竞争的冲击。25 家科技公司上周联名签署的公开信也反映了产业界对"过早限制开源"的担忧。

> 来源：[The Decoder](https://the-decoder.com/)（July 28, 2026）

## 学术前沿：Agent 架构与评估

### 从认知架构到语言 Agent 的机制级谱系

arXiv:2607.23942 从机制层面回顾了认知架构（如 SOAR、ACT-R）与现代语言 Agent 之间的演化谱系。论文分析了两者在记忆管理、目标表征和决策机制上的趋同趋势，同时也指出了从符号推理到神经推理迁移过程中的深层差距。这对于理解当前 Agent 架构的理论根基和未来方向提供了系统性框架。

### 多 Agent 协议蒸馏：缩小专有与开源差距

arXiv:2607.24280 提出了一种新颖的方法：通过多 Agent 协议蒸馏（Multi-Agent Protocol Distillation），将专有模型的 Agentic 行为模式迁移到开源模型中。在搜索场景的实验中，蒸馏后的开源模型在工作流执行和工具调用方面表现出了接近专有模型的能力。这为降低 Agent 部署成本提供了一条可行的技术路径。

### 成功溯源：Agent 评估中被忽视的维度

arXiv:2607.24054 对当前 Agent 基准测试提出了尖锐质疑：我们定义的"成功"到底是什么？论文指出，大多数评估只关注最终结果是否正确，但忽略了到达结果的路径质量、资源消耗和可重复性。研究者提出"成功溯源"（Success Provenance）的概念框架，要求在评估中审计 Agent 完成任务的完整轨迹。

> 来源：[arXiv:2607.23942](https://arxiv.org/abs/2607.23942)；[arXiv:2607.24280](https://arxiv.org/abs/2607.24280)；[arXiv:2607.24054](https://arxiv.org/abs/2607.24054)（2026-07）

## 知识库更新

本次更新涉及以下文档：

- **MCP 文档** (`docs/ai/mcp/index.mdx`): 新增 MCP 2026-07-28 规范发布记录，涵盖无状态协议核心、Extensions 框架、授权强化和弃用策略
- **AI Agents / 前沿趋势** (`docs/ai/agents/10-frontier.mdx`): 新增 10 条前沿趋势（#370-379），包括 MCP 无状态化修订、Amazon Nova 战略收缩、Nvidia 投资 SSI、Kimi Delta Attention 社区解析，以及 6 篇 arXiv 论文

---

*本日内容由 AiDIY 每日知识更新自动化流程生成，覆盖 arXiv、Hacker News、The Decoder 等多源信息。*
