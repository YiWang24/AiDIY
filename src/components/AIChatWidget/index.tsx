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
