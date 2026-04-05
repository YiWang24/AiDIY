# KB RAG 系统 - 完整架构文档

## 项目概述

一个综合性的 RAG（检索增强生成）知识库系统，具有智能代理编排功能，结合语义搜索、网络搜索能力和 AI 驱动的问答功能。

**核心特性：**
- 📚 **文档索引**：自动将 MDX 文档转换为向量嵌入
- 🔍 **混合搜索**：语义 + 关键词搜索与重新排序
- 🤖 **代理编排**：智能路由到专业代理（知识、网络搜索、混合）
- 🌐 **网络搜索回退**：当知识库不足时自动进行网络搜索
- 🛠️ **工具调用**：原生支持 Gemini 函数调用 API
- 📖 **引用跟踪**：每个答案都包含源文档引用
- ⚡ **实时响应**：优化的检索和生成流水线

## 目录

1. [技术栈](#技术栈)
2. [系统架构](#系统架构)
3. [数据流水线](#数据流水线)
4. [代理编排](#代理编排)
5. [工具系统](#工具系统)
6. [API 设计](#api-设计)
7. [模型选择](#模型选择)
8. [部署指南](#部署指南)
9. [配置](#配置)
10. [故障排除](#故障排除)

---

## 技术栈

### 后端（Python）

```yaml
核心框架：
  - FastAPI 0.110+: 高性能 Web 框架
  - Pydantic 2.6+: 数据验证和序列化
  - Uvicorn: ASGI 服务器

数据层：
  - PostgreSQL 15+ with pgvector: 向量数据库
  - psycopg 3: 数据库驱动
  - psycopg-pool: 连接池管理

AI/ML：
  - Gemini API: Google Gemini 2.5 Flash 用于 LLM
  - Gemini Embeddings: models/embedding-001
  - Tavily/Brave Search: 网络搜索集成
  - LangChain: 文本处理和分块

数据处理：
  - PyYAML: 配置管理
  - httpx: 外部 API 的 HTTP 客户端
  - tqdm: 进度条

测试：
  - pytest 8.0+: 单元测试
  - pytest-asyncio: 异步测试支持
```

### 前端（TypeScript/Next.js）

```yaml
框架：
  - Docusaurus: 文档站点生成器
  - React 18+: UI 框架
  - TypeScript: 类型安全

构建工具：
  - npm: 包管理
  - webpack: 模块打包
```

### 基础设施

```yaml
数据库：
  - PostgreSQL 15+
  - pgvector 扩展
  - Python 3.11+

环境管理：
  - Doppler: 环境变量和密钥
  - uv: Python 包管理
```

---

## 系统架构

### 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                     前端（Docusaurus）                     │
│  ┌──────────────────────────────────────────────────────┐   │
│  │   AI 聊天组件（React）                            │   │
│  │   - 用户输入                                       │   │
│  │   - 显示 AI 回答和引用                             │   │
│  │   - SSE 流支持                                    │   │
│  │   - http://localhost:3001                         │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    API 层（FastAPI）                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  POST /ask          代理编排的问答                  │   │
│  │  POST /search       语义搜索                       │   │
│  │  GET /health        健康检查                       │   │
│  │  http://localhost:8000                             │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   代理编排层                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │   代理路由器（问题分类器）                         │   │
│  │   - 基于关键词的路由                               │   │
│  │   - 可选的 LLM 分类                               │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   知识      │  │  网络搜索    │  │    混合      │     │
│  │    代理     │  │    代理     │  │    代理     │     │
│  │  (基于RAG)  │  │ (Tavily/API)│  │  (组合式)   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      业务逻辑层                           │
│  ┌──────────────────┐  ┌──────────────────────────────┐   │
│  │   RAG 流水线   │  │   检索器                      │   │
│  │  - 上下文构建  │  │  - 混合搜索                   │   │
│  │  - 答案生成    │  │  - 重新排序                   │   │
│  └──────────────────┘  └──────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  工具系统                                       │   │
│  │  - 网络搜索 (Tavily/Brave)                      │   │
│  │  - 函数调用接口                                 │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                     数据访问层                            │
│  ┌──────────────────┐  ┌──────────────────────────────┐   │
│  │   向量存储     │  │   文档存储                   │   │
│  │  - pgvector     │  │   - 文档元数据               │   │
│  │  - 相似度       │  │   - 校验和跟踪               │   │
│  └──────────────────┘  └──────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                     存储层                                │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  PostgreSQL + pgvector                              │   │
│  │  - kb_documents: 文档元数据                        │   │
│  │  - kb_chunks_gemini: 向量嵌入 (768维)              │   │
│  │  - kb_index_meta: 索引签名                         │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              数据流水线（离线索引）                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  第 1 阶段：文档清理                              │   │
│  │  - MDX → JSONL (JavaScript 工具)                  │   │
│  │  - 移除运行时代码                                 │   │
│  │  - 生成校验和                                     │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  第 2 阶段：向量索引                              │   │
│  │  - 文本分块                                       │   │
│  │  - 嵌入生成 (Gemini)                              │   │
│  │  - 数据库存储                                     │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 请求流程图

```
用户问题
   │
   ▼
┌──────────────────┐
│  代理路由器      │
│  - 分类问题      │
│  - 选择代理      │
└────────┬─────────┘
         │
    ┌────┴────┬────────────┐
    ▼         ▼            ▼
┌───────┐ ┌─────────┐ ┌─────────┐
│知识  │ │   网络   │ │ 混合   │
│代理  │ │  代理    │ │ 代理   │
└───┬───┘ └────┬────┘ └────┬────┘
    │          │          │
    │    ┌─────▼─────┐    │
    │    │ Tavily/   │    │
    │    │  Brave    │    │
    │    └───────────┘    │
    │                     │
    └──────┬──────────────┘
           ▼
    ┌──────────────┐
    │   检索器      │
    │  - 混合      │
    │  - 重新排序  │
    └──────┬───────┘
           ▼
    ┌──────────────┐
    │上下文构建器  │
    └──────┬───────┘
           ▼
    ┌──────────────┐
    │   LLM 调用   │
    │  (Gemini)    │
    └──────┬───────┘
           ▼
    ┌──────────────┐
    │  回答        │
    │  + 引用      │
    └──────────────┘
           │
           ▼
     返回给用户
```

---

## 数据流水线

### 流水线阶段

#### 第 1 阶段：文档清理

**工具：** JavaScript + mdx-clean

**输入：** MDX 源文件

```bash
docs/
├── cs/
│   ├── algorithms/
│   └── ...
├── ai/
│   ├── agents/
│   └── ...
└── ...
```

**处理步骤：**

1. **读取 MDX 文件**：解析 frontmatter 和内容
2. **移除运行时代码**：
   - 移除导入/导出语句
   - 移除 JSX 语法
   - 保留 markdown 内容
3. **转换特殊语法**：
   - TabItems → 标题
   - 保留代码块
   - 保留 Mermaid 图表
4. **生成元数据**：
   - 文档 ID
   - 标题
   - 路径
   - SHA-256 校验和（用于增量更新）
5. **输出 JSONL**：`kb/data/cleaned/docs.jsonl`

**输出格式：**

```json
{
  "id": "ai/agentops",
  "path": "docs/ai/agents/agentops/index.mdx",
  "title": "AgentOps 和安全",
  "checksum": "6c5bb14e0a5801d7fb4fb4431ef3e58e8c8cf6b19bab56970589111a4007625b",
  "content": "# AgentOps 和安全\n\nAgentOps 结合...",
  "frontmatter": {
    "title": "AgentOps 和安全",
    "tags": ["agents", "security"]
  }
}
```

**CLI 命令：**

```bash
# 仅运行第 1 阶段
kb-build --stage clean

# 指定输入/输出
kb-build --stage clean --docs-dir ./docs --output kb/data/cleaned/custom.jsonl
```

#### 第 2 阶段：向量索引

**工具：** Python + Gemini Embeddings

**输入：** `kb/data/cleaned/docs.jsonl`

**处理流程：**

```mermaid
graph LR
    A[JSONL 文档] --> B[文本分块]
    B --> C{递归分割}
    C --> D[生成块]
    D --> E[嵌入生成]
    E --> F[PostgreSQL+pgvector]
    F --> G[向量索引]
```

**1. 文本分块**

```python
# 策略：MarkdownHeaderTextSplitter + RecursiveCharacterTextSplitter

配置：
- max_section_chars: 2000  # 递归分割前的最大字符数
- chunk_size: 500           # 目标块大小
- chunk_overlap: 80         # 块之间的重叠

保留：
- 标题层次结构（H1、H2、H3...）
- 节结构
- 段落内容
```

**2. 嵌入生成**

```python
# 使用 Gemini Embeddings API

模型：models/embedding-001
API：https://generativelanguage.googleapis.com/v1beta/

批量请求：
- batch_size: 32 个请求/块
- 自动重试机制
- 进度条显示

输出：768 维向量
```

**3. 数据库存储**

```sql
-- 文档元数据表
CREATE TABLE kb_documents (
    doc_id VARCHAR(255) PRIMARY KEY,
    path VARCHAR(1024) NOT NULL,
    title VARCHAR(512) NOT NULL,
    version VARCHAR(64) DEFAULT 'latest',
    checksum VARCHAR(64) NOT NULL,
    chunk_ids JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 向量嵌入表
CREATE TABLE kb_chunks_gemini (
    id SERIAL PRIMARY KEY,
    chunk_id VARCHAR(64) UNIQUE NOT NULL,
    doc_id VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    heading_path JSONB DEFAULT '[]',
    chunk_index INTEGER DEFAULT 0,
    embedding vector(768),  -- Gemini 嵌入维度
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 向量相似度索引 (IVFFlat)
CREATE INDEX kb_chunks_gemini_embedding_idx
ON kb_chunks_gemini
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

**增量更新机制：**

```python
# 基于校验和的增量索引

1. 计算文档内容的 SHA-256 校验和
2. 与数据库校验和比较
3. 如果相同：跳过
4. 如果不同：
   - 删除旧块
   - 重新分块和嵌入
   - 更新数据库
```

**CLI 命令：**

```bash
# 仅运行第 2 阶段
kb-build --stage build

# 强制完全重建
kb-build --stage build --force-rebuild

# 指定 JSONL 输入
kb-build --stage build --output kb/data/cleaned/custom.jsonl
```

#### 性能指标

| 指标 | 当前值 |
|------|--------|
| 总文档数 | 39 个文档 |
| 总块数 | 3,043 个块 |
| 平均块大小 | ~500 字符 |
| 索引时间 | ~2 分钟（56 个文档） |
| 检索延迟 | ~300ms |

---

## 代理编排

### 架构概述

代理编排系统提供智能问题路由到专门的处理程序：

```
用户问题
    ↓
代理路由器（问题分类器）
    ↓
    ├─→ 知识代理（基于 RAG 的问答）
    │       ├─→ 混合搜索（语义 + 关键词）
    │       ├─→ 重新排序
    │       └─→ 生成答案
    │
    ├─→ 网络搜索代理（在线搜索）
    │       ├─→ Tavily/Brave 搜索
    │       └─→ 汇总结果
    │
    └─→ 混合代理（组合）
            ├─→ 首先尝试 RAG
            ├─→ 如果不足：网络搜索
            └─→ 合并并回答
```

### 代理路由器

**文件：** `kb/agents/router.py`

**路由策略：**

1. **基于关键词的启发式**（默认）：
   - 知识： "how to"、"explain"、"architecture"、"implementation"
   - 网络搜索： "latest"、"news"、"current"、"price"、"2025"
   - 混合： 不确定情况的回退选项

2. **可选的 LLM 分类**：
   - 使用 `use_llm_routing: true` 启用
   - 使用 Gemini 分类问题类型
   - 提供更准确的路由

**路由规则：**

```python
ROUTE_RULES = {
    "knowledge": {
        "keywords": [
            "how to", "how do", "explain", "what is", "what are",
            "architecture", "implementation", "api", "design",
            "pattern", "tutorial", "guide", "example",
        ],
        "default_confidence": 0.6,
    },
    "web_search": {
        "keywords": [
            "latest", "news", "current", "recent", "today",
            "price", "cost", "2025", "2024", "2023",
        ],
        "default_confidence": 0.7,
    },
}
```

### 知识代理

**文件：** `kb/agents/knowledge_agent.py`

**职责：**
- 基于 RAG 的问答
- 混合搜索 + 重新排序
- 引用生成

**工作流：**

```python
1. 使用混合检索块
2. 检查结果是否充分（分数 > 0.4）
3. 如果不充分：返回 has_sufficient_knowledge=False
4. 使用检索到的上下文生成答案
5. 返回并添加引用
```

**置信度评分：**
- 技术问题： 0.85
- 通用问题： 0.55
- 知识特定关键词： +0.15

### 网络搜索代理

**文件：** `kb/agents/web_search_agent.py`

**职责：**
- 实时信息检索
- 通过 Tavily 或 Brave 进行网络搜索
- 从搜索结果合成答案

**工作流：**

```python
1. 执行网络搜索
2. 格式化搜索结果
3. 从结果生成答案
4. 返回并包含来源
```

**置信度评分：**
- 实时关键词： 0.90
- 当前事件： 0.75
- 通用： 0.40

### 混合代理

**文件：** `kb/agents/hybrid_agent.py`

**职责：**
- 组合知识库和网络搜索
- 自动回退
- 合并两个来源的信息

**工作流：**

```python
1. 首先尝试知识库
2. 检查结果是否充分（分数 > 0.3）
3. 如果充分：返回知识库结果
4. 如果不充分：
   - 执行网络搜索
   - 合并两个结果
   - 明确区分来源
5. 返回组合答案
```

**置信度评分：**
- 所有问题： 0.65（安全的回退选项）

### 代理接口

所有代理都实现 `Agent` 基类：

```python
class Agent(ABC):
    @abstractmethod
    async def handle(self, question: str, context: Dict) -> Dict:
        """处理问题并返回响应。"""
        pass

    @abstractmethod
    def can_handle(self, question: str) -> float:
        """返回置信度分数（0.0 - 1.0）。"""
        pass
```

---

## 工具系统

### 工具接口

**文件：** `kb/tools/base.py`

工具系统为函数调用提供可插拔接口：

```python
class Tool(ABC):
    @abstractmethod
    def name(self) -> str:
        """函数调用的工具名称。"""
        pass

    @abstractmethod
    def description(self) -> str:
        """向 LLM 描述工具。"""
        pass

    @abstractmethod
    def parameters_schema(self) -> Dict[str, Any]:
        """参数的 JSON 模式。"""
        pass

    @abstractmethod
    async def execute(self, **kwargs) -> str:
        """执行工具并返回结果。"""
        pass

    def to_function_declaration(self) -> Dict[str, Any]:
        """转换为 Gemini 函数声明格式。"""
        return {
            "name": self.name(),
            "description": self.description(),
            "parameters": self.parameters_schema(),
        }
```

### 网络搜索工具

**文件：** `kb/tools/web_search.py`

**支持的提供商：**
- Tavily Search（主要，推荐）
- Brave Search（替代）

**特性：**
- 异步执行
- 可配置的 max_results
- 搜索深度选项（基础/高级）
- LLM 友好的结果格式

**使用示例：**

```python
tool = WebSearchTool(
    provider="tavily",
    api_key=os.getenv("TAVILY_API_KEY"),
    max_results=5,
    search_depth="basic"
)

result = await tool.execute(
    query="2025 年最新 AI 趋势",
    max_results=5
)
```

### 工具调用支持

**文件：** `kb/llm/gemini.py`

Gemini LLM 现在支持函数调用：

```python
async def generate_with_tools(
    prompt: str,
    tools: List[Any],
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    max_tool_calls: int = 5,
) -> LLMResponse:
    """使用工具调用支持生成。

    自动处理工具调用循环并收集结果。
    """
```

**特性：**
- 自动工具执行
- 多步工具调用
- 对话历史管理
- 优雅降级的错误处理

---

## API 设计

### 端点概览

| 端点 | 方法 | 描述 |
|------|------|------|
| `/` | GET | API 信息和可用端点 |
| `/health` | GET | 健康检查 |
| `/search` | POST | 语义搜索（无 LLM） |
| `/ask` | POST | 代理编排的问答 |

### API 详情

#### 1. 根端点 `/`

**请求：**

```http
GET / HTTP/1.1
```

**响应：**

```json
{
  "name": "KB RAG API",
  "version": "1.0.0",
  "description": "基于 RAG 的知识库与代理编排",
  "endpoints": {
    "health": "/health",
    "search": "/search",
    "ask": "/ask"
  },
  "features": [
    "agent_orchestration",
    "hybrid_search",
    "web_search_fallback",
    "tool_calling"
  ]
}
```

#### 2. 健康检查 `/health`

**请求：**

```http
GET /health HTTP/1.1
```

**响应：**

```json
{
  "status": "healthy",
  "timestamp": "2025-02-05T10:30:00Z",
  "components": {
    "database": "healthy",
    "llm": "healthy",
    "web_search": "healthy"
  }
}
```

#### 3. 语义搜索 `/search`

**请求：**

```http
POST /search HTTP/1.1
Content-Type: application/json

{
  "query": "什么是 AgentOps？",
  "k": 5
}
```

**响应：**

```json
[
  {
    "chunk_id": "82cd0834...",
    "doc_id": "docs:ai/prompt-engineering/09-agent-orchestration.mdx",
    "content": "每个代理有一个主要角色...",
    "heading_path": ["最佳实践总结", "2. 清晰的代理边界"],
    "chunk_index": 201,
    "score": 0.708,
    "document": {
      "title": "9 代理编排",
      "path": "docs/ai/prompt-engineering/09-agent-orchestration.mdx"
    }
  }
]
```

#### 4. 代理编排问答 `/ask`

**请求：**

```http
POST /ask HTTP/1.1
Content-Type: application/json

{
  "question": "代理编排模式有哪些？",
  "top_k": 5
}
```

**响应（知识代理）：**

```json
{
  "answer": "基于知识库，代理编排模式包括顺序模式和主管 + 工作者模式...",
  "citations": [
    {
      "id": 1,
      "chunk_id": "42fd61e4...",
      "doc_id": "docs:design-patterns",
      "title": "3. 设计模式",
      "path": "https://docs.yiw.me/docs/ai/agents/design-patterns",
      "heading_path": ["3. 代理设计模式", "3.2 多代理模式", "模式 8：顺序模式"],
      "score": 0.759
    }
  ],
  "has_sufficient_knowledge": true,
  "model": "gemini-2.5-flash",
  "tokens_used": 930,
  "retrieval_time_ms": 242,
  "generation_time_ms": 657,
  "agent_type": "knowledge"
}
```

**响应（网络搜索代理）：**

```json
{
  "answer": "基于网络搜索结果，2025 年的最新代理编排模式包括...",
  "citations": [],
  "has_sufficient_knowledge": true,
  "model": "gemini-2.5-flash",
  "tokens_used": 856,
  "retrieval_time_ms": 1200,
  "generation_time_ms": 543,
  "agent_type": "web_search"
}
```

**响应（混合代理）：**

```json
{
  "answer": "基于知识库和网络搜索：\n\n**来自知识库：**\n传统代理模式包括...\n\n**来自网络搜索：**\n2025 年的最新方法添加...",
  "citations": [
    {
      "id": 1,
      "chunk_id": "abc123...",
      "doc_id": "docs:ai/agents",
      "title": "代理模式",
      "path": "https://docs.yiw.me/docs/ai/agents",
      "heading_path": ["介绍"],
      "score": 0.512
    }
  ],
  "has_sufficient_knowledge": true,
  "model": "gemini-2.5-flash",
  "tokens_used": 1456,
  "retrieval_time_ms": 1442,
  "generation_time_ms": 657,
  "agent_type": "hybrid"
}
```

### 错误处理

**错误响应格式：**

```json
{
  "detail": "问答请求失败：网络搜索 API 错误：401 - 无效的 API 密钥"
}
```

**HTTP 状态码：**

| 状态 | 描述 |
|------|------|
| 200 | 成功 |
| 400 | 错误请求（无效参数） |
| 401 | 未授权（缺失/无效的 API 密钥） |
| 429 | 超出速率限制 |
| 500 | 内部服务器错误 |
| 503 | 服务不可用（LLM/下游 API 错误） |

### 请求/响应模式

**AskRequest：**

```python
class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=500)
    top_k: int = Field(default=10, ge=1, le=20)
```

**AskResponse：**

```python
class AskResponse(BaseModel):
    answer: str
    citations: List[Citation]
    has_sufficient_knowledge: bool
    model: str
    tokens_used: Optional[int]
    retrieval_time_ms: int
    generation_time_ms: int
```

**Citation：**

```python
class Citation(BaseModel):
    id: int
    chunk_id: str
    doc_id: str
    title: str
    path: str
    heading_path: List[str]
    score: float
```

---

## 模型选择

### Gemini 模型比较

| 模型 | 状态 | 用途 | 推荐 |
|------|------|------|------|
| **Gemini 2.5 Flash** | ✅ 稳定 | **生产（默认）** | ⭐⭐⭐⭐⭐ |
| **Gemini 2.5 Pro** | ✅ 稳定 | 高质量推理 | ⭐⭐⭐⭐ |
| **Gemini 1.5 Flash** | ✅ 稳定 | 备用选项 | ⭐⭐⭐ |
| **Gemini Flash 最新** | ✅ 可用 | 最新稳定版 | ⭐⭐⭐⭐ |

### 当前配置

**LLM 模型：**

```yaml
llm:
  model: gemini-2.5-flash       # 当前默认
  temperature: 0.3              # 低值确保事实准确性
  max_tokens: 1024
```

**嵌入模型：**

```yaml
embedding:
  model: models/embedding-001   # 768 维向量
```

### 性能比较

| 模型 | 延迟 | 成本 | 质量 | 稳定性 |
|------|------|------|------|--------|
| **Gemini 2.5 Flash** | ~600ms | 低 | ⭐⭐⭐⭐ | 高 |
| **Gemini 2.5 Pro** | ~1200ms | 中等 | ⭐⭐⭐⭐⭐ | 高 |

---

## 配置

### 完整配置文件

**文件：** `kb/config.yaml`

```yaml
# 输入/输出路径
docs_dir: docs
output_jsonl: kb/data/cleaned/docs.jsonl

# 分块配置
chunking:
  max_section_chars: 2000
  chunk_size: 500
  chunk_overlap: 80

# 嵌入配置
embedding:
  provider: gemini
  model: models/embedding-001

# Gemini API 配置
gemini:
  api_key: ${GEMINI_API_KEY:-}

# 存储配置
storage:
  database_url: ${DATABASE_URL:-postgresql://user:password@localhost:5432/kb}

# 向量存储配置
vector_store:
  table_name: kb_chunks_gemini
  batch_size: 32

# LLM 配置
llm:
  provider: gemini
  model: gemini-2.5-flash
  api_key: ${GEMINI_API_KEY:-}
  temperature: 0.3
  max_tokens: 1024

# RAG 配置
rag:
  retrieval:
    top_k: 10
    score_threshold: 0.6
    max_chunks_per_doc: 3
    use_hybrid_search: true
    use_reranking: true
    hybrid_alpha: 0.7

  context:
    max_length: 4000
    include_headings: true

  generation:
    temperature: 0.3
    max_tokens: 1024

  # 代理编排（新增）
  agent_orchestration:
    enabled: true                    # 启用代理系统
    fallback_to_web: true             # 启用网络搜索回退
    web_fallback_threshold: 0.3       # 如果最高分数 < 0.3，使用网络搜索
    use_llm_routing: false            # 使用 LLM 进行路由（默认：仅关键词）

# 网络搜索配置（新增）
web_search:
  provider: tavily                    # tavily 或 brave
  api_key: ${TAVILY_API_KEY:-}       # 来自 Doppler
  max_results: 5
  search_depth: basic                 # basic 或 advanced
  timeout: 30

# Docusaurus 配置
docusaurus:
  site_url: "https://docs.yiw.me"
```

### 环境变量

**必需的：**

```bash
# 数据库
DATABASE_URL=postgresql://user:password@host:port/dbname

# Gemini API
GEMINI_API_KEY=your-gemini-api-key

# 网络搜索（任选其一）
TAVILY_API_KEY=tvly-your-key
BRAVE_API_KEY=your-brave-key
```

### 使用 Doppler 管理密钥

```bash
# 登录到 Doppler
doppler login

# 设置密钥
doppler secrets set GEMINI_API_KEY "your-key"
doppler secrets set DATABASE_URL "postgresql://..."
doppler secrets set TAVILY_API_KEY "tvly-..."

# 使用 Doppler 运行
doppler run -- uv run uvicorn kb.api.app:create_app --reload
```

---

## 部署指南

### 前置要求

- Python 3.11+
- PostgreSQL 15+ with pgvector
- Doppler CLI（用于密钥管理）
- Node.js 18+（用于前端）

### 安装

#### 1. 克隆和设置

```bash
git clone https://github.com/YiWang24/AiDIY.git
cd AiDIY
```

#### 2. 安装后端依赖

```bash
cd kb
pip install -e .
```

#### 3. 配置环境

```bash
# 使用 Doppler
doppler login

# 设置必需的密钥
doppler secrets set GEMINI_API_KEY "your-gemini-api-key"
doppler secrets set DATABASE_URL "postgresql://user:password@host:port/dbname"
doppler secrets set TAVILY_API_KEY "tvly-your-key"
```

#### 4. 初始化数据库

```sql
-- 安装 pgvector 扩展
CREATE EXTENSION IF NOT EXISTS vector;

-- 创建数据库（如果需要）
CREATE DATABASE kb_db;
```

#### 5. 运行数据流水线

```bash
# 运行完整流水线
doppler run -- uv run python -m kb.cli --stage all

# 强制重建
doppler run -- uv run python -m kb.cli --stage all --force-rebuild
```

#### 6. 启动 API 服务器

```bash
# 开发模式
doppler run -- uv run uvicorn kb.api.app:create_app \
  --host 0.0.0.0 \
  --port 8000 \
  --reload

# 生产模式
doppler run -- gunicorn kb.api.app:create_app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120
```

#### 7. 前端设置

```bash
cd ..
npm install
npm start
# 访问 http://localhost:3001
```

### Docker 部署

**Dockerfile：**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY kb/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY kb/ kb/

# 暴露端口
EXPOSE 8000

# 启动服务
CMD ["uvicorn", "kb.api.app:create_app", "--host", "0.0.0.0", "--port", "8000"]
```

**docker-compose.yml：**

```yaml
version: '3.8'

services:
  kb-api:
    build: ./kb
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - DATABASE_URL=${DATABASE_URL}
      - TAVILY_API_KEY=${TAVILY_API_KEY}
    ports:
      - "8000:8000"
    restart: always
    depends_on:
      - postgres

  postgres:
    image: pgvector/pgvector:pg16
    environment:
      - POSTGRES_DB=kb_db
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: always

volumes:
  postgres_data:
```

---

## 故障排除

### 常见问题

#### 1. "No such table: kb_chunks_gemini"

**原因：** 表未创建

**解决方案：**

```bash
# 确保 pgvector 扩展
psql -d kb_db -c "CREATE EXTENSION IF NOT EXISTS vector;"

# 重新运行流水线
doppler run -- uv run python -m kb.cli --stage all
```

#### 2. "Web search failed: API key required"

**原因：** 缺少网络搜索 API 密钥

**解决方案：**

```bash
# 检查 API 密钥是否设置
doppler secrets get TAVILY_API_KEY

# 设置密钥
doppler secrets set TAVILY_API_KEY "tvly-your-key"
```

#### 3. "Empty retrieval results"

**原因：** score_threshold 过高

**解决方案：**

```yaml
# 在 config.yaml 中降低阈值
rag:
  retrieval:
    score_threshold: 0.4  # 从 0.6 降低
```

#### 4. 代理路由不工作

**原因：** 代理编排被禁用

**解决方案：**

```yaml
# 在 config.yaml 中启用
rag:
  agent_orchestration:
    enabled: true
```

### 调试模式

```bash
# 启用调试日志
LOG_LEVEL=DEBUG doppler run -- uv run uvicorn kb.api.app:create_app --reload
```

### 健康检查

```bash
# 检查 API 健康状态
curl http://localhost:8000/health

# 测试搜索端点
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "test", "k": 5}'

# 测试代理端点
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "什么是 RAG？", "top_k": 5}'
```

---

## 性能优化

### 数据库优化

```sql
-- 创建向量索引（如果不存在）
CREATE INDEX IF NOT EXISTS kb_chunks_gemini_embedding_idx
ON kb_chunks_gemini
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- 创建文档 ID 索引
CREATE INDEX IF NOT EXISTS kb_chunks_gemini_doc_id_idx
ON kb_chunks_gemini(doc_id);
```

### 连接池

```python
# 配置池大小
ConnectionPool(
    conninfo=database_url,
    min_size=1,
    max_size=10,  # 根据并发调整
    open=False
)
```

### 批处理

```yaml
# 优化批处理大小
vector_store:
  batch_size: 32  # 嵌入批处理大小

web_search:
  max_results: 5  # 限制搜索结果
```

---

## 测试

### 单元测试

```bash
cd kb
pytest tests/
```

### 集成测试

```bash
# 使用真实数据库测试
pytest tests/integration/ --integration
```

### 手动测试

```bash
# 测试知识代理
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "如何实现 RAG 架构？", "top_k": 5}'

# 测试网络搜索代理
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "2025 年最新的 AI 趋势是什么？", "top_k": 5}'

# 测试混合代理
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "GPT-4 API 的当前价格是多少？", "top_k": 5}'
```

---

## 路线图

### 第 1 阶段：已完成 ✅

- [x] 基本 RAG 系统
- [x] 文档索引流水线
- [x] 语义搜索
- [x] AI 问答
- [x] 前端集成
- [x] **代理编排系统**
- [x] **网络搜索集成**
- [x] **工具调用支持**
- [x] **混合搜索 + 重新排序**

### 第 2 阶段：进行中 🚧

- [ ] 流式响应（SSE）
- [ ] 多轮对话记忆
- [ ] 用户反馈机制
- [ ] 分析仪表板

### 第 3 阶段：计划中 📋

- [ ] 多模态支持（图像、图表）
- [ ] 可插拔的 LLM 引擎
- [ ] A/B 测试框架
- [ ] 高级过滤策略

### 第 4 阶段：未来 🔮

- [ ] 自定义工具插件
- [ ] 自适应检索策略
- [ ] 知识图谱增强
- [ ] 多语言支持

---

## 参考资料

- [Gemini API 文档](https://ai.google.dev/gemini-api/docs/models)
- [pgvector 文档](https://github.com/pgvector/pgvector)
- [LangChain 文档](https://docs.langchain.com/)
- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [Tavily 搜索 API](https://tavily.com/)
- [Brave 搜索 API](https://brave.com/search/api)

---

## 更新日志

| 日期 | 版本 | 变更 |
|------|------|------|
| 2025-02-05 | v2.0.0 | **代理编排系统**、网络搜索集成、工具调用、混合搜索 |
| 2025-01-XX | v1.0.0 | 初始 RAG 系统 |

---

**文档维护：** 定期更新以反映架构变更

**反馈：** [GitHub Issues](https://github.com/YiWang24/AiDIY/issues)