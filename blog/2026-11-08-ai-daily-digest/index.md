---
slug: ai-daily-digest-2026-11-08
title: "AI Daily Digest: A2A 协议转 stable、Claude Code 泄露 1122 个凭证文件、基准审计击穿评测可信度 - 2026/11/08"
authors: [yiwang]
tags: [ai, daily-digest, a2a, adk, claude-code, security, secrets, evaluation, benchmark, thinking-machines, openai, hn, arxiv]
---

<!--truncate-->

今天的主线是**"协议成熟、信任失守、评测祛魅"**：Google 把 A2A 协议标记为 stable，agent 互操作正式进入生产阶段；同一天，Apiiro 的报告显示用户在 Claude Code 里按下「Don't Ask Again」后，1,122 个公开 GitHub 文件里躺上了真实凭证；而 HN 上的 MaxxBench 和 arXiv 上的基准审计论文则在追问同一个问题——**你引用的那个分数，到底是怎么算出来的**。

## Google ADK 2.14：A2A 协议正式 stable

11 月 7 日发布的 **Google ADK 2.14.0** 把三样东西一并移入 stable：**A2A 协议、执行环境（execution environments）和核心 runtime**。这是 A2A 自 2025 年 4 月发布以来的最重要成熟度信号。

回顾这条时间线：2025 年 4 月 Google 联合 50+ 公司发布 A2A 规范，用 Agent Card 做能力发现、用标准 JSON-RPC 消息替代 agent 两两之间的自定义 API；2025 年内捐赠给 Linux 基金会；到今天，协议本体、执行环境与 runtime 全部 stable。**多 agent 集成从此可以进入 SLA 敏感的生产环境**——你不再需要在架构评审会上为"这是个实验性规范"辩护。

同日，Anthropic 发布 **Claude Code 2.1.319**：MCP 工具调用可以转入后台执行，不再阻塞主对话流；新增 `denyInsteadOfPrompting` 配置项，并改变了 `/loop` 的行为。这两件事放在一起看是一个清晰信号：**agent 基础设施正在从"能跑"走向"可运维"**——协议层有 stable 标准，宿主层有后台任务、细粒度权限控制。

## Claude Code「Don't Ask Again」：1,122 个公开文件里的密码

Apiiro 的安全研究（HN 496 分、356 评论）扫描公开 GitHub 后发现：**1,122 个文件泄露了真实凭证**——云 API key、数据库连接串、CI/CD token，泄漏源头正是 coding agent 的权限确认流程。用户为了减少打断按下「Don't Ask Again」/「Always allow」，agent 随后把含敏感参数的命令原样写进文档、脚本和 commit message。

关键在于泄漏路径：**不是 agent "主动泄密"，而是权限疲劳 + 上下文泄漏的组合**。高频形态包括 `export API_KEY=...` 调试片段、粘贴进 README 的连接串、agent 生成的"复现步骤"里带真实 token。这与本周的 Postman 静默装插件、Codex 数据开关回退构成同一主题的三连：**agent 工具链的信任决策正在成为企业凭证泄漏的主要入口**。

给工程团队的三个可执行动作：

- 把「Don't Ask Again」当作与 `sudo NOPASSWD` 同级的配置项审计——只允许 session 级放行
- pre-commit hook + CI secret scanning 是底线而非加分项；已泄漏的 key 必须轮换，撤回 commit 没有用（历史还在）
- 权限确认 UI 应该按"即将执行的命令内容"放行，而不是按工具名一次性交出整类操作

## 评测可信度危机：MaxxBench 与 BAR 审计

HN 354 分的 **MaxxBench** 直接质问："Nice DeepSWE score. But is it true?"——对 agent 基准跑分做了逐条复核，发现宣传分数与可复现结果之间存在明显差距。同期 arXiv 上的一篇新论文（**BAR：Benchmark Audit and Revision**）给出了更系统的证据：

- 作者用源码溯源、程序执行和对照检查审计了 **9 个公开的 policy-based decision 基准**，发现无依据的标准答案、经重放仍存活的引用错误、拒绝合理答案或给不完整决策加分的评分器
- 最刺眼的数据：在 **LegalBench SARA numeric** 的 96 个案例上，仅仅修正评分器，三个模型的接受率**各提升超过 80 个百分点**——模型回答一个字没改
- 在 **RuleArena Tax** 上，恢复一个必需的零值下限改变了 300 个引用中的 27 个，直接改写观察到的模型差距

这和上周的评测主线（ITBench-AA 全员不及格、模型级联靠置信度校准）指向同一件事：**评测结果的上限由评测器质量决定**。引用任何"模型 X 在基准 Y 上得 Z 分"之前，先问三个问题——评分器是谁写的、答案引用能否重放、换个模型接受率会不会跳 80 个点。

## 快讯五条

- **OpenAI 融资 $11B，估值 $1.25T**：低于最初寻求的 $1.4T（HN 80 分）。Anthropic 信用评级承压的传闻同期发酵，前沿模型的资本密度到了必须用盈利能力说话的阶段
- **Thinking Machines 发布 Inkling 2 Small**：594B MoE，$1.18/任务，声称登顶西方开放权重模型——但 **Apache 2.0 权重并未发布**，目前只能在 Tinker 平台上用，"开放"承诺留待外部安全测试之后
- **llama-modchip**（HN 159 分）：开源项目宣称在 **64GB 内存、无 GPU** 的机器上跑 284B DeepSeek 模型，本地推理的极限又被推了一步
- **"Agent memory needs its OpenTelemetry moment"**（HN 115 分）：呼吁为 agent 记忆制定开放格式与可观测标准——记忆现在是各家 agent 框架的私有格式，正如可观测性标准化之前的日志碎片时代
- **"Goodbye Claude, hello Pi"**（HN 530 分、342 评论）：一位开发者详述从 Claude Code 迁移到 Pi 的原因，热度说明 coding agent 的用户流动已经开始——锁定从来不是永久的

## 结语

今天的三个故事其实是同一枚硬币的三面：**协议 stable 意味着更多人会把 agent 放进生产，而生产化的代价是信任与验证问题从脚注变成主章节**。权限确认的每一次「Don't Ask Again」、每一个被引用的基准分数，都是这个系统里待审计的信任节点。工具在成熟，审计也要跟上。

> 来源：[AIToolsRecap 11-08 汇总](https://aitoolsrecap.com/Blog/ai-news-november-08-2026)、[Apiiro](https://apiiro.com/blog/coding-agents-leaking-secrets-github-dont-ask-again)、[MaxxBench](https://maxxbench.unlap.ai/research/why-maxxbench/)、[HN 首页](https://news.ycombinator.com/)（2026-11-08）
