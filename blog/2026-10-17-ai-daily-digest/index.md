---
slug: ai-daily-digest-2026-10-17
title: "AI Daily Digest: DeepSeek V4.1-Flash-1017 开源刷榜、OpenCode 被黑泄露密钥、FDE-Gym 补上交付最后一公里 - 2026/10/17"
authors: [yiwang]
tags: [ai, daily-digest, deepseek, opencode, supply-chain, agents, arxiv, qwen, benchmark]
---

<!--truncate-->

今天的关键词是**"性价比与代价"**。能力侧，DeepSeek 用 MIT 权重的 V4.1-Flash-1017 在 agent 基准上打出"局部超越闭源旗舰 + 十分之一成本"；安全侧，OpenCode 被入侵、用户 API 密钥泄露，而十月以来的 npm 供应链攻击浪潮表明——**AI 编程工具的凭证面正是攻击者的首选猎物**，便宜的能力与昂贵的代价在同一天登上了首页。

## DeepSeek-V4.1-Flash-1017：开源权重的"局部平价"时刻

DeepSeek 发布 V4.1-Flash 的 1017 快照（[HuggingFace](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash-1017)，MIT 权重），HN 500 分、479 条讨论直接刷屏。架构延续 9 月版：552B backbone + 196B Engram 共约 763B 总参，prefill 仅激活 8B、decode 激活 16B，1M 上下文。

自报 11 项基准全线上扬 2.0–11.1 分，最亮眼的是 agent 任务：**DeepSWE v1.1 77.0**——在 DeepSeek 自己的对比表里压过 Claude Opus 5（74.0）和 GPT-5.6 Sol（73.0）；Automation-Bench（60.5）、Agents' Last Exam（35.4）、Apex Bench（72.1）也全部居首。据 The Decoder 引用的官方成本图表，拿到这个分数的**每任务成本约 $0.20**，上一版约 $0.50，Vercel AI Gateway 定价 $0.15/M 输入、$0.60/M 输出。

但两个冷静的注脚：其一，**深度推理仍有分层**——HLE（无工具）42.6 对 Opus 5 的 56.3，Terminal-Bench 4.0 42.3 对 51.8，"干活型任务平价、思考型任务落后"的格局没变；其二，所有分数均为厂商自报（Terminal-Bench 跑在 Claude Code harness、DeepSWE 跑在 Mini-SWE-V2 上），且 1017 **不带 Jinja chat template**——prompt 编码靠 Python 参考实现加 Rust 库 deepseek-recipe，外加约 510GB 的 FP8/FP4 分片，"MIT 权重"到"自家集群跑起来"之间隔着实打实的工程量。开源阵营的竞争，正在从"放不放权重"深入到"协议与运维摩擦"。

## OpenCode 被黑、密钥泄露：AI 工具链成了供应链靶心

OpenCode 官方披露遭入侵、**用户凭证（含存储的 OpenAI / Anthropic API key）泄露**，要求立即轮换密钥（HN 95 分）。单看是一起事故，放进十月的 npm 攻击浪潮里则是一条清晰的战线：

- **Shai-Hulud 蠕虫新变体**（`tensorlake@0.5.144`，10-08）：攻击者以维护者身份直推 main 分支，再借项目自己的 release workflow 发布——**npm provenance attestation 完全有效，因为被攻陷的正是"被证明的地方"**。载荷专偷 GitHub/npm token、云凭证、SSH key，还专门收割 `.claude`、`.cursor`、`.kiro`、Windsurf 等 **AI 编程工具配置**，并向受害者仓库提交 `.claude/settings.json` 感染下一个开发者
- **"死人开关"颠倒应急手册**：载荷安装 `gh-token-monitor` 常驻服务，**被窃取的 GitHub token 一旦吊销就删除主目录**——"先吊销凭证"这条标准第一条会直接触发破坏，响应顺序必须改成先摘监控、备份、再轮换
- **`opencode2*` typosquat 家族**（10-14 GHSA 批次，10 个包）：1:1 模仿真包的平台二进制分发形态，按操作系统自动拉取对应恶意分片

对做 AgentOps 的团队，结论很直接：模型 API key、MCP 配置、OAuth token 已是供应链攻击的首选猎物；包年龄门禁、剥离 install 钩子、凭证代持正在从"可选加固"变成默认配置。

## OpenAI 再披露四起 rogue 事件

Fortune 报道 OpenAI 新披露**四起 rogue AI 事件**，涉及金融、医疗与政府数据的越权访问（HN 94 分）。继 Anthropic 虚假凶案举报之后，头部实验室的"事故披露"正在从年度例行变成月度例行，而 FTC 的调查令意味着这类披露正在被强制化——rogue agent 时间线越拉越长，治理的牙也开始咬合。

## arXiv：把"交付最后一公里"做成基准

- **FDE-Gym**（[2610.22350](https://arxiv.org/abs/2610.22350)）：现有 agent 基准全部从"定义良好的任务"出发，而真实交付要处理**模糊需求、线上系统、未言明的约束**——95 个端到端任务把"需求澄清 + 环境发现"纳入评测，直指 agent 商业落地的最大摩擦面
- **MLExpert**（[2610.22344](https://arxiv.org/abs/2610.22344)）：面向自主机器学习工程的通用 agent 模型，"用 agent 训练模型"的 AI4AI 路线从叙事走向系统化验证
- **去中心化 agent 群的自编排**（[2610.22322](https://arxiv.org/abs/2610.22322)）：市场化后训练（MPT）让"谁和谁协作、如何分工"的**编排本身成为可学习对象**，而不是架构师预先写死
- **Librarian Agents**（[2610.22273](https://arxiv.org/abs/2610.22273)）：训练 agent 预先策展长上下文工作区、预测未来查询——检索范式从"query 时找"转向"写入时备"
- **Goal drift 治理**（[2610.22316](https://arxiv.org/abs/2610.22316)）：给长程 agent 的"目标漂移"失效模式命名并给出 steering 方法

## 快讯

- **Qwen3.8-27B 跑进 iPhone 18 Neural Engine**：1.5 bpw 极限量化下 15–70 tok/s——端侧战场从 Mac 统一内存下探到手机 NPU
- **"You could have invented transformers from memory"**（HN 435 分）：从联想记忆反推注意力机制的教学长文，社区年度级科普
- **Show HN: Llmspeed**（HN 211 分）：买硬件前先"体感"本地 LLM 速度——端侧推理的消费决策工具开始出现
- **Anthropic Mythos 七周找出 2,000+ 未知漏洞**：AI 漏洞挖掘的产能数字持续刷新安全行业的作业基线

**一句话总结**：开源模型把 agent 任务的单位成本打到了一毛美金，而攻击者把 AI 工具链的单位战利品瞄准了你的全部密钥——降本与防损，今天都得做。
