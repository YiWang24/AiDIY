---
slug: ai-daily-digest-2026-04-28
title: "AI Daily Digest: OpenAI 脱绑 Microsoft，NVIDIA 开源多模态 Agent 模型，DeepSeek V4 引领效率革命 - 2026/04/28"
authors: [yiwang]
tags: [ai, daily-digest, openai, microsoft, nvidia, deepseek, agents, llm, multimodal]
---

# AI Daily Digest: 2026/04/28

今日 AI 行业迎来多个重磅事件。OpenAI 与 Microsoft 正式结束独家合作关系，OpenAI 的 IP 许可变为非独占——这标志着 AI 行业从"绑定巨头"走向多云开放时代。NVIDIA 发布 Nemotron 3 Nano Omni，一个统一视觉、音频和语言的开源多模态模型，专为 Agent 感知设计。DeepSeek V4 的技术细节进一步揭示：Hybrid Attention 架构将 KV cache 压缩至传统 GQA 的 2%。同时，Google 将 Agent Payments Protocol 捐赠给 FIDO Alliance，为 AI Agent 的商业支付建立安全标准。

<!--truncate-->

## OpenAI 与 Microsoft 结束独家合作

OpenAI 与 Microsoft 在 4 月 27 日宣布修改多年来的合作协议，**结束独家绑定关系**。关键变化包括：

- **非独占许可**：Microsoft 对 OpenAI IP 的许可证从独占变为非独占，有效期至 2032 年
- **多云开放**：OpenAI 现可在所有云平台（包括 AWS、Google Cloud 等）提供产品和服务
- **收入分流转**：Microsoft 不再向 OpenAI 支付收入分成；OpenAI 向 Microsoft 的收入分成持续至 2030 年，设有总额上限
- **Azure 仍是首选**：Azure 仍为 OpenAI 的主要云合作伙伴，产品优先在 Azure 上线

**影响分析**：这是 AI 行业格局的重大转折。此前 Microsoft 凭借独家合作成为 OpenAI 唯一的云基础设施提供商，获取了巨大的战略优势。现在 OpenAI 可以自由地在 AWS、Google Cloud 等平台上部署服务，这意味着 AI 模型将成为真正的"多云产品"。对于企业用户而言，这降低了供应商锁定的风险。

🔗 来源：[OpenAI Blog](https://openai.com/index/next-phase-of-microsoft-partnership/) | [Reuters](https://www.reuters.com/legal/litigation/microsoft-end-exclusive-license-openais-technology-2026-04-27/)

---

## NVIDIA Nemotron 3 Nano Omni：开源多模态 Agent 模型

NVIDIA 于 4 月 28 日正式发布 **Nemotron 3 Nano Omni**，一个统一视觉、音频和语言的开源多模态模型，专为 Agent 子系统设计：

- **架构**：30B 总参数，3B 活跃参数（MoE），集成视觉和音频编码器
- **性能**：在六个文档智能、视频和音频理解排行榜上夺冠
- **效率**：比同类开放全模态模型吞吐量高 **9 倍**
- **原生 1080p**：1920×1080 分辨率输入，专为 Computer Use Agent 优化
- **开放获取**：Hugging Face、OpenRouter、NVIDIA NIM 均可获取

**亮点**：该模型最大的创新在于**消除了多感知模型拼接**。传统方案需要分别部署 OCR 模型、ASR 模型和语言模型，而 Nemotron 3 Nano Omni 将三者统一到单一推理流程中，在减少延迟、成本和上下文碎片化方面有显著优势。Nemotron 3 系列过去一年下载量已超 5000 万次。

🔗 来源：[NVIDIA Blog](https://blogs.nvidia.com/blog/nemotron-3-nano-omni-multimodal-ai-agents/) | [Hugging Face](https://huggingface.co/blog/nvidia/nemotron-3-nano-omni-multimodal-intelligence)

---

## DeepSeek V4 技术细节：Hybrid Attention 的工程突破

随着 DeepSeek V4 在 4 月 24 日发布后的持续热议，更多技术细节浮出水面。MIT Technology Review 分析了 V4 重要的三个原因：

**1. 开源模型的性能巅峰**：V4-Pro 在 Agentic Coding 基准上达到开源 SOTA，匹配 Claude Opus 4.6 和 GPT-5.4 等闭源顶级模型。在 85 名资深开发者调研中，超 90% 将 V4-Pro 列为编码任务的首选模型之一。

**2. Hybrid Attention 架构**：V4 的核心创新是两种注意力机制的交替使用：
- **CSA（Compressed Sparse Attention）**：4 倍序列维度压缩，带闪电索引器选择 top-k 压缩块
- **HCA（Heavily Compressed Attention）**：128 倍压缩，密集注意力
- 实测效果：KV cache 仅为传统 GQA 的 **2%**，1M token 上下文的计算量降至前代的 27%

**3. 首次适配国产芯片**：V4 是 DeepSeek 第一个针对华为 Ascend 芯片优化的模型，早期访问仅对中国芯片厂商开放。MIT Tech Review 指出，如果这一路径成功，将是中国建立平行 AI 基础设施的早期信号。

**API 定价**：V4-Pro 输入 $1.74/M tokens，V4-Flash 约 $0.14/M tokens，使百万 token 级推理成为经济可行的选择。

🔗 来源：[MIT Technology Review](https://www.technologyreview.com/2026/04/24/1136422/why-deepseeks-v4-matters/) | [Hugging Face Blog](https://huggingface.co/blog/deepseekv4) | [DeepSeek API Docs](https://api-docs.deepseek.com/news/news260424)

---

## Google 捐赠 Agent Payments Protocol 给 FIDO Alliance

Google 将 **Agent Payments Protocol (AP2)** 捐赠给 FIDO Alliance，推动 AI Agent 支付的标准化和安全性：

- AP2 结合现代区块链（如 Sui）与开放协议（A2A、MCP），建立 Agent 驱动商业的安全框架
- Mastercard 同步宣布与 Google 合作，将 Passkeys 作为 AI 支付的核心验证机制
- OpenAI 也已加入 FIDO Alliance，共同推动 AI Agent 认证标准

**行业意义**：随着 AI Agent 越来越多地参与商业决策（如自动采购、服务订阅、资源调配），安全的 Agent 支付基础设施变得至关重要。将协议捐赠给标准组织而非保留私有，体现了行业对开放标准的共识。

🔗 来源：[Google Blog](https://blog.google/products-and-platforms/platforms/google-pay/agent-payments-protocol-fido-alliance/) | [FIDO Alliance](https://fidoalliance.org/mastercard-ai-payments-passkeys-fido-alliance/)

---

## Musk v. Altman 庭审正式开始

Elon Musk 诉 Sam Altman 一案于 4 月 27 日在加州奥克兰联邦法院正式开庭。9 人陪审团已组建完毕，开庭陈述已进行。本案核心争议在于 OpenAI 是否背离了其最初的非营利使命——Musk 主张 OpenAI 已从"为人类利益开源"转变为"为 Microsoft 利益闭源"。多位科技界重量级人物预计将出庭作证。

🔗 来源：[AP News](https://apnews.com/article/musk-altman-artificial-intelligence-trial-openai-eb854fa682675f70267abd8a7b9a6a43) | [CNBC](https://www.cnbc.com/2026/04/27/musk-altman-trial-openai-jury-selection.html)

---

## Google × Kaggle：AI Agents Vibe Coding 课程

Google 与 Kaggle 联合宣布将于 **6 月 15–19 日**举办免费的 5 天 AI Agents Intensive Vibe Coding 课程。参与者将学习使用 Gemini 构建 Agent，涵盖生产级 Agent 开发的全流程。这是 Google 推动 Agent 开发者生态的重要举措。

🔗 来源：[Google Blog](https://blog.google/innovation-and-ai/technology/developers-tools/kaggle-genai-intensive-course-vibe-coding-june-2026/)

---

## 知识库更新

今日更新了以下知识库文档：

- **AI Agent 前沿趋势**（`docs/ai/agents/10-frontier.mdx`）：新增 OpenAI-Microsoft 合作变更、NVIDIA Nemotron 3 Nano Omni 发布、Google AP2 协议捐赠、Musk v. Altman 庭审等内容
