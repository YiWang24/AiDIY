---
slug: ai-daily-digest-2026-10-21
title: "AI Daily Digest: LiteLLM 投毒命中 LLM 网关、持久记忆成为残留攻击面、扩散语言模型冲进实用区间 - 2026/10/21"
authors: [yiwang]
tags: [ai, daily-digest, litellm, supply-chain, carryover-attack, patch-the-planet, mercury, diffusion-lm, cache-engineering, anthropic, qwen, arxiv]
---

<!--truncate-->

今天的关键词是**"安全边界的时间维度"**。当 LiteLLM 这样的 LLM 网关在 PyPI 被投毒、agent 的持久记忆文件被证明可以携带跨会话的"残留攻击"，安全模型必须从"保护单次会话"扩展到"保护会话之间"；而 Patch the Planet 则把另一面摆上台面——挖掘漏洞的 agent 已经快到需要全球协调机制来接住了。

## LiteLLM 1.107.0 投毒：网关即凭证面

SafeDep 披露 [PyPI 上的 LiteLLM 1.107.0 被植入凭证窃取器与后门](https://safedep.io/litellm-pypi-compromise-credential-stealer-backdoor/)（HN 256 分）。这是十月供应链攻击浪潮中第一个命中 **LLM 网关层**的事件：LiteLLM 这类统一网关天然聚合所有模型的 API key 与全部请求日志，攻陷一个包等于拿到整个 agent 栈的凭证面。网关依赖必须按"凭证托管层"而非普通库定级——锁版本 + 哈希校验、私有镜像、新版本 24-48h 观察窗应成为默认动作。同日 arXiv 的 [After the Attacker Leaves](https://arxiv.org/abs/2610.28425) 把矛头指向另一条被忽视的信道：**长生命周期记忆文件被静默拼进 system prompt、定时任务无需用户在场即可唤醒 agent**——攻击者一次立足，指令在后续所有会话持续生效。配合 [Disclosure Begets Disclosure](https://arxiv.org/abs/2610.28315) 证明的持久记忆隐私泄露自我强化循环：**"清空会话"从来不等于"清除攻击面"**。

## AI 挖洞成为一线战力

[Wiz 的 PHP2Shell](https://www.wiz.io/blog/php2shell-php-rce)（HN 408 分，今日第一）由 AI 辅助分析 uncover PHP 关键 RCE——AI 漏洞研究产出进入可报告 CVE 级别。同日 OpenAI 发布 [Patch the Planet](https://openai.com/index/coordinated-disclosure-of-critical-vulnerabilities/)（HN 176 分）：协同披露一批由 agent 扫描发现的关键漏洞，并提议全球响应协调机制。发现速度与修复速度的剪刀差正在拉开，被外部 agent 扫描将从威胁变为常态——自家产品的披露响应 runbook 需要预置。另一侧的商业信号：[OpenAI 模型登陆 Google Cloud](https://openai.com/index/openai-models-google-cloud/)（HN 132 分）+ NVIDIA Vera Rubin 上云，算力与模型的排他联盟正在解绑。

## 扩散语言模型冲进实用区间

Inception 发布 Mercury 3：扩散语言模型，官方口径 **1,068 tok/s + 1M 上下文**，宣称以 4-8 倍速度跑赢 GPT-6 Luna 与 Claude Haiku 5.5（自报，未独立复现）。若站得住，**循环里跑的模型（路由、分类、摘要）的最优解第一次不是自回归模型**。今天的 arXiv 密集补充了理论侧：[Large Flow Language Models](https://arxiv.org/abs/2610.28559) 给出连续流式生成的规模化配方；[Adaptive MTP](https://arxiv.org/abs/2610.28619) 证明投机解码的收益上限取决于"何时停"；[BitMTP](https://arxiv.org/abs/2610.28500) 把 MTP 与 2-bit 级量化正交叠加。推理竞争正在换轴：从"谁更聪明"到**每美元、每秒多少可用智能**。开源侧 Qwen3.6 27B 今日发布，一周内第三个开源新模型。

## Harness 工程：cache 成为新变量

[Cache Engineering for Agents](https://arxiv.org/abs/2610.28577) 值得所有做长轨迹 agent 的团队细读：当轨迹变长，**KV cache 的 I/O 与存储成为主导成本**，而截断/摘要历史等 context 工程手段会使后续缓存全部失效——"cache 工程"就此与 context 工程并列成独立维度。配套还有 [Evolving Agent Interfaces](https://arxiv.org/abs/2610.28601)（接口设计本身应当是 agent 能力：一行代码替代逐格填表）和 MaD-RSI/ChartEvo 的 harness 自我改进。

## 其余值得关注

- **Anthropic 公共利益章程** + IPO 草案披露 **$80.7B 亏损**：治理叙事与资本现实的张力公开化
- **DHS 要求联邦民用系统移除 DeepSeek 产品**（7 月签署、现在才披露）：开源模型的政府禁令时代开始
- **[GitHub：agent 规模的 Git 基础设施](https://github.blog/engineering/architecture-optimization/the-bridge-to-agent-scale-git-infrastructure/)**：仓库层面开始为 agent 请求模式做架构适配
- **[Alter (YC S25)](https://alterauth.com/)**：多用户 agent 的访问控制——agent 权限管理的商业化正在填充空白

> 深入版分析已同步至知识库：AgentOps 安全章（LiteLLM/残留攻击/Patch the Planet）、Harness 可观测性章（cache 工程与语义观测）、LLM 基础推理章（扩散 LM 与投机解码）。
