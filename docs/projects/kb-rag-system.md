# KB RAG System - Complete Architecture Documentation

## Project Overview

A comprehensive RAG (Retrieval-Augmented Generation) knowledge base system with intelligent agent orchestration, combining semantic search, web search capabilities, and AI-powered question answering.

**Core Features:**
- 📚 **Document Indexing**: Automatic conversion of MDX documents to vector embeddings
- 🔍 **Hybrid Search**: Semantic + keyword search with re-ranking
- 🤖 **Agent Orchestration**: Intelligent routing to specialized agents (Knowledge, Web Search, Hybrid)
- 🌐 **Web Search Fallback**: Automatic web search when knowledge base is insufficient
- 🛠️ **Tool Calling**: Native support for Gemini function calling API
- 📖 **Citation Tracking**: Every answer includes source document references
- ⚡ **Real-time Response**: Optimized retrieval and generation pipeline

## Table of Contents

1. [Technology Stack](#technology-stack)
2. [System Architecture](#system-architecture)
3. [Data Pipeline](#data-pipeline)
4. [Agent Orchestration](#agent-orchestration)
5. [Tool System](#tool-system)
6. [API Design](#api-design)
7. [Model Selection](#model-selection)
8. [Deployment Guide](#deployment-guide)
9. [Configuration](#configuration)
10. [Troubleshooting](#troubleshooting)

---

## Technology Stack

### Backend (Python)

```yaml
Core Framework:
  - FastAPI 0.110+: High-performance web framework
  - Pydantic 2.6+: Data validation and serialization
  - Uvicorn: ASGI server

Data Layer:
  - PostgreSQL 15+ with pgvector: Vector database
  - psycopg 3: Database driver
  - psycopg-pool: Connection pool management

AI/ML:
  - Gemini API: Google Gemini 2.5 Flash for LLM
  - Gemini Embeddings: models/embedding-001
  - Tavily/Brave Search: Web search integration
  - LangChain: Text processing and chunking

Data Processing:
  - PyYAML: Configuration management
  - httpx: HTTP client for external APIs
  - tqdm: Progress bars

Testing:
  - pytest 8.0+: Unit testing
  - pytest-asyncio: Async test support
```

### Frontend (TypeScript/Next.js)

```yaml
Framework:
  - Docusaurus: Documentation site generator
  - React 18+: UI framework
  - TypeScript: Type safety

Build Tools:
  - npm: Package management
  - webpack: Module bundling
```

### Infrastructure

```yaml
Database:
  - PostgreSQL 15+
  - pgvector extension
  - Python 3.11+

Environment Management:
  - Doppler: Environment variables and secrets
  - uv: Python package management
```

---

## System Architecture

### Overall Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (Docusaurus)                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │   AI Chat Widget (React)                          │   │
│  │   - User input                                     │   │
│  │   - Display AI responses and citations             │   │
│  │   - SSE streaming support                         │   │
│  │   - http://localhost:3001                         │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    API Layer (FastAPI)                      │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  POST /ask          Agent-orchestrated Q&A          │   │
│  │  POST /search       Semantic search                 │   │
│  │  GET /health        Health check                    │   │
│  │  http://localhost:8000                             │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   Agent Orchestration Layer                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │   Agent Router (Question Classifier)                │   │
│  │   - Keyword-based routing                          │   │
│  │   - Optional LLM classification                    │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Knowledge  │  │  Web Search  │  │    Hybrid    │     │
│  │    Agent     │  │    Agent     │  │    Agent     │     │
│  │  (RAG-based) │  │ (Tavily/API) │  │  (Combined)  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      Business Logic Layer                    │
│  ┌──────────────────┐  ┌──────────────────────────────┐   │
│  │   RAG Pipeline  │  │   Retriever                  │   │
│  │  - Context build │  │  - Hybrid search             │   │
│  │  - Answer gen    │  │  - Re-ranking               │   │
│  └──────────────────┘  └──────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Tool System                                       │   │
│  │  - Web search (Tavily/Brave)                      │   │
│  │  - Function calling interface                     │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                     Data Access Layer                        │
│  ┌──────────────────┐  ┌──────────────────────────────┐   │
│  │   VectorStore   │  │   DocStore                  │   │
│  │  - pgvector     │  │   - Document metadata       │   │
│  │  - Similarity   │  │   - Checksum tracking       │   │
│  └──────────────────┘  └──────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                     Storage Layer                            │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  PostgreSQL + pgvector                              │   │
│  │  - kb_documents: Document metadata                  │   │
│  │  - kb_chunks_gemini: Vector embeddings (768-dim)   │   │
│  │  - kb_index_meta: Index signatures                 │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Data Pipeline (Offline Indexing)                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Stage 1: Document Cleaning                        │   │
│  │  - MDX → JSONL (JavaScript tools)                  │   │
│  │  - Remove runtime code                             │   │
│  │  - Generate checksums                              │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Stage 2: Vector Indexing                          │   │
│  │  - Text chunking                                   │   │
│  │  - Embedding generation (Gemini)                   │   │
│  │  - Database storage                                │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Request Flow Diagram

```
User Question
   │
   ▼
┌──────────────────┐
│  Agent Router    │
│  - Classify Q    │
│  - Select Agent  │
└────────┬─────────┘
         │
    ┌────┴────┬────────────┐
    ▼         ▼            ▼
┌───────┐ ┌─────────┐ ┌─────────┐
│Know.  │ │   Web   │ │ Hybrid  │
│Agent  │ │  Agent  │ │ Agent  │
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
    │   Retriever  │
    │  - Hybrid    │
    │  - Re-rank   │
    └──────┬───────┘
           ▼
    ┌──────────────┐
    │Context Builder│
    └──────┬───────┘
           ▼
    ┌──────────────┐
    │   LLM Call   │
    │  (Gemini)    │
    └──────┬───────┘
           ▼
    ┌──────────────┐
    │  Response    │
    │  + Citations │
    └──────────────┘
           │
           ▼
     Return to User
```

---

## Data Pipeline

### Pipeline Stages

#### Stage 1: Document Cleaning

**Tool:** JavaScript + mdx-clean

**Input:** MDX source files

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

**Processing Steps:**

1. **Read MDX files**: Parse frontmatter and content
2. **Remove runtime code**:
   - Remove import/export statements
   - Remove JSX syntax
   - Preserve markdown content
3. **Transform special syntax**:
   - TabItems → headings
   - Preserve code blocks
   - Preserve Mermaid diagrams
4. **Generate metadata**:
   - Document ID
   - Title
   - Path
   - SHA-256 checksum (for incremental updates)
5. **Output JSONL**: `kb/data/cleaned/docs.jsonl`

**Output Format:**

```json
{
  "id": "ai/agentops",
  "path": "docs/ai/agents/agentops/index.mdx",
  "title": "AgentOps and Security",
  "checksum": "6c5bb14e0a5801d7fb4fb4431ef3e58e8c8cf6b19bab56970589111a4007625b",
  "content": "# AgentOps and Security\n\nAgentOps combines...",
  "frontmatter": {
    "title": "AgentOps and Security",
    "tags": ["agents", "security"]
  }
}
```

**CLI Commands:**

```bash
# Run Stage 1 only
kb-build --stage clean

# Specify input/output
kb-build --stage clean --docs-dir ./docs --output kb/data/cleaned/custom.jsonl
```

#### Stage 2: Vector Indexing

**Tool:** Python + Gemini Embeddings

**Input:** `kb/data/cleaned/docs.jsonl`

**Processing Flow:**

```mermaid
graph LR
    A[JSONL Docs] --> B[Text Chunking]
    B --> C{Recursive Split}
    C --> D[Generate Chunks]
    D --> E[Embedding Gen]
    E --> F[PostgreSQL+pgvector]
    F --> G[Vector Index]
```

**1. Text Chunking**

```python
# Strategy: MarkdownHeaderTextSplitter + RecursiveCharacterTextSplitter

Configuration:
- max_section_chars: 2000  # Max chars before recursive split
- chunk_size: 500           # Target chunk size
- chunk_overlap: 80         # Overlap between chunks

Preserve:
- Heading hierarchy (H1, H2, H3...)
- Section structure
- Paragraph content
```

**2. Embedding Generation**

```python
# Using Gemini Embeddings API

Model: models/embedding-001
API: https://generativelanguage.googleapis.com/v1beta/

Batch requests:
- batch_size: 32 chunks/request
- Auto-retry mechanism
- Progress bar display

Output: 768-dimensional vectors
```

**3. Database Storage**

```sql
-- Document metadata table
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

-- Vector embeddings table
CREATE TABLE kb_chunks_gemini (
    id SERIAL PRIMARY KEY,
    chunk_id VARCHAR(64) UNIQUE NOT NULL,
    doc_id VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    heading_path JSONB DEFAULT '[]',
    chunk_index INTEGER DEFAULT 0,
    embedding vector(768),  -- Gemini embedding dimension
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Vector similarity index (IVFFlat)
CREATE INDEX kb_chunks_gemini_embedding_idx
ON kb_chunks_gemini
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

**Incremental Update Mechanism:**

```python
# Checksum-based incremental indexing

1. Calculate SHA-256 checksum of document content
2. Compare with database checksum
3. If same: skip
4. If different:
   - Delete old chunks
   - Re-chunk and embed
   - Update database
```

**CLI Commands:**

```bash
# Run Stage 2 only
kb-build --stage build

# Force full rebuild
kb-build --stage build --force-rebuild

# Specify JSONL input
kb-build --stage build --output kb/data/cleaned/custom.jsonl
```

#### Performance Metrics

| Metric | Current Value |
|--------|---------------|
| Total Documents | 39 documents |
| Total Chunks | 3,043 chunks |
| Avg Chunk Size | ~500 chars |
| Index Time | ~2 minutes (56 docs) |
| Retrieval Latency | ~300ms |

---

## Agent Orchestration

### Architecture Overview

The agent orchestration system provides intelligent question routing to specialized handlers:

```
User Question
    ↓
Agent Router (Question Classifier)
    ↓
    ├─→ Knowledge Agent (RAG-based Q&A)
    │       ├─→ Hybrid Search (semantic + keyword)
    │       ├─→ Re-ranking
    │       └─→ Generate Answer
    │
    ├─→ Web Search Agent (Online search)
    │       ├─→ Tavily/Brave Search
    │       └─→ Summarize Results
    │
    └─→ Hybrid Agent (Combined)
            ├─→ Try RAG First
            ├─→ If insufficient: Web Search
            └─→ Merge and Answer
```

### Agent Router

**File:** `kb/agents/router.py`

**Routing Strategy:**

1. **Keyword-based heuristics** (default):
   - Knowledge: "how to", "explain", "architecture", "implementation"
   - Web Search: "latest", "news", "current", "price", "2025"
   - Hybrid: Fallback for uncertain cases

2. **Optional LLM classification**:
   - Enable with `use_llm_routing: true`
   - Uses Gemini to classify question type
   - Provides more accurate routing

**Route Rules:**

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

### Knowledge Agent

**File:** `kb/agents/knowledge_agent.py`

**Responsibilities:**
- RAG-based question answering
- Hybrid search + re-ranking
- Citation generation

**Workflow:**

```python
1. Retrieve chunks using hybrid search
2. Check if results are sufficient (score > 0.4)
3. If insufficient: return with has_sufficient_knowledge=False
4. Generate answer using retrieved context
5. Return enriched with citations
```

**Confidence Scoring:**
- Technical questions: 0.85
- Generic questions: 0.55
- Knowledge-specific keywords: +0.15

### Web Search Agent

**File:** `kb/agents/web_search_agent.py`

**Responsibilities:**
- Real-time information retrieval
- Web search via Tavily or Brave
- Answer synthesis from search results

**Workflow:**

```python
1. Perform web search
2. Format search results
3. Generate answer from results
4. Return with sources
```

**Confidence Scoring:**
- Real-time keywords: 0.90
- Current events: 0.75
- Generic: 0.40

### Hybrid Agent

**File:** `kb/agents/hybrid_agent.py`

**Responsibilities:**
- Combine knowledge base and web search
- Automatic fallback
- Merge information from both sources

**Workflow:**

```python
1. Try knowledge base first
2. Check if results are sufficient (score > 0.3)
3. If sufficient: return KB results
4. If insufficient:
   - Perform web search
   - Merge both results
   - Clearly distinguish sources
5. Return combined answer
```

**Confidence Scoring:**
- All questions: 0.65 (safe fallback)

### Agent Interface

All agents implement the `Agent` base class:

```python
class Agent(ABC):
    @abstractmethod
    async def handle(self, question: str, context: Dict) -> Dict:
        """Handle question and return response."""
        pass

    @abstractmethod
    def can_handle(self, question: str) -> float:
        """Return confidence score (0.0 - 1.0)."""
        pass
```

---

## Tool System

### Tool Interface

**File:** `kb/tools/base.py`

The tool system provides a pluggable interface for function calling:

```python
class Tool(ABC):
    @abstractmethod
    def name(self) -> str:
        """Tool name for function calling."""
        pass

    @abstractmethod
    def description(self) -> str:
        """Tool description for the LLM."""
        pass

    @abstractmethod
    def parameters_schema(self) -> Dict[str, Any]:
        """JSON schema for parameters."""
        pass

    @abstractmethod
    async def execute(self, **kwargs) -> str:
        """Execute tool and return result."""
        pass

    def to_function_declaration(self) -> Dict[str, Any]:
        """Convert to Gemini function declaration format."""
        return {
            "name": self.name(),
            "description": self.description(),
            "parameters": self.parameters_schema(),
        }
```

### Web Search Tool

**File:** `kb/tools/web_search.py`

**Supported Providers:**
- Tavily Search (primary, recommended)
- Brave Search (alternative)

**Features:**
- Async execution
- Configurable max_results
- Search depth options (basic/advanced)
- LLM-friendly result formatting

**Usage Example:**

```python
tool = WebSearchTool(
    provider="tavily",
    api_key=os.getenv("TAVILY_API_KEY"),
    max_results=5,
    search_depth="basic"
)

result = await tool.execute(
    query="latest AI trends 2025",
    max_results=5
)
```

### Tool Calling Support

**File:** `kb/llm/gemini.py`

Gemini LLM now supports function calling:

```python
async def generate_with_tools(
    prompt: str,
    tools: List[Any],
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    max_tool_calls: int = 5,
) -> LLMResponse:
    """Generate with tool calling support.

    Automatically handles tool call loops and collects results.
    """
```

**Features:**
- Automatic tool execution
- Multi-step tool calling
- Conversation history management
- Error handling with graceful degradation

---

## API Design

### Endpoint Overview

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API info and available endpoints |
| `/health` | GET | Health check |
| `/search` | POST | Semantic search (no LLM) |
| `/ask` | POST | Agent-orchestrated Q&A |

### API Details

#### 1. Root Endpoint `/`

**Request:**

```http
GET / HTTP/1.1
```

**Response:**

```json
{
  "name": "KB RAG API",
  "version": "1.0.0",
  "description": "RAG-based knowledge base with agent orchestration",
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

#### 2. Health Check `/health`

**Request:**

```http
GET /health HTTP/1.1
```

**Response:**

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

#### 3. Semantic Search `/search`

**Request:**

```http
POST /search HTTP/1.1
Content-Type: application/json

{
  "query": "What is AgentOps?",
  "k": 5
}
```

**Response:**

```json
[
  {
    "chunk_id": "82cd0834...",
    "doc_id": "docs:ai/prompt-engineering/09-agent-orchestration.mdx",
    "content": "Each agent has ONE primary role...",
    "heading_path": ["Best Practices Summary", "2. Clear Agent Boundaries"],
    "chunk_index": 201,
    "score": 0.708,
    "document": {
      "title": "9 Agent Orchestration",
      "path": "docs/ai/prompt-engineering/09-agent-orchestration.mdx"
    }
  }
]
```

#### 4. Agent-Orchestrated Q&A `/ask`

**Request:**

```http
POST /ask HTTP/1.1
Content-Type: application/json

{
  "question": "What are the agent orchestration patterns?",
  "top_k": 5
}
```

**Response (Knowledge Agent):**

```json
{
  "answer": "Based on the knowledge base, the agent orchestration patterns include the Sequential Pattern and Supervisor + Workers pattern...",
  "citations": [
    {
      "id": 1,
      "chunk_id": "42fd61e4...",
      "doc_id": "docs:design-patterns",
      "title": "3. Design Patterns",
      "path": "https://docs.yiw.me/docs/ai/agents/design-patterns",
      "heading_path": ["3. Agent Design Patterns", "3.2 Multi-Agent Patterns", "Pattern 8: Sequential Pattern"],
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

**Response (Web Search Agent):**

```json
{
  "answer": "Based on web search results, the latest agent orchestration patterns in 2025 include...",
  "citations": [],
  "has_sufficient_knowledge": true,
  "model": "gemini-2.5-flash",
  "tokens_used": 856,
  "retrieval_time_ms": 1200,
  "generation_time_ms": 543,
  "agent_type": "web_search"
}
```

**Response (Hybrid Agent):**

```json
{
  "answer": "Based on the knowledge base and web search:\n\n**From Knowledge Base:**\nTraditional agent patterns include...\n\n**From Web Search:**\nLatest 2025 approaches add...",
  "citations": [
    {
      "id": 1,
      "chunk_id": "abc123...",
      "doc_id": "docs:ai/agents",
      "title": "Agent Patterns",
      "path": "https://docs.yiw.me/docs/ai/agents",
      "heading_path": ["Introduction"],
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

### Error Handling

**Error Response Format:**

```json
{
  "detail": "Ask request failed: Web search API error: 401 - Invalid API key"
}
```

**HTTP Status Codes:**

| Status | Description |
|--------|-------------|
| 200 | Success |
| 400 | Bad request (invalid parameters) |
| 401 | Unauthorized (missing/invalid API key) |
| 429 | Rate limit exceeded |
| 500 | Internal server error |
| 503 | Service unavailable (LLM/downstream API error) |

### Request/Response Schemas

**AskRequest:**

```python
class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=500)
    top_k: int = Field(default=10, ge=1, le=20)
```

**AskResponse:**

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

**Citation:**

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

## Model Selection

### Gemini Model Comparison

| Model | Status | Use Case | Recommended |
|-------|--------|----------|-------------|
| **Gemini 2.5 Flash** | ✅ Stable | **Production (Default)** | ⭐⭐⭐⭐⭐ |
| **Gemini 2.5 Pro** | ✅ Stable | High-quality reasoning | ⭐⭐⭐⭐ |
| **Gemini 1.5 Flash** | ✅ Stable | Backup option | ⭐⭐⭐ |
| **Gemini Flash Latest** | ✅ Available | Latest stable | ⭐⭐⭐⭐ |

### Current Configuration

**LLM Model:**

```yaml
llm:
  model: gemini-2.5-flash       # Current default
  temperature: 0.3              # Low for factual accuracy
  max_tokens: 1024
```

**Embedding Model:**

```yaml
embedding:
  model: models/embedding-001   # 768-dimensional vectors
```

### Performance Comparison

| Model | Latency | Cost | Quality | Stability |
|-------|---------|------|---------|-----------|
| **Gemini 2.5 Flash** | ~600ms | Low | ⭐⭐⭐⭐ | High |
| **Gemini 2.5 Pro** | ~1200ms | Medium | ⭐⭐⭐⭐⭐ | High |

---

## Configuration

### Complete Configuration File

**File:** `kb/config.yaml`

```yaml
# Input/Output paths
docs_dir: docs
output_jsonl: kb/data/cleaned/docs.jsonl

# Chunking configuration
chunking:
  max_section_chars: 2000
  chunk_size: 500
  chunk_overlap: 80

# Embedding configuration
embedding:
  provider: gemini
  model: models/embedding-001

# Gemini API configuration
gemini:
  api_key: ${GEMINI_API_KEY:-}

# Storage configuration
storage:
  database_url: ${DATABASE_URL:-postgresql://user:password@localhost:5432/kb}

# Vector store configuration
vector_store:
  table_name: kb_chunks_gemini
  batch_size: 32

# LLM configuration
llm:
  provider: gemini
  model: gemini-2.5-flash
  api_key: ${GEMINI_API_KEY:-}
  temperature: 0.3
  max_tokens: 1024

# RAG configuration
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

  # Agent orchestration (NEW)
  agent_orchestration:
    enabled: true                    # Enable agent system
    fallback_to_web: true             # Enable web search fallback
    web_fallback_threshold: 0.3       # If max score < 0.3, use web
    use_llm_routing: false            # Use LLM for routing (default: keyword only)

# Web search configuration (NEW)
web_search:
  provider: tavily                    # tavily or brave
  api_key: ${TAVILY_API_KEY:-}       # From Doppler
  max_results: 5
  search_depth: basic                 # basic or advanced
  timeout: 30

# Docusaurus configuration
docusaurus:
  site_url: "https://docs.yiw.me"
```

### Environment Variables

**Required:**

```bash
# Database
DATABASE_URL=postgresql://user:password@host:port/dbname

# Gemini API
GEMINI_API_KEY=your-gemini-api-key

# Web Search (one or both)
TAVILY_API_KEY=tvly-your-key
BRAVE_API_KEY=your-brave-key
```

### Managing Secrets with Doppler

```bash
# Login to Doppler
doppler login

# Set secrets
doppler secrets set GEMINI_API_KEY "your-key"
doppler secrets set DATABASE_URL "postgresql://..."
doppler secrets set TAVILY_API_KEY "tvly-..."

# Run with Doppler
doppler run -- uv run uvicorn kb.api.app:create_app --reload
```

---

## Deployment Guide

### Prerequisites

- Python 3.11+
- PostgreSQL 15+ with pgvector
- Doppler CLI (for secrets management)
- Node.js 18+ (for frontend)

### Installation

#### 1. Clone and Setup

```bash
git clone https://github.com/YiWang24/AiDIY.git
cd AiDIY
```

#### 2. Install Backend Dependencies

```bash
cd kb
pip install -e .
```

#### 3. Configure Environment

```bash
# Using Doppler
doppler login

# Set required secrets
doppler secrets set GEMINI_API_KEY "your-gemini-api-key"
doppler secrets set DATABASE_URL "postgresql://user:password@host:port/dbname"
doppler secrets set TAVILY_API_KEY "tvly-your-key"
```

#### 4. Initialize Database

```sql
-- Install pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create database (if needed)
CREATE DATABASE kb_db;
```

#### 5. Run Data Pipeline

```bash
# Run complete pipeline
doppler run -- uv run python -m kb.cli --stage all

# Force rebuild
doppler run -- uv run python -m kb.cli --stage all --force-rebuild
```

#### 6. Start API Server

```bash
# Development
doppler run -- uv run uvicorn kb.api.app:create_app \
  --host 0.0.0.0 \
  --port 8000 \
  --reload

# Production
doppler run -- gunicorn kb.api.app:create_app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120
```

#### 7. Frontend Setup

```bash
cd ..
npm install
npm start
# Visit http://localhost:3001
```

### Docker Deployment

**Dockerfile:**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY kb/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy code
COPY kb/ kb/

# Expose port
EXPOSE 8000

# Start service
CMD ["uvicorn", "kb.api.app:create_app", "--host", "0.0.0.0", "--port", "8000"]
```

**docker-compose.yml:**

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

## Troubleshooting

### Common Issues

#### 1. "No such table: kb_chunks_gemini"

**Cause:** Tables not created

**Solution:**

```bash
# Ensure pgvector extension
psql -d kb_db -c "CREATE EXTENSION IF NOT EXISTS vector;"

# Re-run pipeline
doppler run -- uv run python -m kb.cli --stage all
```

#### 2. "Web search failed: API key required"

**Cause:** Missing web search API key

**Solution:**

```bash
# Check if API key is set
doppler secrets get TAVILY_API_KEY

# Set the key
doppler secrets set TAVILY_API_KEY "tvly-your-key"
```

#### 3. "Empty retrieval results"

**Cause:** score_threshold too high

**Solution:**

```yaml
# Lower threshold in config.yaml
rag:
  retrieval:
    score_threshold: 0.4  # Lower from 0.6
```

#### 4. Agent routing not working

**Cause:** Agent orchestration disabled

**Solution:**

```yaml
# Enable in config.yaml
rag:
  agent_orchestration:
    enabled: true
```

### Debug Mode

```bash
# Enable debug logging
LOG_LEVEL=DEBUG doppler run -- uv run uvicorn kb.api.app:create_app --reload
```

### Health Checks

```bash
# Check API health
curl http://localhost:8000/health

# Test search endpoint
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "test", "k": 5}'

# Test agent endpoint
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is RAG?", "top_k": 5}'
```

---

## Performance Optimization

### Database Optimization

```sql
-- Create vector index (if not exists)
CREATE INDEX IF NOT EXISTS kb_chunks_gemini_embedding_idx
ON kb_chunks_gemini
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Create document ID index
CREATE INDEX IF NOT EXISTS kb_chunks_gemini_doc_id_idx
ON kb_chunks_gemini(doc_id);
```

### Connection Pooling

```python
# Configure pool size
ConnectionPool(
    conninfo=database_url,
    min_size=1,
    max_size=10,  # Adjust based on concurrency
    open=False
)
```

### Batch Processing

```yaml
# Optimize batch sizes
vector_store:
  batch_size: 32  # Embedding batch size

web_search:
  max_results: 5  # Limit search results
```

---

## Testing

### Unit Tests

```bash
cd kb
pytest tests/
```

### Integration Tests

```bash
# Test with real database
pytest tests/integration/ --integration
```

### Manual Testing

```bash
# Test knowledge agent
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "How do I implement RAG architecture?", "top_k": 5}'

# Test web search agent
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the latest AI trends in 2025?", "top_k": 5}'

# Test hybrid agent
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the current price of GPT-4 API?", "top_k": 5}'
```

---

## Roadmap

### Phase 1: Completed ✅

- [x] Basic RAG system
- [x] Document indexing pipeline
- [x] Semantic search
- [x] AI Q&A
- [x] Frontend integration
- [x] **Agent orchestration system**
- [x] **Web search integration**
- [x] **Tool calling support**
- [x] **Hybrid search + re-ranking**

### Phase 2: In Progress 🚧

- [ ] Streaming responses (SSE)
- [ ] Multi-turn conversation memory
- [ ] User feedback mechanism
- [ ] Analytics dashboard

### Phase 3: Planned 📋

- [ ] Multi-modal support (images, charts)
- [ ] Pluggable LLM engines
- [ ] A/B testing framework
- [ ] Advanced filtering strategies

### Phase 4: Future 🔮

- [ ] Custom tool plugins
- [ ] Adaptive retrieval strategies
- [ ] Knowledge graph enhancement
- [ ] Multi-language support

---

## References

- [Gemini API Documentation](https://ai.google.dev/gemini-api/docs/models)
- [pgvector Documentation](https://github.com/pgvector/pgvector)
- [LangChain Documentation](https://docs.langchain.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Tavily Search API](https://tavily.com/)
- [Brave Search API](https://brave.com/search/api)

---

## Changelog

| Date | Version | Changes |
|------|---------|---------|
| 2025-02-05 | v2.0.0 | **Agent orchestration system**, web search integration, tool calling, hybrid search |
| 2025-01-XX | v1.0.0 | Initial RAG system |

---

**Document Maintenance:** Regularly updated to reflect architecture changes

**Feedback:** [GitHub Issues](https://github.com/YiWang24/AiDIY/issues)
