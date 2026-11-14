---
slug: ai-daily-digest-2026-11-14
title: "AI Daily Digest: Lovable 15.9 万项目数据暴露、Google /teamwork 多智能体科研、双 DGX 跑 GLM-5.3 峰值 607 tok/s - 2026/11/14"
authors: [yiwang]
tags: [ai, daily-digest, security, vibe-coding, supabase, rls, multi-agent, antigravity, teamwork, vllm, glm, inference, hn, arxiv]
---

<!--truncate-->

今天的三个事件各自标定了一条工程边界：**vibe coding 平台的默认权限配置**（Crissy Field 审查 15.9 万个 Lovable 项目，7,403 个站点的数据库记录无需登录即可读取）、**多智能体科研系统的两个核心机制**（Google /teamwork：专职证伪者 + 按构造分区上下文）、**前沿模型的桌面级部署天花板**（NVIDIA 用两台 DGX Station 把 464 GB 的 GLM-5.3 跑到峰值 607.8 tok/s）。三条线索合起来读：AI 工程的竞争正在从「模型能做什么」转移到「默认配置是什么」。

## Lovable 15.9 万项目审查：「一模式一漏洞」的时代

安全公司 Crissy Field 与 Handelsblatt 合作，对 Common Crawl 里 **159,041 个 Lovable 项目**（2025-12 至 2026-09）做了系统审查：34,545 个使用 Supabase，其中 **24,664 个网站在页面加载时就把数据库记录发给浏览器**，不需要登录；用同一 API key 追加只读请求后，在 7,403 个站点（30%）的 10,560 张表里发现了含邮箱的记录——包括护照信息和超过 20 万条私信。根因并不新鲜：Supabase 的 anon key 本来就是公开的，安全性全押在 RLS（行级安全）上，而大量 Lovable 生成的应用没有启用它。

这件事的工程含义大于「又一个泄露事件」：**AI 平台批量生成的应用遵循同一套集成模式，于是一个利用方法可以低成本横扫成千上万个站点**——攻击面从 N 个独立问题塌缩成 1 个批量问题。更刺眼的是产品叙事与责任条款的落差：Lovable 营销说「无需技术背景」，T&C 却把数据安全责任全部推给客户。对任何「AI 替你搞定一切」的平台，结论只有一个：默认生成的权限配置必须默认安全（RLS 默认开启、公开表显式 opt-in），把安全基线内建进生成模板，而不是写进免责声明。处理真实用户数据前的人工安全评审，依然是不可省略的一步。

## Google /teamwork：多智能体科研的两个核心机制

Google Research 公开了 Antigravity /teamwork 多智能体系统在数学、化学、系统软件与 ML 工程上的协作成果（与学术伙伴联合，基于 Gemini 4 Argon/Carbon/Hydrogen），并宣布工具对外开放。设计针对长程任务的两个痛点给出了机制化答案。

其一是**单次生成不可靠**：/teamwork 用「并行探索 + 专职证伪者」弥合差距——证伪者是独立于生成方的验证器：Lean 4 证明检查器、未修改的测试套件、执行模拟器、硬件计数器。其二是**多日任务中注意力随上下文膨胀而涣散**：/teamwork 按构造分区上下文——每个专职 agent 只拿到该步骤精确需要的文件与工具，协调者把任务移交给全新上下文的后继者，批评者与审计者在**不含原始生产者推理痕迹的干净上下文**里挑战结果。

这与昨天的 Anthropic「Worse Together」正好构成一组互补实验：Anthropic 证明了共享协调者拓扑赢过「每人一个 agent」，Google 则给出了「协调者如何保持干净」的具体机制——fresh successor handoff 与干净上下文的批评者。两条结论合起来是多智能体工程目前最完整的实践图谱：先选对拓扑，再治理每个节点的上下文。

## 双 DGX Station 跑 GLM-5.3：吞吐峰值不在最大并发处

NVIDIA 发布了在两台 DGX Station 上用 vLLM 服务 GLM-5.3-NVFP4 的完整方案：753B 参数（每 token 激活 40B）的 MoE 模型权重约 **464 GB**，超过单张 GB300 的 252 GB HBM3e——「本地跑前沿模型」必须跨机。两台 Station 经 ConnectX-8 RDMA 互联，TP=2 起一个 OpenAI 兼容端点，叠加 multi-token prediction、FP8 KV cache 与 prefix caching。

AIPerf 在 SPEED-Bench Coding 上的曲线是这篇博客最有价值的部分：**并发 16 时输出吞吐峰值 607.8 tok/s，并发 32 时跌到 385.0 tok/s、平均请求延迟升到 453.5 秒**。教训很朴素：吞吐峰值不在最大并发处，扩容前先扫出自己工作负载的最优并发点。同一天 HN 上还有两条相关线索：UMich 的研究表明生成式 AI 处理非英语文本要多耗 1.4–180 倍能量（印地语 7.9 倍、孟加拉语 15.3 倍——tokenization 放大直接变成成本税），GitHub 上的 DeepSeek V3 纯 JAX 200 行实现则继续降低「读懂前沿模型」的门槛。

## 快讯

- **意大利对 Meta 罚款 8.87 亿美元**（Android 用户数据访问问题）；**Project Zero 更新披露政策**：报告漏洞 90 天后公开
- **arXiv 值得读**：*Goal Encoding in LLMs*（2611.17297，LLM 内部存在引导行动的目标表征）；*Where LLM Agents Get Stuck Debugging Databases*（2611.17304，Claude Code 排查生产数据库事故的现场观察：瓶颈在数据访问而非推理）
- **EU 峰会**：欧盟领导人在都柏林举行首次专门讨论 AI 的领导人级非正式峰会；SpaceX 宣布投资逾 740 亿美元建设两座 AI 超算园区
