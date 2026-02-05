<!--
Sync Impact Report:
- Version change: Initial → 1.0.0
- Modified principles: N/A (initial creation)
- Added sections: All sections created from template
- Removed sections: None
- Templates requiring updates:
  ✅ plan-template.md - Verified alignment with content quality and separation principles
  ✅ spec-template.md - Verified alignment with Docusaurus + LangChain architecture
  ✅ tasks-template.md - Verified alignment with frontend/backend task categories
  ⚠ commands/*.md - No command files exist yet, defer to future creation
- Follow-up TODOs: None
-->

# AiDIY Constitution

## Core Principles

### I. Content-First Architecture

This is a knowledge base project, not a traditional web application. All development decisions prioritize content quality, accessibility, and searchability over feature-rich functionality.

**Rules:**
- Documentation content (`docs/`) is the primary asset - all features exist to serve content discovery and comprehension
- Frontend (Docusaurus) provides static, SEO-optimized delivery with minimal runtime overhead
- Backend (LangChain) enables semantic search and AI-powered chat assistance
- No unnecessary dynamic features - content should be browsable without JavaScript
- Performance optimization focuses on content delivery speed, not feature latency

**Rationale:** As a technical knowledge base, users prioritize fast access to accurate information over interactive features. Static site generation ensures reliability, SEO, and low operational overhead.

### II. Separation of Concerns

The architecture maintains strict boundaries between content, presentation, and intelligence layers.

**Rules:**
- **Content Layer** (`docs/`): Pure MDX/Markdown files with frontmatter - no business logic
- **Presentation Layer** (`src/`, Docusaurus): Static site generation, theming, navigation - no content processing
- **Intelligence Layer** (`kb/`, Python): LangChain pipeline for embeddings, vector search, RAG - independent of frontend deployment
- Frontend and backend are deployed independently (Vercel for static site, separate service for LangChain API)
- Communication via standard HTTP/JSON - no tight coupling

**Rationale:** Clear separation enables independent evolution. Content authors work in Markdown without touching code. Frontend updates don't require backend changes. Backend intelligence can be swapped or scaled without affecting static content delivery.

### III. Incremental Indexing (NON-NEGOTIABLE)

The knowledge base pipeline MUST support efficient incremental updates to enable rapid iteration on content.

**Rules:**
- TDD mandatory for indexing pipeline - write tests before implementing chunking, embedding, or retrieval logic
- MDX cleaning uses checksum-based change detection - only reprocess modified documents
- Vector database supports incremental updates - add/update/delete chunks without full rebuild
- Pipeline is idempotent - running multiple times produces same result
- Clear error handling - partial failures must not corrupt the index

**Rationale:** Large knowledge bases cannot afford full rebuilds on every content change. Authors need fast feedback loops. Idempotent pipeline enables reliable automation and recovery from failures.

### IV. Content Quality Standards

All documentation MUST meet quality standards before integration into the knowledge base.

**Rules:**
- Integration tests required for:
  - New content passes MDX validation
  - Frontmatter completeness and consistency
  - Broken link detection
  - Code snippet syntax verification
- Content changes trigger validation:
  - All internal links resolve
  - Code examples are syntax-highlighted and tested
  - Diagrams (Mermaid) render correctly
  - Math equations (KaTeX) parse without errors
- Static analysis pre-commit hooks prevent malformed content

**Rationale:** Broken content undermines trust in a knowledge base. Automated validation catches errors before publication. Static analysis scales better than manual review.

### V. Searchability & Discoverability

The primary success metric is how quickly users find relevant information.

**Rules:**
- Vector search (semantic) and keyword search (BM25) MUST both be available
- Hybrid retrieval combines semantic understanding with exact matching
- Search results include relevant context excerpts
- AI chat provides conversational access with source citations
- Content structure (headings, sections) is preserved in chunking for better retrieval

**Rationale:** Different search modes serve different needs. Semantic search handles conceptual queries. Keyword search finds exact terms. Citations build trust and enable deeper exploration.

### VI. Progressive Enhancement

The site MUST be fully functional without JavaScript, with enhanced features layered on top.

**Rules:**
- Core content (Markdown, images, basic navigation) renders without JavaScript
- MDX components degrade gracefully - interactive elements show static fallbacks
- AI chat widget is optional enhancement - site works without it
- Critical paths (reading documentation, searching) don't depend on client-side JavaScript

**Rationale:** Progressive enhancement ensures reliability across devices, network conditions, and browser configurations. Static content is always accessible even if JavaScript fails or is disabled.

## Development Workflow

### Content Creation

1. Author documentation in `docs/` using MDX/Markdown
2. Test locally with `npm start` (Docusaurus dev server)
3. Validate links, syntax, and rendering
4. Commit content changes

### Knowledge Base Indexing

1. Run `kb-build` to process new/changed content
2. Pipeline automatically detects changes via checksums
3. Vector database updates incrementally
4. Backend search endpoint gains new knowledge

### Deployment

- **Frontend**: Push to main branch → Vercel auto-deploys static site
- **Backend**: Independent deployment of LangChain API service
- **Database**: PostgreSQL + pgvector scales separately

## Code Quality Standards

### Frontend (Docusaurus/TypeScript/React)

- Use MDX for interactive content, plain Markdown for static pages
- Custom React components in `src/components/` must be reusable and well-documented
- Follow Docusaurus conventions for themes, plugins, and configuration
- No excessive client-side JavaScript - prefer static generation

### Backend (Python/LangChain)

- Type hints required on all public functions
- Pydantic models for configuration and data validation
- LangChain abstractions only where they add value - prefer explicit implementations
- Tests for all indexing, retrieval, and search logic
- Error handling with clear user-facing messages

### Infrastructure

- Environment variables via Doppler (never hardcode secrets)
- Database migrations handled explicitly
- Observability via structured logging
- No external service dependencies beyond PostgreSQL and embedding API

## Governance

This constitution governs all development decisions for the AiDIY knowledge base.

### Amendment Process

1. Propose changes with rationale and impact analysis
2. Update version according to semantic versioning:
   - **MAJOR**: Remove or redefine core principles (requires migration plan)
   - **MINOR**: Add new principle or significantly expand existing guidance
   - **PATCH**: Clarify wording, fix typos, non-semantic improvements
3. Propagate changes to all dependent templates and documentation
4. Update amendment date and changelog

### Compliance

All pull requests MUST verify compliance with applicable principles:
- Content changes → Content Quality Standards
- Indexing changes → Incremental Indexing + Searchability
- Frontend changes → Progressive Enhancement + Content-First Architecture
- Backend changes → Separation of Concerns + Code Quality Standards

Complexity MUST be justified against simplicity principles. When in doubt, choose the simpler solution.

### Runtime Guidance

For development-specific guidance not covered in this constitution, refer to:
- `/Users/wy/.claude/CLAUDE.md` - Claude Code usage patterns
- `/Users/wy/.claude/rules/` - Coding style, git workflow, testing requirements
- `/Users/wy/Documents/Projects/AiDIY/CLAUDE.md` - Project-specific development guidance

**Version**: 1.0.0 | **Ratified**: 2026-02-04 | **Last Amended**: 2026-02-04
