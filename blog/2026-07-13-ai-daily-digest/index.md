---
slug: ai-daily-digest-2026-07-13
title: "AI Daily Digest: 图灵奖得主创办 Oak Lab、诺奖得主联署 AI 经济警告、纳德拉批评蒸馏禁令 - 2026/07/13"
authors: [yiwang]
tags: [ai, daily-digest, reinforcement-learning, agents, open-source, economics]
---

<!--truncate-->

今日 AI 领域三件大事交汇：2024 年图灵奖得主 Richard Sutton 创办 Oak Lab，押注强化学习路线构建能持续学习的 AI Agent；16 位诺贝尔经济学奖得主联合 200 余位研究者签署声明警告 AI 经济冲击窗口正在关闭；微软 CEO 纳德拉公开批评 AI 实验室禁止蒸馏的虚伪立场。与此同时，德国发布开源 Soofi S 30B 模型，Anthropic 为 Claude Code 添加内置浏览器，arXiv 新增多篇 Agent 记忆与推理论文。

## 图灵奖得主 Rich Sutton 创办 Oak Lab，押注持续学习 Agent

2024 年图灵奖得主、强化学习之父 Richard Sutton 在多伦多联合 Khurram Javed 创办 Oak Lab。二人此前均在 John Carmack 的 AI 公司 Keen Technologies 工作。Sutton 直言当前深度学习方法"薄弱且低效"，需要"根本性新思路而非修补"才能为 AI 的更宏大目标提供坚实基础。

Sutton 的核心主张是：生成式 AI 擅长模仿但无法评估自身输出，因此无法实现真正的发现。Oak Lab 的目标是构建能从环境中持续学习、构建内部世界模型、并自主处理变异、评估和选择的 AI Agent。这延续了他在 Keen Technologies 的信念：AI 应在运行过程中从经验学习，而非在静态数据集上一次性训练。长期愿景是"万亿参数、实时学习规划、20 瓦能耗"的 Agent——对标人脑的能效比。

这一路线与当前主流的大规模预训练范式形成鲜明对比。Sutton 认为静态数据集训练的模型无法适应开放世界的不确定性，只有在线持续学习才能通向通用人工智能。Oak Lab 的成立标志着强化学习学派在产业层面的重要回归。

> 来源：[The Decoder](https://the-decoder.com/turing-award-winner-rich-sutton-founds-oak-lab-to-build-ai-agents-that-learn-on-their-own/)（2026-07-13）

## 16 位诺奖得主联署声明：AI 经济冲击窗口正在关闭

由斯坦福数字经济实验室协调的"We Must Act Now"联合声明获得超过 200 位经济学家和 AI 研究者签署，包括 Daron Acemoglu、Joseph Stiglitz、Paul Krugman、Ben Bernanke 等 16 位诺贝尔经济学奖得主。Google 的 Jeff Dean、Anthropic 联合创始人 Jack Clark、OpenAI 的 Noam Brown 和 Sarah Friar 等 AI 行业代表也签署了声明。

声明的核心论点有三：AI 可能在未来十年变得"极其强大"；这可能引发"比工业革命更大但时间跨度远短"的变革；经济学家、政策制定者和技术领袖需要立即行动建立激励、护栏和制度。声明明确警告"大规模失业"风险，同时也看到"生活水平大幅提升"的潜力。

值得注意的是，声明全程使用条件式语言——AI"可能"变得更强，"可能"引发变革——且未提出具体政策措施。METR 研究组织的 Tom Cunningham 直言："我们在雾中驾驶，极难预见接下来会发生什么。"一些 AI CEO 甚至在签署警告后开始撤回自身言论。目前的研究尚未发现 AI 对劳动力市场产生显著影响的实证证据。

> 来源：[The Decoder](https://the-decoder.com/nobel-laureates-and-ai-leaders-warn-the-window-to-prepare-for-ais-economic-impact-is-closing-fast/)（2026-07-13）

## 微软 CEO 纳德拉批评蒸馏禁令，提出"反向信息悖论"

微软 CEO Satya Nadella 在个人博客上公开批评 OpenAI 和 Anthropic 等 AI 实验室禁止模型蒸馏的做法。蒸馏是指较小模型从较大模型的输出中学习的过程，被 OpenAI 和 Anthropic 在服务条款中明令禁止，主要针对中国 AI 公司。

纳德拉称这种立场"讽刺"：这些厂商以公平使用为由训练公开数据，却禁止他人从其模型输出中学习，同时还保留从客户交互数据中学习的权利。他提出"反向信息悖论"概念：企业在消费 AI 智能的同时也在创造智能——使用 AI 时的更正、评分和交互模式揭示了企业内部知识，AI 厂商可从中学习并构建竞争产品。结果是经济价值向基础设施运营商集中，而非向真正创造知识的企业集中。

纳德拉的论点并非纯粹利他——微软恰好拥有帮助企业控制自身学习循环的基础设施。但这一批评揭示了 AI 行业的核心张力：模型提供商在数据输入端的开放立场与输出端的封闭立场之间存在系统性矛盾。

> 来源：[The Decoder](https://the-decoder.com/nadella-calls-out-ai-labs-like-openai-and-anthropic-for-banning-distillation-while-training-on-everyone-elses-data)（2026-07-13）

## 德国发布开源 Soofi S 30B 模型，欧洲 AI 主权新进展

德国 AI 联邦协会（KI Bundesverband）协调的研究联盟发布 Soofi S 30B-A3B，这是一个完全在德国电信慕尼黑工业 AI 云上训练的开源语言模型。模型采用混合架构，总参数量 31.6B 但每 token 仅激活 3.2B，保持长输入下的吞吐量稳定。

在德语、英语和编程基准测试中，Soofi S 超越了 OLMo 3 32B 和 Apertus 70B 等此前的全开源领导者。模型训练数据刻意增加德语比重，定位介于广泛多语言的欧洲主权项目（如 EuroLLM、Teuken）和国际开源权重模型之间。联盟正在寻找行业合作伙伴，在技术文档、代码生成和 Agent 系统场景中测试模型。

这是欧洲 AI 主权战略的具体落地：训练基础设施、数据策略和模型权重全部在欧洲范围内完成，减少对美国和中国 AI 生态的依赖。

> 来源：[The Decoder](https://the-decoder.com/german-ai-consortium-releases-soofi-s-an-open-30b-model-that-tops-benchmarks-in-both-english-and-german/)（2026-07-13）

## Claude Code 添加内置浏览器，Agent 自主浏览成为标配

Anthropic 于 7 月 10 日为 Claude Code 桌面应用添加沙盒化内置浏览器（快捷键 Cmd+Shift+B），AI 编码助手现在可以直接在应用内打开、导航和交互外部网站，无需切换到独立浏览器窗口。

浏览器支持文档站点、Issue 追踪器等资源，可完成阅读、点击和输入操作。安全方面，所有外部站点的写操作受安全分类器审查，购买和账户创建等敏感操作需用户明确批准。浏览器运行在干净配置文件上，不接触用户保存的登录状态。

这一发布与 OpenAI 同期关闭 Atlas 浏览器形成鲜明对比。OpenAI 将 Atlas 功能并入 Chrome 扩展和桌面端 ChatGPT，而 Anthropic 选择在编码工具中原生集成浏览器能力。Agent 自主浏览正在从实验性功能转变为编码工具的标配——当 Agent 能直接查阅文档和 Issue 时，减少了人工复制粘贴上下文的摩擦。

> 来源：[The Decoder](https://the-decoder.com/claude-code-now-has-a-built-in-browser-that-lets-the-ai-read-click-and-type-on-external-websites/)（2026-07-13）

## 学术前沿：Agent 记忆与推理

### 共享选择性持久记忆架构

arXiv 2607.09493 提出面向 Agent LLM 系统的共享选择性持久记忆架构。核心问题是：多轮工具使用的 Agent 每次会话都从零开始，丢弃了此前积累的配置选择、领域约束、数据模式和工具使用模式。简单持久化全部对话历史既浪费 token 又因无关上下文降低生成质量。

该架构识别并保留四类可复用上下文（任务规范、数据模式、工具配置、输出约束），丢弃会话特定推理轨迹。关键创新在于记忆是"共享的"：封装选择性记忆的工作区可跨用户传输，通过基于角色的访问控制实现协作复用。在三组企业部署场景中，任务完成率达 96%（无记忆 79%、全历史 71%），零 token 数据刷新机制实现 14 倍任务时间缩减，摘要驱动生成将单次调用 token 成本降低 97 倍。

> 来源：[arXiv:2607.09493](https://arxiv.org/abs/2607.09493)（2026-07）

### Agora：拍卖式 Agent 任务分配

arXiv 2607.09600 提出基于拍卖机制的 LLM Agent 任务分配框架 Agora。该框架将推理任务拆分为单元，由多个 Agent 通过竞价机制竞争任务分配权，通过校准的估值机制确保任务分配给最合适的 Agent。这种方法将经济学中的拍卖理论引入多 Agent 系统，增强推理能力和资源效率。

> 来源：[arXiv:2607.09600](https://arxiv.org/abs/2607.09600)（2026-07）

### TrustX Agent 风险分级框架

arXiv 2607.09586 提出 Agent 风险分类框架（ARC），为企业在部署内部创建的 Agent AI 系统前提供风险分层工具。该框架对 Agent 系统按风险等级分类，帮助企业系统化评估和管理 Agent 部署中的安全、合规和运营风险。

> 来源：[arXiv:2607.09586](https://arxiv.org/abs/2607.09586)（2026-07）

## 知识库更新

本次更新涉及以下文档：

- **AI Agents / Frontier Trends** (`docs/ai/agents/10-frontier.mdx`): 新增 8 条前沿趋势（#253-260），覆盖图灵奖得主创办 Oak Lab、诺奖得主 AI 经济警告、纳德拉批评蒸馏禁令、德国开源 Soofi S 模型、Claude Code 内置浏览器、Agora 拍卖式 Agent 分配、共享选择性持久记忆架构、TrustX Agent 风险分级框架

---

*每日知识更新，追踪 AI 领域最新进展。欢迎关注 AiDIY 知识库持续学习。*
