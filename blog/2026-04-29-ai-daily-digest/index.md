---
slug: ai-daily-digest-2026-04-29
title: "AI Daily Digest: IBM Granite 4.1 开源发布，AI 评估成本成新瓶颈，Kimi K2.6 登陆全球平台 - 2026/04/29"
authors: [yiwang]
tags: [ai, daily-digest, ibm, granite, evaluation, kimi, moonshot, agents, llm, open-source]
---

# AI Daily Digest: 2026/04/29

今日 AI 行业迎来多个重要进展。IBM 发布 Granite 4.1 开源 LLM 系列，用 5 阶段渐进式训练让 8B dense 模型匹配上一代 32B MoE 的性能。Hugging Face EvalEval 联盟发布深度报告，揭示 AI 评估成本已与训练成本相当，成为行业新瓶颈。Moonshot AI 的 Kimi K2.6 正式登陆 Cloudflare Workers AI 和 Microsoft Foundry，开源编码模型竞争白热化。

<!--truncate-->

## IBM Granite 4.1：渐进式训练让小模型击败大模型

IBM 于 4 月 29 日发布 **Granite 4.1** 系列开源 LLM（Apache 2.0 许可），包含 3B、8B 和 30B 三个 dense 模型，基于 ~15T tokens 的 **5 阶段渐进式预训练** 流程。

### 核心亮点

- **8B dense 匹配 32B MoE**：8B instruct 模型在多项基准上匹配甚至超越上一代 Granite 4.0-H-Small（32B-A9B MoE），证明精心设计的训练流程可以弥补参数规模差距
- **5 阶段渐进式预训练**：
  1. 通用预训练（10T tokens）—— 59% CommonCrawl + 20% Code + 7% Math
  2. Math/Code 强化（2T tokens）—— Math 占比提升 5 倍
  3. 高质量退火（2T tokens）—— 引入 Long CoT 和指令数据
  4. 退火精炼（0.5T tokens）—— 线性 LR 衰减至零
  5. 长上下文扩展（4K → 32K → 128K → 512K）—— 每阶段使用模型合并保持短上下文性能
- **4 阶段 RL 训练**：Multi-Domain RL → RLHF → Identity/Knowledge Calibration → Math RL，使用 On-policy GRPO + DAPO loss
- **SFT 质量控制**：LLM-as-Judge 框架，6 维加权评估 + 硬拒绝规则

### 技术架构

采用 GQA + RoPE + SwiGLU + RMSNorm + shared embeddings 的现代 dense transformer 设计。RL 训练使用 SkyRL 框架，每个 prompt 采样 16 次进行 on-policy 学习。

**行业意义**：Granite 4.1 的"数据质量优于数量"理念与当前行业"认知密度优于参数规模"的趋势高度吻合。Apache 2.0 许可使其成为企业级自托管场景的优质选择，特别是在金融、医疗等对数据隐私要求严格的领域。

🔗 来源：[Hugging Face Blog](https://huggingface.co/blog/ibm-granite/granite-4-1) | [GitHub](https://github.com/ibm-granite/granite-4.1-language-models) | [Hugging Face Models](https://huggingface.co/collections/ibm-granite/granite-41-language-models)

---

## AI 评估成本：正在成为新的计算瓶颈

Hugging Face 的 EvalEval 联盟发布了一份详尽的报告，揭示了一个令人不安的趋势：**AI 评估成本正在追赶甚至超过训练成本**。

### 关键数据

| 评估项目 | 成本 | 备注 |
|----------|------|------|
| HAL（Agent Leaderboard） | ~$40,000 | 21,730 个 Agent rollout |
| GAIA 单次前沿模型运行 | $2,829 | 缓存前 |
| MLE-Bench 完整运行 | ~$100,000 | 75 竞赛 × 3 seeds × 6 模型 |
| PaperBench 单次评估 | ~$9,500 | 20 篇 ICML 论文复现 |

### 核心发现

1. **更高花费 ≠ 更好结果**：在 Online Mind2Web 基准上，花费 $1,577 的方案仅获 40% 准确率，而花费 $171 的方案获 42%
2. **Agent 基准压缩困难**：静态基准可压缩 100-200×（如 Flash-HELM），但 Agent 基准仅能压缩 2-3.5×，因为长轨迹是不可压缩的成本对象
3. **评估成为乘数**：对于小模型，评估计算可能在模型整个开发周期中占据主导地位
4. **价格差距悬殊**：Claude Opus 4.1 输入 $15/M tokens vs Gemini 2.0 Flash $0.10/M tokens，100 倍差距

### 行业影响

评估成本高企将评估能力集中在少数资金充足的实验室，形成"评估垄断"。开源社区和中小型实验室难以负担全面的模型评估，这可能导致：
- 模型质量评估不充分
- 开源模型在排行榜上被低估
- 行业创新被资金壁垒限制

报告建议行业需要类似 NAS-Bench-101 的"评估评估"基础设施，通过标准化和共享来降低评估门槛。

🔗 来源：[Hugging Face Blog - EvalEval](https://huggingface.co/blog/evaleval/eval-costs-bottleneck)

---

## Kimi K2.6：开源编码模型登陆全球平台

Moonshot AI 的 **Kimi K2.6** 在 4 月 19 日发布后，本周迅速扩展全球部署渠道：

- **Cloudflare Workers AI**：K2.6 已上线 Cloudflare 的边缘推理平台，支持全球低延迟访问
- **Microsoft Foundry**：纳入 Microsoft 的 AI 模型市场，面向企业级用户
- **Moonshot 开放平台**：提供 API 接入，附赠两周充值优惠

### 模型规格

- **架构**：~1T 参数 MoE，32B 活跃参数
- **上下文**：262K tokens
- **能力**：原生多模态（视觉+文本），开源 SOTA 编码能力，Agent 优化
- **开源**：模型权重已开放

Kimi K2.6 的快速平台化部署体现了中国 AI 模型"走出去"的趋势——不再仅限于本土市场，而是积极接入全球主流 AI 基础设施。

🔗 来源：[Cloudflare Changelog](https://developers.cloudflare.com/changelog/post/2026-04-20-kimi-k2-6-workers-ai/) | [Microsoft Foundry](https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/introducing-kimi-k2-6-in-microsoft-foundry/4513125) | [Moonshot Forum](https://forum.moonshot.ai/t/meet-kimi-k2-6-advancing-open-source-coding/369)

---

## DeepSeek V4 生态持续扩展

自 4 月 24 日发布以来，DeepSeek V4 的生态支持快速扩展：

- **DeepInfra**：V4-Pro-Max 已上线，定价 $174/M tokens；V3.2 仅 $26/M tokens
- **Fireworks AI**：已支持 V4 系列
- **Novita AI**：提供 V4 推理服务
- **华为 Ascend 芯片兼容**：华为已确认 V4 模型可在 Ascend 芯片上运行

V4 的 Hybrid Attention 架构（CSA + HCA）使 KV cache 降至传统 GQA 的 2%，让 1M token 上下文在经济上可行。API 同时支持 OpenAI ChatCompletions 和 Anthropic 两种格式。

⚠️ **注意**：DeepSeek 宣布 `deepseek-chat` 和 `deepseek-reasoner` 将于 2026 年 7 月 24 日正式下线，届时将自动路由到 V4-Flash。

🔗 来源：[DeepSeek API Docs](https://api-docs.deepseek.com/news/news260424) | [AP News](https://apnews.com/article/deepseek-ai-china-gpt-v4-d2ed33f2521917193616e061674d5f92)

---

## Kubernetes v1.36 "Haru" 发布

Kubernetes v1.36 于 4 月 28 日发布，代号 "Haru"（春），包含 70 项增强：

- **GA**：细粒度 Kubelet API 授权、Linux User Namespaces
- **Beta**：Resource Health Status（硬件健康状态报告）
- **Alpha**：Workload Aware Scheduling（工作负载感知调度）

User Namespaces 的 GA 化是一个重要里程碑，它为容器提供了用户身份隔离，显著提升了多租户 Kubernetes 集群的安全性。

🔗 来源：[Kubernetes Blog](https://kubernetes.io/blog/2026/04/28/kubernetes-v1-36-staleness-mitigation-for-controllers/)

---

## DeepInfra 登陆 Hugging Face Inference Providers

Hugging Face 宣布 **DeepInfra** 成为其新的推理提供商，用户可以直接在 Hugging Face 平台上通过 DeepInfra 运行模型。DeepInfra 支持 56 个模型，价格从 $0.01/M tokens 起步，包括 DeepSeek V4-Pro-Max、Qwen3.6-27B 等热门开源模型。这进一步降低了开源模型的使用门槛。

🔗 来源：[Hugging Face Blog](https://huggingface.co/blog/inference-providers-deepinfra)

---

## 知识库更新

今日更新了以下知识库文档：

- **LLM 基础 — 模型概览**（`docs/ai/llm-fundamentals/01-introduction.mdx`）：新增 Kimi K2.6、Granite 4.1 到开源模型表，新增企业自托管推荐选项
- **AI Agent 前沿趋势**（`docs/ai/agents/10-frontier.mdx`）：新增 IBM Granite 4.1 发布详情、AI 评估成本瓶颈分析、Kimi K2.6 模型信息、Granite 4.1 到模型发布格局列表
