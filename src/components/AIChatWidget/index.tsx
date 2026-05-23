import { useEffect, useMemo, useRef, useState } from "react";
import type { UIMessage } from "ai";
import { AssistantRuntimeProvider } from "@assistant-ui/react";
import { MessageCircleIcon, SparklesIcon } from "lucide-react";
import {
  AssistantChatTransport,
  useChatRuntime,
} from "@assistant-ui/react-ai-sdk";

import { AssistantModal } from "../assistant-ui/assistant-modal";
import { KbSearchToolUI } from "../assistant-ui/kb-search-tool";
import useSessionId from "./hooks/useSessionId";

// ─── Trigger button stub (shown while history is loading) ─────────────────────
// Visually identical to the real AssistantModal trigger so the swap is seamless.
const TRIGGER_CLS =
  "group size-full rounded-full bg-gradient-to-br from-indigo-500 to-sky-500 text-white shadow-lg shadow-indigo-500/20 ring-1 ring-white/10 transition-all duration-300 hover:scale-110 hover:shadow-indigo-500/40";

function LoadingStub(): JSX.Element {
  return (
    <div className="fixed bottom-6 right-6 z-[60] size-14">
      <button type="button" className={TRIGGER_CLS} aria-label="AiDIY Assistant">
        <div className="relative flex size-full items-center justify-center">
          <MessageCircleIcon className="size-8 fill-white/20" />
          <SparklesIcon className="absolute top-2.5 right-2.5 size-4 fill-white" />
        </div>
      </button>
    </div>
  );
}

// ─── Root widget ──────────────────────────────────────────────────────────────

export default function AIChatWidget(): JSX.Element {
  const { sessionId, startNew } = useSessionId();
  const [pendingOpen, setPendingOpen] = useState(false);
  const [initialMessages, setInitialMessages] = useState<UIMessage[] | null>(null);

  // Fetch history eagerly — usually ready before the user clicks the button.
  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const res = await fetch(
          `/api/messages?sessionId=${encodeURIComponent(sessionId)}`,
        );
        if (cancelled) return;
        const data = res.ok
          ? ((await res.json()) as { messages: UIMessage[] })
          : { messages: [] };
        if (!cancelled)
          setInitialMessages(Array.isArray(data.messages) ? data.messages : []);
      } catch {
        if (!cancelled) setInitialMessages([]);
      }
    })();
    return () => { cancelled = true; };
  }, [sessionId]);

  if (initialMessages === null) {
    return (
      <div className="ai-chat-widget" onClick={() => setPendingOpen(true)}>
        <LoadingStub />
      </div>
    );
  }

  return (
    <ChatWidgetInner
      key={sessionId}
      sessionId={sessionId}
      initialMessages={initialMessages}
      onStartNew={() => { setInitialMessages([]); return startNew(); }}
      defaultOpen={pendingOpen}
    />
  );
}

// ─── Full widget (mounted after history is ready) ─────────────────────────────

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
  useEffect(() => { sessionIdRef.current = sessionId; }, [sessionId]);

  const transport = useMemo(
    () =>
      new AssistantChatTransport({
        api: "/api/chat",
        headers: () => ({ "x-aidiy-session": sessionIdRef.current }),
      }),
    [],
  );

  const initialMessagesRef = useRef(initialMessages);
  const runtime = useChatRuntime({ transport, messages: initialMessagesRef.current });

  return (
    <AssistantRuntimeProvider runtime={runtime}>
      <div className="ai-chat-widget">
        {/* Registers kb_search tool renderer — renders nothing visible */}
        <KbSearchToolUI />
        <AssistantModal onClear={onStartNew} defaultOpen={defaultOpen} />
      </div>
    </AssistantRuntimeProvider>
  );
}
