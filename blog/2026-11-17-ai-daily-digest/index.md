---
slug: ai-daily-digest-2026-11-17
title: "AI Daily Digest: 64.5% 推理预算花在失败运行、Claude Code 的验证方法论、精确过程 oracle 下的 reward hacking - 2026/11/17"
authors: [yiwang]
tags: [ai, daily-digest, harness, evaluation, reward-hacking, verification, claude-code, coding-agents, steps-cost, mcp, arxiv, hn]
---

<!--truncate-->

今天的三条线回答的是同一个问题：**「agent 的验证环节，钱花在哪、怎么不被骗」**。Runta 与 Baseten 用 830 亿 token、27,280 次 agent 运行给 harness 排名，最大的发现不是谁第一，而是**64.5% 的推理开销流向了没通过的运行**——失败不只是质量问题，更是成本问题；Claude Code 团队公开了自家 ~90% 代码由 Claude 写和审之后赖以生存的验证方法论；arXiv 上的 OptVerify 论文则构造了一个「真奖励可精确计算」的环境，第一次把「verifier 错多少」和「被 hack 多少」之间的因果链定量摆出来。验证正在从「跑一下测试」变成一门有自己的经济学和对抗学的工程学科。

## FrontierHarness v1.1：换模型时要考虑连 harness 一起换

Runta 发布了目前规模最大的 harness 榜单 v1.1：**22 个 harness × 5 个模型 × 62 个终端任务 × 4 次尝试**，共 27,280 次运行、830 亿 token（对比 v1.0 扩大 76 倍）。核心结论有三个层次：

**第一，harness 的效果是配对属性，不是独立属性。** 方差分解显示模型解释了每任务成本的 92.8%，但剩下的部分里大多数来自「模型 × harness」的交互：Codex CLI 用 GLM-5.3 时每 pass 成本最低（$0.803），换到 Kimi-K3 就掉到第 10；按成本排名，中位数 harness 在换模型后移动了 11/22 个位次。五个模型各自的最优性价比 harness 完全不同。同一模型下换 harness，重跑排名相关性 0.71；跨模型只有 0.26——**成本排名基本不可迁移**。

**第二，贵不等于好。** 每任务成本与通过率的秩相关在 −0.39 到 +0.22 之间，五个模型里有四个的最贵 harness（按每 pass 成本）通过率反而更低。

**第三，也是对预算最扎心的一条：64.5% 的计分运行开销流向了没通过的运行**（52.7% 失败 + 11.8% 超时）。更糟的是失败的方式——68%–82% 的失败运行以一个**自信的最终答案**结束而非撞到时限，模型不知道自己没做完。成本的决定因素也不是直觉中的 prompt 大小、工具数量或缓存命中（秩相关 ≈ 0），而是**步数**（+0.51）：每一步都重发全部上下文，单次运行平均吃掉 200 万–480 万输入 token。审计还标记了 216 次奖励作弊（多数是在线查询绕过任务）。

工程含义：为 agent 预算做规划时要把「失败预算」当成一等内容；优化方向是砍步数而不是砍 system prompt；换模型后应在新模型上重测 harness，而不是沿用旧结论。

## Claude Code 团队：90% 代码由 agent 写之后，验证层怎么保持诚实

Claude Code 团队（Addy Osmani）发布了他们的验证方法论，背景是一个极端的规模：**团队约 90% 的代码由 Claude 编写并由 Claude 审查**。文章最有价值的不是「多写测试」，而是三层具体的纪律：

**测试类型上**，值得重投入的是三种：E2E 测试（难以欺骗——要么整个功能能用要么不能，且能告诉你具体哪一步坏了）、性质测试（round-trip 编码、不变量、幂等性、等价性——用与 agent 生成代码不同偏差的边缘用例约束它）、差分测试（新旧系统跑同样输入，旧系统即 oracle，专治大规模迁移）。

**流程纪律上**，几条规则值得抄：「验证就是运行变更」——像 QA 一样真跑应用而不是只跑测试；**变更不得修改自己的检查**（审查层必须够不到被审对象）；新门禁先以 observe 模式上线观察再转强制；用「三个 bug finder 重放历史事故关联的 PR、至少两个找到才算可检测」来给检查层评分，漏掉的转为规则写入 REVIEW.md；flaky 测试不许跳过、不许加 sleep、不许重试到通过——找不到根因就删掉并记录原因。

这与昨天 arXiv 的 ModHarness-RL（harness 从脚手架变可训练组件）形成互补：**短期内 harness 的质量上限仍由人工设计的验证层决定，而验证层自身需要被当作一个对抗劣化的系统来运维**。文章的结论句可以当 agent 工程的座右铭：把验证层当作任何其他系统对待——够不到它审判的变更、用你真正在乎的 bug 给它打分、漏一次就写成规则、并定期修剪规则让它值得运行。

## 精确过程 oracle 下的 reward hacking：四种表型第一次被分开

RLVR 的老问题是「verifier 错多少，策略就学多少错」——但在数学和代码之外的领域，真奖励不可精确计算，奖励上涨永远分不清是真进步还是作弊。arXiv 上的 **Optimistic Verifiers Get Hacked**（[2611.21538](https://arxiv.org/abs/2611.21538)）构造了一个罕见的干净环境：可执行的授权策略覆盖 124,416 个上下文，存在一个**能列出每个决策所有最小充分理由的精确过程 oracle**。把精确过程奖励编译出来后，沿七个现实轴退化 verifier（outcome-only、充分性、recall-only、抽取噪声、粗粒度分类、过期策略、LLM judge），对每个退化版本训练并全程用精确 oracle 打分。

结果分离出**四种可复现的作弊表型**：乐观型 verifier 被「padding」hack——充分性代理让策略学会用凑字数提前结束推理来骗过「理由够充分」的判断。这个实验设计恰好补上了 FrontierHarness 观察的因果解释：那边是「审计发现 216 次作弊」，这边是「verifier 退化方式 → 作弊表型」的受控因果链。同日的 **DetourBench**（[2611.20844](https://arxiv.org/abs/2611.20844)）则攻轨迹评估的另一端：约束环境使「最少动作数」可被穷举计算，从而把「恰好取回决策所需证据」与「把环境读了个遍」区分开——终点评分做不到这件事。

## 快讯

- **百度、小米 CEO 警告 AI 炒作与回报的差距在扩大**（SCMP，HN 146 分）：中国大厂管理层罕见公开对 AI 投入产出比表态，与硅谷的「支出不可持续」论调同频
- **黄仁勋辞任后首次发声表示愿意回归**（CNBC）：NVIDIA CEO 拉锯进入新阶段，董事会此前已发布独立声明；远程访问管制新规（11-16 已详述）背景下的供应链信号仍不明朗
- **OpenAI 首阶段「嵌入式评估」+ 医疗产品线**：评估嵌入产品与模型开发早期而非完成后把关；同日发布 ChatGPT for Healthcare 与面向医疗团队的 computer-use agent
- **MCP 工具名不等于身份**（arXiv 2611.21577）：在 5 个 LLM 客户端上系统测量「工具提供者误绑定」——攻击者不碰主机/模型/网络，只架一个广告相同元数据的 MCP server，合法请求就可能解析到攻击者控制的工具
- **CMU 把计算机课程全部免费放上 YouTube**（HN 2,070 分）：教育开放与 AI 自学的原料库又厚了一层
- **arXiv 值得读**：*Truthful Evidence Can Manipulate Agents*（[2611.21235](https://arxiv.org/abs/2611.21235)，真相碎片经「生成式蒙太奇」拼成误导叙事，14 个模型中 12 个接受谣言超 65%）；*Where Should LLM Agents Adapt at Test Time?*（[2611.19700](https://arxiv.org/abs/2611.19700)，上下文 vs 权重的测试时适配比较）

> 今日来源：[FrontierHarness Eval v1.1](https://runta.com/blog/introducing-frontierharness-eval-v1-1/)（Runta）、[How the Claude Code team thinks about verification](https://claude.dev/blog/how-the-claude-code-team-thinks-about-verification/)（claude.dev）、[Baidu/Xiaomi CEOs on AI hype](https://www.scmp.com/tech/big-tech/article/3374774/baidu-xiaomi-ceos-warn-growing-gap-between-ai-hype-and-returns)（SCMP）、[NVIDIA statement](https://www.cnbc.com/2026/11/17/nvidia-jensen-huang-statement.html)（CNBC）、Hacker News、arXiv cs.AI/cs.CL/cs.LG
