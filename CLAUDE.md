# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a standalone Docusaurus documentation site that serves as a technical knowledge base covering:
- **CS Core**: Algorithms, System Design, Database Internals, Network & OS
- **AI & Agents**: LLM Fundamentals, Prompt Engineering, RAG, Agents, MCP, Context Engineering
- **Engineering**: Backend (Java), Frontend, DevOps & Cloud, Dev Tools
- **Case Studies**: Real-world project examples and refactorings

## Architecture

### Deployment

- **Production**: Deployed as static site on Vercel
- **Development**: Runs on `http://localhost:3001`
- **Output**: Static files in `build/` directory

### Key Components

1. **Documentation Content** (`docs/`)
   - Organized by topic (cs/, ai/, engineering/, projects/)
   - Uses MDX format for enhanced markdown with React components
   - Sidebar structure defined in `sidebars.ts`

2. **AI Chat Widget** (`src/components/AIChatWidget/`)
   - Floating chat interface on all pages
   - Streaming responses via Server-Sent Events (SSE)
   - Session-based conversation management

3. **Custom Docusaurus Theme** (`src/theme/Root.tsx`)
   - Wraps all pages with AIChatWidget component
   - Global layout customization

## Development Commands

### Start Development Server

```bash
npm start
```

- Runs Docusaurus on `http://localhost:3001`
- Hot reload enabled
- MDX and live codeblock support active

### Build for Production

```bash
npm run build
```

- Builds static site to `build/` directory
- Deploy `build/` to Vercel

### Other Useful Commands

```bash
npm run clear          # Clear Docusaurus cache
npm run serve          # Serve production build locally
npm run swizzle        # Customize Docusaurus components
```

## Content Structure

### Adding Documentation Pages

1. Create `.md` or `.mdx` file in appropriate `docs/` subdirectory
2. Add entry to `sidebars.ts` under the relevant sidebar

```typescript
// sidebars.ts
csSidebar: [
  {
    type: "doc",
    id: "cs/algorithms/index",  // maps to docs/cs/algorithms/index.md
    label: "Overview",
  },
]
```

### Adding Blog Posts

Create file in `blog/YYYY-MM-DD-title/index.md`

### Supported Features

- **MDX**: Import/use React components in markdown
- **Live Codeblocks**: Interactive React code editing (use `LiveCodeBlock` from theme)
- **Mermaid Diagrams**: Embed diagrams with ```mermaid blocks
- **Math**: LaTeX math support via KaTeX (remark-math + rehype-katex)
- **Image Zoom**: Click images to zoom (docusaurus-plugin-image-zoom)
- **npm2yarn**: Auto-generate npm/yarn/pnpm tabs for install commands
- **Copy Page**: Copy entire page as markdown (docusaurus-plugin-copy-page-button)

## Custom Components

### AIChatWidget

Located at `src/components/AIChatWidget/index.tsx`

**Key behaviors:**
- Generates unique session IDs for each chat session
- Streams responses using SSE protocol
- Parses events: `response_delta`, `thinking_delta`, `complete`, `error`
- Auto-scrolls to latest message
- Clears chat with new session generation
- Uses backend URL from `docusaurus.config.ts` custom fields

## Important Configuration Files

- `docusaurus.config.ts` - Main Docusaurus configuration, themes, plugins, custom fields
- `sidebars.ts` - Documentation navigation structure
- `vercel.json` - Vercel deployment settings
- `remark-plugin.ts` - Custom remark plugin for code block escaping
- `tsconfig.json` - TypeScript configuration (extends @docusaurus/tsconfig)

## Content Guidelines

- Use `.mdx` for pages requiring React components or interactive elements
- Use `.md` for static content
- Follow existing folder structure when adding new topics
- Update `sidebars.ts` when adding new documentation pages
- Keep frontmatter consistent with existing pages
- Use Mermaid for diagrams, not images
- Leverage MDX components for enhanced interactivity
