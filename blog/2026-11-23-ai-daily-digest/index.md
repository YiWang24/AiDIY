---
slug: ai-daily-digest-2026-11-23
title: "AI Daily Digest: Nvidia 董事会全票恢复黄仁勋 CEO 职务、智谱 GLM-5.4 首个旗舰 Loop Transformer、本地 AI 入门热帖 - 2026/11/23"
authors: [yiwang]
tags: [ai, daily-digest, nvidia, jensen-huang, glm, loop-transformer, local-ai, arxiv]
---

<!--truncate-->

今天的主题词是**回归**。Nvidia 董事会全票通过恢复黄仁勋的 CEO 职务——距他辞职仅 11 天；Z.ai 的 GLM-5.4 则让架构本身「回归」：同一组层循环执行两次，用循环深度替代参数堆叠。一个公司在找回创始人，一个行业在重访旧想法。

## Nvidia 全票恢复黄仁勋：11 天的 CEO 空缺结束

Nvidia 官方宣布（11 月 23 日）：董事会**全票通过**恢复黄仁勋担任总裁、CEO 及董事，即时生效。董事会主席 Harvey Jones 表示，在与黄仁勋进行一系列会谈后，董事会对其「坦诚与领导能力」感到满意，并在决策过程中听取了美国政府高层意见；此外董事会确认其回归不构成国家安全风险。

回顾这条时间线：11 月 11 日董事会接受辞职（11 月 12 日以 8-K 文件披露，媒体报道与个人关系及外国情报关注有关，公司未确认指控），CFO Colette Kress 出任临时 CEO，股价当日跌约 5%。随后科技行业多方游说董事会请回黄仁勋，今天上午特朗普公开呼吁其回归，数小时后董事会完成投票。市场反应剧烈：**NVDA 盘中大涨约 30%**。Kress 继续留任 CFO，Jones 留任董事长。

值得注意的是治理层面的后续：Nvidia 将成立由独立董事组成的委员会，继续调查针对黄仁勋的「外国情报行动」，同时新设**国家安全与出口管制委员会**并招聘首席合规官。一家芯片公司的 CEO 人选已经变成国家安全议题——AI 供应链的地缘化正在从政策讨论进入公司治理架构。

> 来源：[NVIDIA Board Reinstates Jensen Huang](https://nvidianews.nvidia.com/news/nvidia-board-reinstates-jensen-huang-as-president-ceo-and-board-director)（NVIDIA，2026-11-23）、[Fortune](https://fortune.com/2026/11/23/nvidia-board-votes-unanimously-to-reinstate-jensen-huang-after-deciding-he-poses-no-national-security-risk)

## GLM-5.4：智谱首个旗舰 Loop Transformer，「广义编码」开场

HN 当日热榜第二（686 分，252 评论）：Z.ai 发布 **GLM-5.4**，是其首个基于 **Loop Transformer** 架构的旗舰模型。核心思路：约 **750B 参数**的模型不增加新层，而是把 GLM-5 基座的 **28 层在一次前向中循环执行两次**，配合门控与受限的二次传递缓存——用循环深度换取推理深度，官方称智能水平可比 **2T-3T 参数**模型。

几个工程细节值得展开：

- **训练路线**：Z.ai 明确承认从零训练的循环模型在同算力预算下仍落后于层不共享的模型，所以 GLM-5.4 是在预训练好的基座上继续训练而来。循环架构目前是「增强项」而非「替代项」。
- **已知短板**：官方承认模型会陷入长「马拉松思考」循环；下一步方向是自适应计算——难的 token 动态获得更多迭代次数。
- **吞吐靠协同设计**：多遍执行会放大中间内存读写，GLM-5.4 通过内核融合、KV cache 与稀疏索引的联合设计做到闲时 **200 tokens/s**、峰值 **70-80 tokens/s**。这与昨天 OpenAI 公开 perplexity 曲线呼应：架构创新正在从「堆参数」转向「每 FLOP 榨出更多智能」。
- **产品形态**：新增视觉编码能力与 1M token 上下文，Coding Plan 周配额较 GLM-5.3 提高 50%；API 待安全评估后开放，权重计划在安全加固后开源（无日期）。**尚未发布任何第三方基准成绩**，「2T-3T 智能水平」目前是自述。

更值得琢磨的是叙事：Z.ai 把 GLM-5.4 定位为「**广义编码**」（Generalized Coding）的起点——代码成为通用任务基底，演示了模型自己配乐的 MV、用 FreeCAD 设计的六轴机械臂、完整游戏和带自定义 shader 的 3D 场景。当编码模型开始覆盖视频、CAD 与 3D，「编码智能体」的边界正在被重写。

> 来源：[Toward Generalized Coding with Our First Loop Transformer](https://z.ai/blog/glm-5.4)（Z.ai，2026-11-23）、[The Decoder](https://the-decoder.com/z-ai-follows-openai-into-loop-transformer-territory-with-its-new-750b-flagship-model)

## 本地 AI 的高热：Inkling + Qwen + Unsloth 入门指南

HN 当日第三高热帖（662 分，270 评论）：[A Beginner's Guide to Local AI with Inkling, Qwen, and Unsloth](https://gpupartner.com/)——用消费级 GPU 跑开源模型并进行微调的入门指南。在同一天，Ladybird 浏览器宣布进入 Alpha（134 分）。两条线索的共同点：**不依赖云端 API 的技术栈正在成熟**。当模型能力增速放缓、而蒸馏与量化持续进步，本地部署的性价比拐点值得每个团队重新测算。知识库的 Transformer 架构笔记已补充 Loop Transformer 的架构分析。

> 来源：[Hacker News](https://news.ycombinator.com/)（2026-11-23）

## arXiv 精选

**[MemOnce: A Scalable Memory Architecture for Large Language Models](https://arxiv.org/abs/2611.27973)**（11-20）：LLM 在长程与持续交互中需要维护可复用的记忆状态，标准架构对此力不从心。MemOnce 提出可扩展的记忆架构，让跨会话记忆成为模型状态的一部分——与本周 agent 记忆管理话题直接相关。

**[Model Carving: Training Transformers That Optimize Their Own Topology](https://arxiv.org/abs/2611.27962)**（11-20）：架构选择与训练过程历来分离，这篇工作让 Transformer 在训练中**自己优化拓扑结构**（哪些子层保留、哪些裁剪）。与 GLM-5.4 的循环思路互为镜像：前者动态决定「结构」，后者复用「结构」。

**[Speculative Decoding Is Less Speculative Than You Think](https://arxiv.org/abs/2611.27891)**（11-20）：重新分析投机解码效率的来源——不取决于表层一致率，而取决于有限草稿计算的分配方式。知识库推理笔记已更新本篇解读。

**[BioEmu2: Scalable Emulation of Biomolecular Dynamics](https://arxiv.org/abs/2611.27924)**（11-20）：结构预测之后，生成式模型开始模拟驱动生物功能的分子运动与相互作用——AI for Science 从「静态结构」走向「动态过程」。

**[Hy-MT3](https://arxiv.org/abs/2611.27673)**（11-20）：腾讯混元第三代多语言翻译模型（1.8B/7B/30B-A3B MoE），主打真实场景下的准确率与鲁棒性。

## 快讯

- Show HN：[TrnRT](https://github.com/RunanywhereAI/trnrt)——面向 AWS Trainium 的开源 LLM 推理引擎（47 分），自研芯片生态的工具链缺口开始被社区填补。
- Show HN：[Pulsar](https://news.ycombinator.com/show)——跨 harness 的 agent-to-agent 通信与消息传递协议，多 agent 编排正在出现标准化尝试。
- [Alloy CSS](https://alloyhtml.com/example.html)：对话框、菜单与标签页组件在**无 JavaScript** 下工作（182 分）——平台原生能力继续蚕食 JS 框架领地。
- Apple 开始向第三方开发者开放 Siri AI 预览；OpenAI 首席科学家 Jakub Pachocki 公开内部预训练困惑度数据后，呼吁前沿实验室建立共享安全指标（接昨日报道）。

---

今天的三个故事共享一个结构：**旧路径的新版本**。黄仁勋的回归不是简单的复职——附带新的安全委员会与合规官；循环架构不是新发明——但第一次跑进了旗舰级产品；本地 AI 也不是新话题——但入门指南能拿 662 分说明需求真实存在。有时进步就是把旧东西跑通。明天见。
