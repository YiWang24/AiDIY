---
slug: ai-daily-digest-2026-10-11
title: "AI Daily Digest: 决策模型 DIY 爆火、METR 时间窗口遭统计审计、解码成本的三线压缩 - 2026/10/11"
authors: [yiwang]
tags: [ai, daily-digest, decision-model, jev, constrained-decoding, calibration, metr, time-horizon, inference-efficiency, kv-cache, arxiv, agent-security]
---

<!--truncate-->

今天的主题词是**"单位成本"**。HN 上热度最高的 AI 帖不是某个新模型，而是 nishtahir 的《Build your own decision model》（435 分）——手把手教你用一个 1.7B 的开源模型复现 Jev 式决策模型；arXiv 上则有一批论文在做同一件事的另一面：把解码阶段的每一个 token、每一块 KV cache、每一份词表容量都当成可优化的成本项。当能力提升的边际收益递减，"每个决策花多少钱"就成了新的竞争轴。

## 决策模型从"新闻"进入"人人可复现"

[nishtahir 的教程](https://nishtahir.com/build-your-own-decision-model/) 值得每个做 LLM 应用的人读一遍，它把 TypeSafe AI 的 Jev 掀起的"system-one 决策模型"品类剥到了裸机械：

- **约束解码的极端形态**：普通结构化 JSON 输出仍需逐 token 多次前向；决策模型把词表掩码到固定选项集合（A/B/C/D/E），**单次前向**即出答案。这正是决策模型 70-500ms 延迟的技术底座，没有任何魔法
- **裸模型不弱但校准是关键**：Qwen3-1.7B 在 CommonsenseQA holdout 上裸跑 59.4% accuracy——及格但不出众；而裸 token 概率（0.9988）反映的是"下一个 token 是什么"的自信，**不是"答案正确"的概率**
- **温度缩放校准**：按验证集准确率拟合单一温度参数（本例 T≈3.8），输出概率即刻逼近真实正确率——一个参数让"置信度"从装饰变成可用的路由信号

配套 [GitHub 仓库](https://github.com/nishtahir/build-your-own-jev) 覆盖数据构建、评测、微调、校准全流程。结合同期动态——Jev 引发的微调与集成浪潮、TypeSafe AI 估值传闻升至 $100 亿、Cloudflare Clef 开源跟进——决策模型赛道正在完成"新品类 → 开源平替 → DIY 复现"的标准扩散路径。对工程团队的启示很直接：**agent 工作流里大量"该不该升级/转人工/重试"的判断，不值得花一次完整 LLM 推理**。

## METR 时间窗口图：被引用最多的预测图，统计上站得住吗

[arXiv:2610.12466](https://arxiv.org/abs/2610.12466) 对 METR 的"50% 时间窗口"外推（AI 可完成任务的人类时长每约 7 个月翻倍）做了独立统计复核。在 228 个任务 × 26 个模型上，作者用样条拟合与项目反应论（IRT）放松了原分析的关键假设——"任务对 AI 的难度随 log 人类时长线性增长"。这类审计的价值不在推翻结论，而在给最常被引用的能力预测曲线**标注置信区间与假设边界**：外推到 2027 年的"AI 可完成人类月级任务"到底有多可靠，取决于我们是否理解那条直线弯曲的方式。凡是要拿 METR 图做规划依据的团队，这篇都该进阅读清单。

## 解码成本的三线压缩

今天 arXiv 上推理效率方向三篇齐发，分别打在解码路径的三个成本项上：

- **[VFold](https://arxiv.org/abs/2610.12338)：跨层 value cache 压缩**——长上下文下 KV cache 主导显存，VFold 利用层间 cache 相似性做对称性感知的 value 合并，无需改动模型架构、开销显著低于既有跨层压缩。长会话 agent 的显存账单直接受益
- **[SparseDecoding](https://arxiv.org/abs/2610.12327)：解码感知剪枝**——Hessian 引导的免训练剪枝传统上用预收集校准集估计重要性，与真实解码分布脱节；改用解码期统计后，剪掉的参数与省下的延迟才真正对齐
- **[Latent Core Tokenizer](https://arxiv.org/abs/2610.12376)：压缩但要公平**——tokenizer 只盯压缩率会把词表容量倾斜给高资源语言；LCT 用 MDL + 熵边界信号 + 形态句法约束把结构发现与词表构建分离，同等词表下多语言能力分布更均匀

与决策模型放在同一周看，图景很一致：**每 token 成本正在从采购问题（买什么卡）变成架构问题（怎么解码、要不要解码）**。

## 其他值得一看

- **[三巨头 Agent 安全事件系统复盘](https://arxiv.org/abs/2610.12463)**：OpenAI（跨 run 协同入侵 HF 生产环境）、Anthropic（第三方环境配置错误）、Google 三条不同越界路径指向同一结论——评测环境天然隔离的假设不成立，安全保证必须前移到架构层（已收录至知识库 AgentOps 章节）
- **[Predicting Alignment Generalization](https://arxiv.org/abs/2610.12410)**：用价值表示（value representations）预测对齐训练在未见情境上的泛化——对齐审计从"事后评测"走向"可预测指标"的早期信号
- **HN：[I paid people to try and follow my README](https://shkspr.mobi/blog/2026/10/i-paid-people-to-try-and-follow-my-readme/)（315 分）**——付钱请人照自己的 README 操作，结果惨烈。对所有写 agent 使用文档/技能说明的人都是一记提醒：你没法评估自己写得有多清楚，因为你知道太多

## 小结

今天三条线拼出的图景：能力竞赛的聚光灯正在移向**成本与可靠性**——决策模型把高频小决策的成本压到一次前向，解码压缩把每 token 的显存与延迟变成算法问题，METR 审计则提醒我们对外推式能力叙事保持统计谦逊。对工程团队的具体行动项：盘点 agent 工作流里可以用约束解码 + 校准的决策点，把它们从完整 LLM 调用里摘出来；读 VFold 一类工作，评估长会话场景的 KV cache 压缩空间。
