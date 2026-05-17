import React, { useState, useRef, useEffect, useCallback } from "react";
import clsx from "clsx";
import { useChat } from "@ai-sdk/react";
import { DefaultChatTransport, type UIMessage } from "ai";
import useKeyboardShortcuts from "./hooks/useKeyboardShortcuts";
import useSessionId from "./hooks/useSessionId";
import FloatingButton from "./components/FloatingButton";
import ChatHeader from "./components/ChatHeader";
import WelcomeScreen from "./components/WelcomeScreen";
import MessageBubble from "./components/MessageBubble";
import MessageInput from "./components/MessageInput";
import styles from "./AIChatWidget.module.css";

const transport = new DefaultChatTransport({ api: "/api/chat" });

export default function AIChatWidget(): JSX.Element {
  const [isOpen, setIsOpen] = useState(false);
  const { sessionId, startNew } = useSessionId();
  const [inputValue, setInputValue] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const { messages, sendMessage, status, stop, setMessages } = useChat({
    id: sessionId ?? undefined,
    transport,
  });

  const isLoading = status === "submitted" || status === "streaming";

  // Load persisted history when the session id becomes available or changes.
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
        if (!cancelled && Array.isArray(data.messages)) {
          setMessages(data.messages);
        }
      } catch {
        // Ignore: empty history is the default.
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
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    if (isOpen) setTimeout(() => inputRef.current?.focus(), 300);
  }, [isOpen]);

  const handleSend = useCallback(() => {
    const text = inputValue.trim();
    if (!text || isLoading) return;
    setInputValue("");
    sendMessage({ text });
  }, [inputValue, isLoading, sendMessage]);

  const handleSuggestionSelect = useCallback((query: string) => {
    setInputValue(query);
    setTimeout(() => inputRef.current?.focus(), 50);
  }, []);

  const handleClear = useCallback(() => {
    if (isLoading) stop();
    startNew();
    setMessages([]);
    setTimeout(() => inputRef.current?.focus(), 100);
  }, [isLoading, stop, startNew, setMessages]);

  return (
    <>
      <FloatingButton isOpen={isOpen} onClick={handleToggle} />

      <div
        className={clsx(
          styles.chatWindow,
          isOpen ? styles.chatWindowOpen : styles.chatWindowClosed,
        )}
        role="dialog"
        aria-label="AI Chat"
      >
        <ChatHeader onClear={handleClear} onClose={handleClose} />

        <div className={styles.messages} aria-live="polite">
          {messages.length === 0 ? (
            <WelcomeScreen onSelectSuggestion={handleSuggestionSelect} />
          ) : (
            messages.map((message) => (
              <MessageBubble
                key={message.id}
                message={message}
                isStreaming={
                  isLoading && message.id === messages[messages.length - 1].id
                }
              />
            ))
          )}
          <div ref={messagesEndRef} />
        </div>

        <MessageInput
          value={inputValue}
          onChange={setInputValue}
          onSend={handleSend}
          isLoading={isLoading}
          inputRef={inputRef}
        />
      </div>
    </>
  );
}
