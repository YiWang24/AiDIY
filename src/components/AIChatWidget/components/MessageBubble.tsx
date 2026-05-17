import React, { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import type { UIMessage } from "ai";
import CitationList from "./CitationList";
import type { RetrievalToolOutput } from "../types";
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

interface Props {
  message: UIMessage;
  isStreaming: boolean;
}

// Extract text content across all text parts of a message.
function extractText(message: UIMessage): string {
  return (message.parts ?? [])
    .filter((p): p is { type: "text"; text: string } => p.type === "text")
    .map((p) => p.text)
    .join("\n\n");
}

function isToolPart(
  part: UIMessage["parts"][number],
): part is { type: string; state?: string; output?: unknown; input?: unknown } {
  return typeof part.type === "string" && part.type.startsWith("tool-");
}

export default function MessageBubble({
  message,
  isStreaming,
}: Props): JSX.Element {
  const isUser = message.role === "user";
  const text = extractText(message);

  const kbToolParts = (message.parts ?? []).filter(
    (p) => isToolPart(p) && p.type === "tool-kb_search",
  );

  const allChunks = kbToolParts.flatMap((p) => {
    const out = (p as { output?: RetrievalToolOutput }).output;
    return out?.chunks ?? [];
  });

  const totalRetrievalMs = kbToolParts.reduce((sum, p) => {
    const out = (p as { output?: RetrievalToolOutput }).output;
    return sum + (out?.retrieval_time_ms ?? 0);
  }, 0);

  return (
    <div
      className={`${styles.message} ${isUser ? styles.messageUser : styles.messageAssistant}`}
    >
      <div className={styles.messageBubble}>
        {isStreaming && allChunks.length > 0 && (
          <div className={styles.retrievalStatus}>
            <span className={styles.retrievalBadge}>
              Retrieved {allChunks.length} chunks
            </span>
            {totalRetrievalMs > 0 && (
              <span className={styles.timeBadge}>{totalRetrievalMs}ms</span>
            )}
          </div>
        )}

        {text ? (
          <div className={styles.markdownContent}>
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
              {text}
            </ReactMarkdown>
          </div>
        ) : isStreaming ? (
          <StreamingBar />
        ) : null}

        {!isStreaming && totalRetrievalMs > 0 && (
          <div className={styles.performanceMetrics}>
            <span className={styles.metric}>
              Retrieval: {totalRetrievalMs}ms
            </span>
          </div>
        )}

        {!isUser && allChunks.length > 0 && (
          <CitationList chunks={allChunks} />
        )}
      </div>

      {!isUser && text && !isStreaming && (
        <div className={styles.messageActions}>
          <CopyButton text={text} />
        </div>
      )}
    </div>
  );
}
