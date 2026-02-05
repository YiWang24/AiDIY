# KB Pipeline - 使用指南

完整的离线知识库索引流水线，将 MDX 文档转换为可语义搜索的向量数据库。

## 架构

```
MDX 文档 (docs/)
    ↓
Stage 1: 清理 (JS mdx-clean)
    ↓
JSONL (kb/data/cleaned/docs.jsonl)
    ↓
Stage 2: 索引 (Python + Gemini Embeddings + PGVector)
    ↓
向量数据库 (PostgreSQL + pgvector)
```

## 快速开始

### 安装 CLI 命令

```bash
# 安装包（会注册 kb-build 命令）
pip install -e .

# 或使用 uv
uv pip install -e .
```

### 使用 kb-build 命令

```bash
# 运行完整流水线（使用 kb/config.yaml）
kb-build

# 仅运行 Stage 1（文档清洗）
kb-build --stage clean

# 仅运行 Stage 2（构建索引）
kb-build --stage build

# 使用自定义配置文件
kb-build --config kb/custom-config.yaml

# 强制完全重建
kb-build --force-rebuild

# 启用噪音过滤
kb-build --noise-filter

# 覆盖配置文件中的路径
kb-build --docs-dir ../docs --output kb/data/cleaned/custom.jsonl
```

### Python 模块方式

```bash
# 直接运行 Python 模块
python -m kb.cli

# 带参数
python -m kb.cli --stage build --config kb/custom-config.yaml
```

## 配置文件

Pipeline 使用 `kb/config.yaml` 进行配置。创建配置文件：

```bash
# 复制示例配置
cp kb/config.example.yaml kb/config.yaml

# 编辑配置，设置必要的参数
nano kb/config.yaml
```

### 配置项说明

```yaml
# 输入/输出路径
docs_dir: docs                                    # MDX 文档目录
output_jsonl: kb/data/cleaned/docs.jsonl          # 清理后的 JSONL 输出路径

# 分块配置
chunking:
  max_section_chars: 2000                          # 最大章节字符数
  chunk_size: 500                                  # 目标分块大小
  chunk_overlap: 80                                # 分块重叠大小

# 嵌入模型配置
embedding:
  provider: gemini                                 # 提供商: gemini
  model: models/embedding-001                      # Gemini 模型: models/embedding-001, models/text-embedding-004

# Gemini API 配置
gemini:
  api_key: ${GEMINI_API_KEY:-}                     # 从环境变量读取

# 数据库配置
storage:
  database_url: ${DATABASE_URL:-postgresql://user:password@localhost:5432/kb}
```

### 环境变量

推荐使用环境变量设置敏感信息：

```bash
# 数据库连接（必需）
export DATABASE_URL="postgresql://user:pass@host:port/dbname"

# Gemini API Key（使用 Gemini embeddings 时必需）
export GEMINI_API_KEY="your-gemini-api-key"

# 或者使用 Doppler
export DATABASE_URL=$(doppler secrets get POSTGRES_URL --plain)
export GEMINI_API_KEY=$(doppler secrets get GEMINI_API_KEY --plain)
```

## Stage 1: 文档清洗

使用 JS 工具清理 MDX 文档：

- 移除 MDX 运行时代码（import/export/JSX）
- 转换 TabItem 为标题
- 保留文档结构和内容
- 生成 SHA-256 checksum（用于增量更新）
- 输出 JSONL 格式

**输出格式：**
```json
{
  "id": "ai/agentops",
  "path": "docs/ai/agentops/index.md",
  "title": "AgentOps and Security",
  "checksum": "abc123...",
  "content": "# AgentOps...\n\n## Fundamentals\n...",
  "frontmatter": { "title": "...", "tags": [...] }
}
```

## Stage 2: 向量索引

将清理后的文档索引到向量数据库：

- 使用 MarkdownHeaderTextSplitter 保留文档结构
- 使用 Gemini 生成嵌入向量（维度由模型决定）
- 存储到 PostgreSQL + pgvector
- 支持增量更新（基于 checksum）
- 支持完全重建

**数据库表：**
- `kb_documents` - 文档元数据（checksum, chunk_ids）
- `kb_chunks_<model>` - 向量嵌入（PGVector 自动创建）

## 运行结果

### Stage 1 示例输出
```
🧹 Cleaning MDX documents...
📂 Roots: docs
📤 Output: kb/data/cleaned/docs.jsonl

✅ Done!
📊 Total records: 56
✓ Success: 55
✗ Errors: 1
💾 Saved to: kb/data/cleaned/docs.jsonl
```

### Stage 2 示例输出
```
Indexing: 100%|████████████████| 56/56
✓ Indexed: 56/56 documents
  Skipped: 0
  Chunks added: 342
  Chunks deleted: 0
```

## 增量更新

Pipeline 支持增量更新：

1. **首次运行**：索引所有文档
2. **后续运行**：仅处理变更的文档（基于 checksum）
3. **强制重建**：使用 `--force-rebuild` 强制重新索引所有文档

```bash
# 增量更新（默认）
python scripts/build_kb.py

# 强制完全重建
python scripts/build_kb.py --force-rebuild
```

## 故障排除

### 数据库连接失败
```
Error: connection to server at "10.0.0.4", port 5432 failed
```
**解决方案：**
1. 检查数据库是否运行
2. 验证 DATABASE_URL 配置
3. 确认网络连接

### Gemini API 调用失败
```
Error: Gemini API key is required when using Gemini embeddings
```
**解决方案：**
1. 确保 `GEMINI_API_KEY` 环境变量已设置
2. 或在 `kb/config.yaml` 中设置 `gemini.api_key`
3. 验证 API Key 有效性

### 数据库连接失败
```
Error: connection to server at "10.0.0.4", port 5432 failed
```
**解决方案：**
1. 检查数据库是否运行
2. 验证 DATABASE_URL 配置
3. 确认网络连接

### Stage 1 清理 0 个文档
```
📊 Total records: 0
```
**解决方案：**
1. 检查 `docs_dir` 配置路径是否正确
2. 确认目录下有 `.md` 或 `.mdx` 文件
3. 检查排除规则

## 开发

### 运行测试
```bash
cd kb
PYTHONPATH=. python -m pytest tests/ -v
```

### 代码结构
```
kb/
├── domain/          # 领域实体（Document, Chunk）
├── storage/         # 存储适配器（DocStore, VectorStore）
├── pipeline/        # 流水线逻辑
│   ├── clean.py     # Stage 1: JS 工具封装
│   ├── chunk.py     # 文档分块
│   ├── config.py    # 配置管理
│   ├── incremental.py  # 增量索引
│   ├── index.py     # 索引构建器
│   └── pipeline.py  # 完整流水线
├── tools/           # JS 工具（mdx-clean）
├── tests/           # 测试套件
├── cli.py           # CLI 入口点（kb-build 命令）
├── config.yaml      # 配置文件
└── __init__.py      # 包导出
```

## 技术栈

- **Stage 1**: Node.js + mdx-clean 工具
- **Stage 2**: Python 3.11+
  - LangChain (text splitters, embeddings interface)
  - Gemini API (embeddings)
  - PostgreSQL + pgvector (psycopg3)
  - httpx (HTTP client for Gemini API)
  - PyYAML (配置文件)
  - tqdm (进度条)

## 相关链接

- [Gemini API 文档](https://ai.google.dev/gemini-api/docs/embeddings) - Gemini 嵌入 API
- [pgvector](https://github.com/pgvector/pgvector) - PostgreSQL 向量扩展
- [LangChain](https://docs.langchain.com/) - LLM 应用框架
