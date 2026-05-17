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
  useThreadRuntime,
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

export default function AIChatWidget(): JSX.Element | null {
  const { sessionId, startNew } = useSessionId();
  if (!sessionId) return null;
  return <ChatWidgetInner sessionId={sessionId} onStartNew={startNew} />;
}

function ChatWidgetInner({
  sessionId,
  onStartNew,
}: {
  sessionId: string;
  onStartNew: () => string;
}): JSX.Element | null {
  const sessionIdRef = useRef<string>(sessionId);
  useEffect(() => {
    sessionIdRef.current = sessionId;
  }, [sessionId]);

  const [initialMessages, setInitialMessages] = useState<UIMessage[] | null>(
    null,
  );
  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const res = await fetch(
          `/api/messages?sessionId=${encodeURIComponent(sessionId)}`,
        );
        if (!res.ok) {
          if (!cancelled) setInitialMessages([]);
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

  const runtime = useChatRuntime({
    transport,
    messages: initialMessages ?? undefined,
  });

  // Wait for history fetch before mounting — useChatRuntime locks in
  // `messages` on first render, so we can't seed it asynchronously.
  if (initialMessages === null) return null;

  return (
    <AssistantRuntimeProvider runtime={runtime}>
      <KbSearchToolUI />
      <AssistantModalPrimitive.Root>
        <AssistantModalPrimitive.Anchor className="fixed bottom-6 right-6 z-[60] size-14">
          <AssistantModalPrimitive.Trigger
            asChild
            className="group size-full rounded-full bg-gradient-to-br from-indigo-500 to-sky-500 text-white shadow-lg shadow-indigo-500/20 ring-1 ring-white/10 transition-all duration-300 hover:scale-110 hover:shadow-indigo-500/40 data-[state=open]:rotate-90"
            aria-label="AiDIY Assistant"
          >
            <button type="button">
              <div className="relative flex size-full items-center justify-center transition-transform group-data-[state=open]:opacity-0">
                <MessageCircleIcon className="size-8 fill-white/20" />
                <SparklesIcon className="absolute top-2.5 right-2.5 size-4 fill-white" />
              </div>
              <XIcon className="absolute inset-0 m-auto size-6 opacity-0 transition-opacity group-data-[state=open]:opacity-100" />
            </button>
          </AssistantModalPrimitive.Trigger>
        </AssistantModalPrimitive.Anchor>

        <AssistantModalPrimitive.Content
          sideOffset={16}
          className="z-[70] flex h-[720px] max-h-[85vh] w-[440px] max-w-[95vw] flex-col overflow-hidden rounded-[2rem] border border-neutral-200 bg-white shadow-2xl dark:border-neutral-800 dark:bg-neutral-950 transition-all"
        >
          <Header onClear={onStartNew} />
          <Thread />
        </AssistantModalPrimitive.Content>
      </AssistantModalPrimitive.Root>
    </AssistantRuntimeProvider>
  );
}

function Header({ onClear }: { onClear: () => string }): JSX.Element {
  const runtime = useThreadRuntime();
  const handleClear = () => {
    runtime.import({ messages: [] });
    onClear();
  };
  return (
    <div className="flex items-center justify-between border-b border-neutral-200 bg-white/70 px-4 py-3 backdrop-blur dark:border-neutral-800 dark:bg-neutral-950/70">
      <div className="flex items-center gap-2.5">
        <div className="flex size-8 items-center justify-center rounded-full bg-gradient-to-br from-indigo-500 to-sky-500 text-white">
          <SparklesIcon className="size-4" />
        </div>
        <div className="leading-tight">
          <div className="text-sm font-semibold text-neutral-900 dark:text-neutral-100">
            AiDIY Assistant
          </div>
          <div className="text-[11px] text-neutral-500 dark:text-neutral-400">
            Powered by RAG Knowledge Base
          </div>
        </div>
      </div>
      <div className="flex items-center gap-1">
        <button
          type="button"
          onClick={handleClear}
          aria-label="New conversation"
          className="rounded-md p-1.5 text-neutral-500 hover:bg-neutral-100 hover:text-neutral-900 dark:hover:bg-neutral-800 dark:hover:text-neutral-100"
        >
          <RotateCcwIcon className="size-4" />
        </button>
      </div>
    </div>
  );
}

function Thread(): JSX.Element {
  return (
    <ThreadPrimitive.Root className="flex flex-1 flex-col overflow-hidden bg-neutral-50/60 dark:bg-neutral-900/40">
      <ThreadPrimitive.Viewport className="flex-1 overflow-y-auto px-4 py-4">
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
    <div className="flex h-full flex-col items-center justify-center gap-5 px-4 py-8 text-center">
      <div className="flex size-14 items-center justify-center rounded-2xl bg-gradient-to-br from-indigo-500 to-sky-500 text-white shadow-lg">
        <SparklesIcon className="size-7" />
      </div>
      <div>
        <h2 className="text-lg font-semibold text-neutral-900 dark:text-neutral-100">
          AiDIY Assistant
        </h2>
        <p className="mt-1 text-sm text-neutral-500 dark:text-neutral-400">
          Ask anything about the CS / AI / engineering docs.
        </p>
      </div>
      <div className="w-full space-y-2">
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
      className="group flex w-full items-center justify-between rounded-xl border border-neutral-200 bg-white px-3.5 py-2.5 text-left text-sm text-neutral-700 transition hover:border-neutral-300 hover:bg-neutral-50 dark:border-neutral-800 dark:bg-neutral-900 dark:text-neutral-200 dark:hover:bg-neutral-800/70"
    >
      <span className="line-clamp-1">{label}</span>
      <ArrowUpIcon className="size-4 shrink-0 -rotate-90 text-neutral-400 transition group-hover:text-neutral-700 dark:group-hover:text-neutral-200" />
    </ThreadPrimitive.Suggestion>
  );
}

function Composer(): JSX.Element {
  return (
    <ComposerPrimitive.Root className="flex items-end gap-2 border-t border-neutral-200 bg-white/80 p-3 backdrop-blur dark:border-neutral-800 dark:bg-neutral-950/70">
      <ComposerPrimitive.Input
        rows={1}
        autoFocus
        placeholder="Ask about the docs..."
        className="max-h-32 flex-1 resize-none bg-transparent px-3 py-2 text-sm text-neutral-900 placeholder:text-neutral-400 focus:outline-none dark:text-neutral-100"
      />
      <ThreadPrimitive.If running={false}>
        <ComposerPrimitive.Send
          aria-label="Send"
          className="flex size-9 items-center justify-center rounded-full bg-neutral-900 text-white transition hover:bg-neutral-700 disabled:opacity-40 dark:bg-white dark:text-neutral-900 dark:hover:bg-neutral-200"
        >
          <ArrowUpIcon className="size-4" />
        </ComposerPrimitive.Send>
      </ThreadPrimitive.If>
      <ThreadPrimitive.If running>
        <ComposerPrimitive.Cancel
          aria-label="Stop"
          className="flex size-9 items-center justify-center rounded-full bg-neutral-900 text-white transition hover:bg-neutral-700 dark:bg-white dark:text-neutral-900 dark:hover:bg-neutral-200"
        >
          <SquareIcon className="size-3.5" />
        </ComposerPrimitive.Cancel>
      </ThreadPrimitive.If>
    </ComposerPrimitive.Root>
  );
}

function UserMessage(): JSX.Element {
  return (
    <MessagePrimitive.Root className="mb-3 flex justify-end">
      <div className="max-w-[85%] rounded-2xl rounded-tr-sm bg-neutral-900 px-3.5 py-2 text-sm text-white dark:bg-white dark:text-neutral-900">
        <MessagePrimitive.Parts />
      </div>
    </MessagePrimitive.Root>
  );
}

function AssistantMessage(): JSX.Element {
  return (
    <MessagePrimitive.Root className="mb-4 flex justify-start">
      <div className="max-w-[92%] space-y-2 text-sm text-neutral-900 dark:text-neutral-100">
        <MessagePrimitive.Parts
          components={{
            Text: () => (
              <div className="prose prose-sm max-w-none rounded-2xl rounded-tl-sm border border-neutral-200 bg-white px-3.5 py-2 shadow-sm dark:prose-invert dark:border-neutral-800 dark:bg-neutral-900">
                <MarkdownTextPrimitive />
              </div>
            ),
          }}
        />
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
