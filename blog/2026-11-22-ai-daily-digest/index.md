---
slug: ai-daily-digest-2026-11-22
title: "AI Daily Digest: OpenAI 公开预训练困惑度曲线、OpenRouter 下线三家推理提供商、Cursor 或弃用中国开源权重、Beam 501B MoE 技术报告 - 2026/11/22"
authors: [yiwang]
tags: [ai, daily-digest, openai, perplexity, openrouter, zdr, cursor, kimi, beam, arxiv]
---

<!--truncate-->

今天的主题词是**透明**。OpenAI 首次公开内部预训练困惑度曲线，并呼吁全行业把它作为共享进度与安全指标；OpenRouter 公开下线三家数据政策失守的推理提供商；美国众议院委员会的报告则把 Cursor 旗舰模型的底座——中国开源权重——推到了台前。当「模型背后是什么」开始被要求公开回答，行业信任的验证方式正在改变。

## OpenAI 公开预训练困惑度：一个指标统一行业进度

OpenAI 发布文章 **Perplexity and Intelligence**（HN 267 分，179 评论），首次公开了从 GPT-3.5 至今的内部预训练困惑度曲线，并主张把 **perplexity（困惑度）/交叉熵损失** 确立为跨厂商可比的共享指标，用于校准行业进度乃至安全标准。

几个关键数据点：在其内部代码库评测集上，GPT-3.5 的对数损失约 **0.99**（催生了初代 ChatGPT 的流利对话），GPT-4 约 **0.91**（有效利用链式推理的前提），当前模型已降到 **0.8 以下**——伴随而来的是网络安全与数学等领域能力的涌现。OpenAI 的论点是：下游 benchmark 迭代太快、饱和太快（GPT-4 时代已大面积饱和），而预训练损失数十年保持稳定，多个重大能力跃迁大致对应特定损失阈值。作者同时承认公开内部数据给了竞争对手一面镜子，但认为建立行业共享安全度量更为紧迫；局限也很明确——perplexity 的含义依赖训练数据分布，跨厂商比较必须约定共同评测集。

对工程实践的启示：当我们评估「基础模型换代值不值得升级」时，预训练损失是比榜单分数更接近「底料」的信号——后训练与 elicitation 可以大幅改变表现，但改变不了智能底层的压缩效率。

> 来源：[Perplexity and Intelligence](https://openai.com/index/perplexity-and-intelligence/)（OpenAI，2026-11-22）

## OpenRouter 下线三家推理提供商、撤销 125 个 ZDR 端点

安全研究人员本周披露：部分推理提供商存在**数据被泄露或数据政策未被实际执行**的证据。OpenRouter 调查后采取行动：**下线三家提供商**、**撤销 125 个端点的零数据留存（ZDR）资格**、通知所有可能受影响的客户。已公开事故的提供商包括 Novita（MiniMax 请求隐私通知）、Phala（11 月初步事件报告）、Together（2026 年 6-7 月请求的 prompt 泄漏事件）。OpenRouter 强调自身未被入侵，问题在上游提供商侧，并正在把研究者的探测方法纳入常态化检查（HN 264 分，88 评论）。

这件事对每个在多提供商路由架构上跑生产流量的团队都是提醒：**「零数据留存」是运行时属性，不是合同条款**。标记 ZDR 的端点仍可能把请求转发给第三方——信任链的每一跳（router → provider → 上游转发）都需要独立验证。知识库的 AgentOps 安全笔记（`docs/ai/agentops-security`）已更新本案例的完整分析。

> 来源：[Data Processing Incidents on Inference Providers](https://openrouter.ai/blog/announcements/data-processing-incidents-on-inference-providers/)（OpenRouter，2026-11-22）

## 国会报告：Cursor 或逐步淘汰中国开源权重

美国众议院国土安全委员会与中共问题特设委员会发布联合报告（11 月 20 日，CNBC 报道）：Cursor 母公司 Anysphere 已告知国会，将「探索逐步淘汰 PRC 开发的开源权重模型」。尴尬之处在于产品本身——Cursor 旗舰编码模型 **Composer 2 正是构建在月之暗面的 Kimi K2.5 之上**（这一事实最初还是外部开发者逆向识别出来的），此后 Cursor 用自己的数据做了强化学习。报告同时点名 Airbnb 用阿里 Qwen 做客服、DoorDash 用 Kimi 处理内部任务，并直言美国缺乏「在价格与性能上满足市场需求」的开源替代：中国开源模型每百万 token 约 **$1.15-$4.95**，西方替代品 **$30-$35**，强制替换意味着 10-20 倍的单 token 成本。委员会把过渡规模类比为电信业移除华为/中兴，并建议整合公共算力、共享模型评测基础设施。

另一个背景变量：SpaceX 于今年 8 月以约 **$600 亿**隐含估值完成对 Cursor 的收购。开源权重作为「地缘资产」被审查，可能成为 2027 年 AI 供应链政策的主线之一。

> 来源：[AI Weekly](https://aiweekly.co/alerts/cursor-tells-house-it-may-drop-chinese-open-weight-models)、[MLQ.ai](https://mlq.ai/news/cursor-tells-lawmakers-it-is-considering-phasing-out-chinese-ai-models)（2026-11-21/22）

## Anthropic 数据中心：2028 年 87% 天然气 + 11% 煤

HN 当日最高热帖之一（676 分，733 评论）：Better Data Center Project 的分析估算，到 **2028 年 Anthropic 的数据中心电力约 87% 来自天然气、11% 来自煤**。这组数字直指 AI 行业「清洁能源承诺」与自建电厂（Behind-the-Meter）现实之间的落差——当训练与推理需求增速超过电网清洁化速度，自备电厂的燃料结构就是最诚实的答案。AI 的能耗核算正在从企业 CSR 报告走向可审计的电力合同层面。

> 来源：[How AI is powered: a breakdown of BYOP and grid power](https://betterdatacenterproject.com/2026/11/16/how-ai-is-powered-a-breakdown-of-byop-and-grid-power/)（2026-11-16）

## arXiv 精选

**[Beam Model Technical Report](https://arxiv.org/abs/2611.26358)**（11-19）：新的稀疏 MoE 模型，**501.3B 总参、23.4B 激活**，专为编码/推理/agentic 工作负载优化，推理计算较同级别模型少 3-4 倍。23.8T token 预训练 + 两阶段 midtraining 达成 **1M token 上下文**；后训练在 **10.5K 张 GB300 上跑了 4 周全异步 RL、超 1 亿次 rollout**——作者称这是开源实验室迄今最大规模的 RL 运行之一，且能力随 RL 算力持续提升未见平台期。配 1.93B 参数的 DFlash 2 投机解码草稿模型与 FP8/NVFP4 量化。安全侧：有害请求拒绝/转向率 88.9%、无害请求合规率 81.5%。

**[Twice-Told Critiques](https://arxiv.org/abs/2611.26286)**（11-19）：量化 LLM 时代同行评审的同质化——ICLR 评审的 claim 级重叠率从 **2026 年的 12.0% 升至 2027 年的 21.3%**。当评审开始用模型辅助写作，「多个独立读者发现不同问题」这一同行评审的核心前提正在被侵蚀。

**[MemFolder](https://arxiv.org/abs/2611.26427)**（11-19）：长程 agent 的外部记忆会随交互不断膨胀，存储、检索与生成的成本被两个耦合因素约束。MemFolder 提出**结构引导的记忆折叠**，把长期记忆按结构折叠以降低检索与响应开销——与本周知识库 harness-engineering 笔记中的 agent 记忆管理话题直接相关。

## 快讯

- OpenAI 语音模型 **GPT-Live-1.1** 上线 API，并引入待机计费：空闲 $0.02/分钟 vs 激活推理 $0.05/分钟，空闲超时可设 5-60 秒——为实时语音 agent 降低常驻成本。
- Liquid AI 发布 **d1.2** 决策模型系列；Elorian 发布视觉推理模型 Glimpse（$0.60/$3 定价）。
- Show HN 有趣项目：[worker755](https://github.com/gulivan/worker755)——让你扮演 LLM 的 subagent 的游戏（188 分），亲身体验被 orchestrator 派活的滋味。
- Simon Willison 介绍 **Muru**：mod_wsgi 作者做的 AI 辅助 Rust 服务器，用于直接跑 Python 应用（HN 58 分）。

---

今天的三个故事共享一个结构：**承诺需要验证，验证需要透明**。Perplexity 曲线是对「模型有多聪明」的验证，ZDR 审计是对「数据没被留下」的验证，国会报告是对「你的模型底座是什么」的验证。明天见。
