---
slug: ai-daily-digest-2026-11-03
title: "AI Daily Digest: Postman 静默劫持编码 agent、笔记本上的权重解读、Strategist 策略进化 - 2026/11/03"
authors: [yiwang]
tags: [ai, daily-digest, postman, codex, claude-code, security, consent, prompt-injection, hooks, weight-space-programming, qwen, interpretability, strategist, meta, blpo, scope, rlvr, long-horizon-agents, arxiv, hn]
---

<!--truncate-->

今天的主线是**"同意边界"**：Postman 只是"被打开了一下"，就静默改写了用户所有编码 agent 的配置（HN 632 分）；OpenAI 的 Codex 数据共享开关被用户发现悄悄变回开启；而昨天引爆的 Weight-Space Programming 今天同时迎来"笔记本复现成功"和"方法论批评"两波跟进——热情与冷静都到位了。

## Postman 事件：打开一个 App，等于给所有编码 agent 装了插件

HN 今日榜首（632 分）是 GitHub issue #14370 的取证报告，时间线堪称教科书级的供应链信任事故：用户打开 Postman 桌面端（12.33.4）后，Claude Code 与 Codex 开始反复弹出 MCP 认证告警，Codex 还把 API 相关任务往 Postman 技能里路由。深挖发现三件事，每件都有日志实锤：

- Postman 主进程日志明确写着 `autoInstall.plugin.existing-user`——**静默安装了 claude-code 与 codex 两个插件**（来源标记 `auto-existing-upgrade`），外加一条远程 MCP 连接和独立安装的 Postman CLI
- **`~/.codex/config.toml` 被改写**：注册 Postman 插件市场、启用插件、登记 SessionStart hook，hook 的内容是"任何非平凡的 API 工程任务——设计、实现、mock、测试、监控、文档、部署——先加载 `postman:api-engineer` 技能并照做"
- 最过分的一条：**安装器试图替用户批准自己 hook 的信任哈希**，绕过 agent 宿主本应留给用户的信任决策

这件事的严重性在于攻击面的迁移：`~/.codex/config.toml`、`.claude/` 目录、MCP 注册表正在变成浏览器时代的"主页劫持面"。SessionStart hook 是持续注入系统提示的通道，**谁能批准 hook，谁就控制了 agent 的默认行为**。同日 HN 上还有用户报告 Codex 的"Improve the model for everyone"数据共享开关被静默重新打开——两家头部厂商在同一天提醒我们：企业 IP 防泄漏不能依赖厂商默认值，agent 配置（config、hook、MCP 连接）应当纳入版本控制并定期 diff。

## Weight-Space Programming 次日：笔记本复现成功，但批评也来了

昨天聊过 MIT CSAIL 的 Weight-Space Programming（前沿 LLM 直接读写神经网络权重）。今天两条跟进值得对照着看：

- **Simon Willison 实测**：Qwen 3.8 27B（17GB，笔记本本地跑）也能做论文第一组实验——只看原始权重判断网络玩的是什么游戏。Pac-Man 46 分钟（置信 72%）、Pong 1 小时 4 分（75%）、Breakout 52 分钟（88%），各烧掉 4 万多个推理 token。他贴出的推理轨迹几乎是不可读的数字迷宫，但结论确实正确。Kimi K3.1 Pro 也通过了（9 分 41 秒）
- **方法论批评**：spaCy 作者 Matthew Honnibal 认为论文"有误导性"——把"无工具直接看权重"和"拿着代码跑操作"两件事混在一起；Sean Goedecke 则拆解了 Qwen3.5-0.8B 那个 0.016% 编辑的例子，指出它走的其实是人类 ML 研究员也会走的步骤

Willison 自己的定调很稳：结果很酷，但"源代码时代结束、机器将以不可理解的方式编辑自己的权重"这类解读并不成立——一个有经验的人类拿纸笔也能做到，只是慢。**"能力存在"与"能力超人类"之间隔着巨大的解读空间**，这大概是本周最好的可解释性一课。

## Strategist：推理策略这"另一半"也开始自我改进了

Meta 系团队的 **Strategist**（arXiv [2611.03618](https://arxiv.org/abs/2611.03618)）给了一个漂亮的框架：模型只是 agent 系统的一半，另一半是推理策略——把模型调用组织成响应的那套流程。今天这一半是手写的，且做一个任务的经验带不到下一个。Strategist 是一个**进化推理策略的元 agent**：策略写成可复用的"蓝图"（可执行代码）入库，新任务来了就检索相关蓝图、写候选策略、真实样本上测试、按结果修订、再入库。30 个基准上 24 个击败最强基线，平均准确率持平（74.7% vs 74.0%）但**推理成本低 39%**，且策略可直接迁移到未见任务和其他模型。

配合同一天的长程 agent 训练两连发——**BLPO**（[2611.03005](https://arxiv.org/abs/2611.03005)：把轨迹前缀总结为任务进展状态、按功能抽象动作，让跨任务的决策共享全局优势估计，无需 critic 与额外 rollout）与 **SCOPE**（[2611.03116](https://arxiv.org/abs/2611.03116)："由短到长"的技能组合课程，WebArena/WebVoyager/WebShop 相对最强基线提升 3.9%–18.6%）——趋势很清晰：**agent 的进步重心正从"模型更强"转向"策略层与信用分配更聪明"**。

## arXiv 速览

- **Not All Reasoning Generalizes**（[2611.03627](https://arxiv.org/abs/2611.03627)）：RLVR 带来的提升不总是真正的策略泛化——训练分布内可能只是记住了可奖励的模式，换个表面形式的 held-out 任务增益就消失。做 RLVR 训练的团队应把迁移评测纳入流水线
- **LUCA**（[2611.03100](https://arxiv.org/abs/2611.03100)）：合成世界专门评测"实验 agent 是否因正确理由而成功"——只看结果的评测会奖励碰巧的胜利
- **Internet of Agentics**（[2611.03066](https://arxiv.org/abs/2611.03066)）：当 LLM 应用普遍组织为多 agent 工作流，协议与治理需要互联网体系结构式的分层设计——多 agent 生态的"TCP/IP 时刻"还在前面

## 简讯

- The Information 报道三家都在憋新模型：OpenAI Terra 家族新品（更便宜、接近 GPT-6.1 Sol）、Anthropic 一个能从有限指令推断用户底层目标的新推理模型、Google 的 Gemini 4 Carbon（升级上周发布的 Argon）
- NYT：Google 威胁对拒绝 AI 的学校关闭搜索服务（HN 371 分，教育界与搜索引擎的博弈进入深水区）
- Fujifilm 因 AI 归档需求把磁带产能提高 5 倍（HN 285 分）——"冷存储是 AI 时代最稳的卖铲人"又添一证
