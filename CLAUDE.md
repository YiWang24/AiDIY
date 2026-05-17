# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Standalone Docusaurus knowledge base + RAG chat assistant covering:
- **CS Core**: Algorithms, System Design, Database Internals, Network & OS
- **AI & Agents**: LLM Fundamentals, Prompt Engineering, RAG, Agents, MCP, Context Engineering
- **Engineering**: Backend (Java), Frontend, DevOps & Cloud, Dev Tools
- **Case Studies**: Real-world project examples and refactorings

## Architecture

Single Vercel project. No standalone backend, no Docker, no SSH targets.

```
[ Browser ]
   └── Docusaurus pages + AIChatWidget (@ai-sdk/react useChat)
            │
            ▼  POST /api/chat  (UIMessage stream, AI SDK v5)
[ Vercel Functions / Node runtime ]
   ├── api/chat.ts       — streamText + kb_search tool + persistence
   ├── api/messages.ts   — GET history for a session
   └── api/sessions.ts   — GET list / DELETE
            │
            ├──▶ Neon Postgres (Vercel Marketplace integration)
            │      tables: kb_documents, kb_chunks_glm (vector 2048),
            │              chat_sessions, chat_messages
            │      extensions: vector, pg_trgm
            │
            └──▶ GLM (Zhipu BigModel, OpenAI-compatible)
                   chat = glm-4.7
                   embedding = embedding-3 (2048-dim)
```

Ingestion runs in GitHub Actions (`.github/workflows/ingest.yml`) on push to
main when `docs/**`, `blog/**`, or the ingest pipeline changes. Incremental via
`kb_documents.checksum`.

### Code map

| Path | Role |
|---|---|
| `src/components/AIChatWidget/` | Chat UI (Docusaurus swizzle), now backed by `useChat` |
| `api/chat.ts` | Streaming chat endpoint with `kb_search` tool |
| `api/messages.ts` | Loads persisted history for a session |
| `api/sessions.ts` | Lists / deletes sessions |
| `lib/db/client.ts` | Neon serverless driver (HTTP + Pool) |
| `lib/db/schema.sql` | Source of truth for all tables / indexes |
| `lib/db/queries.ts` | Typed query helpers used by api/* and scripts/* |
| `lib/ai/provider.ts` | GLM OpenAI-compatible provider |
| `lib/ai/embed.ts` | Single / batch embeddings + pgvector wire format |
| `lib/rag/retrieve.ts` | embed → pgvector cosine top-k |
| `lib/rag/chunk.ts` | Markdown header-aware splitter |
| `scripts/ingest.ts` | CLI: clean MDX → chunk → embed → upsert |
| `scripts/migrate.ts` | Applies `lib/db/schema.sql` |
| `kb/tools/mdx-clean/` | Existing JS MDX cleaner — reused by ingest |

## Development Commands

```bash
npm install                         # install deps (incl. ai/@ai-sdk/* + @neondatabase/serverless)
npm run db:migrate                  # one-time: create tables in Neon
npm run ingest                      # embed docs/ + blog/ into kb_chunks_glm
npm start                           # Docusaurus dev server on :3001
vercel dev                          # full stack locally (api/* + Docusaurus)
npm run build                       # static build to build/
```

Required env (local: `.env.local`; prod: Vercel dashboard / Neon Marketplace):
`DATABASE_URL`, `GLM_API_KEY`, `GLM_CHAT_MODEL`, `GLM_EMBED_MODEL`,
`GLM_EMBED_DIM`, optional `GLM_BASE_URL`.

## Content Structure

### Adding Documentation Pages

1. Create `.md` or `.mdx` file in appropriate `docs/` subdirectory
2. Add entry to `sidebars.ts` under the relevant sidebar
3. Merging to main triggers `.github/workflows/ingest.yml` which re-embeds the changed docs into Neon

### Adding Blog Posts

Create file in `blog/YYYY-MM-DD-title/index.md`. Ingestion picks these up too.

### Supported Features

- **MDX**: Import/use React components in markdown
- **Live Codeblocks**: Interactive React code editing
- **Mermaid Diagrams**: ```` ```mermaid ```` blocks
- **Math**: LaTeX via KaTeX (remark-math + rehype-katex)
- **Image Zoom**: docusaurus-plugin-image-zoom
- **npm2yarn**: Auto-generated install command tabs
- **Copy Page**: Copy entire page as markdown

## AIChatWidget

`src/components/AIChatWidget/index.tsx` mounts globally via the Docusaurus Root
swizzle (`src/theme/Root.tsx`). It wraps `useChat` from `@ai-sdk/react`:

- `useSessionId` hook persists `sessionId` in `localStorage` so refresh resumes the conversation
- On session change, history is hydrated from `GET /api/messages?sessionId=...`
- "Clear chat" rotates to a new session id
- Tool results from `kb_search` are rendered as a citation list under the assistant message

The server side keeps things minimal: `streamText` with a single `kb_search`
tool, `stopWhen: stepCountIs(4)`, and `toUIMessageStreamResponse` with an
`onFinish` callback that upserts the full conversation into `chat_messages`.

## Important Configuration Files

- `docusaurus.config.ts` — Main Docusaurus config (no longer has backendUrl)
- `sidebars.ts` — Documentation navigation structure
- `vercel.json` — Sets `maxDuration: 300` for `api/chat.ts`
- `remark-plugin.ts` — Custom remark plugin for code block escaping
- `tsconfig.json` — extends `@docusaurus/tsconfig`
- `lib/db/schema.sql` — Source of truth for the Neon schema

## Legacy

The `kb/` directory still contains the original Python FastAPI + LangChain
implementation along with `Dockerfile` / `docker-compose.yml` / `start.sh`.
These are **kept temporarily for rollback** during the migration cutover. They
are not part of the active stack and will be removed after the new system has
been verified stable in production. The only file in `kb/` still imported by
active code is `kb/tools/mdx-clean/` (the JS MDX cleaner), used by
`scripts/ingest.ts`.

## Content Guidelines

- Use `.mdx` for pages requiring React components or interactive elements
- Use `.md` for static content
- Follow existing folder structure when adding new topics
- Update `sidebars.ts` when adding new documentation pages
- Keep frontmatter consistent with existing pages
- Use Mermaid for diagrams, not images
