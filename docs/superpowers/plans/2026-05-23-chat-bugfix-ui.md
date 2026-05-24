# Chat Bug Fixes + UI Polish Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix button delay (3-5s), no-content output bug (step limit), and add compact tool-call display + auto-scroll to answer.

**Architecture:** Five targeted file changes — new `useSessionMessages` hook for localStorage SWR removes the null-wait gate; `stepCountIs(10)` fixes the step-exhaustion bug; `turnAnchor="message"` fixes scroll; `ghost` variant + compact pill redesign declutter the modal UI.

**Tech Stack:** React 18, AI SDK v5, @assistant-ui/react ^0.14, TypeScript, Tailwind CSS

**Spec:** `docs/superpowers/specs/2026-05-23-chat-bugfix-ui-design.md`

---

## File Map

| File | Action | Responsibility |
|------|--------|---------------|
| `src/components/AIChatWidget/hooks/useSessionMessages.ts` | **Create** | localStorage stale-while-revalidate for session messages |
| `src/components/AIChatWidget/index.tsx` | **Modify** | Use new hook, remove null-guard and LoadingStub |
| `api/chat.ts` | **Modify** | `stepCountIs(10)`, updated system prompt |
| `src/components/assistant-ui/thread.tsx` | **Modify** | `turnAnchor="message"`, ghost ToolGroup variant |
| `src/components/assistant-ui/kb-search-tool.tsx` | **Modify** | Compact single-row pill with inline source toggle |

---

## Task 1: Create `useSessionMessages` hook

**Files:**
- Create: `src/components/AIChatWidget/hooks/useSessionMessages.ts`

- [ ] **Step 1: Create the hook file**

```typescript
// src/components/AIChatWidget/hooks/useSessionMessages.ts
import { useEffect, useState } from "react";
import type { UIMessage } from "ai";

const PREFIX = "aidiy.messages.";
const MAX_MSGS = 30;

function cacheKey(sessionId: string): string {
  return `${PREFIX}${sessionId}`;
}

function readCache(sessionId: string): UIMessage[] {
  try {
    const raw = localStorage.getItem(cacheKey(sessionId));
    if (!raw) return [];
    const data = JSON.parse(raw) as unknown;
    return Array.isArray(data) ? (data as UIMessage[]) : [];
  } catch {
    return [];
  }
}

function writeCache(sessionId: string, messages: UIMessage[]): void {
  try {
    localStorage.setItem(
      cacheKey(sessionId),
      JSON.stringify(messages.slice(-MAX_MSGS)),
    );
  } catch {
    // localStorage quota exceeded or unavailable — ignore
  }
}

export function clearSessionCache(sessionId: string): void {
  try {
    localStorage.removeItem(cacheKey(sessionId));
  } catch {
    // ignore
  }
}

/**
 * Returns cached messages from localStorage immediately (never null).
 * Fetches from /api/messages in background to keep cache fresh for the
 * NEXT page load. Does NOT remount the runtime — only updates storage.
 */
export function useSessionMessages(sessionId: string): UIMessage[] {
  const [messages] = useState<UIMessage[]>(() => readCache(sessionId));

  useEffect(() => {
    let cancelled = false;
    void (async () => {
      try {
        const res = await fetch(
          `/api/messages?sessionId=${encodeURIComponent(sessionId)}`,
        );
        if (cancelled || !res.ok) return;
        const data = (await res.json()) as { messages: UIMessage[] };
        if (!cancelled && Array.isArray(data.messages)) {
          writeCache(sessionId, data.messages);
        }
      } catch {
        // network error — use cache silently
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [sessionId]);

  return messages;
}
```

- [ ] **Step 2: Verify TypeScript compiles**

```bash
cd /Users/wy/projects/AiDIY
npx tsc --noEmit --pretty false 2>&1 | grep useSessionMessages
```

Expected: no errors (or only pre-existing errors unrelated to this file).

- [ ] **Step 3: Commit**

```bash
git add src/components/AIChatWidget/hooks/useSessionMessages.ts
git commit -m "feat(widget): add useSessionMessages hook with localStorage SWR"
```

---

## Task 2: Update `AIChatWidget/index.tsx` — remove null-guard

**Files:**
- Modify: `src/components/AIChatWidget/index.tsx`

The current file has:
1. `useState<UIMessage[] | null>(null)` — null causes LoadingStub
2. `LoadingStub` component — fake button while waiting
3. `pendingOpen` state — stores click intent while loading
4. `defaultOpen` prop on `ChatWidgetInner`

All of these are removed. `ChatWidgetInner` mounts on first render.

- [ ] **Step 1: Replace the full file**

```tsx
// src/components/AIChatWidget/index.tsx
import { useMemo, useRef, useEffect } from "react";
import type { UIMessage } from "ai";
import { AssistantRuntimeProvider } from "@assistant-ui/react";
import {
  AssistantChatTransport,
  useChatRuntime,
} from "@assistant-ui/react-ai-sdk";

import { AssistantModal } from "../assistant-ui/assistant-modal";
import { KbSearchToolUI } from "../assistant-ui/kb-search-tool";
import useSessionId from "./hooks/useSessionId";
import {
  clearSessionCache,
  useSessionMessages,
} from "./hooks/useSessionMessages";

// ─── Root widget ──────────────────────────────────────────────────────────────

export default function AIChatWidget(): JSX.Element {
  const { sessionId, startNew } = useSessionId();
  const initialMessages = useSessionMessages(sessionId);

  return (
    <ChatWidgetInner
      key={sessionId}
      sessionId={sessionId}
      initialMessages={initialMessages}
      onStartNew={() => {
        clearSessionCache(sessionId);
        return startNew();
      }}
    />
  );
}

// ─── Full widget ──────────────────────────────────────────────────────────────

function ChatWidgetInner({
  sessionId,
  initialMessages,
  onStartNew,
}: {
  sessionId: string;
  initialMessages: UIMessage[];
  onStartNew: () => string;
}): JSX.Element {
  const sessionIdRef = useRef<string>(sessionId);
  useEffect(() => {
    sessionIdRef.current = sessionId;
  }, [sessionId]);

  const transport = useMemo(
    () =>
      new AssistantChatTransport({
        api: "/api/chat",
        headers: () => ({ "x-aidiy-session": sessionIdRef.current }),
      }),
    [],
  );

  const initialMessagesRef = useRef(initialMessages);
  const runtime = useChatRuntime({
    transport,
    messages: initialMessagesRef.current,
  });

  return (
    <AssistantRuntimeProvider runtime={runtime}>
      <div className="ai-chat-widget">
        {/* Registers kb_search tool renderer — renders nothing visible */}
        <KbSearchToolUI />
        <AssistantModal onClear={onStartNew} />
      </div>
    </AssistantRuntimeProvider>
  );
}
```

- [ ] **Step 2: Verify TypeScript**

```bash
npx tsc --noEmit --pretty false 2>&1 | grep -E "AIChatWidget|index.tsx"
```

Expected: no new errors.

- [ ] **Step 3: Remove `defaultOpen` from `AssistantModal` call in `assistant-modal.tsx`**

Open `src/components/assistant-ui/assistant-modal.tsx` and remove the `defaultOpen` prop from the interface and usage since it's no longer needed:

```tsx
// Before
interface AssistantModalProps {
  onClear: () => void;
  defaultOpen?: boolean;
}

export const AssistantModal: FC<AssistantModalProps> = ({
  onClear,
  defaultOpen = false,
}) => {
  return (
    <AssistantModalPrimitive.Root defaultOpen={defaultOpen}>

// After
interface AssistantModalProps {
  onClear: () => void;
}

export const AssistantModal: FC<AssistantModalProps> = ({ onClear }) => {
  return (
    <AssistantModalPrimitive.Root>
```

- [ ] **Step 4: Verify TypeScript again**

```bash
npx tsc --noEmit --pretty false 2>&1 | grep -E "error TS"
```

Expected: no new errors.

- [ ] **Step 5: Start dev server and manually verify**

```bash
# In one terminal (if not already running):
vercel dev --listen 3001 &

# Open browser at http://localhost:3001
# Test: immediately after page load, click the chat button
# Expected: modal opens instantly (< 300ms) with no delay
```

- [ ] **Step 6: Commit**

```bash
git add src/components/AIChatWidget/index.tsx \
        src/components/assistant-ui/assistant-modal.tsx
git commit -m "fix(widget): eliminate button delay via localStorage SWR — removes null-guard and LoadingStub"
```

---

## Task 3: Fix step count limit in `api/chat.ts`

**Files:**
- Modify: `api/chat.ts`

- [ ] **Step 1: Update step count and system prompt**

Open `api/chat.ts` and apply these two changes:

**Change A — step count** (around line 65):
```typescript
// Before:
stopWhen: stepCountIs(6),

// After:
stopWhen: stepCountIs(10),
```

**Change B — system prompt** (replace the SYSTEM_PROMPT constant, around lines 16-22):
```typescript
const SYSTEM_PROMPT = `You are the AiDIY documentation assistant.

You answer questions about computer science, AI engineering, backend/frontend
engineering, and case studies hosted on this site. Call kb_search 1–3 times
at most to find relevant context, then write your answer directly. Do not
search more times than necessary to answer the question. Cite specific sources
by their path when you use them. If the knowledge base lacks the answer, say
so plainly instead of inventing facts.`;
```

- [ ] **Step 2: Verify TypeScript**

```bash
npx tsc --noEmit --pretty false 2>&1 | grep "api/chat"
```

Expected: no errors.

- [ ] **Step 3: Test via curl — verify text output with a question that previously triggered 6 searches**

```bash
curl -s -X POST http://localhost:3001/api/chat \
  -H "Content-Type: application/json" \
  -H "x-aidiy-session: test-step-fix-$(date +%s)" \
  -d '{"id":"test","messages":[{"id":"m1","role":"user","parts":[{"type":"text","text":"What is AgentOps and how does it work?"}]}]}' \
  --max-time 60 | grep -c "text-delta"
```

Expected: output shows `> 0` (at least one text-delta event confirms text was generated).

- [ ] **Step 4: Commit**

```bash
git add api/chat.ts
git commit -m "fix(api): increase step limit to 10 and constrain search count in system prompt"
```

---

## Task 4: Fix scroll behavior and ToolGroup variant in `thread.tsx`

**Files:**
- Modify: `src/components/assistant-ui/thread.tsx`

- [ ] **Step 1: Change `turnAnchor` from `"top"` to `"message"`**

In `thread.tsx`, find the `ThreadPrimitive.Viewport` component (around line 61) and change `turnAnchor`:

```tsx
// Before:
<ThreadPrimitive.Viewport
  turnAnchor="top"
  data-slot="aui_thread-viewport"
  className="relative flex flex-1 flex-col overflow-x-auto overflow-y-scroll scroll-smooth"
>

// After:
<ThreadPrimitive.Viewport
  turnAnchor="message"
  data-slot="aui_thread-viewport"
  className="relative flex flex-1 flex-col overflow-x-auto overflow-y-scroll scroll-smooth"
>
```

- [ ] **Step 2: Change ToolGroup variant from default to `"ghost"`**

In the same file, find the `case "group-tool":` block (around line 272) and add `variant="ghost"`:

```tsx
// Before:
case "group-tool":
  return (
    <ToolGroupRoot>
      <ToolGroupTrigger
        count={part.indices.length}
        active={part.status.type === "running"}
      />
      <ToolGroupContent>{children}</ToolGroupContent>
    </ToolGroupRoot>
  );

// After:
case "group-tool":
  return (
    <ToolGroupRoot variant="ghost">
      <ToolGroupTrigger
        count={part.indices.length}
        active={part.status.type === "running"}
      />
      <ToolGroupContent>{children}</ToolGroupContent>
    </ToolGroupRoot>
  );
```

- [ ] **Step 3: Verify TypeScript**

```bash
npx tsc --noEmit --pretty false 2>&1 | grep "thread.tsx"
```

Expected: no errors. (`variant="ghost"` is a valid value — defined in `tool-group.tsx` `toolGroupVariants`.)

- [ ] **Step 4: Commit**

```bash
git add src/components/assistant-ui/thread.tsx
git commit -m "fix(thread): scroll to message anchor and use ghost ToolGroup variant"
```

---

## Task 5: Compact `kb-search-tool.tsx` — single-row pill design

**Files:**
- Modify: `src/components/assistant-ui/kb-search-tool.tsx`

- [ ] **Step 1: Replace the full file with compact design**

```tsx
// src/components/assistant-ui/kb-search-tool.tsx
import { useState, type FC } from "react";
import {
  ChevronDownIcon,
  ExternalLinkIcon,
  LinkIcon,
  SearchCheckIcon,
} from "lucide-react";
import { makeAssistantToolUI } from "@assistant-ui/react";

import type { RetrievalToolOutput, RetrievedChunk } from "../AIChatWidget/types";

// docs/cs/algorithms/index.md → /docs/cs/algorithms
function toDocLink(rawPath: string): string {
  const noExt = rawPath.replace(/\.(mdx?|MDX?)$/i, "");
  const noIndex = noExt.replace(/\/index$/i, "");
  return "/" + noIndex.replace(/^\/+/, "");
}

function dedupeChunks(chunks: RetrievedChunk[]): RetrievedChunk[] {
  const seen = new Set<string>();
  return chunks.filter((c) => {
    const key = `${c.doc_id}::${c.path}`;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

// ─── Inner component (needs useState) ─────────────────────────────────────────

interface KbSearchToolProps {
  args: { query: string; top_k?: number };
  result?: RetrievalToolOutput;
  status?: { type: string };
}

const KbSearchToolRender: FC<KbSearchToolProps> = ({ args, result, status }) => {
  const [sourcesOpen, setSourcesOpen] = useState(false);
  const running = status?.type === "running";
  const chunks = dedupeChunks(result?.chunks ?? []);

  return (
    <div className="my-0.5">
      {/* Single-row status line */}
      <div className="flex items-center gap-1.5 text-xs">
        <SearchCheckIcon
          className={`size-3 shrink-0 ${
            running
              ? "animate-pulse text-indigo-400"
              : "text-emerald-500"
          }`}
        />
        <span className="font-medium text-neutral-600 dark:text-neutral-300">
          {running ? "Searching" : "Searched"}
        </span>
        {args?.query && (
          <span className="max-w-[200px] truncate text-neutral-400 dark:text-neutral-500">
            · &ldquo;{args.query}&rdquo;
          </span>
        )}

        {/* Source count toggle — only when done */}
        {!running && chunks.length > 0 && (
          <button
            type="button"
            onClick={() => setSourcesOpen((v) => !v)}
            className="ml-auto flex items-center gap-1 rounded px-1.5 py-0.5 text-neutral-400 transition-colors hover:bg-neutral-100 hover:text-neutral-600 dark:hover:bg-neutral-800 dark:hover:text-neutral-300"
          >
            <LinkIcon className="size-3 shrink-0" />
            <span>{chunks.length}</span>
            <ChevronDownIcon
              className={`size-3 transition-transform duration-150 ${
                sourcesOpen ? "rotate-180" : ""
              }`}
            />
          </button>
        )}
      </div>

      {/* Inline source list */}
      {sourcesOpen && chunks.length > 0 && (
        <ul className="mt-1 space-y-0.5 pl-5">
          {chunks.map((c) => (
            <li key={c.chunk_id}>
              <a
                href={toDocLink(c.path)}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-1.5 rounded px-1.5 py-0.5 text-xs text-neutral-500 hover:bg-neutral-50 hover:text-neutral-700 dark:text-neutral-400 dark:hover:bg-neutral-800 dark:hover:text-neutral-200"
              >
                <ExternalLinkIcon className="size-3 shrink-0 text-neutral-400" />
                <span className="truncate">{c.title ?? c.path}</span>
              </a>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

// ─── Tool UI registration ──────────────────────────────────────────────────────

// Renders the kb_search tool call:
// - while running: a compact "Searching · query" single-row pill
// - after done: "Searched · query ▸ N" with togglable inline source list
export const KbSearchToolUI = makeAssistantToolUI<
  { query: string; top_k?: number },
  RetrievalToolOutput
>({
  toolName: "kb_search",
  render: (props) => <KbSearchToolRender {...props} />,
});
```

- [ ] **Step 2: Verify TypeScript**

```bash
npx tsc --noEmit --pretty false 2>&1 | grep "kb-search"
```

Expected: no errors.

- [ ] **Step 3: Commit**

```bash
git add src/components/assistant-ui/kb-search-tool.tsx
git commit -m "feat(ui): compact kb-search tool pill — single row with inline source toggle"
```

---

## Task 6: End-to-end verification

- [ ] **Step 1: Start the dev server (if not running)**

```bash
vercel dev --listen 3001
```

Wait for: `[SUCCESS] Docusaurus website is running at: http://localhost:3001/`

- [ ] **Step 2: Test button responsiveness**

Open `http://localhost:3001` in a browser. Immediately after the page loads (< 1 second), click the chat button (bottom-right).

Expected: modal opens instantly, no 3-5s delay.

- [ ] **Step 3: Test content output**

In the chat modal, send: `What is AgentOps and how does it work?`

Wait for completion (~15-25 seconds). Expected:
- Tool calls show as compact single-row pills (not large bordered box)
- After completion, text answer is visible in the modal without manual scrolling
- Text answer IS present (not empty)

- [ ] **Step 4: Test source toggle**

Click the source count button (e.g., "▸ 6") on one of the kb_search pills.

Expected: inline source list expands below the pill. Click again → collapses.

- [ ] **Step 5: Take a before/after screenshot for the commit**

```bash
# Take screenshot of the completed chat
agent-browser open http://localhost:3001
# ... open modal, send message, wait ...
agent-browser screenshot /tmp/aidiy-after-fixes.png
```

- [ ] **Step 6: Final commit**

```bash
git add -A
git commit -m "chore: verified all 4 fixes — button delay, no-content, scroll, tool pill UI"
```
