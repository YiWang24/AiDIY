---
slug: ai-daily-digest-2026-06-07
title: "AI Daily Digest: OpenAI 宣布 ChatGPT 转型 Agent 超级应用、Perplexity Search as Code、DeepSeek 登顶美国企业趋势榜 - 2026/06/07"
authors: [yiwang]
tags: [ai, daily-digest, openai, perplexity, deepseek, agents, llm, security]
---

<!--truncate-->

今天的 AI 领域被 OpenAI 的一句 **"Chat is dead"** 震动——ChatGPT 将进行自 2022 年发布以来最大规模的重构，从聊天机器人转型为整合编码、Agent 和第三方集成的**"超级应用"**。与此同时，**Perplexity 推出 "Search as Code" 架构**，让 AI 模型自行编写搜索管线，成本降低 85%；**DeepSeek 登顶 Ramp 美国企业 AI 软件趋势榜**，中国企业 AI 模型加速渗透美国市场；学术界的 MLEvolve、Code2LoRA、RREDCoT 等论文展示了 AI 自进化、代码知识注入和推理训练的新突破。Hacker News 上关于 LLM 对软件工程职业影响的讨论获得 655 分，反映了技术社区的深层焦虑。

## OpenAI："Chat is dead"，ChatGPT 转型 Agent 超级应用

OpenAI 首席产品官 Thibault Sottiaux 在接受 Financial Times 采访时明确表示 **"Chat is dead"**。这不仅仅是一句口号，而是 OpenAI 产品战略的全面转向。

### 核心变化

- **ChatGPT 重构**：自 2022 年发布以来最大规模的产品重构，从"回答问题的聊天机器人"转向"自主处理任务的 Agent"
- **超级应用定位**：整合编码工具（Codex）、AI Agent 和与 Canva、Booking 等公司的合作伙伴集成
- **团队合并**：ChatGPT、Codex 等产品团队已全部合并至 Sottiaux 麾下
- **UI 改版**：未来几周将重新设计 Web 和移动端界面，引导用户使用编码、图像生成和合作应用

### 长期愿景

Sottiaux 描述的终极目标是："你将拥有一个个人 Agent，能够在个人生活和工作中帮助你处理一切事务。" 随着时间推移，模型将学会自主判断用户需求，不再需要显式引导。

这一转型标志着 AI 产品从 **"工具"（Tool）到"代理"（Agent）** 的根本范式转变，对整个行业具有深远影响。

> 来源：[Financial Times](https://www.ft.com/)（2026-06-07）

## Perplexity "Search as Code"：AI 自写搜索管线

Perplexity 推出了突破性的 **"Search as Code"** 架构，彻底改变了 AI Agent 使用搜索的方式。

### 技术创新

传统做法是为 AI Agent 提供固定的搜索 API，Agent 只能调用预定义的搜索接口。Perplexity 的新方案让 **AI 模型在沙箱中自行编写 Python 搜索程序**：

- **自主过滤和去重**：Agent 自己决定如何处理搜索结果
- **灵活查询构建**：不再受限于固定 API 的查询格式
- **沙箱安全**：在隔离环境中执行，防止安全风险

### 性能表现

在关键基准测试上超越 OpenAI 和 Anthropic 的方案，同时**将 token 成本降低高达 85%**。这表明在 AI Agent 架构中，给模型更多自主权（而非更多约束）可能带来更好的性能和效率。

> 来源：[The Decoder](https://the-decoder.com/perplexitys-search-as-code-lets-ai-models-write-their-own-search-pipelines-instead-of-calling-fixed-apis/)（2026-06-07）

## ChatGPT Lockdown Mode：对抗提示注入

OpenAI 为 ChatGPT 推出 **Lockdown Mode**，用户可以禁用 Web 访问、Deep Research 和 Agent Mode。

### 工作原理

Lockdown Mode 的设计思路是阻断提示注入攻击的**数据泄露链**——即使攻击者成功注入了恶意指令，没有网络访问和工具调用能力，也无法将窃取的数据发送出去。

### 局限性

需要注意的是，该模式**不能完全防止提示注入**，仅阻断泄露链的最终环节。提示注入（Prompt Injection）仍是 AI 安全领域未解决的难题。Lockdown Mode 本质上是一种"纵深防御"策略——增加攻击者成功泄露数据的难度，而非从根本上解决漏洞。

> 来源：[The Decoder](https://the-decoder.com/chatgpts-new-lockdown-mode-lets-you-disable-web-access-and-more-to-protect-sensitive-data-from-prompt-injection/)（2026-06-07）

## DeepSeek 登顶美国企业 AI 趋势榜

据企业支出管理平台 Ramp 数据，**DeepSeek 在 2026 年 6 月成为美国企业使用增长最快的 AI 软件服务商**。这是一个标志性事件——中国 AI 模型开始以付费服务的形式直接服务美国企业客户。

### 关键数据

- 美国公司直接向 DeepSeek 发送数据处理
- 成本意识是采用的主要驱动力
- Ramp 首席经济学家 Ara Kharazian 警告使用中国模型存在安全风险

### 行业影响

这一趋势凸显了 AI 市场的**成本敏感性与安全顾虑之间的张力**。企业希望在降低 AI 使用成本的同时，也面临数据跨境传输和地缘政治风险。DeepSeek 的成功表明，在当前 AI 基础设施成本高企的环境下，价格优势可以驱动快速采用。

> 来源：[The Decoder](https://the-decoder.com/deepseek-topped-ramps-trending-software-vendors-in-june-2026-as-us-companies-chase-cheaper-ai/)（2026-06-07）

## Anthropic 挖角 OpenAI 芯片工程师

Anthropic 招募了 **OpenAI 的第二位芯片工程师**，两家公司均在竞相推进 IPO。这一动向表明：

- AI 公司的竞争已从软件人才扩展到**硬件基础设施人才**
- AI 芯片自主设计能力正成为战略重点
- 定制芯片可能成为下一代 AI 模型训练和推理效率的关键差异化因素

> 来源：[The Decoder](https://the-decoder.com/)（2026-06-07）

## 学术前沿

### MLEvolve：LLM 自进化框架实现 ML 算法自动发现

[MLEvolve](https://arxiv.org/abs/2606.06473)（Du 等）提出基于 LLM 的自进化多 Agent 框架，用于端到端机器学习算法发现。核心创新包括：

- **Progressive MCGS**：扩展树搜索实现跨分支信息流动，渐进式从探索转向利用
- **Retrospective Memory**：结合领域知识库和动态全局记忆，实现经验检索和复用
- **解耦架构**：策略规划与代码生成分离，支持自适应编码模式

在 MLE-Bench 上 12 小时预算内（标准时间的一半）达到 SOTA，在数学算法优化上超越 AlphaEvolve。

### Code2LoRA：超网络为零开销代码知识注入

[Code2LoRA](https://arxiv.org/abs/2606.06492)（Hotsko 等）提出超网络框架，为代码语言模型生成仓库特定的 LoRA 适配器。两种模式：

- **Code2LoRA-Static**：将仓库快照转换为适配器，适合稳定代码库
- **Code2LoRA-Evo**：基于 GRU 隐藏状态按代码 diff 更新适配器，适合活跃开发的演进代码库

静态模式在 604 个 Python 仓库基准上达到 63.8% 跨仓库精确匹配，匹配每仓库 LoRA 上限。

### RREDCoT：推理模型的分段奖励重分配

[RREDCoT](https://arxiv.org/abs/2606.06475)（Ielanskyi 等）解决了 GRPO 训练推理模型的核心问题——延迟奖励的高方差。通过利用模型自身近似最优奖励重分配，无需额外生成，实现 CoT 轨迹的精细信用分配。

### LLM 规模效应机制揭示

新研究使用从 400 万到 40 亿参数的模型，揭示了小模型在罕见任务上失败的机制——**频繁任务的训练信号不断覆盖已学到的罕见任务知识**。实用发现：增加目标任务在训练数据中的出现频率，效果可能等同于增大模型规模。

> 来源：[arXiv](https://arxiv.org/)（2026-06-04）

## Hacker News AI 热点

### "LLMs are eroding my software engineering career"（655 分）

一篇关于 LLM 对软件工程师职业生涯影响的个人反思在 HN 引起巨大共鸣。作者描述了 AI 工具如何逐渐改变其工作内容和职业前景。655 分的高关注度反映了技术社区对 AI 替代效应的深层焦虑和真实讨论。

### "Anthropic, please ship Claude Desktop for Linux"（327 分）

开源社区呼吁 Anthropic 发布 Linux 版 Claude Desktop 的 GitHub issue 获得大量支持。反映了 Linux 用户在 AI 工具生态中仍被忽视的现状。

### Tokenomics：Agentic 软件工程中的 Token 使用量化（155 分）

来自 arXiv 的 [Tokenomics](https://arxiv.org/abs/2601.14470) 论文量化分析了 Agent 软件工程中 token 的使用分布，为理解和优化 AI 编程成本提供了数据驱动的视角。

### Speculative KV Coding：无损压缩 KV 缓存 4 倍（127 分）

通过投机编码技术实现 KV 缓存的无损压缩，最高可达约 4 倍。这对长上下文推理的效率优化具有重要意义。

## 知识库更新

本次更新涉及以下文档：

- **AI Agents / Frontier Trends** (`docs/ai/agents/10-frontier.mdx`): 添加 OpenAI ChatGPT Agent 转型、Perplexity Search as Code、ChatGPT Lockdown Mode、DeepSeek 企业趋势、Anthropic 芯片人才争夺、MLEvolve 自进化框架、Code2LoRA 仓库适配器、RREDCoT 奖励重分配、LLM 规模效应机制研究、关键趋势 #56-#62

---

*本消化报告由 AiDIY 知识库自动生成，覆盖 2026 年 6 月 7 日的主要 AI 动态。如需查阅历史更新，请访问 [AiDIY 博客存档](https://aidiy.dev/blog)。*
