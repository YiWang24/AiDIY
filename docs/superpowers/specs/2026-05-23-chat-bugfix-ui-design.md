# Chat Bug Fixes + UI Polish Design

**Date**: 2026-05-23  
**Status**: Approved  
**Scope**: Bug fixes (button delay, no-content output) + UI improvement (scroll, tool call display)

---

## Problem Summary

Three confirmed bugs found via local testing + browser automation:

| # | Problem | Severity | Root Cause |
|---|---------|----------|------------|
| 1 | Chat button unresponsive for 3–5 s after page load | 🔴 High | `initialMessages === null` → `LoadingStub` rendered until Neon Postgres fetch completes |
| 2 | Some queries produce no text output | 🔴 High | `stopWhen: stepCountIs(6)` — when model makes 6 kb_search calls, all steps are consumed and no step remains for the text response |
| 3 | Text answer not visible after tool calls complete | 🟡 Medium | `turnAnchor="top"` keeps viewport anchored to user message; text answer below tool calls requires manual scroll |
| 4 | Tool call section visually dominates the modal | 🟡 Medium | Large bordered ToolGroupRoot + nested `<details>` make tool results feel heavy |

---

## Architecture

No new dependencies. All changes are within existing files.

```
src/components/AIChatWidget/
  index.tsx                    ← remove null-wait; use useSessionMessages
  hooks/
    useSessionId.ts            (unchanged)
    useSessionMessages.ts      ← NEW: localStorage stale-while-revalidate

src/components/assistant-ui/
  kb-search-tool.tsx           ← compact single-row pill design
  thread.tsx                   ← turnAnchor="message", ghost ToolGroup variant

api/
  chat.ts                      ← stepCountIs(10), updated system prompt
```

---

## Fix 1: Button Delay — `useSessionMessages` hook

**File**: `src/components/AIChatWidget/hooks/useSessionMessages.ts` (new)

**Pattern**: Stale-While-Revalidate using localStorage as an L1 cache.

```
Page load
  ↓ synchronously
read localStorage["aidiy.messages.{sessionId}"]
  → parse → use as initialMessages immediately
  ↓ asynchronously (in parallel)
fetch /api/messages?sessionId={sessionId}
  → on success: write to localStorage (capped at 30 messages)
  → if thread is still empty: update runtime messages
  → if user already started typing: discard (don't interrupt)
```

**Key behaviors**:
- `initialMessages` is NEVER `null` — starts as `[]` if no cache exists
- `ChatWidgetInner` mounts on first render, button is immediately clickable
- Cache key: `aidiy.messages.{sessionId}` — per-session, no cross-session leakage
- Max 30 messages stored (older ones truncated) to keep localStorage footprint small
- On `startNew()`: clear cache entry for old session

**`AIChatWidget/index.tsx` change**:

Remove the null-guard. `ChatWidgetInner` mounts immediately on first render:

```tsx
// Before: renders LoadingStub until fetch completes (~3-5s)
if (initialMessages === null) return <LoadingStub />;

// After: mounts immediately with cached or empty messages
// useSessionMessages returns [] synchronously if no cache
```

---

## Fix 2: No-Content Output — Step Limit + System Prompt

**File**: `api/chat.ts`

### Step count increase
```diff
- stopWhen: stepCountIs(6),
+ stopWhen: stepCountIs(10),
```

With 10 steps, even if the model makes 6 kb_search calls (observed maximum), 4 steps remain for the text response.

### System prompt update
Add a search discipline clause to prevent the model from over-searching:

```
Call kb_search 1–3 times at most to find relevant context, then write
your answer. Do not search more times than needed to answer the question.
```

---

## Fix 3: Scroll Behavior

**File**: `src/components/assistant-ui/thread.tsx`

```diff
- <ThreadPrimitive.Viewport turnAnchor="top" ...>
+ <ThreadPrimitive.Viewport turnAnchor="message" ...>
```

`turnAnchor="message"` scrolls each new message (including the assistant text response) into view as it arrives, instead of keeping the viewport fixed at the user message top.

---

## Fix 4: Tool Call Display — Compact Pills

**File**: `src/components/assistant-ui/kb-search-tool.tsx`

### Current behavior
- While running: "Searching" pill + pulsing icon
- After done: "Searched · query" pill + `<details>` accordion for sources

### New design
Single-line, no nested `<details>`. Keep pill for status, inline expandable chip for sources:

```
● Searched · "AgentOps"  ▸ 6 sources
```

- Searching state: animated pulse icon + "Searching" label
- Done state: green checkmark + truncated query + source count as inline button
- Sources: expand inline on click (small list, not a nested `<details>`)
- Remove the outer `<div className="space-y-1.5">` wrapper that adds spacing

### ToolGroup variant

**File**: `src/components/assistant-ui/thread.tsx`

```diff
case "group-tool":
  return (
-   <ToolGroupRoot>
+   <ToolGroupRoot variant="ghost">
```

`ghost` variant removes the large border and `py-3` padding, making the tool call block visually lighter.

---

## Data Flow (after fixes)

```
User opens page
  → useSessionMessages: read localStorage → initialMessages = [] or [cached messages]
  → ChatWidgetInner mounts immediately
  → User clicks button → Modal opens instantly ✓
  → Background: /api/messages fetch completes → update localStorage

User sends message
  → POST /api/chat
  → GLM model calls kb_search 1–3 times (stepCountIs(10) allows up to 9 tool calls)
  → Each kb_search renders compact pill in chat
  → Final text response streams in
  → turnAnchor="message" scrolls text into view ✓
  → On finish: text appears visibly without scrolling ✓
```

---

## Error Handling

- **localStorage unavailable** (private browsing): `useSessionMessages` catches the exception and falls back to `[]`; history fetch still runs normally
- **History fetch fails**: `useSessionMessages` catches and returns `[]` silently; user starts fresh (same behavior as before)
- **Step limit hit before text** (stepCountIs(10) with 10 tool calls): AI SDK returns `finishReason: "max-steps"` — assistant-ui renders the tool calls with no text; this is acceptable for edge cases

---

## Files to Change

| File | Change Type | Notes |
|------|-------------|-------|
| `src/components/AIChatWidget/hooks/useSessionMessages.ts` | Create | localStorage SWR hook |
| `src/components/AIChatWidget/index.tsx` | Modify | Use `useSessionMessages`, remove null-guard |
| `api/chat.ts` | Modify | `stepCountIs(10)`, update system prompt |
| `src/components/assistant-ui/thread.tsx` | Modify | `turnAnchor="message"`, ghost ToolGroup |
| `src/components/assistant-ui/kb-search-tool.tsx` | Modify | Compact pill design |
