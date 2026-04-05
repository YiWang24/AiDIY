import React, { useState, useRef, useEffect, useCallback } from "react";
import clsx from "clsx";
import useChatSession from "./hooks/useChatSession";
import useKeyboardShortcuts from "./hooks/useKeyboardShortcuts";
import FloatingButton from "./components/FloatingButton";
import ChatHeader from "./components/ChatHeader";
import WelcomeScreen from "./components/WelcomeScreen";
import MessageBubble from "./components/MessageBubble";
import MessageInput from "./components/MessageInput";
import styles from "./AIChatWidget.module.css";

export default function AIChatWidget(): JSX.Element {
  const [isOpen, setIsOpen] = useState(false);
  const [sessionId] = useState(
    () => `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
  );
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const {
    messages,
    inputValue,
    setInputValue,
    isLoading,
    sendMessage,
    clearChat,
    deduplicateCitations,
  } = useChatSession(sessionId);

  // Keyboard shortcuts
  const handleToggle = useCallback(() => setIsOpen((v) => !v), []);
  const handleClose = useCallback(() => setIsOpen(false), []);
  useKeyboardShortcuts({
    onEscape: handleClose,
    onToggle: handleToggle,
  });

  // Auto-scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Focus input on open
  useEffect(() => {
    if (isOpen) {
      setTimeout(() => inputRef.current?.focus(), 300);
    }
  }, [isOpen]);

  const handleSuggestionSelect = (query: string) => {
    setInputValue(query);
    setTimeout(() => inputRef.current?.focus(), 50);
  };

  const handleClear = () => {
    clearChat();
    setTimeout(() => inputRef.current?.focus(), 100);
  };

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
                deduplicateCitations={deduplicateCitations}
              />
            ))
          )}
          <div ref={messagesEndRef} />
        </div>

        <MessageInput
          value={inputValue}
          onChange={setInputValue}
          onSend={sendMessage}
          isLoading={isLoading}
          inputRef={inputRef}
        />
      </div>
    </>
  );
}
