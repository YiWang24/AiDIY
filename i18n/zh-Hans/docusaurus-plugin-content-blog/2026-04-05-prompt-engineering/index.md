---
slug: prompt-engineering-system-contracts
title: "提示词工程：从经验法则到系统契约"
authors: [yiwang]
tags: [prompt-engineering, ai-architecture, reasoning-models, llm-ops, engineering-standards]
---

在大语言模型（LLM）的早期，提示词工程（Prompt Engineering）经常被轻蔑地比作“炼金术”或“咒语”。开发人员花费无数小时测试“请”是否能提高模型的准确性，或者威胁模型要扣除“虚拟罚款”是否能生成更好的代码。那是属于**启发式方法（Heuristics）**的年代——那些模糊的、通过不断试错得出的模式，依赖于早期 Transformer 架构的特有行为。

随着我们步入 2026 年，那个时代已经彻底结束。“魔法咒语”已经消亡，取而代之的是**系统契约（System Contract）**。提示词工程已经成熟为软件工程的一个严谨分支。在这里，自然语言被视为一种高级编排层，受到结构完整性、模式强制（Schema Enforcement）和严格性能优化的约束。本文将探讨这一转变，以及定义生产级 AI 系统的全新模式。

<!--truncate-->

### “魔法咒语”的消亡

从启发式方法到系统契约的转变，源于一个根本性的认识：LLM 不是通过说服来响应的“魔盒”，而是基于上下文运作的**概率推理引擎**。当我们告诉模型“一步步思考”时，我们并不是在“激励”它，而是在触发一条特定的推理路径，为推理过程分配更多的计算资源（Token）。

在 2026 年，我们不再依赖这些脆弱的助推。现代框架将提示词视为一种**规范（Specification）**。正如 OpenAPI 规范定义了两个微服务之间的契约，系统契约定义了 LLM 交互的预期行为、约束条件和数据格式。如果模型失败了，我们不会去文本中寻找更好的“感觉（Vibe）”，而是寻找契约逻辑的漏洞或支撑数据的匮乏。这一转变标志着“提示词的专业化”：目标不再是诱导模型给出响应，而是从非确定性引擎中工程化出确定性的结果。

### 推理模型的转向：边界比指令更重要

“推理模型”（如 OpenAI 的 o1/o3 以及随后的 GPT-5 一代）的到来，从根本上改变了提示词工程的版图。早期的模型需要关于“如何思考”的显式引导。然而，重推理的模型自带了内置的、内化的**思维链（Chain of Thought, CoT）**机制。

在与 GPT-5 或 o3 协作时，添加“让我们一步步思考”往往是多余的，甚至可能适得其反。正如 Google AI 在其 2025 年的《Gemini 3.0 架构报告》中指出的，在具有原生推理时间扩展（Inference-time Scaling）的模型中过度指定推理路径会导致“指令干扰”：模型优化的内部逻辑会与用户的脚本指令发生冲突。

在这种新范式下，**指令的重要性在下降，而边界的重要性在上升。**我们不再告诉模型*如何*解决问题，而是定义其**解空间（Solution Space）**。这包括：
- **负向约束（Negative Constraints）**：清晰地定义模型*绝不能*做什么。这能防止模型滑向其内部推理可能会探索的、不理想的逻辑路径。
- **成功准则（Success Criteria）**：定义成功输出的可量化指标或状态。通过定义“终点线”，我们允许模型在其内部推理循环中进行回溯和自我修正。
- **上下文隔离（Context Isolation）**：确保模型仅使用提供的数据，而不漂移到通用知识（即幻觉）中。

通过专注于边界，我们允许模型的内部推理在既定的安全护栏内，寻找通往解决方案的最有效路径。我们将 LLM 视为一个能力极强但极度刻板的代理（Agent），它需要严谨的工作范围。

### 结构化模式：XML 标签化与角色扮演 2.0

结构完整性是系统契约的支柱。依赖“自然语言流”是产生解析错误和幻觉的温床。

#### XML 标签化：Anthropic 的深远影响
提示词设计中最显著的变化之一是 XML 标签的普及。虽然最初是由 Anthropic 推广的，但这种模式现在已成为跨模型的标准。诸如 `<context>`、`<instructions>`、`<example>` 和 `<output_schema>` 之类的 XML 标签提供了清晰的语义边界，模型的注意力机制可以轻松锁定这些边界。

```xml
<task_specification>
  <context>
    你正在分析一个旧有的 COBOL 代码库，以查找潜在的内存泄漏。
    该系统运行在基于 CICS 的 IBM z/OS 环境中。
  </context>
  <constraints>
    - 仅报告与 CICS 事务处理相关的泄漏。
    - 忽略批处理模块中的泄漏。
    - 输出必须是符合所提供模式的有效 JSON。
  </constraints>
  <input_code>
    {{CODE_SNIPPET}}
  </input_code>
</task_specification>
```

XML 优于 Markdown 标题，因为它是无歧义的。当“关于代码的指令”和“包含指令的代码”被包裹在不同的标签中时，模型可以轻易区分它们。它还支持嵌套结构，这对于复杂的、多阶段的 Agent 工作流至关重要。

#### 角色扮演 2.0：系统能力配置集
陈旧的“扮演一名高级开发人员”已经演变为**系统能力配置集（System Capability Profiles）**。我们不再定义模糊的人格，而是定义一套可用的“思维工具”和知识领域。我们告诉模型：“你可以访问以下领域知识：[Rust 所有权检查器, Actix-Web 模式]。你被限制在以下编码风格：[禁止使用 Unsafe, 函数式优先]。”

这是一份能力的契约，而不是一场戏剧表演。通过显式定义模型的“心理状态”和“工具箱”，我们降低了其响应的方差。本质上，我们是在通过上下文“配置”模型的权重，将其引导至与任务最相关的高维子空间。

#### 强制输出模式：最后的环节
在 2026 年，“纯文本”被视为一种过时的输出格式。现代系统使用**结构化输出（Structured Outputs）**或**受限解码（Constrained Decoding）**来确保模型的输出符合严格的 JSON Schema 或 Pydantic 模型。这使 LLM 从“散文生成器”转变为“数据生成器”。

当输出被保证是匹配特定模式的有效 JSON 对象时，LLM 可以直接集成到类型安全的代码库中，无需脆弱的正则解析或“遇错重试”循环。模式（Schema）本身成为系统契约的一部分，精确定义了模型必须提供什么信息以及以何种格式提供。

### 性能优化：提示词缓存与前缀模式

随着 LLM 集成到实时生产系统中，延迟成为了首要敌人。业界的回答是**提示词缓存（Prompt Caching）**。

提示词缓存允许 LLM 供应商存储提示词初始部分的“编译状态”。如果提示词的前缀（例如，你那 10,000 Token 的系统指令和文档语料库）在不同调用之间保持一致，模型可以“跳过”该部分的计算，从而极大地缩短**首字延迟（Time-To-First-Token, TTFT）**并降低成本。

这催生了**前缀模式（Prefixing Pattern）**：
1.  **静态层**：海量的系统指令、工具定义和少样本（Few-shot）示例。这一层应该置于提示词的最前端，且永不改变。
2.  **半动态层**：用户画像、长期记忆或会话历史。这一层变化缓慢，可以在会话级别进行缓存。
3.  **动态层**：特定的用户查询和即时任务上下文。这是每次请求中唯一改变的部分。

提示词工程现在涉及精细地排列这些层，以最大化“缓存命中”。如果你在提示词的最开始放了一个动态日期或用户名，你就破坏了其后所有内容的缓存，实际上会导致延迟翻倍并显著增加账单。

### 智力的规模化：多样本 ICL 与微调

AI 工程中一个反复出现的辩论是：何时微调模型，何时使用**上下文学习（In-Context Learning, ICL）**。在 2026 年的格局中，**多样本 ICL（Many-shot ICL）**已成为大多数企业任务的主导策略。

随着上下文窗口达到数百万 Token（如 Gemini 2.0/3.0, Claude 5），我们可以将数百甚至数千个示例直接注入提示词。OpenAI 在 2025 年关于“多样本上下文学习”的研究表明，提供 500-1000 个高质量示例的模型在相同任务上的表现往往优于微调模型，且具有“即时更新”的额外优势。

如果业务逻辑发生了变化——比如你的金融代理有了新的监管要求——你只需更新提示词中的示例即可。相比之下，微调会创建一个“冻结”的伪像，需要完整的重新训练周期和评估流程才能更新。ICL 是 LLM 世界的“内存（RAM）”——快速、灵活、易失；而微调则是“硬盘”。在 2026 年，对于任何需要敏捷性的任务，我们优先考虑**上下文智能（Contextual Intelligence, ICL）**而非**参数化智能（Parametric Intelligence, Fine-tuning）**。

### 实战模式：构建生产级编程代理提示词

为了说明这些概念，让我们看看 AiDIY 项目中使用的现代编程代理提示词结构。注意其中没有废话，并大量使用了结构化契约。

```markdown
# 系统契约：AiDIY-CODE-V2
## 版本：2026.4.5
## 状态：生产环境

<capabilities>
- 多文件重构及依赖图分析。
- 通过 `grep_search` 和 `ast_parser` 进行符号搜索。
- 生成单元测试（Vitest/Pytest），目标是 100% 的分支覆盖率。
</capabilities>

<environment_context>
- 项目：AiDIY 知识库（微前端架构）
- 语言：TypeScript 5.8 / Node.js 24
- 标准：整洁架构（Clean Architecture）, 六边形架构, 领域驱动设计 (DDD)。
- 测试：Vitest + Playwright。
</environment_context>

<operating_protocol>
1. 研究：使用 `list_directory` 和 `grep_search` 映射依赖关系。
2. 计划：在 `<plan>` 标签内输出技术实现方案。
3. 执行：使用 `replace` 工具应用手术式的更改。避免对部分更新使用 `write_file`。
4. 验证：执行本地测试套件和 Lint 检查。
</operating_protocol>

<constraints>
- 在 TypeScript 中绝不使用 'any' 或 'as' 类型断言。
- 所有文件路径必须是绝对路径，并经由 `ls` 验证。
- 不得修改 `.env` 文件或凭据。
- 更改范围严格限制在 `<task>` 标签内。
</constraints>

<output_contract>
- 所有推理过程必须包裹在 <thought> 标签内。
- 工具调用必须是符合工具规范（Tool Specification）的有效 JSON。
- 最终响应必须对照原始 `<plan>` 总结更改内容。
</output_contract>
```

这个提示词不是一段对话，它是一个**执行环境**。它定义了工具、规则以及代理预期的状态转换。

### 结语：作为代码的未来

展望 2020 年代的后半叶，“代码”与“提示词”之间的界限将继续模糊。我们正看到 **提示词领域特定语言（Prompt DSLs）**和编译器的兴起，它们接收高级意图并针对特定的模型架构进行优化，自动从向量数据库注入相关示例，并修剪不必要的 Token 以适应模型的特定注意力头配置。

在这个时代取得成功的工程师将不是那些懂得如何与 AI “交谈”的人，而是那些懂得如何为其**构建架构**的人。他们将理解 ICL 与微调之间的权衡、提示词缓存的细微差别，以及模式驱动契约的至关重要性。提示词工程并未消亡，它终于成为了一门真正的工程学。我们正在从“魔法咒语”迈向“系统契约”，其结果比我们在 LLM 早期所想象的任何事物都更可靠、更具扩展性、更强大。

---

### 参考文献
- **OpenAI (2025).** *Inference-Time Scaling and the o1 Architecture.* [https://openai.com/research/o1-reasoning](https://openai.com/research/o1-reasoning)
- **Anthropic (2026).** *Structural Integrity in Large Context Windows.* [https://anthropic.com/research/xml-contracts](https://anthropic.com/research/xml-contracts)
- **Google AI (2026).** *Gemini 3.0: The End of Prompt Heuristics.* [https://ai.google/blog/gemini-3-heuristics](https://ai.google/blog/gemini-3-heuristics)
- **AiDIY (2026).** *The Harness Engineering Manifesto.* [https://aidiy.io/blog/harness-engineering](/blog/2026-04-05-harness-engineering/)

---

### 术语选择说明 (Summary of Terminology Choices)

在翻译过程中，我遵循了 2026 年 AI 领域的专业语境，选择了以下术语：

1.  **Prompt Engineering -> 提示词工程**：行业标准译法，强调其工程属性。
2.  **Heuristics -> 经验法则 / 启发式方法**：在软件工程和算法中，这通常指基于经验而非严谨证明的方法。文中将其与“系统契约”对立。
3.  **System Contract -> 系统契约**：将提示词视为一种像 API 契约一样的约束性协议。
4.  **Chain of Thought -> 思维链**：LLM 逐步推理的核心概念。
5.  **Prompt Caching -> 提示词缓存**：LLM 推理优化的关键技术。
6.  **In-Context Learning (ICL) -> 上下文学习**：利用提示词内的示例让模型学习任务，而不修改权重。
7.  **Reasoning Models -> 推理模型**：指代如 OpenAI o1 等具备强逻辑推理能力的模型。
8.  **Solution Space -> 解空间**：数学和算法术语，指所有可能解的集合。
9.  **Many-shot ICL -> 多样本上下文学习**：对应长文本时代的数百/数千示例注入。
10. **Parametric Intelligence vs Contextual Intelligence -> 参数化智能 vs 上下文智能**：区分固化在模型参数中的知识与通过上下文实时获取的智能。
