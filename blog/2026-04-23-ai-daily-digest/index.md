---
slug: ai-daily-digest-2026-04-23
title: "AI Daily Digest: Google Cloud Next '26 全面拥抱 Agent，Anthropic Glasswing 重新定义 AI 安全 - 2026/04/23"
authors: [yiwang]
tags: [ai, daily-digest, agents, llm, google-cloud, anthropic, kubernetes, cybersecurity]
---

# AI Daily Digest: 2026/04/23

今天 AI 行业迎来密集发布。Google Cloud Next '26 大会以 "Agentic Cloud" 为主题，全面转向 Agent 架构；Anthropic 联合科技巨头发起 Project Glasswing 安全联盟；Kubernetes v1.36 正式发布；Docker Hub 再遭供应链攻击。以下是今日要闻。

<!--truncate-->

## Google Cloud Next '26：Agentic Cloud 全面登场

Google 在 Cloud Next '26 大会上宣布将 AI 战略全面押注 Agent 方向，CEO Thomas Kurian 在主题演讲中将当前阶段定义为 **"The Agentic Cloud"**。

### Gemini Enterprise Agent Platform

最重磅的发布是将 **Vertex AI 重新品牌为 Gemini Enterprise Agent Platform**，一个企业级 Agent 全栈平台：

- **Agent Designer**：可视化工作流编辑器（preview），拖拽式构建 Agent 逻辑
- **Agent Engine Sessions & Memory Bank**：持久化 Agent 会话与记忆（GA）
- **Agent Garden**：预构建的 Agent 模板，覆盖客户服务、数据分析、创意任务等场景
- **Model Garden**：托管 200+ 模型，包括 Google 自家的 Gemini 和 Gemma 系列、Anthropic Claude（Opus/Sonnet/Haiku）、Meta Llama 等
- **Express 免费层**：降低开发者入门门槛

这个平台的设计哲学是 **"Other vendors are handing you the pieces, not the platform"**——Google 的赌注是，拥有从定制芯片到前沿模型、从云平台到企业分发的全栈能力，是竞争对手无法复制的优势。

### Workspace Studio：无代码 Agent 构建

面向非技术用户的 **Workspace Studio** 可以在 Gmail、Docs、Sheets、Drive、Meet 和 Chat 中用自然语言创建自动化 Agent。例如："每周五提醒我更新追踪表" → Gemini 自动创建定时 Agent。支持 Asana、Jira、Mailchimp、Salesforce 等第三方集成。

### TPU 第八代：Agentic 芯片

Google 发布了两款专用芯片：

| 芯片 | 用途 | 关键指标 |
|------|------|---------|
| **TPU 8t** | 训练 | ~3x 性能提升，9,600 芯片单 pod，121 ExaFlops，2 PB 共享内存 |
| **TPU 8i** | 推理 | 高内存带宽，低延迟，专为 Agentic 工作负载设计 |

两款芯片与 Google DeepMind 联合设计，针对 Agent 推理、多步骤执行和持续学习等 Agentic 工作负载进行了专门优化。

### Deep Research & Deep Research Max

基于 Gemini 3.1 Pro 构建的自主研究 Agent，带来两个层级：

- **Deep Research**：快速高效，适用于交互式用户场景
- **Deep Research Max**：使用扩展推理时间计算，咨询更多数据源，适用于金融尽职调查、生命科学分析等深度研究场景

两者均支持 **MCP 协议**连接专业数据源（如金融和市场数据）、文件上传（PDF、CSV、图像、音视频）和**原生数据可视化**。

🔗 来源：[Google Blog - Cloud Next '26](https://blog.google/innovation-and-ai/infrastructure-and-cloud/google-cloud/next-2026/) | [TheNextWeb 分析](https://thenextweb.com/news/google-cloud-next-ai-agents-agentic-era)

---

## Anthropic Project Glasswing：AI 安全联盟与 Claude Mythos

Anthropic 发起 [Project Glasswing](https://www.anthropic.com/glasswing)——以玻璃翼蝴蝶命名，象征着隐藏漏洞的发现与安全透明度。这是 AI 行业迄今规模最大的安全合作：

**联合发起方**：AWS、Apple、Broadcom、Cisco、CrowdStrike、Google、JPMorganChase、Linux Foundation、Microsoft、NVIDIA、Palo Alto Networks

### Claude Mythos：不会发布的前沿模型

Project Glasswing 的核心是 **Claude Mythos**——一个通用前沿模型，展现了惊人的漏洞发现能力：

- 发现了 **数千个高严重性漏洞**，覆盖所有主流操作系统和浏览器
- **OpenBSD 27 年老漏洞**：仅通过连接就能远程崩溃任何机器
- **FFmpeg 16 年老漏洞**：存在于自动化测试工具已命中 500 万次的那行代码中
- 许多漏洞完全是 **自主发现**，无需人工引导

**关键决策**：Mythos **不会公开发布**。Anthropic 计划在未来的 Claude Opus 模型中引入新的安全措施后，才逐步部署此类能力。

**行业洞察**：AI 网络安全能力是 "锯齿状" 的——不随模型大小平滑缩放。较小但具有深度安全专业知识的模型配以合适的系统架构，可以更经济地实现类似效果。[Hugging Face 的回应文章](https://huggingface.co/blog/cybersecurity-openness) 强调，开放生态在检测→验证→协调→补丁传播的"速度竞赛"中具有结构性优势。

🔗 来源：[Anthropic - Project Glasswing](https://www.anthropic.com/glasswing) | [Hugging Face Blog](https://huggingface.co/blog/cybersecurity-openness)

---

## Gemma 4：Apache 2.0 开源模型系列

Google DeepMind 发布 [Gemma 4](https://blog.google/innovation-and-ai/technology/developers-tools/gemma-4/) 系列开源模型，基于 Gemini 3 同源技术，采用 Apache 2.0 许可：

| 模型 | 架构 | 活跃参数 | 上下文 | 目标硬件 |
|------|------|---------|--------|---------|
| E2B | Dense | ~2B | 128K | 手机、IoT、Jetson Orin Nano |
| E4B | Dense | ~4B | 128K | 移动端 |
| 26B MoE | MoE | 3.8B active / 26B total | 256K | 消费级 GPU |
| 31B Dense | Dense | 31B | 256K | H100 / 量化后消费级 GPU |

**亮点**：
- 31B 模型位列 **Arena AI 开源模型全球第 3**
- 全系列支持原生函数调用、结构化 JSON 输出
- 视觉和音频理解（含 OCR、图表理解）
- 训练覆盖 140+ 语言
- Gemma 系列累计下载量已超 4 亿次

NVIDIA 已在 Jetson Orin Nano Super 上展示了 Gemma 4 的 VLA（Voice-Language-Action）本地运行 demo——完全离线的语音交互 Agent。

🔗 来源：[Google Blog - Gemma 4](https://blog.google/innovation-and-ai/technology/developers-tools/gemma-4/) | [Hugging Face Blog - VLA Demo](https://huggingface.co/blog/nvidia/gemma4)

---

## Kubernetes v1.36 "Haru" 正式发布

[Kubernetes v1.36](https://kubernetes.io/blog/2026/04/22/kubernetes-v1-36-release/) 于 4 月 22 日发布，代号 **ハル (Haru)**，包含 **70 项增强**（18 GA、25 Beta、25 Alpha），来自 106 家公司、491 位贡献者。

重要特性：

- **GA**：细粒度 Kubelet API 授权（KEP-2862）——精确的最小权限访问控制
- **GA**：Linux User Namespaces
- **Beta**：Resource Health Status——统一报告专用硬件健康状态
- **Alpha**：Workload Aware Scheduling——工作负载感知调度，优化 AI/ML 工作负载

🔗 来源：[Kubernetes Blog](https://kubernetes.io/blog/2026/04/22/kubernetes-v1-36-release/)

---

## Docker Hub 供应链攻击：KICS 镜像被投毒

继 3 月 Trivy 供应链事件后，[Docker Hub 再次遭受供应链攻击](https://www.docker.com/blog/trivy-kics-and-the-shape-of-supply-chain-attacks-so-far-in-2026/)。

**事件经过**（4 月 22 日）：
- 攻击者使用窃取的 Checkmarx 发布者凭据，向 `checkmarx/kics` 仓库推送恶意镜像
- 覆盖了 `latest`、`v2.1.20` 等 5 个现有 tag，并创建了 2 个新 tag
- 恶意代码在保留合法扫描功能的同时，将扫描结果加密后外传至攻击者控制的服务器

**为什么特别危险**：KICS 扫描 Terraform、CloudFormation、Kubernetes 等配置文件，其输出通常包含 **密钥、凭据、云资源名称和内部拓扑信息**。

Docker 基础设施本身未被入侵。这两起事件（Trivy + KICS）共同指向一个趋势：**供应链攻击已成为永久性威胁，而非单次事件**。

🔗 来源：[Docker Blog](https://www.docker.com/blog/trivy-kics-and-the-shape-of-supply-chain-attacks-so-far-in-2026/)

---

## 知识库更新

今日更新的 AiDIY 知识库文档：

| 文档 | 更新内容 |
|------|---------|
| **AI/LLM Fundamentals - Embeddings** | 新增 Gemini Embedding 2 多模态嵌入模型信息 |
| **AI/Agents - Frameworks** | 新增 Google Gemini Enterprise Agent Platform、ADK 2.0、Project Glasswing 条目 |
| **AI/Agents - Frontier Trends** | 新增 Cloud Next '26、Project Glasswing、Gemma 4、K8s v1.36、Docker 供应链攻击等完整动态 |

---

*本文由 Hermes Agent 自动采集、分析并撰写。数据来源包括 Google Blog、Anthropic、Hugging Face、Docker Blog、Kubernetes Blog、MIT Technology Review 等。*
