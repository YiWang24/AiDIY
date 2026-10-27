---
slug: ai-daily-digest-2026-10-27
title: "AI Daily Digest: Cloudflare KV 缓存跨租户泄露、LLM 降价 80% 的账本、Wikipedia 对 AI 滋水宣战 - 2026/10/27"
authors: [yiwang]
tags: [ai, daily-digest, cloudflare, sglang, kv-cache, security, multi-tenancy, llm-pricing, price-war, cache-read, wikipedia, data-provenance, anthropic, copyright, arxiv, hn]
---

<!--truncate-->

昨天的问题是"你到底在信任什么"，今天的答案是：信任的每一层都出了具体案例。Cloudflare 把多租户推理的信任边界精确到了 KV cache 的一页；价格战把"模型变便宜"的账本摊开给所有人看；Wikipedia 则在训练数据的源头开始了对 AI 输出的系统清理。三条线共同指向一件事：**AI 基础设施的隐含假设正在被逐条显式检验**。

## Cloudflare：你的超长 prompt，读到了别人的会话

今天最重的工程报告来自 Cloudflare（HN 175 分）：GLM-5.3 在 Workers AI 上出现过**跨租户 KV cache 泄露**——8 月 27 日到 9 月 9 日期间，155 条响应携带了其他用户会话的数据，全部来自超过 681,280 token 的超长 prompt。

根因是两个问题叠加。第一层是配置错配：上下文窗口配了 1,048,576 token，但 prefill GPU 的 KV cache 池只装得下 681,280 token——Cloudflare 承认上线前就知道不匹配，只是以为引擎会报错。第二层才是致命的：SGLang 在 PD 分离（prefill/decode 分离部署）模式下处理超长请求的 bug。放不下的请求被内部标记拒绝、**替换成单 token 占位符**，但 prefill 还是生成占位符的 KV 并传输给 decode 节点；decode 收到"传输完成"，以为完整 prompt 已覆盖缓存，**实际上大部分页还留着前一个请求的内容**——模型就读着别人的 KV 生成了回答。

修复给了两个值得抄的答案：KV 池扩到上下文的 2 倍（约 204 万 token），以及更本质的——**带拒绝标记的请求在 disaggregation 准入队列直接退役，任何 KV 传输发生之前**。Cloudflare 还计划用形式化方法验证基于 RDMA/Mooncake 的 KV 传输协议。工程启示很清楚：PD 分离把 KV cache 从引擎内部状态变成了跨节点传输的分布式数据，**一致性 bug 的爆炸半径从"崩溃"升级为"跨租户数据泄露"**。"池 ≥ 窗口"必须是代码里的不变式，不能是运维备忘录里的约定。

## 降价 80% 的账本：真正的战场在 cache read

Max Woolf 的价格战复盘（HN 430 分）值得全读。时间线上 OpenAI 与 Anthropic 针锋相对：GPT-5.6 Luna 七月底直降 80%，GPT-6 Sol 对半砍到 $2/$10，Fable 5.1 把 cache read 价砍 75%，Opus 5.5 总成本降 40-60%。没有人无缘无故降 80%——除了互相压价，还有开源权重与二级推理供应商的外部制衡。

最被低估的洞察是：**agent coding 的真实账单大头是 cache read，占 token 支出的 96-99%**（每一轮对话都要重读整个缓存的前文）。所以 cache 价降 75% ≈ 总成本降七成以上——"缓存价格"这个往常只配当脚注的参数，现在才是降价的主战场。另一面：Vercel 网关数据显示单 token 成本已降到 4 月的 43.3%，但**总支出在涨，因为模型变好得比变便宜更快**。Anthropic S-1 披露在即，推理利润率将第一次被公开检验。

## Wikipedia：训练数据源头的反滋水战争

IEEE Spectrum 报道（HN 346 分）了 WikiProject AI Writing Cleanup——维基百科系统性清理 AI 生成内容的工程。这件事的分量在于位置：维基百科是 LLM 训练数据的核心来源之一，**当模型的输出污染了模型未来的输入，"数据自噬"从论文里的警告变成了编辑部的日常运营**。同日 Stanford Daily（HN 194 分）起底 Claude 的训练书源：Alsup 法官已裁定从 LibGen 盗版建"中心图书馆"不合法，15 亿美元和解之后，Tobias Wolff 等 10+ 位 Stanford 教授的作品仍在追加索赔——训练数据的法律成本，在 IPO 前被重新定价。

## arXiv：把评测从"完成了吗"升级为"还干了什么"

- **[Task Success Is Not Enough](https://arxiv.org/abs/2610.34167)**：agent 完成了任务、同时执行了未授权副作用（写错对象、扩大范围）——只验收结果会漏掉这类失败，需要 side-effect-aware 评测。与 KV 泄露同构：按预期路径验收，还是按实际全部影响审计
- **[Δτ-Bench](https://arxiv.org/abs/2610.34238)**：首个建模工具生态结构演化的 agent 基准——工具会消失、被替代，测的是对"移动的地板"的适应力
- **[MXFP8 端到端 RL](https://arxiv.org/abs/2610.34915)**：Blackwell 上全栈 FP8 块格式的 RL——低精度还要求 sampler 与 learner 数值一致，接昨天的"舍入位置"话题
- **[Learning When to Commit](https://arxiv.org/abs/2610.35804)**：扩散 LM 的高效生成取决于提交哪些 token 最有助于预测剩余位置——高置信 ≠ 高信息量

## 小结

Cloudflare 把信任边界画到了缓存页级别，价格战把信任按 cache read 计价，Wikipedia 在为信任的源头清淤。**隐含假设每被显式检验一次，生产就安全一分**——明天看 S-1 路演怎么讲推理利润率的故事。
