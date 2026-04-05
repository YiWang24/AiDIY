import React from "react";
import Translate, { translate } from "@docusaurus/Translate";
import BotIcon from "../icons/BotIcon";
import styles from "../AIChatWidget.module.css";

export default function ChatHeader({
  onClear,
  onClose,
}: {
  onClear: () => void;
  onClose: () => void;
}): JSX.Element {
  return (
    <div className={styles.header}>
      <div className={styles.headerInfo}>
        <div className={styles.headerIconWrap}>
          <BotIcon size={28} />
        </div>
        <div>
          <h3 className={styles.headerTitle}>
            <Translate id="chatbot.title">AiDIY Assistant</Translate>
          </h3>
          <span className={styles.headerSubtitle}>
            <Translate id="chatbot.subtitle">
              Powered by RAG Knowledge Base
            </Translate>
          </span>
        </div>
      </div>
      <div className={styles.headerActions}>
        <button
          className={styles.headerActionButton}
          onClick={onClear}
          title={translate({
            id: "chatbot.clearChat",
            message: "Clear chat",
          })}
          aria-label={translate({
            id: "chatbot.clearChat",
            message: "Clear chat",
          })}
        >
          <svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
          >
            <path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2" />
          </svg>
        </button>
        <button
          className={styles.headerActionButton}
          onClick={onClose}
          title={translate({
            id: "chatbot.closeChat",
            message: "Close chat",
          })}
          aria-label={translate({
            id: "chatbot.closeChat",
            message: "Close chat",
          })}
        >
          <svg
            width="18"
            height="18"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2.5"
          >
            <path d="M18 6L6 18M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>
  );
}
