import React, {
  useState,
  useRef,
  useEffect,
  useCallback,
  useMemo,
} from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import styles from "./AIChatWidget.module.css";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  isStreaming?: boolean;
  citations?: Citation[];
  agentType?: "knowledge" | "web_search" | "hybrid" | "hybrid_knowledge";
  retrievalChunks?: RetrievedChunk[];
  retrievalTimeMs?: number;
  generationTimeMs?: number;
}

interface RetrievedChunk {
  chunk_id: string;
  doc_id: string;
  content: string;
  heading_path: string[];
  score: number;
}

interface Citation {
  id: number;
  chunk_id: string;
  doc_id: string;
  title: string;
  path: string;
  heading_path: string[];
  score: number;
}

interface AskResponse {
  answer: string;
  citations: Citation[];
  has_sufficient_knowledge: boolean;
  model: string;
  tokens_used: number | null;
  retrieval_time_ms: number;
  generation_time_ms: number;
  agent_type?: "knowledge" | "web_search" | "hybrid" | "hybrid_knowledge";
}

export default function AIChatWidget(): JSX.Element {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId] = useState(
    () => `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
  );
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Focus input when opened
  useEffect(() => {
    if (isOpen) {
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  }, [isOpen]);

  // Deduplicate citations by doc_id to avoid showing the same source multiple times
  const deduplicateCitations = useCallback(
    (citations: Citation[]): Citation[] => {
      const seen = new Set<string>();
      return citations.filter((citation) => {
        const key = `${citation.doc_id}-${citation.path}`;
        if (seen.has(key)) {
          return false;
        }
        seen.add(key);
        return true;
      });
    },
    [],
  );

  const sendMessage = useCallback(async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: "user",
      content: inputValue.trim(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue("");
    setIsLoading(true);

    // Create assistant message placeholder
    const assistantMessageId = `assistant-${Date.now()}`;
    setMessages((prev) => [
      ...prev,
      {
        id: assistantMessageId,
        role: "assistant",
        content: "",
        isStreaming: true,
        retrievalChunks: [],
      },
    ]);

    try {
      // Call Edge Function proxy (handles Cloudflare Access authentication)
      const response = await fetch(`/api/stream`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: userMessage.content,
          session_id: sessionId,
          top_k: 5,
          mode: "auto",
        }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`HTTP ${response.status}: ${errorText}`);
      }

      // Parse SSE stream
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let eventType = "";
      let fullContent = "";
      let buffer = ""; // Buffer for incomplete lines

      if (!reader) {
        throw new Error("Response body is null");
      }

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        // Decode chunk and append to buffer
        buffer += decoder.decode(value, { stream: true });

        // Split by newlines
        const lines = buffer.split("\n");

        // Keep the last line in buffer if it doesn't end with newline
        // (it might be incomplete)
        if (lines.length > 0 && !buffer.endsWith("\n")) {
          buffer = lines.pop() || "";
        } else {
          buffer = "";
        }

        for (const line of lines) {
          if (!line.trim()) continue; // Skip empty lines

          if (line.startsWith("event:")) {
            // Use substring to remove 'event:' prefix (more reliable than split)
            eventType = line.substring(7).trim(); // 'event:' is 7 characters
          } else if (line.startsWith("data:")) {
            // Use substring to remove 'data:' prefix (more reliable than split)
            const dataStr = line.substring(5).trim(); // 'data:' is 5 characters
            if (!dataStr) continue; // Skip if no data content

            let data: any;
            try {
              data = JSON.parse(dataStr);
            } catch (e) {
              console.error("Failed to parse SSE JSON:", e);
              continue;
            }

            if (eventType === "retrieval_start") {
              // Retrieval started - can show loading indicator
              console.log("Retrieval started");
            } else if (eventType === "retrieval_complete") {
              // Update with retrieved chunks
              setMessages((prev) =>
                prev.map((msg) =>
                  msg.id === assistantMessageId
                    ? {
                        ...msg,
                        retrievalChunks: data.chunks || [],
                        retrievalTimeMs: data.retrieval_time_ms || 0,
                      }
                    : msg,
                ),
              );
            } else if (eventType === "generation_start") {
              // Generation started
              console.log("Generation started");
            } else if (eventType === "generation_delta") {
              // Stream content
              const delta = data.delta || "";
              fullContent += delta;
              console.log(
                "Generation delta:",
                delta,
                "Full content so far:",
                fullContent,
              );
              setMessages((prev) =>
                prev.map((msg) =>
                  msg.id === assistantMessageId
                    ? { ...msg, content: fullContent }
                    : msg,
                ),
              );
            } else if (eventType === "generation_complete") {
              // Final response with citations
              console.log("=== GENERATION COMPLETE EVENT ===");
              console.log("Raw data:", JSON.stringify(data, null, 2));
              console.log("Full content accumulated:", fullContent);

              const metadata = data.metadata || {};
              const answer = data.answer || fullContent || ""; // Fallback to accumulated content

              console.log("Parsed answer:", answer);
              console.log("data.answer:", data.answer);
              console.log("Using fallback?:", !data.answer);

              setMessages((prev) => {
                const updated = prev.map((msg) =>
                  msg.id === assistantMessageId
                    ? {
                        ...msg,
                        content: answer,
                        isStreaming: false,
                        citations: data.citations || [],
                        agentType: metadata.agent_type || "unknown",
                        generationTimeMs: metadata.generation_time_ms || 0,
                      }
                    : msg,
                );
                console.log(
                  "Updated messages:",
                  updated.map((m) => ({
                    id: m.id,
                    content: m.content?.substring(0, 50),
                  })),
                );
                return updated;
              });
            } else if (eventType === "complete") {
              // Stream completed
              console.log("Stream completed for session:", data.session_id);
            } else if (eventType === "error") {
              const errorMsg = data.detail || data.error || "Unknown error";
              throw new Error(errorMsg);
            }
          }
        }
      }
    } catch (error) {
      console.error("Chat error:", error);
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === assistantMessageId
            ? {
                ...msg,
                content: `Sorry, I encountered an error: ${error instanceof Error ? error.message : "Unknown error"}`,
                isStreaming: false,
              }
            : msg,
        ),
      );
    } finally {
      setIsLoading(false);
    }
  }, [inputValue, isLoading, sessionId]);

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const clearChat = () => {
    setMessages([]);
  };

  return (
    <>
      {/* Floating Button */}
      <button
        className={styles.floatingButton}
        onClick={() => setIsOpen(!isOpen)}
        aria-label={isOpen ? "Close chat" : "Open AI chat"}
      >
        {isOpen ? (
          <svg
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
          >
            <path d="M18 6L6 18M6 6l12 12" />
          </svg>
        ) : (
          <svg
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
          >
            <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z" />
          </svg>
        )}
      </button>

      {/* Chat Window */}
      {isOpen && (
        <div className={styles.chatWindow}>
          {/* Header */}
          <div className={styles.header}>
            <div className={styles.headerInfo}>
              <span className={styles.headerIcon}>🤖</span>
              <div>
                <h3 className={styles.headerTitle}>AI Assistant</h3>
                <span className={styles.headerSubtitle}>
                  Powered by RAG Knowledge Base
                </span>
              </div>
            </div>
            <div className={styles.headerActions}>
              <button
                className={styles.clearButton}
                onClick={clearChat}
                title="Clear chat"
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
                className={styles.closeButton}
                onClick={() => setIsOpen(false)}
                title="Close chat"
              >
                <svg
                  width="20"
                  height="20"
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

          {/* Messages */}
          <div className={styles.messages}>
            {messages.length === 0 && (
              <div className={styles.welcomeMessage}>
                <p>👋 Hi! I'm your AI documentation assistant.</p>
                <p>I can help you find information from the knowledge base.</p>
                <div className={styles.suggestions}>
                  <button
                    onClick={() =>
                      setInputValue("What is AgentOps and how does it work?")
                    }
                  >
                    🤖 What is AgentOps?
                  </button>
                  <button
                    onClick={() =>
                      setInputValue("Explain the agent loop architecture")
                    }
                  >
                    🏗️ Agent loop architecture
                  </button>
                  <button
                    onClick={() =>
                      setInputValue(
                        "What are the patterns of agent orchestration?",
                      )
                    }
                  >
                    🔗 Agent orchestration patterns
                  </button>
                </div>
              </div>
            )}

            {messages.map((message) => {
              console.log(
                "Rendering message:",
                message.id,
                "Role:",
                message.role,
                "Content length:",
                message.content?.length,
                "Content preview:",
                message.content?.substring(0, 50),
              );
              return (
                <div
                  key={message.id}
                  className={`${styles.message} ${styles[message.role]}`}
                >
                  <div className={styles.messageContent}>
                    {/* Retrieval Status */}
                    {message.isStreaming &&
                      message.retrievalChunks &&
                      message.retrievalChunks.length > 0 && (
                        <div className={styles.retrievalStatus}>
                          <span className={styles.retrievalBadge}>
                            🔍 Retrieved {message.retrievalChunks.length} chunks
                          </span>
                          {message.retrievalTimeMs && (
                            <span className={styles.timeBadge}>
                              ⏱️ {message.retrievalTimeMs}ms
                            </span>
                          )}
                        </div>
                      )}

                    {/* Agent Type Badge */}
                    {message.agentType && (
                      <div className={styles.agentBadge}>
                        {message.agentType === "knowledge" &&
                          "📚 Knowledge Base"}
                        {message.agentType === "web_search" && "🌐 Web Search"}
                        {message.agentType === "hybrid" &&
                          "🔗 Hybrid (KB + Web)"}
                        {message.agentType === "hybrid_knowledge" &&
                          "📚 Knowledge Base"}
                      </div>
                    )}

                    {/* Message Content */}
                    {message.content ? (
                      <div className={styles.markdownContent}>
                        <ReactMarkdown
                          remarkPlugins={[remarkGfm]}
                          components={{
                            // Custom code block styling
                            code({
                              node,
                              inline,
                              className,
                              children,
                              ...props
                            }) {
                              const match = /language-(\w+)/.exec(
                                className || "",
                              );
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
                            // Style links
                            a({ node, children, ...props }) {
                              return (
                                <a
                                  {...props}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                >
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
                      <span className={styles.typingIndicator}>
                        <span></span>
                        <span></span>
                        <span></span>
                      </span>
                    ) : null}

                    {/* Performance Metrics */}
                    {!message.isStreaming &&
                      (message.retrievalTimeMs || message.generationTimeMs) && (
                        <div className={styles.performanceMetrics}>
                          {message.retrievalTimeMs && (
                            <span className={styles.metric}>
                              📊 Retrieval: {message.retrievalTimeMs}ms
                            </span>
                          )}
                          {message.generationTimeMs && (
                            <span className={styles.metric}>
                              ✨ Generation: {message.generationTimeMs}ms
                            </span>
                          )}
                        </div>
                      )}

                    {/* Citations */}
                    {message.citations &&
                      message.citations.length > 0 &&
                      (() => {
                        const uniqueCitations = deduplicateCitations(
                          message.citations,
                        );
                        return uniqueCitations.length > 0 ? (
                          <div className={styles.citations}>
                            <p className={styles.citationsTitle}>📚 Sources:</p>
                            <ul className={styles.citationsList}>
                              {uniqueCitations.map((citation) => (
                                <li key={citation.id}>
                                  <a
                                    href={citation.path}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className={styles.citationLink}
                                  >
                                    {citation.title}
                                  </a>
                                  <span className={styles.citationScore}>
                                    ({(citation.score * 100).toFixed(0)}% match)
                                  </span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        ) : null;
                      })()}
                  </div>
                </div>
              );
            })}
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className={styles.inputContainer}>
            <input
              ref={inputRef}
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask about the docs..."
              disabled={isLoading}
              className={styles.input}
            />
            <button
              onClick={sendMessage}
              disabled={!inputValue.trim() || isLoading}
              className={styles.sendButton}
            >
              {isLoading ? (
                <span className={styles.loadingSpinner}></span>
              ) : (
                <svg
                  width="20"
                  height="20"
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
        </div>
      )}
    </>
  );
}
