---
slug: ai-daily-digest-2026-07-20
title: "AI Daily Digest: 欧盟强制 Google 开放 Android、Gemini 3.5 Pro 三度延期、Oracle 裁员 3 万人押注 Stargate - 2026/07/20"
authors: [yiwang]
tags: [ai, daily-digest, regulation, google, oracle, microsoft, sap, anthropic, open-weight]
---

<!--truncate-->

今日 AI 圈围绕"监管重塑分发格局"和"AI 基础设施的代价"两条主线展开：欧盟依据《数字市场法》做出历史性裁定，强制 Google 向竞争对手开放 Android 分发渠道和搜索数据；Gemini 3.5 Pro 第三次延期暴露 Google 在前沿模型竞赛中掉队；Oracle 以 3 万人的代价为 5000 亿美元的 Stargate 基础设施买单。与此同时，微软的 Project Perception 展示了多模型路由如何让 AI 安全扫描在经济上可行，SAP 以 10 亿欧元押注表格基础模型这一被忽视的前沿，而 DeepSeek V4 和 Kimi K3 的开放权重发布倒计时正在重塑整个行业的定价权。

## 欧盟强制 Google 开放 Android 和共享搜索数据

欧盟委员会依据《数字市场法》（DMA）对 Google 做出了今年最具影响力的 AI 监管裁定。根据该约束性决定，Google 必须：

- **向第三方 AI 助手开放 Android**：符合条件的竞争对手助手获得跨 11 个 Android 功能组的语音激活和跨应用能力，需通过认证并获得用户同意。Android 互操作性须在 2027 年 7 月前实现。
- **共享搜索数据**：Google 须以公平、合理和非歧视性（FRAND）条款向竞争对手（包括 AI 开发者）提供匿名化的搜索排名、查询、点击和浏览数据。搜索数据共享自 2027 年 1 月开始。

这一裁定直击 Google 两大护城河。第一是分发优势：Gemini 之所以能在移动端占据位置，是因为它被预装在 20 亿台 Android 设备上。允许竞争对手以语音唤醒并跨应用工作，等于拆除了这个结构性壁垒。第二是数据优势：竞争对手可以获得过去 20 年只有 Google 才能积累的搜索行为信号——这对训练和排序 AI 系统至关重要。

Google 全球事务总裁 Kent Walker 反驳称，该决定可能破坏数百万欧洲人的隐私和安全保障。但时机极为微妙：Google 本月刚经历旗舰模型延期，正是最脆弱的时刻。对所有非 Google 的 AI 公司而言，这是本月最好的消息。

> 来源：[Computerworld](https://www.computerworld.com/article/4198420/google-must-open-android-to-rival-ai-agents-eu-orders.html)；[US News](https://www.usnews.com/news/technology/articles/2026-07-16/eu-forces-google-to-share-search-data-and-open-android-to-rival-ai-companies)

## Gemini 3.5 Pro 第三次延期，Google 考虑过渡版 3.6 Flash

Gemini 3.5 Pro 再次错过 7 月 17 日的发布目标，这是该旗舰模型的第三次延期。据报道，模型在编码和复杂推理测试中未达标——此前 Google 已在 6 月废弃原始基座模型并重启预训练。

第三次延期改变了问题的性质。一次延期是工程纪律的体现，三次延期则暗示存在结构性问题，无论问题出在训练运行还是 Google 为自己设定的评估标准。Google 目前正探索发布过渡版 Gemini 3.6 Flash，以在 Pro 模型修复期间向市场投放产品。但发布一个 Flash 级别的模型来填补 Pro 级别的空白，等于默认承认旗舰模型并不接近完成。

Google 仍未发布官方模型卡、定价或基准数据。Alphabet 股价因延期报道下跌约 4%。竞争对手的成本每天都在累积——本季度评估前沿模型的企业正在 GPT-5.6、Claude、Grok 4.5 和 Kimi K3 之间签约，Gemini 缺席的每一周，合同都在别处签订。

> 来源：[Build Fast with AI](https://www.buildfastwithai.com/blogs/ai-news-today-july-20-2026-16-biggest-stories)（2026-07-20）

## Oracle 裁员 30,000 人，为 Stargate 释放百亿美元现金流

Oracle 宣布裁员多达 30,000 人，约占全球员工 18%，是公司历史上最大规模的裁员。预计每年释放 80-100 亿美元现金流用于 AI 基础设施建设。

裁员的内部分配比标题数字更能说明问题：Oracle Health、云基础设施和咨询部门受创最重，而 Stargate 数据中心团队不仅被保留，还在加速招聘。这是一家公司在逐部门地将自己改造为 AI 基础设施提供商，用被降优先级业务的薪资来资助转型。

Oracle 的 Stargate 项目是与 OpenAI 和 SoftBank 合作的 5000 亿美元基础设施计划，其中包含与 OpenAI 签订的 5 年 3000 亿美元云合同，覆盖 4.5GW 的数据中心容量，预计从 2025 年起每年产生约 300 亿美元收入。

这一案例赤裸裸地揭示了 AI 基础设施建设的真实成本：用于千兆瓦级基础设施的资本不是凭空出现的，而是从现有业务线、员工薪资和 AI 成为优先级之前资助公司运营的业务中提取的。Oracle 只是把这一切做得足够公开，以至于可以计算。

> 来源：[Capacity](https://capacityglobal.com/news/oracle-cuts-up-to-30000-jobs-to-fund-ai-data-centre-push/)；[Build Fast with AI](https://www.buildfastwithai.com/blogs/ai-news-today-july-20-2026-16-biggest-stories)

## 微软 Project Perception：多模型路由让 AI 安全扫描经济可行

微软正筹备 Project Perception，一个 AI 网络安全平台，集成了微软、OpenAI 和 Anthropic 三家公司的模型。该系统的核心创新在于编排层架构——它不会把所有任务都发送给最强大也最昂贵的模型，而是根据任务复杂度智能路由：

- 廉价模型处理清单检查、日志解析和常见漏洞类型的初步分类
- 前沿模型仅在需要推理复杂漏洞链或编写涉及生产环境的修复方案时才被调用

这种路由架构使持续的、始终在线的漏洞扫描在经济上变得可行，而不是一个没人批准的预算项目。Project Perception 定位为 Anthropic Mythos 级安全产品的低成本替代品。值得注意的是，微软在产品中使用了 Anthropic 的模型来与 Anthropic 竞争——这是 2026 年的典型场景。

Anthropic 的 Project Glasswing 已扩展到 15 个国家的 150 个组织，微软则以多模型路由和庞大的企业安装基础作为回应。微软 7 月的 Patch Tuesday 在 AI 辅助下修复了创纪录的 570 个漏洞，AI 安全收购从去年的 10 起增至 2026 年上半年的 29 起。

> 来源：[TechRepublic](https://www.techrepublic.com/article/news-microsoft-project-perception-ai-security-tool/)

## SAP 以逾 10 亿欧元收购 Prior Labs，押注表格基础模型

SAP 完成了对 Prior Labs 的收购，并承诺 4 年内投资超过 10 亿欧元，将这家弗莱堡的初创公司建设为全球领先的前沿 AI 实验室。Prior Labs 将继续作为独立实体运营。

Prior Labs 18 个月前由 Frank Hutter、Noah Hollmann 和 Sauraj Gambhir 创立，专注于表格基础模型（Tabular Foundation Models）。其 TabPFN 模型系列发表于 Nature，在数百项独立学术研究中确立了表格基准的 SOTA。

这笔交易背后的逻辑出人意料地逆向。SAP 认为，企业 AI 中最大的未开发机会不是大语言模型，而是为业务实际运行的结构化数据——表格、账本、库存和交易记录——专门构建的 AI。语言模型擅长处理文档和对话，但处理电子表格的能力很差。而 SAP 坐拥比几乎任何公司都多的企业结构化数据。

这也是一个有意义的欧洲 AI 故事。一个成立 18 个月、有一篇 Nature 论文的德国初创公司，被以 10 亿欧元规模投资建设为前沿实验室——这正是欧洲技术政策十年来试图制造的成果。在通常被认为是在监管而非建设的欧洲大陆，这是一个令人耳目一新的逆向叙事。

> 来源：[SAP News](https://news.sap.com/2026/07/sap-completes-prior-labs-acquisition/)；[Tech.eu](https://tech.eu/2026/07/17/sap-acquires-prior-labs-just-18-months-after-launch-in-eur1b-deal/)

## Anthropic Fable 5 免费窗口到期，Opus 5 或将来临

Claude Fable 5 的免费访问窗口于 7 月 19 日太平洋时间 23:59 到期。Anthropic 现在面临三选一：发布 Opus 5、第四次延长免费访问，或转向基于积分的模式。

时机对 Anthropic 来说相当尴尬。在 Kimi K3 刚刚登顶编码排行榜并承诺 7 月 27 日免费发布权重的同一周，结束旗舰模型的免费访问——这个对比很难管理。但 Anthropic 本周的整体表现是所有实验室中最好的：机密 IPO 申请、最高安全评级、以及据报道 Karpathy 的加盟。

分析认为，Anthropic 最可能利用这个时机发布 Opus 5 公告，从而以自己的条件重置对话。无论 Anthropic 接下来发布什么，都会被解读为对 Kimi K3 的回应——无论公平与否——而这正是开放权重攻势旨在制造的压力。

> 来源：[The Decoder](https://the-decoder.com/anthropic-extends-free-fable-5-access-for-subscribers-as-openais-gpt-5-6-sol-heats-up-the-pricing-war)

## 开放权重倒计时：DeepSeek V4（7 月 24）+ Kimi K3 权重（7 月 27）

7 月最后一周的两个日期现在锚定了整个行业的注意力：

- **7 月 24 日**：DeepSeek V4 稳定版发布。约 0.44 美元/百万输出 token 的定价已是行业衡量的价格下限，稳定版消除了谨慎企业将生产工作负载迁移到该模型的最后一个技术异议。
- **7 月 27 日**：Kimi K3 开放权重免费发布。一个刚登顶编码排行榜的模型将进入任何人的手中，在自有基础设施上运行，无需按 token 付费。

两者合在一起，代表了行业迄今为止最集中的开放权重发布窗口。对于在前沿 API 调用上花费大量资金的高频编码或 Agent 工作负载，7 月最后一周是进行严肃评估的时刻。实际建议是：用你的真实工作负载对比稳定版 V4、K3 Max 和当前闭源模型，衡量质量和总成本（包括自托管的基础设施），让数据而非排行榜做决定。

> 来源：[Build Fast with AI](https://www.buildfastwithai.com/blogs/ai-news-today-july-20-2026-16-biggest-stories)

## 学术前沿：Agent 与推理能力

### 从预训练到后训练的推理理解（arXiv:2607.16097）

系统研究大语言模型推理能力在预训练和后训练阶段的发展轨迹，揭示不同训练阶段对推理能力的差异化贡献。

### Muon 优化器何时助力 Agent 强化学习（arXiv:2607.16169）

研究 Muon 优化器在 Agent 强化学习场景下的效果，分析其适用条件和性能边界。

### 多 Agent 系统何时有用——信息瓶颈视角（arXiv:2607.16133）

从信息瓶颈理论视角分析多 Agent 系统的效能条件，为"何时采用多 Agent 架构"提供理论指导。

### ToolVerse：解锁大规模环境和长周期任务（arXiv:2607.15660）

提出 ToolVerse，为 Agent 强化学习提供大规模环境支持和长周期任务评测能力，突破现有 RL 训练环境的规模限制。

### 编码 Agent 与 ARC-AGI-3（arXiv:2607.15439）

探讨编码 Agent 解决 ARC-AGI-3 抽象推理基准所需的关键能力：可执行世界模型、问题简化和形式化验证。

> 来源：[arXiv:2607.16097](https://arxiv.org/abs/2607.16097)；[arXiv:2607.16169](https://arxiv.org/abs/2607.16169)；[arXiv:2607.16133](https://arxiv.org/abs/2607.16133)；[arXiv:2607.15660](https://arxiv.org/abs/2607.15660)；[arXiv:2607.15439](https://arxiv.org/abs/2607.15439)（2026-07）

## 知识库更新

本次更新涉及以下文档：

- **AI Agents / Frontier** (`docs/ai/agents/10-frontier.mdx`): 新增 17 条前沿趋势（#326-342），涵盖欧盟 DMA 裁定、Gemini 3.5 Pro 延期、Oracle 裁员与 Stargate、微软 Project Perception、SAP 收购 Prior Labs、Anthropic Fable 5 到期、AI 检测器失败率、RadLE 2.0 放射学基准、WAIC 2026 闭幕与 WAICO 成立，以及 7 篇 Agent 与推理相关 arXiv 论文
