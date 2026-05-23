import React, { useEffect, useMemo, useRef, useState } from "react";
import type { UIMessage } from "ai";
import {
  ArrowUpIcon,
  ChevronDownIcon,
  ExternalLinkIcon,
  LinkIcon,
  MessageCircleIcon,
  RotateCcwIcon,
  SearchCheckIcon,
  SparklesIcon,
  SquareIcon,
  XIcon,
} from "lucide-react";

import {
  AssistantModalPrimitive,
  AssistantRuntimeProvider,
  ComposerPrimitive,
  MessagePrimitive,
  ThreadPrimitive,
  makeAssistantToolUI,
} from "@assistant-ui/react";
import {
  AssistantChatTransport,
  useChatRuntime,
} from "@assistant-ui/react-ai-sdk";
import { MarkdownTextPrimitive } from "@assistant-ui/react-markdown";

import useSessionId from "./hooks/useSessionId";
import type { RetrievalToolOutput, RetrievedChunk } from "./types";

const SUGGESTIONS: ReadonlyArray<{ label: string; query: string }> = [
  {
    label: "What is AgentOps and how does it work?",
    query: "What is AgentOps and how does it work?",
  },
  {
    label: "Explain the agent loop architecture",
    query: "Explain the agent loop architecture",
  },
  {
    label: "Patterns for agent orchestration?",
    query: "What are the patterns of agent orchestration?",
  },
];

// docs/cs/algorithms/index.md -> /docs/cs/algorithms
function toDocLink(rawPath: string): string {
  const noExt = rawPath.replace(/\.(mdx?|MDX?)$/i, "");
  const noIndex = noExt.replace(/\/index$/i, "");
  return "/" + noIndex.replace(/^\/+/, "");
}

// ─────────────────────────────────────────────────────────────────────────────
// Trigger button shared styles — used by both the loading stub and the real
// AssistantModalPrimitive.Trigger so they look identical.
// ─────────────────────────────────────────────────────────────────────────────
const TRIGGER_CLS =
  "group size-full rounded-full bg-gradient-to-br from-indigo-500 to-sky-500 text-white shadow-lg shadow-indigo-500/20 ring-1 ring-white/10 transition-all duration-300 hover:scale-110 hover:shadow-indigo-500/40 data-[state=open]:rotate-90";

function TriggerIconContent(): JSX.Element {
  return (
    <>
      <div className="relative flex size-full items-center justify-center transition-transform group-data-[state=open]:opacity-0">
        <MessageCircleIcon className="size-8 fill-white/20" />
        <SparklesIcon className="absolute top-2.5 right-2.5 size-4 fill-white" />
      </div>
      <XIcon className="absolute inset-0 m-auto size-6 opacity-0 transition-opacity group-data-[state=open]:opacity-100" />
    </>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// Root — shows button immediately; switches to the full runtime-backed widget
// once history has been fetched (usually <300ms, invisible to the user).
// ─────────────────────────────────────────────────────────────────────────────

export default function AIChatWidget(): JSX.Element {
  const { sessionId, startNew } = useSessionId();
  // Track whether the user clicked the stub button before history loaded.
  const [pendingOpen, setPendingOpen] = useState(false);
  const [initialMessages, setInitialMessages] = useState<UIMessage[] | null>(
    null,
  );

  // Fetch chat history eagerly — usually ready before the user has time to click.
  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const res = await fetch(
          `/api/messages?sessionId=${encodeURIComponent(sessionId)}`,
        );
        if (cancelled) return;
        if (!res.ok) {
          setInitialMessages([]);
          return;
        }
        const data = (await res.json()) as { messages: UIMessage[] };
        if (!cancelled)
          setInitialMessages(Array.isArray(data.messages) ? data.messages : []);
      } catch {
        if (!cancelled) setInitialMessages([]);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [sessionId]);

  // While history is loading show a visually identical stub button (no runtime).
  // The stub is replaced by the real AssistantModalPrimitive.Trigger the moment
  // history arrives — seamless because they look exactly the same.
  if (initialMessages === null) {
    return (
      <div className="ai-chat-widget">
        <div className="fixed bottom-6 right-6 z-[60] size-14">
          <button
            type="button"
            className={TRIGGER_CLS}
            aria-label="AiDIY Assistant"
            onClick={() => setPendingOpen(true)}
          >
            <TriggerIconContent />
          </button>
        </div>
      </div>
    );
  }

  // History ready — mount the full widget.
  // key=sessionId forces a clean remount whenever the session changes (clear chat).
  return (
    <ChatWidgetInner
      key={sessionId}
      sessionId={sessionId}
      initialMessages={initialMessages}
      onStartNew={() => {
        setInitialMessages([]);
        return startNew();
      }}
      defaultOpen={pendingOpen}
    />
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// Full chat widget — identical to the original structure so AssistantModalPrimitive
// and ComposerPrimitive get all the context they need.
// ─────────────────────────────────────────────────────────────────────────────

function ChatWidgetInner({
  sessionId,
  initialMessages,
  onStartNew,
  defaultOpen,
}: {
  sessionId: string;
  initialMessages: UIMessage[];
  onStartNew: () => string;
  defaultOpen: boolean;
}): JSX.Element {
  const sessionIdRef = useRef<string>(sessionId);
  useEffect(() => {
    sessionIdRef.current = sessionId;
  }, [sessionId]);

  const transport = useMemo(
    () =>
      new AssistantChatTransport({
        api: "/api/chat",
        // AssistantChatTransport always sends its own internal thread id as
        // body.id (e.g. "__LOCALID_*"), so we ferry our persistent session id
        // via a custom header instead.
        headers: () => ({
          "x-aidiy-session": sessionIdRef.current,
        }),
      }),
    [],
  );

  // Capture initialMessages once at mount time. Passing a stable ref value
  // prevents any potential reactive reset inside useChatRuntime during
  // streaming. The key={sessionId} on this component's parent ensures a
  // fresh mount (and thus correct initial messages) on session change.
  const initialMessagesRef = useRef(initialMessages);
  const runtime = useChatRuntime({ transport, messages: initialMessagesRef.current });

  return (
    <AssistantRuntimeProvider runtime={runtime}>
      <div className="ai-chat-widget">
        <AssistantModalPrimitive.Root defaultOpen={defaultOpen}>
          <AssistantModalPrimitive.Anchor className="fixed bottom-6 right-6 z-[60] size-14">
            <AssistantModalPrimitive.Trigger
              asChild
              className={TRIGGER_CLS}
              aria-label="AiDIY Assistant"
            >
              <button type="button">
                <TriggerIconContent />
              </button>
            </AssistantModalPrimitive.Trigger>
          </AssistantModalPrimitive.Anchor>

          <AssistantModalPrimitive.Content
            sideOffset={16}
            className="ai-chat-widget z-[70] flex h-[720px] max-h-[85vh] w-[440px] max-w-[95vw] flex-col overflow-hidden rounded-[2.5rem] border border-neutral-200 bg-white shadow-2xl transition-all dark:border-neutral-800 dark:bg-neutral-950"
          >
            <Header onClear={onStartNew} />
            <Thread />
          </AssistantModalPrimitive.Content>
        </AssistantModalPrimitive.Root>
      </div>
    </AssistantRuntimeProvider>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// UI components
// ─────────────────────────────────────────────────────────────────────────────

function Header({ onClear }: { onClear: () => string }): JSX.Element {
  return (
    <div className="flex items-center justify-between border-b border-neutral-100 bg-white/80 px-6 py-4 backdrop-blur-md dark:border-neutral-800 dark:bg-neutral-950/80">
      <div className="flex items-center gap-3">
        <div className="flex size-9 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-500 to-sky-500 text-white shadow-sm">
          <SparklesIcon className="size-4.5" />
        </div>
        <div className="leading-tight">
          <div className="text-sm font-bold tracking-tight text-neutral-900 dark:text-neutral-100">
            AiDIY Assistant
          </div>
          <div className="text-[11px] font-medium text-neutral-500 dark:text-neutral-400">
            Powered by RAG Knowledge Base
          </div>
        </div>
      </div>
      <div className="flex items-center gap-1">
        <button
          type="button"
          onClick={onClear}
          aria-label="New conversation"
          className="rounded-lg p-2 text-neutral-400 transition-colors hover:bg-neutral-100 hover:text-neutral-900 dark:hover:bg-neutral-800 dark:hover:text-neutral-100"
        >
          <RotateCcwIcon className="size-4" />
        </button>
      </div>
    </div>
  );
}

function Thread(): JSX.Element {
  return (
    <ThreadPrimitive.Root className="flex flex-1 flex-col overflow-hidden bg-neutral-50/50 dark:bg-neutral-900/30">
      <ThreadPrimitive.Viewport className="flex-1 overflow-y-auto px-5 py-6 scrollbar-thin scrollbar-thumb-neutral-200 dark:scrollbar-thumb-neutral-800">
        <ThreadPrimitive.Empty>
          <Welcome />
        </ThreadPrimitive.Empty>
        <ThreadPrimitive.Messages
          components={{
            UserMessage,
            AssistantMessage,
          }}
        />
      </ThreadPrimitive.Viewport>
      <Composer />
    </ThreadPrimitive.Root>
  );
}

function Welcome(): JSX.Element {
  return (
    <div className="flex h-full flex-col items-center justify-center gap-6 px-6 py-8 text-center">
      <div className="flex size-16 items-center justify-center rounded-2xl bg-gradient-to-br from-indigo-500 to-sky-500 text-white shadow-xl shadow-indigo-500/20">
        <SparklesIcon className="size-8" />
      </div>
      <div className="space-y-2">
        <h2 className="text-xl font-bold tracking-tight text-neutral-900 dark:text-neutral-100">
          How can I help you?
        </h2>
        <p className="mx-auto max-w-[280px] text-sm font-medium leading-relaxed text-neutral-500 dark:text-neutral-400">
          Ask me about AgentOps, orchestration patterns, or anything else in the docs.
        </p>
      </div>
      <div className="w-full space-y-2.5">
        {SUGGESTIONS.map((s) => (
          <SuggestionButton key={s.query} query={s.query} label={s.label} />
        ))}
      </div>
    </div>
  );
}

function SuggestionButton({
  query,
  label,
}: {
  query: string;
  label: string;
}): JSX.Element {
  return (
    <ThreadPrimitive.Suggestion
      prompt={query}
      method="replace"
      autoSend
      className="group flex w-full items-center justify-between rounded-2xl border border-neutral-200 bg-white px-4 py-3 text-left text-sm font-medium text-neutral-700 shadow-sm transition-all hover:border-indigo-300 hover:bg-indigo-50/30 dark:border-neutral-800 dark:bg-neutral-900 dark:text-neutral-200 dark:hover:border-indigo-900/50 dark:hover:bg-indigo-950/20"
    >
      <span className="line-clamp-1">{label}</span>
      <ArrowUpIcon className="size-4 shrink-0 -rotate-90 text-neutral-400 transition group-hover:text-indigo-500 dark:group-hover:text-indigo-400" />
    </ThreadPrimitive.Suggestion>
  );
}

function Composer(): JSX.Element {
  return (
    <ComposerPrimitive.Root className="flex items-end gap-3 border-t border-neutral-100 bg-white/90 p-4 backdrop-blur-md dark:border-neutral-800 dark:bg-neutral-950/90">
      <div className="relative flex flex-1 items-center rounded-2xl border border-neutral-200 bg-neutral-50/50 px-4 py-2 transition-all focus-within:border-indigo-400 focus-within:ring-2 focus-within:ring-indigo-500/10 dark:border-neutral-800 dark:bg-neutral-900/50 dark:focus-within:border-indigo-500/50">
        <ComposerPrimitive.Input
          rows={1}
          autoFocus
          placeholder="Ask about the docs..."
          className="max-h-32 flex-1 resize-none bg-transparent py-1 text-sm text-neutral-900 placeholder:text-neutral-400 focus:outline-none dark:text-neutral-100"
        />
      </div>
      <ThreadPrimitive.If running={false}>
        <ComposerPrimitive.Send
          aria-label="Send"
          className="flex size-10 items-center justify-center rounded-xl bg-neutral-900 text-white transition-all hover:scale-105 hover:bg-neutral-800 disabled:opacity-40 dark:bg-white dark:text-neutral-900 dark:hover:bg-neutral-100"
        >
          <ArrowUpIcon className="size-4.5" />
        </ComposerPrimitive.Send>
      </ThreadPrimitive.If>
      <ThreadPrimitive.If running>
        <ComposerPrimitive.Cancel
          aria-label="Stop"
          className="flex size-10 items-center justify-center rounded-xl bg-neutral-900 text-white transition-all hover:scale-105 hover:bg-neutral-800 dark:bg-white dark:text-neutral-900 dark:hover:bg-neutral-100"
        >
          <SquareIcon className="size-3.5" />
        </ComposerPrimitive.Cancel>
      </ThreadPrimitive.If>
    </ComposerPrimitive.Root>
  );
}

function UserMessage(): JSX.Element {
  return (
    <MessagePrimitive.Root className="mb-4 flex justify-end">
      <div className="max-w-[85%] rounded-[1.25rem] rounded-tr-none bg-neutral-900 px-4 py-2.5 text-sm font-medium text-white shadow-md dark:bg-white dark:text-neutral-900">
        <MessagePrimitive.Parts />
      </div>
    </MessagePrimitive.Root>
  );
}

function AssistantMessage(): JSX.Element {
  return (
    <MessagePrimitive.Root className="mb-6 flex justify-start">
      <div className="max-w-[95%] space-y-2 text-sm text-neutral-900 dark:text-neutral-100">
        <MessagePrimitive.Parts components={PARTS_COMPONENTS} />
      </div>
    </MessagePrimitive.Root>
  );
}

// Renders the kb_search tool invocation: a small "searching" pill while running,
// then a collapsible "Used N sources" disclosure with deep links to docs.
const KbSearchToolUI = makeAssistantToolUI<
  { query: string; top_k?: number },
  RetrievalToolOutput
>({
  toolName: "kb_search",
  render: ({ args, result, status }) => {
    const running = status?.type === "running";
    const chunks = dedupeChunks(result?.chunks ?? []);

    return (
      <div className="my-1 space-y-1.5 text-sm">
        <div className="inline-flex items-center gap-1.5 rounded-full border border-neutral-200 bg-white px-2.5 py-1 text-xs text-neutral-600 dark:border-neutral-800 dark:bg-neutral-900 dark:text-neutral-300">
          <SearchCheckIcon
            className={`size-3.5 ${running ? "animate-pulse text-indigo-500" : "text-emerald-500"}`}
          />
          <span className="font-medium">
            {running ? "Searching" : "Searched"}
          </span>
          {args?.query && (
            <span className="max-w-[180px] truncate text-neutral-500 dark:text-neutral-400">
              · "{args.query}"
            </span>
          )}
        </div>
        {chunks.length > 0 && (
          <details className="group rounded-lg border border-neutral-200 bg-white px-2 py-1.5 dark:border-neutral-800 dark:bg-neutral-900">
            <summary className="flex cursor-pointer list-none items-center gap-1.5 text-xs font-medium text-neutral-600 dark:text-neutral-300">
              <LinkIcon className="size-3.5" />
              Used {chunks.length}{" "}
              {chunks.length === 1 ? "source" : "sources"}
              <ChevronDownIcon className="ml-auto size-4 transition group-open:rotate-180" />
            </summary>
            <ul className="mt-1.5 space-y-0.5">
              {chunks.map((c) => (
                <li key={c.chunk_id}>
                  <a
                    href={toDocLink(c.path)}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-1.5 rounded px-1.5 py-1 text-xs text-neutral-600 hover:bg-neutral-50 hover:text-neutral-900 dark:text-neutral-400 dark:hover:bg-neutral-800 dark:hover:text-neutral-100"
                  >
                    <ExternalLinkIcon className="size-3 shrink-0 text-neutral-400" />
                    <span className="truncate">{c.title ?? c.path}</span>
                  </a>
                </li>
              ))}
            </ul>
          </details>
        )}
      </div>
    );
  },
});

function dedupeChunks(chunks: RetrievedChunk[]): RetrievedChunk[] {
  const seen = new Set<string>();
  return chunks.filter((c) => {
    const key = `${c.doc_id}::${c.path}`;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

// ─────────────────────────────────────────────────────────────────────────────
// Module-level component definitions — MUST live outside any render function.
//
// React identifies component types by reference. If `Text` is defined inline
// inside `AssistantMessage` (e.g. as `Text: () => <div>...</div>`), every
// render of `AssistantMessage` creates a brand-new function reference. React
// sees a "different" component type, unmounts the old one, and mounts a fresh
// copy. MarkdownTextPrimitive resubscribes to the runtime on mount, which
// fires a state update, which re-renders AssistantMessage, which creates yet
// another new function… → infinite render loop at 100% CPU.
//
// Defining them at module level gives a single, stable reference forever.
// ─────────────────────────────────────────────────────────────────────────────

function AssistantTextPart(): JSX.Element {
  return (
    <div className="prose prose-sm max-w-none rounded-[1.25rem] rounded-tl-none border border-neutral-200 bg-white px-4 py-3 shadow-sm dark:prose-invert dark:border-neutral-800 dark:bg-neutral-900">
      <MarkdownTextPrimitive />
    </div>
  );
}

const PARTS_COMPONENTS = {
  Text: AssistantTextPart,
  tools: {
    by_name: {
      kb_search: KbSearchToolUI,
    },
  },
} as const;
