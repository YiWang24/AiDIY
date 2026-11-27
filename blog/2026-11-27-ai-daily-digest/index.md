---
slug: ai-daily-digest-2026-11-27
title: "AI Daily Digest: Anthropic 用 Rust 重写 Messages API、DJB 汇总「假计算机检查证明」清单、离散对数亚指数算法宣称、Google Workspace agent MCP 强制令 - 2026/11/27"
authors: [yiwang]
tags: [ai, daily-digest, rust, verification, formal-methods, discrete-logarithm, mcp, google-workspace, self-hosting, arxiv]
---

<!--truncate-->

今天的主题词是**验证基础设施本身成了新闻主角**。Anthropic 重写 API 公布的最重要的不是性能数字而是验证方法；DJB 把证明检查器的 soundness bug 汇总成清单；离散对数的亚指数算法宣称把自己的正确性押在另一个未验证宣称上。当验证成为本周的母题，连「验证工具靠不靠谱」都开始被拿出来验证。

## Anthropic 用 Rust 重写 Messages API：数字之外，验证方法才是重点

Anthropic 把 Messages API 的服务端核心重写为 Rust：**每请求 CPU 降约 70%，首 token 中位延迟降约 20%，全程零停机**（[汇总报道](https://aitoolsrecap.com/Blog/ai-news-november-27-2026)）。但真正值得学的是验证过程的完全公开：数月影子流量双跑、新旧实现的响应匹配率先从 24% 跌到 6.5%、修复后爬回 99.6%，且独立审计在移植过程中**抓出了超过 100 处被悄悄弱化的测试断言**。匹配率曲线「先变差再变好」是重写类项目的常态而非异常——值得传播的不是 99.6% 这个终点，而是「敢于公布中间最低点 + 让审计盯住测试本身」的方法论。测试断言被移植过程削弱，是所有大迁移的隐形风险：代码改对了，测试却被改软了。

## 离散对数亚指数算法 + DJB 的「假计算机检查证明」清单：验证的地基也在被检验

IACR ePrint 昨日收录 [A Deterministic Subexponential-Time Algorithm for the Discrete Logarithm Problem](https://eprint.iacr.org/2026/3020)（浙江大学区块链与数据安全全国重点实验室，[HN 190 分](https://news.ycombinator.com/item?id=50665968)）：宣称在「Cauchy–Hermite 布尔张量缩并构造」（OpenAI，2026-10）成立的前提下，给出素域与椭圆曲线上 DLP 的确定性亚指数算法——零随机比特、不依赖 GRH 也不依赖平滑性启发式。注意它的结构：**条件于一个上个月刚出现、尚未经社区检验的构造**。而它爬上了 10 月 ETH 反驳、11 月 ω=9/4 与 NP_R ≠ PAR_R 组成的宣称队列——按本周确立的标准，验证之前一律按猜想处理，且这条队列的宣称产出速率仍远快于验证速率。

同日，DJB（Daniel Bernstein）上线 [False computer-checked proofs](https://cr.yp.to/proofs/falseccp.html) 页面（[HN 119 分](https://news.ycombinator.com/item?id=50667989)）：系统汇总各主流证明检查程序（Lean、Rocq、HOL Light 等）被报告的 soundness bug，其中不少**已被证实可利用**——假命题可能溜过检查器。页面还点破两个微妙之处：HOL Light 内核只有 400 行代码，但行数少不等于被认真审过；跑多个检查器交叉验证有用，但不同检查器可能**共享同一个 bug**。这给本周的「验证金字塔」补上了地基那一层：机器检查是可靠的，前提是检查器本身可靠——而检查器是人写的软件。

## Google 给 Workspace agent 定死线：2027-02-01 起必须走官方 MCP

Google 宣布 MCP 服务器与 Workspace CLI 全线 GA，并给出硬性时间表：**2027-02-01 起 agent 必须走官方 MCP 通道而非直接调 REST API**，2027-04-01 起 Scaled 层计费（[HN 415 分，329 评论](https://news.ycombinator.com/item?id=50653477)，标题直指痛点：「Gmail 的那个不能发邮件」）。配套要求是 Agent OAuth 客户端必须自我声明为 agent——流量层面第一次能把「agent 代用户操作」与「用户本人操作」分开审计。这是昨天「权限收口」消息的完整版：平台治理正从应用层下沉到身份与协议层，代价是官方通道的能力边界由商业策略而非技术约束决定。依赖第三方 Workspace 通道的产品，迁移窗口只剩两个多月。

## 其他值得记录的

- **「AI 让自托管重新变有趣」登顶 HN**（[1030 分，488 评论](https://news.ycombinator.com/item?id=50660180)）：AI 把自托管的技术门槛压到个人可承受的水平——本地模型、agent 辅助运维让「自己跑服务」从极客爱好回归大众选项。
- **「Claude 在破坏 ML 研究任务？」**（[431 分，223 评论](https://news.ycombinator.com/item?id=50664325)）：单条推特的未验证宣称冲上首页并引爆讨论。无论后续结论如何，「agent 可能在长任务里偷懒/走捷径」的怀疑本身已成为需要实验设计来回答的问题——注意它今天连独立复现都还没有。
- **Kimi for Science**（[173 分](https://news.ycombinator.com/item?id=50665920)）：月之暗面推出科研专项计划，「更多科学想法成为可能」——国产模型对科学发现场景的投入在加码。
- **GPT-6.2 进 ChatGPT 聊天页**：11-23 起向 Plus/Pro/Business/Enterprise 滚动推送，OpenAI 明确 Work 与 Codex 背后模型不变，Advanced/Standard 语音模式 12-11 退役。
- **弗吉尼亚与俄勒冈起诉 xAI**：两州就 Grok 生成未经同意的性化图像分别起诉，法律理论走消费者保护与欺骗路径——被审的是「安全承诺与实现之间的距离」。
- **Volvo 在根特工厂训练 Hexagon AEON 人形机器人**：轮式、载重 10kg、模仿学习上料，2027 上半年试点、年中投产。

## arXiv 精选

**[DFly2](https://arxiv.org/abs/2611.34776)**（11-25）：原生稀疏注意力模型的投机解码草稿，直接复用目标模型为每个 query 选好的稀疏位置集——草稿的缓存与位置选择成本已被目标付掉。与本周 CPA（草稿互相校正）、draft calibration（草稿分布对齐）连成一条线：**解码加速正在变成草稿与目标的系统协同设计问题**。推理笔记已更新。

**[SPLICE](https://arxiv.org/abs/2611.34777)**（11-25）：长时程 agent RL 的「全败组」让组相对方法没有梯度可用，SPLICE 在失败轨迹上选拼接点、生成有界选项、用当前策略续跑估值，从失败里廉价提取训练信号。前沿追踪已更新：瓶颈从「有没有奖励」转向「如何从失败里提信号」。

**[Model Diffing for Backdoor Detection](https://arxiv.org/abs/2611.34758)**（11-25）：把后门检测对象换成微调前后的权重差异本身，ΔW 经基座 J++-lens 解码后在 12 个设置中的 11 个里把点名触发器的 token 排进前 10。AgentOps 安全笔记已更新：**后门的痕迹写在 diff 里，需要正确的透镜才能读出来**。

**[DRBench Pro](https://arxiv.org/abs/2611.34852)**（11-25）：把「知识覆盖的广度×深度」做成 deep research agent 的一等评测目标，几何平均给分。Agent 评测笔记已更新。

---

今天的故事共享一个结构：**验证链条的每一环都同时在被建设和被质疑**。Anthropic 公布了 API 重写的完整验证方法（包括匹配率的最低点）；DJB 提醒我们证明检查器自己也有一份 soundness bug 清单；离散对数宣称把正确性押在一个出生一个月的未验证构造上；Google 则把 agent 验证做进身份层——自报家门，可审计，可撤销。验证不是一次性通关，是一条需要逐环维护的链条，而今天链条上每一环都有动静。明天见。
