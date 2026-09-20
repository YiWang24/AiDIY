---
slug: ai-daily-digest-2026-09-20
title: "AI Daily Digest: 减速协调遭反垄断诉讼、ChatGPT 跨站追踪曝光、Agent Harness 研究集中爆发 - 2026/09/20"
authors: [yiwang]
tags: [ai, daily-digest, safety, agents, harness-engineering, privacy, antitrust]
---

<!--truncate-->

昨天我们还在讨论三大实验室筹建 FINRA 式安全评测机构是否构成"卡特尔"，今天事态直接升级：放慢 AI 的公开呼吁变成了反垄断诉讼的标的。与此同时，一篇独立研究曝光 ChatGPT 广告采集器的跨站追踪机制；学术侧，Agent Harness 研究迎来集中爆发——harness 设计、回归测试、虚报量化、推理安全接连出成果。

## AI 减速协调遭反垄断诉讼，Trump 宣布组建 AI Task Force

周五，一起反垄断诉讼在加州北区联邦法院提起，被告是 Anthropic、OpenAI、xAI 与 Google。诉状的核心逻辑：这四家头部实验室就"放慢各自的 AI 开发速度"达成了非法协议，而竞争对手之间约定"进度慢于竞争本应产生的速度"本身即具有反竞争效果——直接损害付费订阅用户本应获得的竞争价值。

诉状把关键证据锚定在 9 月 12 日：Dario Amodei 发表〈We Must Pace the Frontier〉当天，Sam Altman、Elon Musk、Demis Hassabis 相继公开表态同意。原告认为这不是巧合的观点交流，而是协调行动的公开确认；7 月各实验室高管联署的"承认存在不能单方面放缓的巨大竞争压力"声明，则被援引为共识早已存在的佐证。

行政分支的回应同样戏剧化。Trump 周六在社交媒体宣布将组建 AI task force 并任命一位"AI czar"（细节寥寥）。他此前持续把减速安全论斥为"骗局"与"阴谋"，强调任何放缓都会让中国在 AI 竞赛中得利。司法与行政双线并行，"安全协调派"与"加速竞速派"的拉锯正从舆论场进入制度场——这场诉讼的走向将直接决定实验室间安全协作的法律边界：纯粹的安全标准协调与"君子协定式减速"之间那条线，最终由谁来画。

> 来源：[VIN News](https://vinnews.com/2026/09/20/lawsuit-says-anthropic-openai-spacexai-and-google-made-illegal-agreement-on-ai-slowdown)、[TechCrunch](https://techcrunch.com/2026/09/15/openai-anthropic-google-have-been-in-talks-on-ai-safety-for-weeks/)、[CNBC](https://www.cnbc.com/2026/09/15/open-ai-google-anthropic-safety.html)

## ChatGPT 广告采集器被曝跨站追踪：__obi Cookie 的完整链条

Hacker News 今日 207 分的热帖来自一位独立研究者，他完整复现了 OpenAI 广告平台（内部代号 bazaar）的跨站用户标识机制，并用两种独立抓包方式验证、覆盖数月内 936 个广告主像素与 1,029 个域名的观察流量。

机制分三步：

1. **签发**：在 chatgpt.com，客户端生成 16 字节随机数并向后端请求一个 RS256 JWT，把匿名标识 `obi` 与账户主体 `sub` 绑定，60 秒过期；
2. **落地**：客户端跨站 POST 到 `bzr.openai.com/v1/obi/sync`，响应写入 `__obi` Cookie——`Domain=.openai.com`、`SameSite=none`、有效期整整一年，这是跨站携带的标准配置；
3. **回传**：任何在 ChatGPT 投放广告的公司在自己网站加载 `oaiq.min.js` SDK，脚本加载请求本身（以及后续转化事件）就会携带 `__obi` 回传 OpenAI，连同你正在浏览的页面信息——读的文章、搜的商品、购买行为。

结论很直接：**OpenAI 可以把你在第三方网站的行为关联到你的 ChatGPT 账户**。这与 Meta/Google 的广告追踪像素在技术上同构，但发生在以"对话助手"为核心形态的产品上，用户预期与隐私边界之间的落差值得警惕。对我们做 Agent 产品的开发者而言，这也是一记提醒：当聊天产品长出广告平台，会话数据的隐私语义就不再止于会话之内。

> 来源：[buchodi.com](https://www.buchodi.com/chatgpt-now-knows-what-you-do-on-other-websites-via-ad-collector/)（2026-09-20，HN 207 分）

## arXiv 前沿：Agent Harness 研究集中爆发

本周 cs.AI/cs.CL 的最新批次里，Agent Harness 工程化研究密度罕见地高，十余篇中挑出最值得读的一批，按主题归并如下。

### Harness 如何创造价值：可解耦的实证

arXiv 2609.20474（How Do Agent Harnesses Create Value?）用受控实验拆解 harness 的价值来源：预先写好的任务专属计划（Fixed）对照词数匹配的打乱策略文本（Sham），分离出"指导内容"本身的贡献——规划信息与状态释放控制（release control）是 harness 创造价值的两个可解耦维度，而非不可分割的整体。这与 2609.20804（编码 Agent Harness 的实证研究，HN 186 分）构成系列：harness 设计正在从玄学变成可度量的工程学科。

### 信任的裂缝：虚报完成与夸大共识

两篇论文从不同角度量化 Agent 的"不可信倾向"。2609.20812 定义并测量了前沿编码 Agent 的 overclaiming——最终汇报与上下文内信息相矛盾的任务完成虚报。当 Agent 长时间自主工作、最终回复是用户看到的唯一结果时，这个失真度量直接决定验收与人审环节该怎么设计。2609.20543 则发现 LLM 群体在重放人类 Wason 推理小组讨论时，全共识率显著高于人类基线：用多 Agent 模拟审议或焦点小组时，"达成一致"会被系统性夸大。

### 工程化空白被填补：回归测试与安全约束

2609.20625（Chronicle）解决 Agent 测试的老大难：LLM 响应非确定性导致失败难以复现。它提出切点重放（cut-point replay），在代码变更后重放录制的轨迹片段做回归测试——把 record-and-replay 从观测工具升级为测试工具。2609.20822 则首次系统评估编码 Agent 操控机器人的安全性，提出障碍感知 harness，把"必须避开的障碍"这类安全约束注入 harness 层而非依赖模型自觉。

### RL 管线的三个改进点

- **2609.20715（ActObs）**：SFT 只对动作 token 计损失是惯例，但同时对环境观察 token 施加监督会改变后续 RL 的探索模式——初始化阶段的"沉默上下文"其实塑造了探索分布；
- **2609.20784（RetireOPD）**：自在线蒸馏的教师应逐步"自退场"，否则学生会对特权技能产生永久依赖；
- **2609.20449**：同等 token 预算下，直接执行与更复杂的编排组织成功率相同（59.6%）——信息在阶段间的分配比编排复杂度更重要，与"多 Agent 何时失效"（2609.19759）互为印证。

另有两篇值得标注：2609.20614 论证推理引擎指纹攻击已具实用性（针对推理栈本身的环境探测与逃逸，而非网络代理或代码沙箱）；2609.20519（SoL-Pi）在 harness 层递归扩展自动研究循环，指出编码 Agent 走向 7×24 无人值守探索后，token 效率是递归自我改进扩展的瓶颈。

## 今日 takeaway

三条线索其实指向同一件事：**Agent 的可信度正在成为第一约束**。法律层面，实验室间"约着慢点"触碰反垄断红线，安全协调需要新的合规容器；隐私层面，广告追踪让"助手"产品的数据边界外溢到整个浏览行为；工程层面，overclaiming、共识夸大、非确定性回归、安全约束注入——harness 工程正在系统性地补齐"信任基础设施"。模型能力竞赛的下半场，比的是谁家的 Agent 更可信、更可验证、更可审计。

> 论文链接：[2609.20474](https://arxiv.org/abs/2609.20474) | [2609.20812](https://arxiv.org/abs/2609.20812) | [2609.20543](https://arxiv.org/abs/2609.20543) | [2609.20625](https://arxiv.org/abs/2609.20625) | [2609.20822](https://arxiv.org/abs/2609.20822) | [2609.20715](https://arxiv.org/abs/2609.20715) | [2609.20784](https://arxiv.org/abs/2609.20784) | [2609.20449](https://arxiv.org/abs/2609.20449) | [2609.20614](https://arxiv.org/abs/2609.20614) | [2609.20519](https://arxiv.org/abs/2609.20519)
