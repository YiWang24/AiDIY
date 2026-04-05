import React, { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Message } from "../hooks/useChatSession";
import CitationList from "./CitationList";
import styles from "../AIChatWidget.module.css";

function StreamingBar() {
  return <div className={styles.streamingBar} />;
}

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      /* ignore */
    }
  };

  return (
    <button
      className={styles.messageActionBtn}
      onClick={handleCopy}
      title={copied ? "Copied!" : "Copy response"}
      aria-label="Copy response"
    >
      {copied ? (
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M20 6L9 17l-5-5" />
        </svg>
      ) : (
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <rect x="9" y="9" width="13" height="13" rx="2" />
          <path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1" />
        </svg>
      )}
    </button>
  );
}

export default function MessageBubble({
  message,
  deduplicateCitations,
}: {
  message: Message;
  deduplicateCitations: (citations: Message["citations"]) => NonNullable<Message["citations"]>;
}): JSX.Element {
  const isUser = message.role === "user";

  return (
    <div
      className={`${styles.message} ${isUser ? styles.messageUser : styles.messageAssistant}`}
    >
      <div className={styles.messageBubble}>
        {/* Retrieval Status */}
        {message.isStreaming &&
          message.retrievalChunks &&
          message.retrievalChunks.length > 0 && (
            <div className={styles.retrievalStatus}>
              <span className={styles.retrievalBadge}>
                Retrieved {message.retrievalChunks.length} chunks
              </span>
              {message.retrievalTimeMs && (
                <span className={styles.timeBadge}>
                  {message.retrievalTimeMs}ms
                </span>
              )}
            </div>
          )}

        {/* Agent Type Badge */}
        {message.agentType && (
          <div className={styles.agentBadge}>
            {message.agentType === "knowledge" && "Knowledge Base"}
            {message.agentType === "web_search" && "Web Search"}
            {message.agentType === "hybrid" && "Hybrid (KB + Web)"}
            {message.agentType === "hybrid_knowledge" && "Knowledge Base"}
          </div>
        )}

        {/* Content */}
        {message.content ? (
          <div className={styles.markdownContent}>
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                code({
                  inline,
                  className,
                  children,
                  ...props
                }: any) {
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
              {message.content}
            </ReactMarkdown>
          </div>
        ) : message.isStreaming ? (
          <StreamingBar />
        ) : null}

        {/* Performance Metrics */}
        {!message.isStreaming &&
          (message.retrievalTimeMs || message.generationTimeMs) && (
            <div className={styles.performanceMetrics}>
              {message.retrievalTimeMs && (
                <span className={styles.metric}>
                  Retrieval: {message.retrievalTimeMs}ms
                </span>
              )}
              {message.generationTimeMs && (
                <span className={styles.metric}>
                  Generation: {message.generationTimeMs}ms
                </span>
              )}
            </div>
          )}

        {/* Citations */}
        {message.citations && message.citations.length > 0 && (
          <CitationList
            citations={message.citations}
            deduplicate={deduplicateCitations}
          />
        )}
      </div>

      {/* Message Actions — assistant only */}
      {!isUser && message.content && !message.isStreaming && (
        <div className={styles.messageActions}>
          <CopyButton text={message.content} />
        </div>
      )}
    </div>
  );
}
