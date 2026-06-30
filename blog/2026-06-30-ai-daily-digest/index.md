---
slug: ai-daily-digest-2026-06-30
title: "AI Daily Digest: Anthropic Claude Science 发布与模型成本优化竞赛 - 2026/06/30"
authors: [yiwang]
tags: [ai, daily-digest, agents, llm, research]
---

<!--truncate-->

今日 AI 新闻聚焦两大主题：Anthropic 发布专为科研人员设计的 Claude Science AI 工作台，整合 60+ 预配置技能；模型厂商展开成本优化竞赛，OpenAI 将推理成本削减一半，美团证明国产芯片可训练 1.6 万亿参数模型。同时，Meta 内部安全性测试揭示竞品 AI 漏洞，Google 推出新一代图像和视频生成模型。

## Anthropic 发布 Claude Science：AI 科研工作台

Anthropic 正式发布 Claude Science，这是专为科研人员设计的 AI 工作台应用。该应用整合了数十个数据库、工具和软件包于统一界面中，研究人员可以进行文献分析、运行多步分析、创建图表和起草论文。

Claude Science 预配置了 60+ 技能，覆盖基因组学、蛋白质组学、化学信息学等领域。应用本地运行于 macOS 或 Linux，通过 SSH 连接远程机器或 HPC 集群，确保敏感数据无需离开实验室基础设施。只有 Claude 实际需要的上下文才会发送到模型。

当任务需要更多计算能力时，应用可从单个 GPU 扩展到数百个 GPU。Claude Science 集成了 Nvidia 的新 BioNeMo agent toolkit，内置 Evo 2、Boltz-2、OpenFold3 等模型。研究人员还可以将自己的 pipeline 保存为可复用技能。

该应用目前处于 beta 阶段，面向 Pro、Max、Team 和 Enterprise 用户开放。Anthropic 还为多达 50 个研究项目提供每个最高 3 万美元的积分支持，申请截止 2026 年 7 月 15 日。

> 来源：[The Decoder](https://the-decoder.com/anthropic-launches-claude-science-an-ai-workspace-built-specifically-for-researchers/)

## Claude Sonnet 5 性能接近 Opus 系列

Anthropic 新发布的 Claude Sonnet 5 在多项基准测试中表现出接近高价 Opus 模型系列的性能。这一进展标志着 Anthropic 在中端模型上的技术进步，为用户提供更高性价比的选择。

Sonnet 5 的发布进一步模糊了中端与高端模型的界限，使得更多用户能够以较低成本获得接近顶级模型的能力。这对于需要大规模部署 AI 应用的企业尤为重要。

> 来源：[The Decoder](https://the-decoder.com/anthropics-new-claude-sonnet-5-closes-the-gap-to-the-pricier-opus-model-series/)

## OpenAI 大幅降低 ChatGPT 响应成本

据 The Information 报道，OpenAI 工程师本月早些时候向同事透露，他们成功将现有 AI 模型的推理成本削减了一半以上。这一工程优化使得 OpenAI 能够在不牺牲性能的前提下显著降低运营成本。

成本降低主要来自于模型推理过程的工程优化，而非模型架构的改变。这一进展对于 ChatGPT 的商业化至关重要——随着用户量增长，单位成本降低直接转化为利润率提升。

> 来源：[The Decoder](https://the-decoder.com/openai-reportedly-cut-response-costs-for-guest-chatgpt-users-by-more-than-half/)

## 美团 1.6 万亿参数模型完全国产芯片训练

中国美团公司宣布成功训练名为 LongCat-2.0 的 1.6 万亿参数 AI 模型，完全使用国产芯片，无需 Nvidia GPU。该公司表示："LongCat-2.0 已经证明我们现在具备在国产计算集群上训练大规模模型的能力。"

这一成就表明，在美国出口管制背景下，中国科技公司正在加速推进国产 AI 芯片和训练基础设施的成熟。虽然国产芯片在单卡性能上仍落后于 Nvidia H100/A100，但通过集群优化和软件栈改进，已经能够支持超大规模模型训练。

> 来源：[The Decoder](https://the-decoder.com/meituan-trains-a-1-6-trillion-parameter-ai-model-entirely-on-chinese-chips-no-nvidia-required/)

## Meta 内部测试竞品 AI 安全性

Meta 公司报告称，他们安排了数百名承包商伪装成未成年人，向 OpenAI 的 ChatGPT、Google 的 Gemini 和 Character.AI 的聊天机器人发送了超过 45,000 个与自杀、性、毒品相关的提示。这一大规模安全性测试揭示了竞品 AI 系统在面对恶意提示时的漏洞。

测试显示，即使在防护措施下，主流聊天机器人仍然可能被诱导生成不安全内容。这一发现为 AI 安全研究提供了宝贵的真实世界数据，也反映了行业对 AI 安全性的持续关注。

> 来源：[The Decoder](https://the-decoder.com/meta-secretly-tested-chatgpt-gemini-and-character-ai-with-thousands-of-minor-perspective-crisis-prompts/)

## Google 推出 Nano Banana 2 Lite 与 Gemini Omni Flash

Google 发布了新一代 AI 生成模型：Nano Banana 2 Lite 用于快速 AI 图像生成，Gemini Omni Flash 用于视频生成 API。这两个模型通过 API 提供，面向开发者和企业用户。

Nano Banana 2 Lite 专注于速度优化，适合需要实时图像生成的应用场景。Gemini Omni Flash 则扩展到视频领域，为内容创作者提供新的工具。

> 来源：[The Decoder](https://the-decoder.com/google-launches-nano-banana-2-lite-for-fast-ai-images-and-gemini-omni-flash-for-video-via-api/)

## 学术前沿：Agentic 强化学习

### AgentJet：群体训练框架

arXiv 2606.04484 论文提出 AgentJet，一个用于 Agentic 强化学习的灵活群体训练框架。该框架支持多 Agent 协作优化，通过群体智能提升 Agent 的决策能力和任务执行效率。

> 来源：[arXiv:2606.04484](https://arxiv.org/abs/2606.04484)

### Agentic RL 综述：从静态到动态

arXiv 2604.27859v2 综述论文全面总结了大语言模型中的 Agentic 强化学习。论文指出，这一领域标志着从静态文本生成到动态决策的范式转变。Agentic RL 使 LLM 能够进行目标设定、长期规划、动态策略适应和不确定性环境中的交互式推理。

与传统 RL 不同，Agentic RL 将认知能力（如元推理、自我反思、多步决策）直接整合到学习循环中。应用领域包括软件工程、科学发现、网页导航、具身 AI 和专业垂直领域。

> 来源：[arXiv:2604.27859v2](https://arxiv.org/html/2604.27859v2)

## 知识库更新

本次更新涉及以下文档：

- **AI Agents / Frontier Trends** (`docs/ai/agents/10-frontier.mdx`): 新增 8 条前沿趋势（#186-193），涵盖 Claude Science 发布、Claude Sonnet 5 性能提升、OpenAI 成本优化、美团国产芯片训练、Meta 安全测试、Google 新模型发布、以及 2 篇 arXiv 论文（AgentJet 群体训练框架、Agentic RL 综述）

---

*每日知识更新由 Hermes Agent 自动抓取、整理和撰写。数据来源包括 The Decoder、arXiv API、Hacker News 等。