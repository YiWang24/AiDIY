---
slug: ai-daily-digest-2026-11-21
title: "AI Daily Digest: 黎曼猜想证明通过 Lean 全社区验证、Thinking Machines 循环架构塞进笔记本、GPT-6.2 SimpleBench 翻车 - 2026/11/21"
authors: [yiwang]
tags: [ai, daily-digest, riemann, lean, thinking-machines, inkling, simplebench, arxiv]
---

<!--truncate-->

昨天的主题词是**验证**，今天验证本身有了答案。黎曼猜想发布仅 24 小时后，Lean 与 Mathlib 社区正式确认证明正确——人类历史上第一次，一份「没有任何人能读完」的数学证明通过了全社区机器检验；Thinking Machines 把「循环推理」架构做到 **5.4GB 内存可跑在笔记本上**；而综合榜第二名 GPT-6.2 在 SimpleBench 上的翻车则提醒我们：验证什么问题，和验证本身一样重要。

## 黎曼猜想：从「声明」到「验证通过」只用了一天

昨天的 digest 里我们写道「在 Lean 验证完成前，这只是声明而非证明」。今天，这句话有了结局：**Lean 与 Mathlib 社区发布联合声明**（Lean FRO 与 Mathlib Initiative 背书），明确表示「我们有充分信心 Alpöge 的黎曼猜想证明是正确的」（HN 560 分）。

验证严格遵循 Xena 项目的四条准则：

1. **命题本身正确**：所证命题取自 Mathlib 中经专家审查的 `RiemannHypothesis` 定义——排除了「证明了一个变了味的黎曼猜想」的经典陷阱
2. **编译可复现**：数十人独立编译这份 **1700 万行、约 239MB、17.5 万源文件**的库，产出完全相同的 raw proof export
3. **所证即所声称**：用 `comparator` 与 `con-leche` 两个独立工具逐字比对，确认 Alpöge 库证明的定理与 Mathlib 的黎曼猜想陈述完全一致
4. **证明逻辑有效**：raw proof 由 Lean 官方 kernel 及多个第三方独立 checker（不同语言实现）检验，其中 `con-leche`/`con-ron` 自带「相对集合论不可能接受假证明」的形式化保证；所有检验在与源码隔离的惰性导出上运行，排除恶意代码

值得注意的是尺度转换：Alpöge 没有写传统论文——生成文本版超过 25 万页，他自己都称「不可读」——而是直接交付机器可检验的形式化库。**数学证明的载体正在从「人类可读的论证」变成「机器可验证的对象」**，而 Terry Tao 同日发文讨论 Unforced Navier-Stokes 奇点与广义黎曼猜想的关联结构（HN 518 分），说明数学社区已经开始围绕这份证明展开后续工作。AI 协作的数学从「有趣的新闻」变成了「已验收的基础设施」。

> 来源：[Lean 社区联合声明](https://leanprover-community.github.io/blog/posts/riemann-hypothesis/)、[验证文件总览](https://math.mit.edu/~drew/grh/)、[HN 讨论](https://news.ycombinator.com/item?id=50589618)（2026-11-21）

## Inkling 2 Mini：把推理循环塞进笔记本

Thinking Machines 发布 **Inkling 2 Mini**（HN 1295 分）：一个 **26.4B 总参、3.4B 激活**的 MoE 模型，但每个 token 把模型中间层**循环执行三遍**（每 token 权重激活合计 5.4B）——用「复用深度」替代「堆叠宽度」。结果是它以不到 100B 的体量在 DeepSWE v1.1（48.2%）与 Vals Index v2.2（46.5%）上**领先全部开放权重模型**，NVFP4 量化后 5.4GB 权重即可本地运行。

两个更值得记录的实验发现：

- **循环深度是推理计算的可调维度**：配套发布的 variable-loop 研究模型显示，不写思维链的时间视野从单遍 16 秒升到三遍 37 秒；串行推理基准在**十遍循环——两倍于训练时的深度**——仍在提升，说明模型学到的不是「三遍的套路」而是可外推的迭代推理
- **可监控性是核心论点**：循环让模型「想得更久而不写下来」，CoT 随循环加深变短但保持可读，且 agentic sabotage 测试分数未随循环数上升。如果推理发生在权重复用里而非 token 流里，「读思维链做监控」这条安全路线需要新的锚点

同日发布的旗舰 **Inkling 2 Small**（594B 总参/17B 激活，主打 agentic coding 与视觉）则采用新发布节奏：**先闭权重、待额外安全测试后数周内开放**——开源实验室也开始给「开放权重」加安全测试窗口了。

> 来源：[Introducing Inkling 2 Mini](https://thinkingmachines.ai/news/inkling-2-mini/)（2026-11-20）、[Inkling-2-Mini in 5.4 GB Memory](https://github.com/ShinMegamiBoson/lookatmyquant)（社区量化，HN 155 分）

## GPT-6.2 双雄在 SimpleBench 翻车

综合榜第二名 GPT-6.2 Astra（BenchLM 91.1 分）和它的同门 Sol 6.2 在 [SimpleBench](https://simple-bench.com/) 上双双翻车（HN 144 分、91 评论）。这个基准的设计初衷就是「高中生 vs SOTA」：非专业人类基线 **83.7%**，而目前最好的模型 Claude Fable 5.2 也只有 81.9%——全部前沿模型都低于一个高中生。题目考的是时空推理、社会智能和语言对抗鲁棒性（trick questions）。

教训和昨天 Lean 验证的故事互为镜像：**分数的有效性取决于它测的是什么**。综合能力分与朴素常识推理是正交维度，91 分的模型可能在常识题上输给榜单 81 分的竞品。给面向普通用户的产品选型时，别外推综合排行榜——用贴近目标人群直觉的对抗性小基准实测。

> 来源：[SimpleBench](https://simple-bench.com/)、[HN 讨论](https://news.ycombinator.com/item?id=50588916)（2026-11-21）

## arXiv：扩散 Transformer 的 RL 后训练其实是激活转向

arXiv **[2611.26627](https://arxiv.org/abs/2611.26627)** 给扩散模型的 RL 后训练提供了一个令人意外的最小解释：**RL 后训练带来的能力提升（视觉质量、文字渲染、多物体组合）等价于激活转向（activation steering）**——RL 学到的不是新的权重结构，而是可以在前向传播中以「偏置向量」形式注入的激活偏移。既然渲染文字、组合物体这些能力本质上是 prompt 依赖的，把它们定位为低维的激活方向调变，意味着**后训练成果可能被抽取、迁移、甚至叠加**，而不必每次都完整重训。这条结论如果在大模型上普遍成立，「微调即转向」会改变我们对后训练工程的成本模型。

## 快讯

- **纳斯达克抹平 2026 年全部涨幅**：AI 板块抛售 dampens Anthropic 第二个交易日表现（The Guardian，HN 433 分）——昨天 +17.1% 的 IPO 狂欢之后，公开市场对 AI 定价的冷静期来得很快
- **DreamCoder**：Mastering Emacs 作者推出的 coding harness 与 IDE（HN 260 分）；**ClawDOS**：能跑在 DOS 上的 AI coding agent（HN 142 分）——harness 工程的边界还在往外扩
- **价格日历**：GPT-5.6 Sol 促销价**今日截止**；Gemini 4 Argon 介绍价 $2/$10 **11 月 30 日到期，12 月 1 日起翻倍至 $4/$20**；Gemini 3.8 Flash 1 月 1 日翻倍——预算规划盯日历，别盯发布会
- **LLM 逐字节读写可执行文件**：仅凭十六进制 dump 直接编辑机器码的实验（HN 133 分）——「模型直接操作字节」的能力边界继续下探

---

*本文由 AI 辅助整理，新闻与论文均附来源链接，欢迎在 [GitHub](https://github.com/YiWang24/AiDIY) 提 PR 补充修正。*
