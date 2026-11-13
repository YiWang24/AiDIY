---
slug: ai-daily-digest-2026-11-13
title: "AI Daily Digest: Anthropic「Worse Together」共享协调者胜出、OpenAI 解散独立机器人团队、AI 解锁哥德尔笔记本 - 2026/11/13"
authors: [yiwang]
tags: [ai, daily-digest, multi-agent, mamubench, anthropic, openai-robotics, godel-notebooks, alphagenome-2, x402, agentic-payments, hn, arxiv]
---

<!--truncate-->

今天的三个事件分别回答了 agent 工程里的一个「应该怎么摆」问题：**多 agent 系统的拓扑怎么选**（Anthropic：共享协调者打赢每人一个的 agent 团队，最多差 45 分）、**通用模型和专用硬件团队的关系怎么摆**（OpenAI 解散独立机器人团队，让通用模型直接接管机器人）、**AI 在科学史研究里站哪**（AI 读完哥德尔遗留的千页速记手稿，据说里面有数百条已被证明的定理）。

## Anthropic「Worse Together」：每人一个 agent，不如一个共享的协调者

Anthropic Fellows 团队发布了一组反直觉的实验结果：在四个共享资源环境里测试 Claude Opus 5 / Sonnet 5、GPT-5.6-sol / terra、Qwen3.8-max，**单个协调者 agent 比每人配一个独立 agent 团队好 10–45 个百分点**。「给团队每个人都配一个自己的 agent」这个听上去最自然的产品形态，在需要协调的场景里反而系统性落后。

失效模式比分数本身更有信息量。其一是**沉默化**：群体规模从 4 涨到 16 时，Sonnet 5 曾真正采取行动的 agent 占比从 66% 跌到 10%——大量 agent 不是做错，而是干脆不作为。其二是**虚构他人**：团队化 episode 中超过一半出现编造其他用户行为的描述，多 agent 通信链路成了幻觉的新温床。Anthropic 给出的缓解手段很具体：指定一个 team lead agent，并强制 agent 在结束前读完未读消息。三个实验环境已以 MAMUBench 开源。

这与本周的线索正好互补：昨天的 Gemini Orchestrator 优化的是**单 agent 轨迹内**的模型选择，今天这组实验警告的是**多 agent 之间**的拓扑选择。两个结论指向同一条工程纪律——协调是有代价的，且这个代价随规模超线性增长；先证明一个共享协调者不够用，再考虑拆分成多 agent。对正在设计「每人一个 AI 助理」产品的团队，这份数据值得直接放进评审文档。

## OpenAI 解散独立机器人团队：让通用模型直接跑机器人

据 Fortune 独家报道，OpenAI 已解散其独立的机器人团队，研究人员并入主研究团队（汇报给首席研究官 Mark Chen），应用机器人与硬件团队并入 Applied 部门（汇报给总裁 Greg Brockman）。公司口径强调这是加速而非放弃：让**通用模型直接控制机器人**（包括人形机器人），而不是养一支专用团队。一个耐人寻味的细节是，重组发生得太快，OpenAI 在本周 CoRL 会议注册的展位空着， logo 都没来得及撤。

这一幕与 2020 年那次解散高度呼应——当时联合创始人 Zaremba 给出的理由是机器人数据有限、超大语言模型是更高效的 AGI 路径，六年后这条路径的产物开始反哺机器人。再加上本周 arXiv 上 Metal Sandbox（Apple Silicon 上为 GPU 编码 agent 做隔离执行）这类工作，「通用模型 + 专用执行环境」正在取代「专用模型 + 专用团队」成为具身智能的组织范式。对旁观者的启示：当一家公司的通用能力曲线足够陡，为单一领域保留的独立团队反而是瓶颈。

## AI 解锁哥德尔笔记本：数百条定理等了半个世纪

据《卫报》报道，AI 正在帮助解读 Kurt Gödel 遗留的笔记本——1,009 页用一种已基本失传的速记体（Gabelsberger shorthand）密写的文字，其中据说包含**数百条已被证明但从未发表的定理**。哥德尔在 1930 年代的不完备性定理之后公开发表极少，未出版手稿总量达数万页，一直是科学史研究的富矿兼难关。

这个故事值得放进今天的 digest，是因为它是「AI 作为科学工具」的一个干净样本：这里没有生成式模型的炫技，AI 做的是**海量手写体的转录与规模化解读**——恰好是人力无法承受、机器恰好能做的部分。从本周 AlphaGenome 2（在 1.07 亿个细胞profile上把因果变异识别准确率从 16% 提到 30%）到哥德尔笔记，AI 对科学的增量正越来越多地出现在「把人类专家读不完的材料读完」这一环。

## 快讯

- **Brave Search API 接入 x402 agentic 支付**（HN 250 分）：agent 可以用链上微支付自主付费调用搜索 API——机器对机器的支付基础设施落地了一个真实用例
- **claude.ai / Claude Code 大面积报错**（HN 465 分）：Anthropic 状态页确认平台异常，多 agent 工作流对单一供应商的可用性依赖再次暴露
- **AlphaGenome 2**（DeepMind，11-11）：基于 68 种组织 1.07 亿细胞profile训练，TenK10K 免疫细胞集上因果变异识别 30% vs 16%、基因效应方向判断 43% vs 23%，非商业研究免费
- **OpenAI 开源 Codex Security CLI/SDK**（Apache 2.0）：仓库扫描、提交前变更审查、CI 卡点；分析服务仍闭源，接入限 beta
- **arXiv 2611.17304 Where LLM Agents Get Stuck Debugging Databases**：对 Claude Code 调试真实数据库的田野观察——卡点主要在**访问权限**而非推理能力
- **arXiv 2611.17297 Goal Encoding in LLMs**：LLM 内部存在先于行动、可经多条执行路径实现的「目标」神经表征，为 agent 可解释性提供新的探测点
- **arXiv 2611.17309 Classical Energies Learn to Reason 1,000x Faster than Looped Models**：用经典能量模型替代循环模型做推理，速度提升三个数量级
- **arXiv 2611.17316 CoReMem**：编码 agent 的跨任务记忆选择引入「前瞻估值」，把未来任务的未知性内部化为成本——agent 记忆治理继续从「多记」走向「选优」

> 数据截至 2026-11-13 15:00 EST，来源：Hacker News、arXiv（cs.AI/cs.CL）、Anthropic Alignment、Fortune、The Guardian、AIToolsRecap。
