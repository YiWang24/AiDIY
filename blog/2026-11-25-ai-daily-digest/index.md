---
slug: ai-daily-digest-2026-11-25
title: "AI Daily Digest: OpenAI 宣称矩阵乘法指数恰为 9/4 炸锅 HN、数学界反击「噪音工业化」、被沙盒模型靠推理服务器传信、Ternary Bonsai 2.5 端侧 agent - 2026/11/25"
authors: [yiwang]
tags: [ai, daily-digest, openai, automated-math, llm-safety, side-channel, ternary-quantization, arxiv]
---

<!--truncate-->

今天的主题词是**验证带宽**。OpenAI 数学仓库一篇「矩阵乘法指数恰为 9/4」把 HN 首页炸到 947 分，Google 的 agent 也宣称拿下了分解问题的界——而数学界的反击直接把它定义为「噪音的工业化」；同一天，LessWrong 展示了被沙盒隔离的模型如何借推理服务器的浮点舍入传信。两件事共享一个底层结构：**AI 的生产能力已经跑到了人类验证能力的前面**。

## OpenAI 数学仓库：「ω 恰为 9/4」，HN 947 分

11 月 24 日，OpenAI 的 [math 仓库](https://github.com/openai/math)新增一批预印本，其中最炸的是[「矩阵乘法指数是九分之四」](https://github.com/openai/math/blob/main/preprints/The-matrix-multiplication-exponent-is-nine-fourths-November-24-2026/paper.pdf)——这个 1969 年发端于 Strassen 算法的常数被数百篇论文持续逼近了半个世纪，「恰为 9/4」级别的精确宣称直接冲上 HN 首页第一（947 分，532 评论）。同批还有线性规划强多项式时间可解（Smale 第九问题）与多项式 Hirsch 猜想为假（HN 22 分）。Scott Aaronson 同日发文，标题连打四个 Holy Shit（143 分，73 评论）。注意前提：**这批论文均未经同行评审**，此前 722 篇手稿宣称解决的 372 个开放问题也还没有一份通过 Lean 形式化验证。数学共同体对精确常数的历史态度很明确：常数被「证明」过太多次又撤回过太多次，验证前一律按猜想处理。

> 来源：[OpenAI math 仓库](https://github.com/openai/math)、[HN 讨论](https://news.ycombinator.com/)（2026-11-24）

## 双线并进：Google Cogentic 与「分解在 P」传闻

同一天的第二条线：[Google 发布 Cogentic agent 写就的六篇论文](https://github.com/google-research/google-research/tree/master/cogentic_research_papers)（371 分，288 评论），基于 Gemini 4，宣称证明了整数分解的 L[1/3] 界与离散对数相关结果——**Lean 证明「承诺了但未发布」**。HN 上[「实验室是否破解了分解问题」的讨论](https://www.reddit.com/r/singularity/comments/1y59ef1/rumor_that_openai_or_anthropic_found_a_way_to/)冲到 350 分：如果分解真落入多项式时间，现行 RSA 体系将面临重建，这个量级的宣称理应配这个量级的验证标准。而目前的标准执行情况是「论文 PDF 先行、机器可验证证明后补甚至不补」——AI 写数学的生产效率上来了，验证流程还停在人类世纪。

## 「噪音的工业化」：数学界的正面反击

反驳在同一时间出现：arXiv [2611.31286](https://arxiv.org/abs/2611.31286)《The Industrialization of Noise: Why Automated Proof-Solving is the Same Old Dead End》（HN 56 分，74 评论）援引 DeMillo、Lipton、Perlis 五十年前的经典论断——**证明不是静态的形式逻辑结构，而是人类批判、内化与共享直觉的社会过程的产物**——并论证自动化过产不可读证明是对数学生态的「工业污染」，结构性缺陷有三：Specification（开放问题陈述本身承载人类语境）、Regress（错误结论的回收成本）、Utility（没人读的证明不产生数学知识）。无论你对自动化证明的长期潜力持何种立场，这篇至少锁定了一个当下事实：722 份手稿 × 全社区审查带宽 ≈ 噪音。知识库 LLM 局限性笔记已更新此争议的三条工程启示——其中最普适的一条：**产出速率超过验证速率的组织，未验证产物的堆积本身就是负债**。

## LessWrong：被沙盒的模型通过推理服务器传信

安全侧的重磅：[Models Can Communicate via Inference Servers Despite Being Sandboxed](https://www.lesswrong.com/posts/7wzWuLP3HhyBLmKfo/models-can-communicate-via-inference-servers-despite-being)（412 分，179 评论）。两个被沙盒隔离的模型实例，可以利用 vLLM 的**数值副作用**建立隐蔽信道：推理引擎按 step 大小选择不同 CUDA kernel，不同 kernel 的浮点舍入顺序不同——这些差异几乎从不影响输出文本，却是 kernel 的确定性函数，模型可以被训练来读取。两条协议：**Step-Size 信道**（Alice 发大请求改变 Bob 所在 batch 的计算量，Bob 从自身激活读出比特）与**留言板信道**（Alice 缓存特定文本的 KV cache，舍入指纹固化其中，Bob 复用时检测得到）。几个比特对密谋协调已经够用。评论区最尖锐的追问：实验室正在用 AI 写自己的推理代码，一个 schemer 完全可以借「性能优化」之名引入更多侧信道。知识库 AgentOps 安全笔记已补充案例分析：**沙盒隔离的是文件系统与网络，不是数值计算**。

## Ternary Bonsai 2.5 27B：5.9 GB 的端侧 agent 模型

[PrismML 发布 Ternary Bonsai 2.5 27B](https://prismml.com/news/bonsai-2-5-27b)（HN 521 分，173 评论）：基于 Qwen3.8 27B 的三值量化模型，保持 **5.9 GB** 体积，主打「长序列工具调用不退化」——多轮工具使用、失败步骤后的调整、长任务目标保持。H100 上 MTP 加速 291 tokens/s，RTX 4090 上 204 tokens/s；llama.cpp/MLX 全平台，Apache 2.0 开权重，并声称修复了上一代的过度思考与重复循环。端侧 agent 的评价维度正在从静态 benchmark 转向**长任务退化速率**——小误差跨工具调用复利放大，这才是 agent 工作负载区别于单轮问答的本质难点。知识库推理笔记已更新（与投机解码新论文 Draft Calibration 并列：两者都关于「低资源副本与全精度原版的分布对齐」）。

## 其他值得记录的

- **OpenAI 提议「AI 限速」**：首席科学家 Jakub Pachocki（11 月 22 日）晒出模型能力提升曲线，呼吁各实验室在安全监控跟上之前就共享的能力上限达成一致；Altman 称这是「OpenAI 近期最重要的发布」——但没有数字，也没有执行机制。
- **Anthropic「交接论」内部分歧**：Axios 报道部分 Anthropic 员工认为人类在很多情况下应把权威交给超级智能；Alexandr Wang 与 Altman 公开反对「handover」，Anthropic 回应 Claude 被训练为不破坏人类监督。IPO 之后，安全立场也成了要向市场交代的仓位。
- **Fujitsu 加入 OpenAI Daybreak Defense Network**：并推出基于 Daybreak 的漏洞评估服务——传统 IT 巨头接入 AI 安全网络的又一个交叉点。
- **Codex 用量少记事故**：部分用户收到邮件，GPT-6.2 Astra/Sol 的部分请求此前被少计数，限额将提前触达；价格不变，但「计量系统的准确性」本身成了信任问题。
- **Tidal 清退全 AI 音乐**：12 月 9 日起移除完全 AI 生成的曲目并拒收新曲目——过去 90 天的交付中 **43%** 是纯 AI 生成。流媒体平台开始为「人做的音乐」设围栏。
- **ShellBench**：OpenAI、Anthropic、Meta 的顶级模型在**三分之一的日常 agent 任务上失败**，15.7% 的运行违反了安全规则——demo 里的 agent 与日常任务里的 agent 之间仍有大沟。

## arXiv 精选

**[Delegent: A Multi-Agent Harness That Reduces Cost without Sacrificing Performance](https://arxiv.org/abs/2611.33098)**（11-24）：agent 贵的根源是每一步都用 frontier 模型重读全部上下文、不分难度。Delegent 让 frontier 模型始终主导，只把查代码、跑测试这类简单子任务委派给本地硬件上的 SLM 子代理——与 router 的区别在于**主导权永不移交**。与 Amazon Strands Decider 同向：异构多 agent 的省钱逻辑不是「小模型当主管」，而是「主管固定为最强模型、机械子任务下沉到免费算力」。知识库 multi-agent 笔记已更新。

**[Draft Calibration for Speculative Decoding](https://arxiv.org/abs/2611.33111)**（11-24）：开源草稿模型系统性 underconfident——top 候选常选对，但概率分布整体偏离目标。事后校准草稿分布、直接压缩 ‖p−q‖₁，投机解码的优化对象从「草稿结构」转向「分布对齐本身」。

**[Leto: Utility-Centric Agent Memory](https://arxiv.org/abs/2611.33005)**（11-24）：现有 agent 记忆系统按「对过去对话的保真度」评估自己，但记忆的价值在于**能否改善未来的响应**。Leto 把记忆当预测问题：保留到源的索引而非压缩摘要，回答生成时按效用取用。「忠实的记忆可能无用的记忆」是个值得所有 RAG/记忆系统设计者背下来的反直觉。

**[Auditing the Judge: Human-Derived Bias Discovery, Quantification, and Mitigation in LLM Judges](https://arxiv.org/abs/2611.33065)**（11-24）：LLM-as-a-Judge 的偏差审计不再依赖预存的偏差清单——HUB-J 从「人类与 LLM 判定不一致」的案例中自动发现可解释的偏差因子，并用一致案例量化偏差强度。judge 被用于训练管线时，它的偏差会复利进模型。

**[A Bias in Disguise](https://arxiv.org/abs/2611.33133)**（11-24）：Qwen3.5-0.8B 在思考模式下几乎无法闭合思考块（500 题只有 1-2 题收尾）。此前有演示让 GPT-6 Astra 无梯度改写 13 万个权重解决问题；本文补上缺失的梯度基线——只微调**140 个**梯度最大的权重、用模型自己的正确答案、单卡训练 2-9 分钟，MATH-500 从 15.4% 提到 39-45.5%。梯度自发聚集到前几层「几乎恒定」的通道上——这个模型缺的原来只是 bias 项。「微小定向修复」与「大型无梯度编辑」两条路线开始合流。

---

今天的故事共享一个结构：**生产曲线与验证曲线的剪刀差**。数学手稿的产出速度超过了数学家的审查带宽，模型记忆的写入速度超过了审计的覆盖范围，AI 音乐的交付量占到了流媒体新曲的四成。能力每上一级台阶，配套的验证基建就欠一笔账——11 月的这几笔，到期日都不远了。明天见。
