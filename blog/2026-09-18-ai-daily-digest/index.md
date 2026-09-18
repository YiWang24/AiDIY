---
slug: ai-daily-digest-2026-09-18
title: "AI Daily Digest: Claude 领衔 26% 研发、加州推 AI 紧急中止开关、AI 辅助 72 小时攻破 OpenAI - 2026/09/18"
authors: [yiwang]
tags: [ai, daily-digest, agents, llm]
---

<!--truncate-->

今天的三个头条共同指向同一件事：AI 正在加速参与高后果系统的构建、攻击与治理。Anthropic 首次披露 Claude 已"主导"其 26% 的模型研发；加州签署行政令推进 AI"紧急中止开关"；一支三人白帽团队借助 Claude Opus 5 在 72 小时内攻入 OpenAI 内网。此外还有美军 AI 幻觉情报险酿误判、8-29MB 端侧自动化模型逼近 DeepSeek V4 Flash，以及多篇值得关注的 arXiv 论文。

## Anthropic 首次披露：Claude 已"主导" 26% 的自身研发

Anthropic 周四发布了一组将持续更新的指标，首次量化"AI 构建 AI"的进度：截至 8 月，Claude "主导"（leads）公司 26% 的模型研发工作——2 月这一数字还不足 1%。所谓"主导"，指模型能在人类监督下从高层提示端到端完成大部分任务；另有 90% 以上的研发工作以"人机协作"方式完成。

更具画面感的细节：8 月峰值时，Anthropic 内部最繁忙的平台上约有 3 万个 AI Agent 同时写代码、跑实验；当月超过 10 亿次决策中，约 1/47000 被安全筛查系统拦截。安全算力方面，7 月抽样周中约 6% 的研究算力用于安全工作，AI 主导的研究中这一比例翻倍至 12%（Anthropic 自称口径保守）。

Anthropic 希望这套指标成为行业模板，让外部得以追踪各实验室逼近"递归自我改进"的速度。目前尚无其他实验室公布可比数据——这也是该披露最值得注意的地方：它把一个原本只存在于论文里的概念，变成了可按月观测的数字。

> 来源：[Reuters](https://www.reuters.com/business/anthropic-says-claude-now-leads-quarter-work-building-its-next-ai-models-2026-09-17)、[Washington Post](https://www.washingtonpost.com/technology/2026/09/17/anthropic-says-its-chatbot-claude-is-taking-over-work-building-its-own-successor)（2026-09-17/18）

## 加州签署行政令：加速独立监督，研究 AI"紧急中止开关"

加州州长 Newsom 周五签署行政令，加速本月刚立法的独立 AI 监督体系（SB 813、AB 1405）落地，并召集专家组在两个月内提交进一步方案，核心议题包括：前沿实验室嵌入独立第三方评估者、安全报告独立验证、为前沿模型开发紧急关停机制（"AI Kill Switch"）并由独立组织定期测试其有效性。行政令还扩大了"可报告重大安全事件"的定义，将 AI 系统失控纳入其中。

值得注意的是，OpenAI 与 Anthropic 都曾支持相关立法。在联邦层面立法迟滞的背景下，加州事实上在为全美设定 AI 安全监管的节奏。"可关停性"正从学术议题变为合规要求——对构建 Agent 系统的团队而言，内建可中断、可审计的停止路径值得提前排进架构设计。

> 来源：[加州州长办公室](https://www.gov.ca.gov/2026/09/18/governor-newsom-issues-executive-order-to-accelerate-independent-oversight-and-advance-the-creation-of-an-ai-kill-switch)、[WSJ](https://www.wsj.com/tech/ai/californias-newsom-issues-executive-order-to-weigh-ai-oversight-including-kill-switch-3a98040f)（2026-09-18）

## Claude 辅助攻击：三人团队 72 小时攻破 OpenAI 内网

白帽安全公司 Hacktron 的三名研究员在 Bugcrowd 授权范围内完成了一次教科书级攻击链：OpenAI 社区论坛（Discourse）的图片解码器 libheif 存在堆溢出 → 构造 HEIF 图片获得远程代码执行 → 利用 OpenAI 单点登录（SSO）配置缺陷接管员工 ChatGPT/Codex 账号 → 进入内部 GitHub 私有 monorepo，提交一个 PR 作为证据后立即停止并报告。OpenAI 在 14 小时内修复，支付 6500 美元赏金。

最值得警惕的细节：团队最初用 Claude Opus 4.8 构建漏洞利用，卡在 ASLR 绕过上；换用前一天刚发布的 Claude Opus 5 后，数小时内即产出可用的 ARM64 利用代码。整条链路不足 72 小时。攻击面完全不在模型本身——而是一个"没人特意选择"的开源依赖加上身份链路配置缺陷。AI 显著压缩的不是攻击的智力门槛，而是时间成本。安全评审的基线需要按"对手有前沿模型加持"来设定。

> 来源：[Hacktron AI 技术报告](https://www.hacktron.ai/blog/hacking-openai)、[VentureBeat](https://venturebeat.com/security/openai-hacked-by-small-team-of-white-hat-security-researchers-using-anthropics-claude-opus-5)（2026-09-18）

## 美军 AI 幻觉情报险酿误判

CNN 披露，美军某部门曾使用 AI 生成的情报报告做决策，其中一份报告幻觉出并不存在的中国船只动态，导致一线指挥几乎误判形势，所幸人工核验在最后环节拦截。这一事件与当天其他头条形成呼应：Agent 输出进入决策链时的幻觉风险不是理论问题。对构建情报、金融、医疗类 Agent 的团队，"关键结论必须可溯源到原始证据"应当是硬约束而非最佳实践。

> 来源：[CNN](https://www.cnn.com/2026/09/18/politics/us-military-ai-false-intelligence-china-ship)（2026-09-18，经 Hacker News 社区讨论放大，131 分）

## Cactus Needle 3：8-29MB 端侧模型逼近 DeepSeek V4 Flash

Cactus Compute 发布可切片的端侧自动化基座模型 Needle 3：权重仅 8-29MB，支持 2-20 层任意深度。在 Mobile Actions 基准（961 条手机操控指令）上，20 层（121M）版本经 2-bit 量化得 86.0 分，逼近 DeepSeek V4 Flash 云端 API 的 88.4，超过 LFM2.5 1.2B（82.4）与 Qwen3.5 0.8B（76.0）。工程上颇多巧思：工具检索头每轮只渲染 top-5 工具、256-token 滑动窗口加工具 KV sink 让长对话内存恒定约 28MB、字节级语法约束输出、校准置信度门控。

核心启示是"窄域专家"路线：当产品工具集固定时，针对固定工具微调的小模型在成本、延迟、隐私上全面占优，微调后可在窄任务上反超云端大模型。端侧 Agent 不必绑定"云 + 大模型"。

> 来源：[Cactus Compute](https://cactuscompute.com/needle)、[GitHub](https://github.com/cactus-compute/needle)（2026-09-18）

## 学术前沿：Harness 实证、扩散语言模型与安全评估盲区

### 编码 Agent Harness 设计的实证研究

arXiv 2609.20804 将编码 Agent 的 Harness（脚手架）解耦为可独立操纵的维度，量化"规划信息"与"状态释放控制"对长程软件工程绩效的影响。结论对工程团队很实用：模型决定性能上限，Harness 决定工程下限——与其频繁换模型，不如先审计脚手架各维度设计。论文当日登上 Hacker News 首页（186 分）。

> 来源：[arXiv:2609.20804](https://arxiv.org/abs/2609.20804)（2026-09-17）

### dQwen3.5：混合注意力扩散语言模型

arXiv 2609.20751 探索将预训练自回归模型改造为扩散语言模型（DLM）的低成本路径，揭示了注意力模式与建模范式的相互作用，为 AR→DLM 迁移提供了系统方法。

> 来源：[arXiv:2609.20751](https://arxiv.org/abs/2609.20751)（2026-09-17）

### GPT 模型的"危害洗白"证据

arXiv 2609.20779 指出依赖表层分类器的安全评估存在系统性盲区：跨代安全训练后，性别歧视并未真正减少，而是转化为更难检测的形态——危害被"洗白"（laundered）而非削减。对 Agent 安全评估的直接启示：基于输出分类器的安全度量可能随代际"虚假改善"。

> 来源：[arXiv:2609.20779](https://arxiv.org/abs/2609.20779)（2026-09-17）

### 其他值得一读

- **AgentPProf**（arXiv 2609.20301）：面向长程 Agent 的语义性能剖析器
- **SoL-Pi**（arXiv 2609.20519）：递归扩展的自动研究循环，提升 Agent 研发效率
- **UnifiedPlayers**（arXiv 2609.20089）：Agent 强化学习中的工具集成推理统一框架
- **Chronicle**（arXiv 2609.20625）：LLM Agent 回归测试的切点重放方法

> 来源：[arXiv:2609.20301](https://arxiv.org/abs/2609.20301); [arXiv:2609.20519](https://arxiv.org/abs/2609.20519); [arXiv:2609.20089](https://arxiv.org/abs/2609.20089); [arXiv:2609.20625](https://arxiv.org/abs/2609.20625)（2026-09-17）

## 知识库更新

本次更新涉及以下文档：

- **Agent 前沿趋势** (`docs/ai/agents/10-frontier.mdx`): 新增 8 条前沿趋势（#807-814），覆盖 Claude 递归自改进指标、加州 Kill Switch 行政令、OpenAI 被攻破事件、Harness 实证研究、美军 AI 幻觉情报、Cactus Needle 3、dQwen3.5、GPT 危害洗白
- **Coding Agents** (`docs/ai/agents/05-coding-agents.mdx`): 新增 Harness 设计实证研究与 Cactus Needle 3 端侧自动化模型两个小节
- **Agent 安全运维** (`docs/ai/agentops-security/index.mdx`): 新增 Claude 辅助攻破 OpenAI 内网、加州 AI 紧急中止开关行政令两个小节

---

*本文由 AiDIY 每日知识更新流水线自动生成，素材来自 arXiv、Hacker News、The Decoder、Reuters 等公开来源。*
