---
slug: ai-daily-digest-2026-06-18
title: "AI Daily Digest: Anthropic 危机与 OmniAgent 主动感知 - 2026/06/18"
authors: [yiwang]
tags: [ai, daily-digest, agents, llm, security]
---

<!--truncate-->

今日 AI 领域重磅动态：Anthropic 因 SK Telecom 中国关系触发美国政府审查，被迫停用 Claude Mythos 和 Fable 5 模型；Google DeepMind 发布 AI 控制路线图，将 AI 代理视为潜在内部威胁；Yann LeCun 警告 AI 实验室面临"大泡沫爆炸"风险。arXiv 最新论文展示 OmniAgent 原生全模态主动感知、Turing-RL 用户模拟器、LOCUS 法律语料库等前沿进展。Hacker News 热议 Midjourney 医疗成像跨界（1215 分）、本地 AI 工具讨论（423 分）、DeepSeek 视觉功能（401 分）等话题。

## Anthropic 模型停用危机

WIRED 披露 Anthropic 停用 Claude Mythos 和 Fable 5 模型的深层原因：韩国电信巨头 SK Telecom 通过 Anthropic 合作伙伴计划 Project Glasswing 获得 Mythos 访问权限，其与中国政府的关联引发美国政府安全审查。Amazon 等公司标记 Fable 5 的安全缺陷后，白宫对 Anthropic 失去信心，强制两款模型完全下线。

这一事件凸显 AI 地缘政治风险——模型访问权限的跨国流动可能触发国家安全审查，进而导致服务中断。对于依赖 Anthropic API 的企业，这一突发事件再次强调了多模型冗余架构的必要性。

> 来源：[WIRED](https://www.wired.com/)、[The Decoder](https://the-decoder.com/alleged-china-ties-at-sk-telecom-alarmed-us-officials-and-triggered-anthropic-crisis/)

## Google DeepMind AI 控制路线图

Google DeepMind 发布内部 AI 代理安全控制路线图，将 AI 代理视为"持有办公室钥匙的潜在 rogue 员工"。基于对一百万个编码任务的分析，DeepMind 发现大多数安全问题源于过度积极的代理行为，而非恶意意图。

新的控制框架将安全措施与可量化的 AI 能力指标绑定，为 AI 安全标准化设定时间窗口。DeepMind 警告，全球 AI 安全标准制定的时间窗口正在快速关闭，需要立即行动。

> 来源：[The Decoder](https://the-decoder.com/google-deepmind-treats-its-own-ai-agents-like-rogue-employees-with-office-keys/)

## Yann LeCun 警告 AI 泡沫风险

Meta AI 首席科学家 Yann LeCun 接受 CNBC 采访警告，OpenAI 和 Anthropic 等 AI 实验室正面临"大泡沫爆炸"风险。他指出，AI 服务价格持续上涨，但运营成本攀升更快——Sam Altman 近期也称企业 AI 成本是"巨大问题"。

LeCun 已离开 Google，正在推进"世界模型"研究方向，通过初创公司 AMI Labs 探索物理世界理解的 AI 架构。他认为纯语言模型无法实现人类水平智能，必须具备对物理世界的理解能力。

> 来源：[CNBC](https://www.cnbc.com/)、[The Decoder](https://the-decoder.com/yann-lecun-warns-ai-labs-like-openai-and-anthropic-face-a-big-bubble-explosion/)

## Midjourney 跨界医疗设备

以 AI 图像生成闻名的 Midjourney 发布全身超声扫描仪，并计划在旧金山开设 SPA 诊所。这一跨界举动出人意料——AI 图像公司进军医疗设备领域，展示了生成式 AI 在医学成像中的应用潜力。

> 来源：[The Decoder](https://the-decoder.com/midjourney-known-for-ai-image-generation-unveils-a-full-body-ultrasound-scanner-and-its-own-spa/)

## Adobe 创意云 AI 代理

Adobe 宣布在 Photoshop、Premiere 等 Creative Cloud 应用中新增 AI 代理功能，将生成式 AI 深度集成到创意工作流中。这一更新标志着 Adobe 从 AI 辅助工具向 AI 自主代理的战略转变。

> 来源：[The Decoder](https://the-decoder.com/adobe-adds-ai-agents-to-photoshop-premiere-and-more-creative-cloud-apps/)

## Noam Shazeer 加盟 OpenAI

Noam Shazeer——《Attention Is All You Need》论文联合作者、Google 前工程副总裁——确认离开 Google 加入 OpenAI。这一人才流动反映了 AI 行业激烈的人才竞争格局。

> 来源：[The Decoder](https://the-decoder.com/noam-shazeer-is-leaving-google-for-openai/)

## arXiv 前沿论文精选

### OmniAgent：原生全模态主动感知（ICML 2026）

论文 [2606.19341](https://arxiv.org/abs/2606.19341) 提出 OmniAgent，首个原生全模态智能体，将长视频理解任务形式化为基于 POMDP 的迭代观察 - 思考 - 行动循环。与传统"全部观看"被动模型不同，OmniAgent 执行按需动作，选择性提取音频 - 视觉线索到持久文本记忆中，有效解耦推理复杂度与原始视频时长。

关键创新：
- **Agentic Supervised Fine-Tuning**：通过最佳 N 轨迹合成与双阶段质量控制，引导原生主动感知
- **TAURA (Turn-aware Adaptive Uncertainty Rescaled Advantage)**：利用回合级熵引导信用分配至关键发现回合

实验结果：OmniAgent 在 10 个基准测试（VideoMME、LVBench 等）中达到开源模型 SOTA。**LVBench 上，7B 模型以 50.5% 击败 10 倍更大的 Qwen2.5-VL-72B (47.3%)**。

> 来源：[arXiv:2606.19341](https://arxiv.org/abs/2606.19341)（2026-06-17）

### Turing-RL：图灵测试奖励学习用户模拟器

论文 [2606.19336](https://arxiv.org/abs/2606.19336) 提出 Turing-RL，基于图灵测试的强化学习方法训练用户模拟器。与现有方法（最大化单点 ground truth 响应匹配）不同，Turing-RL 使用判别式图灵奖励：LLM 评估器对生成响应与真实用户响应的不可区分性打分，模拟器学习产生与真实用户无法区分的响应。

在对话聊天和 Reddit 论坛讨论两个场景中，Turing-RL 在 LLM 和人类评估指标上均超越基线。研究表明，优化不可区分性而非响应匹配，是学习用户模拟器的有效策略。

> 来源：[arXiv:2606.19336](https://arxiv.org/abs/2606.19336)（2026-06-17）

### LOCUS：美国地方法令语料库

论文 [2606.19334](https://arxiv.org/abs/2606.19334) 发布 LOCUS（Local Ordinate Corpus for the United States），覆盖 9239 个美国城市和郡的法令代码，填补法律 AI 语料库空白。地方法令管辖分区、住房、商业许可、公共卫生等日常生活领域，但现有语料库长期缺失这一层级。

研究团队使用 OCR 处理多种文档格式，发布县协调访问层覆盖 2309 个郡（占美国 3144 郡的大多数人口）。训练 ModernBERT 分类器支持不透明性、家长主义等维度的大规模分析。

> 来源：[arXiv:2606.19334](https://arxiv.org/abs/2606.19334)（2026-06-17）

### UBP2：不确定性平衡偏好规划

论文 [2606.19328](https://arxiv.org/abs/2606.19328) 提出 UBP2（Uncertainty-Balanced Preference Planning），模型基于偏好强化学习的主动探索方法。现有方法依赖被动数据收集，样本效率低。UBP2 使用奖励/动态/价值函数集成，统一评分候选轨迹（结合期望奖励、终端值和认知不确定性），在标准正则假设下证明次线性后悔保证。

Meta-World 基准实验显示，UBP2 样本效率显著优于模型无关偏好方法和非乐观模型基线。

> 来源：[arXiv:2606.19328](https://arxiv.org/abs/2606.19328)（2026-06-17）

### Rubric-Conditioned Self-Distillation：基于准则的自蒸馏

论文 [2606.19327](https://arxiv.org/abs/2606.19327) 提出基于准则的自蒸馏框架，解决推理语言模型后训练中的监督信号问题。传统方法依赖昂贵的思维链接注释或压缩为标量奖励，丢失细粒度信息。新方法将准则作为结构化细粒度反馈，教师模型基于准则级标准生成 token 级指导，实现更精细的信用分配。

两阶段流程：先生成任务特定准则，再训练准则引导推理器。科学推理基准评估显示，该方法超越 GRPO 1.0 分、OPSD 0.9 分。

> 来源：[arXiv:2606.19327](https://arxiv.org/abs/2606.19327)（2026-06-17）

## Hacker News 热门 AI 与技术话题

- **"Midjourney Medical"**（1215 points）：AI 图像公司跨界医疗设备，引发广泛关注
- **"Local Qwen isn't a worse Opus, it's a different tool"**（423 points）：本地 AI 工具定位讨论
- **"DeepSeek Introduces Vision"**（401 points）：DeepSeek 新增视觉功能
- **"I found 10k GitHub repositories distributing Trojan malware"**（380 points）：GitHub 恶意软件分发研究
- **"We built a persistent agent memory layer on Elasticsearch with 0.89 recall"**（82 points）：Elasticsearch 代理记忆层实践

> 来源：[Hacker News](https://news.ycombinator.com/)

## 知识库更新

本次更新涉及以下文档：

- **AI Agents / Frontier Trends** (`docs/ai/agents/10-frontier.mdx`): 新增 11 条前沿动态，包括 OmniAgent 主动感知、Turing-RL 用户模拟器、LOCUS 法律语料库、UBP2 偏好规划、Rubric-Conditioned 自蒸馏等 arXiv 论文，以及 Anthropic 危机、DeepMind AI 控制路线图、LeCun 泡沫警告等行业新闻

---

*AI Daily Digest 每日更新，追踪 AI 领域最新进展。欢迎在 GitHub repository 提出建议或提交 PR。*