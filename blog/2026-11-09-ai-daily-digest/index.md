---
slug: ai-daily-digest-2026-11-09
title: "AI Daily Digest: Claude Fable/Mythos 5.2 双旗舰、Meta Muse Ember 效率前沿、Opus 5.5「被削」争议 - 2026/11/09"
authors: [yiwang]
tags: [ai, daily-digest, anthropic, claude, fable, mythos, meta, muse-ember, model-drift, livenerf, memory-poisoning, documentation-debt, hn, arxiv]
---

<!--truncate-->

今天的主线是**模型层的两极分化与信任焦虑**：Anthropic 一天发布 Fable 5.2 与 Mythos 5.2 双旗舰，FrontierCode 2.0 冲到 49.1%；Meta 同步推出 Muse Ember，把"智能/美元"压到 $0.14 一档——旗舰更贵更强、小模型更小更便宜，中间的模型逐渐没有存在感。而 HN 543 分的「Opus 5.5 被削了？」争论则在追问另一件事：**当模型 API 是黑盒，你怎么知道自己今天用的还是昨天那个模型**。

## Anthropic：Claude Fable 5.2 与 Mythos 5.2

Anthropic 发布了 Fable/Mythos 系列的年度升级（HN 423 分）。同一个底模两个出口：**Fable** 带网络安全与生物安全防护面向所有用户，**Mythos** 减少防护、只对通过 Cyber/Life Sciences 验证程序的组织开放。核心数据：

- **FrontierCode 2.0：49.1%（Xhigh 档）**，所有已发布模型最高；High 档即可与 Opus 5.5 的 Max 档打平（45.3% vs 45.5%），**单任务成本约为后者一半**
- 生成速度比 5.1 快 30%，价格降至 **$8/$40 每百万 token**；另有 2.5 倍速的 fast mode（$16/$80）
- 真实任务侧：帮助工程师完成原本"不可行"的软件迁移（Python→Rust，启动快 26 倍）、30 小时形式化费马大定理证明；一个内测案例里，模型协调 **1,000+ subagent 工作 8 天**，从空文件夹写出一个能在笔记本上启动的原型操作系统

更值得注意的是结构性信号：官方披露 **Anthropic 核心代码库 90%+ 的 merge 已由 Claude 完成**，且 Fable 5.2 被设计为 Advisor/Orchestrator——供 Haiku/Sonnet/Opus 遇到难题时咨询、或把简单任务下派给小模型。**旗舰的新角色不是替代小模型，而是当小模型的上诉法院**。

## Meta：Muse Ember 把 subagent 价格打到 $0.14/任务

Meta 同日发布 **Muse Ember**，明确定位 agent 全天重复的"小活"：工具调用、代码子任务、路由、抽取、长文档解析。$0.10/$0.50 每百万 token、**1M 上下文 + 512K 输出**，Artificial Analysis 口径约 **$0.14/任务**——同分下约为 Claude Haiku 5.5 最佳档的三分之一成本。AutomationBench-AA 上 37.8%（Haiku 13.9%、GPT-6 Luna 20.2%）。

真正值得记的是训练方式：**Muse Ember 是第一个用 Muse Wonder Full（旗舰）训练出来的专用小模型**。"旗舰训练小模型、小模型跑生产流量"的族谱分工正式落地——今天两家的发布其实是同一个策略的上下两半。

## 「Opus 5.5 被削了？」：部署后模型漂移没人测

HN 543 分的争论：11 月 7 日起大量开发者抱怨 Opus 5.5 在 Claude Code 里"变弱"。用户 Shane Melaugh 让 Gemini 4 Argon 分析自己 1,400 个会话，声称 11 月 3 日前后推理风格突变而模型名未变；Theo 给出替代解释——Anthropic 在按账号灰度发布**推理摘要器**变更，"thinking 看起来不一样"不等于模型变了。

开源侧的回应 **LiveNerf** 提供了正确的方法论：每天在固定 harness 版本上重跑同样 78 道难题，变化必须连续两个窗口超 99% 置信区间、≥3 分、且对照组不出现才计数。截至 10 月 23 日：**0.571 vs 基线 0.584，误差范围内，未检出削弱**。教训有三层——"变弱"可能来自权重、推理服务层（量化/算力/摘要器）、或 harness 默认值，三者感知相同但对策完全不同；单用户轶事加 LLM 分析证据等级很低；**依赖模型 API 的团队应当自建固定探针漂移监测**，因为基准只测发布时的模型，没人测你明天用的那个。

## arXiv 三篇：记忆投毒、文档债、并行 agent 团队

- **MemoryDojo（2611.09721）**：首次系统基准化 agent 记忆投毒——一次会话里遇到的恶意指令经记忆持久化后，**跨会话持续改变 agent 行为**。记忆写入需要与读取同等强度的治理：来源标记、会话隔离、写入过滤
- **When Instruction Files Go Stale（2611.09802）**：量化 `AGENTS.md`/`CLAUDE.md` 的文档债——指令文件每步都被读入，过时内容不但烧 token 还主动误导 agent。指令文件要像代码一样 review、检测过期、指定 owner
- **Test-Time Compute Scales Better with Parallel Agent Teams（2611.09798）**：有 verifier 打分时，同等推理预算下**并行多 agent 团队**比 Best-of-N 扩展性更好——与 Fable 的 Orchestrator、Muse Ember 的 subagent 定位互相印证

## 快讯四条

- **H100 租赁价差 4.6 倍**（HN 146 分）：同样的卡，$2.69 与 $12.29 一小时取决于租在哪——推理成本优化里，"选哪家云"经常比"选哪个模型"杠杆更大
- **DeepX 第二代推理芯片**：宣称 5W 以内跑 100B 参数推理，LPDDR5X PIM 路线——边缘侧大模型推理的算力/功耗曲线继续左移
- **OpenAI 收购 Pierre Computer Company、发布 GPT-Image 2.6**（11 月 4 日），并预告下一轮安全加固——旗舰迭代与安全 sprint 交替进行已成节奏
- **Next-Concept Modeling**（HN 173 分，[arXiv 2610.14162](https://arxiv.org/abs/2610.14162)）：粗到细并行文本生成，绕开逐 token 自回归的吞吐上限

## 结语

今天的故事拼在一起是一张完整的图：**旗舰负责仰望上限（49.1% FrontierCode），小模型负责踩住成本线（$0.14/任务），中间层被挤压**；而当模型供给变成持续流动的黑盒服务，「模型被削」从阴谋论变成需要 LiveNerf 式基础设施回答的工程问题。选模型的自由度在扩大，验证模型的义务也在同步加重。

> 来源：[Anthropic](https://www.anthropic.com/claude-fable-and-mythos-5-2)、[Meta Muse Ember](https://research.meta.ai/blog/muse-ember)、[HN: Is Opus 5.5 nerfed?](https://news.ycombinator.com/item?id=50422069)、[HN 首页](https://news.ycombinator.com/)（2026-11-09）
