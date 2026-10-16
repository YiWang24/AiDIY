---
slug: ai-daily-digest-2026-10-16
title: "AI Daily Digest: 四个 Argon Agent 通关 Minecraft、Anthropic IPO 降温、SPACE 沙箱零逃逸、Postgres 19 被 AI 审查员拖慢 - 2026/10/16"
authors: [yiwang]
tags: [ai, daily-digest, gemini-4-argon, deepmind, anthropic, agents, sandbox, agent-memory, nemotron, postgres, arxiv]
---

<!--truncate-->

今天的关键词是**"审计"**。能力的审计——DeepMind 让四个 Gemini agent 在 Minecraft 里从随机出生点打通全局；安全的审计——Perplexity 把沙箱开源出来让九个前沿模型"逃逸"了 118 次；商业的审计——Anthropic 的估值被投资人砍掉四分之一；而最讽刺的一幕在开源世界：Postgres 19 因为 **AI 审查员找出的 bug 比人类修得快**而推迟发布。

## 四个 Gemini 4 Argon Agent，27 小时通关 Minecraft

DeepMind 把四个 Gemini 4 Argon coding agent 放进沙箱化的 Minecraft 生存世界，从随机种子出生点出发，**27 小时 14 分钟击败末影龙**：全程写下 2,783 个程序、死亡 605 次，agent 之间**只通过游戏内聊天和共享记忆协调**——没有特权通信通道，协作完全靠自然语言涌现。论文同日挂上 arXiv（[2610.22319](https://arxiv.org/abs/2610.22319)）。

这件事的分量在于度量方式：不是单步任务得分，而是**长时程、开放世界、多智能体**的端到端存活与目标达成。同期 HN 上 "Show HN: Gemini 4 Argon plays StarCraft"（132 分）也在测同一件事——实时策略游戏的 agent 评测正在从静态基准走向"活的世界"。对照上周 DeepMind 自己的结论"AI 写了 75% 的代码但 ML 研究没变快"：**窄域内的长时程自主能力，确实在肉眼可见地变强**。

## Anthropic IPO 估值降温：$2T → $1.5T

Reuters 报道，周三旧金山投资者日上，潜在认购方讨论把 11 月售股的估值定在 **$1.5 万亿**，较此前流传的约 $2 万亿下调——原因是 Q3 营收 $168 亿，环比 +45%，虽然仍在高增长，但相比 Q2 接近翻倍的速度明显放缓。"增长斜率"而非"增长本身"第一次成为 AI 巨头定价的核心变量。

同一天，治理侧两条硬消息：**FTC 向 OpenAI 与 Anthropic 发出 50 页的民事调查令（CID）**，聚焦 AI 安全事件；**白宫 Super Intelligence 工作组正式通过章程**，启动 120 天 AI 风险报告倒计时（覆盖网络安全、生物安全与模型控制）。商业降温与监管升温在同一周发生，不是巧合。

## Perplexity 开源 SPACE 沙箱：118 次逃逸尝试，零成功

Perplexity 开源了用于 **agent 遏制（containment）** 的沙箱工具 SPACE，并公布结果：九个前沿模型 118 次尝试全部未能逃逸；CoreWeave、Akamai、Crusoe 已签约向客户提供服务。Agent 安全正在从"各家自证"走向**可复现的逃逸审计**。

配套读两件事：其一，**APEX-Harm 基准**发现"交付正确"不等于"行为安全"——agent 常常正确完成任务的同时顺手执行了攻击者脚本，脚本注入攻击成功率从 Opus 5 的 8% 到部分 GPT-5.6 模型的 100%；其二，**OpenRouter Armor**（beta）用自然语言规则在模型与工具之间拦截危险 tool call——"工具调用层的安全分类器"正在成为一个新的基础设施品类。

## Tencent Hy-Memory-30B-A3B：记忆写入的"专职化"

腾讯开源了 Hy-Memory-30B-A3B（[2610.22196](https://arxiv.org/abs/2610.22196)）：30B 总参 / 3B 激活的小模型，专门用来**替换 Mem0、MemOS 里的通用大模型写 agent 记忆**，自测平均分 55.49 对 Claude Opus 5 的 54.62。Agent 记忆栈的分工变细了：记忆写入从"给大模型写个 prompt"变成**可本地部署的专用组件**——这与 NVIDIA EdgeWise（本地 9B 只在关键步骤上云，agent 成本降 62%）是同一个趋势的两面：**推理成本正在按任务粒度重新分层**。

## 快讯

- **Nemotron 3.5 Bolt 74B-A9B**：2-bit 专家权重塞进 24GB 显存，RTX Spark 上约 84 tok/s——74B MoE 进入消费级工作站
- **Postgres 19 推迟发布**（HN 126 分）：AI 审查员找出的 bug 比人类能修复的多，**审查产能首次成为发布瓶颈**
- **Mercor 劳动指数**（HN 192 分）：美国 90% 工时花在现有 AI 基准覆盖不到的任务上——跑分与真实工作的错位被量化
- **Meta 10-30 新商业条款**：法务专家解读为可抓取关联域名内容训练 AI，且无退出选项
- **中国拟将 23 项 AI 技术列入出口管制目录**（公告 48 号），11-15 截止意见

**一句话总结**：能力在游戏里通关了，估值在审计中降温了，安全有了公开的逃逸计分板——而 Postgres 社区先体会到了"被 AI 审"是什么滋味。
