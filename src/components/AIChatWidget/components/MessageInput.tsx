import React from "react";
import { translate } from "@docusaurus/Translate";
import styles from "../AIChatWidget.module.css";

export default function MessageInput({
  value,
  onChange,
  onSend,
  isLoading,
  inputRef,
}: {
  value: string;
  onChange: (val: string) => void;
  onSend: () => void;
  isLoading: boolean;
  inputRef: React.RefObject<HTMLInputElement | null>;
}): JSX.Element {
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      onSend();
    }
  };

  return (
    <div className={styles.inputContainer}>
      <input
        ref={inputRef}
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyPress={handleKeyPress}
        placeholder={translate({
          id: "chatbot.placeholder",
          message: "Ask about the docs...",
        })}
        disabled={isLoading}
        className={styles.input}
      />
      <button
        onClick={onSend}
        disabled={!value.trim() || isLoading}
        className={styles.sendButton}
        aria-label={translate({
          id: "chatbot.sendMessage",
          message: "Send message",
        })}
      >
        {isLoading ? (
          <span className={styles.loadingSpinner} />
        ) : (
          <svg
            width="18"
            height="18"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
          >
            <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z" />
          </svg>
        )}
      </button>
    </div>
  );
}
