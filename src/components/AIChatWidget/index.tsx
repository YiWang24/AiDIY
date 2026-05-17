import React, { useState, useRef, useEffect, useCallback } from "react";
import clsx from "clsx";
import { useChat } from "@ai-sdk/react";
import {
  DefaultChatTransport,
  type UIMessage,
  type ToolUIPart,
} from "ai";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

import {
  Conversation,
  ConversationContent,
  ConversationScrollButton,
} from "src/components/ai-elements/conversation";
import {
  Message,
  MessageContent,
} from "src/components/ai-elements/message";
import {
  PromptInput,
  PromptInputBody,
  PromptInputTextarea,
  PromptInputToolbar,
  PromptInputSubmit,
  type PromptInputMessage,
} from "src/components/ai-elements/prompt-input";
import {
  Reasoning,
  ReasoningTrigger,
  ReasoningContent,
} from "src/components/ai-elements/reasoning";
import {
  Sources,
  SourcesTrigger,
  SourcesContent,
  Source,
} from "src/components/ai-elements/sources";
import {
  Tool,
  ToolHeader,
  ToolContent,
  ToolInput,
} from "src/components/ai-elements/tool";
import { TooltipProvider } from "src/components/ui/tooltip";

import useKeyboardShortcuts from "./hooks/useKeyboardShortcuts";
import useSessionId from "./hooks/useSessionId";
import FloatingButton from "./components/FloatingButton";
import ChatHeader from "./components/ChatHeader";
import WelcomeScreen from "./components/WelcomeScreen";
import type { RetrievalToolOutput, RetrievedChunk } from "./types";
import styles from "./AIChatWidget.module.css";

const transport = new DefaultChatTransport({ api: "/api/chat" });

// rawPath e.g. "docs/cs/algorithms/index.md" -> "/docs/cs/algorithms"
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

export default function AIChatWidget(): JSX.Element {
  const [isOpen, setIsOpen] = useState(false);
  const { sessionId, startNew } = useSessionId();

  const { messages, sendMessage, status, stop, setMessages } = useChat({
    id: sessionId ?? undefined,
    transport,
  });

  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Hydrate persisted history on session change.
  useEffect(() => {
    if (!sessionId) return;
    let cancelled = false;
    (async () => {
      try {
        const res = await fetch(
          `/api/messages?sessionId=${encodeURIComponent(sessionId)}`,
        );
        if (!res.ok) return;
        const data = (await res.json()) as { messages: UIMessage[] };
        if (!cancelled && Array.isArray(data.messages) && data.messages.length) {
          setMessages(data.messages);
        }
      } catch {
        /* empty history is the default */
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [sessionId, setMessages]);

  const handleToggle = useCallback(() => setIsOpen((v) => !v), []);
  const handleClose = useCallback(() => setIsOpen(false), []);
  useKeyboardShortcuts({ onEscape: handleClose, onToggle: handleToggle });

  useEffect(() => {
    if (isOpen) setTimeout(() => inputRef.current?.focus(), 300);
  }, [isOpen]);

  const handleSubmit = useCallback(
    (message: PromptInputMessage) => {
      const text = message.text?.trim();
      if (!text) return;
      sendMessage({ text });
    },
    [sendMessage],
  );

  const handleSuggestionSelect = useCallback(
    (query: string) => {
      sendMessage({ text: query });
    },
    [sendMessage],
  );

  const handleClear = useCallback(() => {
    if (status === "streaming" || status === "submitted") stop();
    startNew();
    setMessages([]);
    setTimeout(() => inputRef.current?.focus(), 100);
  }, [status, stop, startNew, setMessages]);

  return (
    <TooltipProvider delayDuration={400}>
      <FloatingButton isOpen={isOpen} onClick={handleToggle} />

      <div
        className={clsx(
          "ai-chat-widget",
          styles.chatWindow,
          isOpen ? styles.chatWindowOpen : styles.chatWindowClosed,
        )}
        role="dialog"
        aria-label="AI Chat"
      >
        <ChatHeader onClear={handleClear} onClose={handleClose} />

        <Conversation className="flex-1 min-h-0">
          {messages.length === 0 ? (
            <div className="p-4">
              <WelcomeScreen onSelectSuggestion={handleSuggestionSelect} />
            </div>
          ) : (
            <ConversationContent>
              {messages.map((m) => (
                <MessageRow key={m.id} message={m} />
              ))}
            </ConversationContent>
          )}
          <ConversationScrollButton />
        </Conversation>

        <div className="border-t border-border bg-background p-3">
          <PromptInput onSubmit={handleSubmit} className="rounded-xl">
            <PromptInputBody>
              <PromptInputTextarea
                ref={inputRef as React.Ref<HTMLTextAreaElement>}
                placeholder="Ask about the docs..."
              />
              <PromptInputToolbar className="justify-end">
                <PromptInputSubmit status={status} />
              </PromptInputToolbar>
            </PromptInputBody>
          </PromptInput>
        </div>
      </div>
    </TooltipProvider>
  );
}

interface MessageRowProps {
  message: UIMessage;
}

function MessageRow({ message }: MessageRowProps): JSX.Element {
  const isUser = message.role === "user";

  // Pull all kb_search tool parts to collect citations across steps.
  const kbToolParts = (message.parts ?? []).filter(
    (p): p is ToolUIPart =>
      typeof p.type === "string" && p.type === "tool-kb_search",
  );
  const allChunks: RetrievedChunk[] = kbToolParts.flatMap((p) => {
    const out = (p as { output?: RetrievalToolOutput }).output;
    return out?.chunks ?? [];
  });
  const uniqueChunks = dedupeChunks(allChunks);

  return (
    <Message from={isUser ? "user" : "assistant"}>
      <MessageContent>
        {(message.parts ?? []).map((part, idx) => {
          if (part.type === "text") {
            const textPart = part as { type: "text"; text: string };
            if (!textPart.text) return null;
            return (
              <div
                key={`${message.id}-text-${idx}`}
                className={styles.markdownContent}
              >
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  components={{
                    code({ inline, className, children, ...props }: any) {
                      return !inline ? (
                        <code className={className} {...props}>
                          {children}
                        </code>
                      ) : (
                        <code className={styles.inlineCode} {...props}>
                          {children}
                        </code>
                      );
                    },
                    a({ children, ...props }: any) {
                      return (
                        <a {...props} target="_blank" rel="noopener noreferrer">
                          {children}
                        </a>
                      );
                    },
                  }}
                >
                  {textPart.text}
                </ReactMarkdown>
              </div>
            );
          }

          if (part.type === "reasoning") {
            const r = part as { type: "reasoning"; text: string };
            if (!r.text) return null;
            return (
              <Reasoning
                key={`${message.id}-reasoning-${idx}`}
                isStreaming={false}
                className="mb-2"
              >
                <ReasoningTrigger />
                <ReasoningContent>{r.text}</ReasoningContent>
              </Reasoning>
            );
          }

          if (part.type === "tool-kb_search") {
            const tool = part as ToolUIPart;
            return (
              <Tool key={`${message.id}-tool-${idx}`}>
                <ToolHeader
                  type={tool.type as ToolUIPart["type"]}
                  state={tool.state}
                  title="Knowledge base search"
                />
                <ToolContent>
                  {(tool as { input?: unknown }).input != null && (
                    <ToolInput input={(tool as { input?: unknown }).input} />
                  )}
                </ToolContent>
              </Tool>
            );
          }

          return null;
        })}

        {!isUser && uniqueChunks.length > 0 && (
          <Sources>
            <SourcesTrigger count={uniqueChunks.length} />
            <SourcesContent>
              {uniqueChunks.map((c) => (
                <Source
                  key={c.chunk_id}
                  href={toDocLink(c.path)}
                  title={c.title ?? c.path}
                />
              ))}
            </SourcesContent>
          </Sources>
        )}
      </MessageContent>
    </Message>
  );
}
