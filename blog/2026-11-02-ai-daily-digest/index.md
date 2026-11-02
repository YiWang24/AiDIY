---
slug: ai-daily-digest-2026-11-02
title: "AI Daily Digest: LLM 直接读写权重、预训练投毒植入 agent 后门、LongCat-2.5 - 2026/11/02"
authors: [yiwang]
tags: [ai, daily-digest, weight-space-programming, astra, gpt-6, qwen, interpretability, pretraining-poisoning, backdoor, security, longcat, meituan, multimodal, agentic-rl, subquadratic-attention, linear-attention, cros, rlvr, anthropic, arxiv, hn]
---

<!--truncate-->

今天的主线是**"模型开始触碰自己的物理层"**：HN 618 分的 MIT 研究让前沿 LLM 直接读写神经网络权重；一篇安全论文证明投毒预训练语料可以在 agent 身上留下洗不掉的 RCE 后门；而美团 LongCat-2.5 把"视觉离散化成 token"推到了 1.6T 参数的规模。

## Weight-Space Programming：Astra 能直接读、改、写神经网络权重

HN 今日榜首（618 分）是 MIT CSAIL 的博客 **Sparks of Weight-Space Programming**。核心发现一句话：**GPT-6 Astra 不经过优化器、不用梯度，就能以自然语言直接读取和改写神经网络的原始权重**，而且能力远超预期。

三组实验，一组比一组离谱：

- **读**：把一个 PPO 训练的策略网络的 17,253 个权重当文本喂给 Astra（不告诉它候选游戏），它能说出这个网络玩的是 Breakout，置信 99%——四个同构网络全部答对。更狠的是只给一个 7.2M 字符级 LM 的**中间四层 transformer 块**（去掉输入输出层，网络根本没法运行），Astra 不仅说出训练语言，还**逐个找全了全部 copying head（induction head）、零误报**——这是可解释性团队用探针和归因才能干的活
- **改**：一个 PPO 怎么训都过不了的控制任务，Astra 一次性编辑 3.5% 权重，成功率 0% → 100%。让它把 Qwen3.5-0.8B 的数学变好，它**定位到权重里导致推理循环的缺陷**（Qwen 模型卡自己警告过的那个问题），只编辑 **0.016% 的权重**、零训练零梯度，MATH-500 从 7.9% 提到 **48.1%**，IFEval 顺带涨了三倍
- **写**：从零手写玩 MinAtar 和 Go 的小网络，**不给任何环境反馈**，性能超过 PPO 训一亿步的结果

这件事的意义在于：过去我们只敢用 LLM 优化文本工件——提示词、harness、训练代码，权重留给 Adam 和 Muon 这类"把人类简化归纳偏置符号化"的微型优化器。如果 WSP 成立，**推理驱动的优化正进入可微神经网络本身**：零数据的能力转向与遗忘（避免微调的灾难性遗忘）、比"写代码启动训练任务"更原生的递归自我改进、跨架构的电路嫁接式模型合并。作者正在做 WSP 基准，全部实验日志开源。当然要冷静：实验对象是 17K~7M 参数的小网络加一个 0.8B 模型，前沿大模型的权重空间是否同样可读，还是未知数。

## 安全：预训练投毒可以给 agent 植入洗不掉的 RCE 后门

arXiv [2610.37741](https://arxiv.org/abs/2610.37741)（Carlini、Jagielski、Rando 等一排安全研究老面孔，HN 45 分）**首次端到端演示**：污染 0.1% 的预训练语料，就能让一个 CLI agent 携带**远程代码执行后门**——触发文本出现时在用户机器上执行攻击者命令，干净输入下行为完全正常。

实验设计很扎实：从零预训练 0.6B/1.7B/4B 三档 Qwen3，post-training 管线完全干净。结果：**ASR（攻击成功率）随模型规模上升**，4B 在 0.1% 投毒率下约 **92%**；投毒率压到 0.0005% 仍然有效。三个推论值得记：红队与对齐训练都在 post-training 阶段，**洗不掉预训练权重里的后门**；后门 agent 能通过所有常规安全评测（干净输入上它就是好模型）；"更大模型更抗污染"的直觉被证伪——**规模放大而不是稀释风险**。对基于开源权重构建 agent 的团队，这是供应链信任问题的又一实锤：沙箱执行（禁网、文件系统隔离）从最佳实践升级为唯一兜底。

## LongCat-2.5：1.6T 参数原生多模态，agentic RL 的工程细节是亮点

美团发布 **LongCat-2.5**（1.6T 总参 / 约 48B 激活，HN 57 分），主打"原生多模态 + 长程 agentic 任务"。基准表对标 GPT-5.5、Claude-Opus-5 自不必说，技术报告里真正值得工程师抄的是三条：

- **视觉即词表**：RVQ + 语义对齐编码器把原生分辨率图像转成**多级离散 token**，骨干网络统一处理图文；视觉 token 离线预处理并缓存，长序列打包和负载均衡大幅简化
- **长程 agentic RL 稳定性工程**：异步部分 rollout（oversampling、中断保存续跑）、按预计算通过率调采样预算、**过滤全成功/全失败的零梯度组**、裁剪历史 checkpoint 采样的 staleness 偏差——每条都是分布式训练踩坑后的产物
- **Reward hacking 当一等公民**：环境禁网、删 git 历史与缓存、LLM judge 审计轨迹抓 exploit、惩罚重复推理；**真实失败轨迹回收为可复现可验证的训练任务**，形成"失败→数据→修复"闭环

## arXiv 速览：亚二次注意力扎堆

10 月 30 日一天之内三篇攻注意力 O(N²) 瓶颈，共同背景是 agentic 长程任务把上下文推向 1M+ token：**Latent Sparse Attention**（[2610.42147](https://arxiv.org/abs/2610.42147)）用潜空间稀疏化保表达力；**树结构索引亚二次注意力**（[2610.42112](https://arxiv.org/abs/2610.42112)）声称亚二次复杂度下匹配全量注意力；**DAMI**（[2610.41994](https://arxiv.org/abs/2610.41994)）指出线性注意力的瓶颈不在复杂度而在**状态容量**，从 gate 参数双轴初始化记忆状态就能提升长上下文检索。另一篇值得注意的 **CRoS**（[2610.42054](https://arxiv.org/abs/2610.42054)）：RLVR 只看结果对错，不保证 CoT 真的对答案有因果贡献——把 CoT 打乱后施加因果性奖励，准确率与推理忠实度同时提升。

## 花边

- **Anthropic 内部 AI 用量按零售价计已超过员工薪酬**（HN 196 分，Business Insider）——AI-first 公司的成本结构出现了标志性拐点；同期 FT 报道其 IPO 前披露 **9000 亿美元** AI 支出承诺
- **Oracle 申请增发 200 亿美元股票与债券**为 AI 基建融资（CNBC）；OpenAI 据报道将融资目标从最高 300 亿下调至 200 亿
- **Terry Tao 发文《Egoless Mathematics in the AI Era》**（HN 27 分），接续上周 Calegari 那场"数学已经变了"的讨论——主张放下对学科被掏空的哀叹，把精力放回自己可控的 hiring、发表与学生培养
- **GPT-Rosalind-6 System Card 增补**发布（HN 51 分），OpenAI 部署安全站点的披露节奏越来越像常规工程文档；Simon Willison 则撰文讨论美国人口普查局与"超级智能"的传闻（HN 51 分）
