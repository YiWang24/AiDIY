import { useState, useCallback, useRef } from "react";

export interface Citation {
  id: number;
  chunk_id: string;
  doc_id: string;
  title: string;
  path: string;
  heading_path: string[];
  score: number;
}

export interface RetrievedChunk {
  chunk_id: string;
  doc_id: string;
  content: string;
  heading_path: string[];
  score: number;
}

export interface Message {
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

export default function useChatSession(sessionId: string) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const abortRef = useRef<AbortController | null>(null);

  const deduplicateCitations = useCallback((citations: Citation[]): Citation[] => {
    const seen = new Set<string>();
    return citations.filter((citation) => {
      const key = `${citation.doc_id}-${citation.path}`;
      if (seen.has(key)) return false;
      seen.add(key);
      return true;
    });
  }, []);

  const clearChat = useCallback(() => {
    if (abortRef.current) {
      abortRef.current.abort();
      abortRef.current = null;
    }
    setMessages([]);
    setIsLoading(false);
  }, []);

  const sendMessage = useCallback(async () => {
    const trimmed = inputValue.trim();
    if (!trimmed || isLoading) return;

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: "user",
      content: trimmed,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue("");
    setIsLoading(true);

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

    const controller = new AbortController();
    abortRef.current = controller;

    try {
      const response = await fetch(`/api/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question: trimmed,
          session_id: sessionId,
          top_k: 5,
          mode: "auto",
        }),
        signal: controller.signal,
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`HTTP ${response.status}: ${errorText}`);
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let eventType = "";
      let fullContent = "";
      let buffer = "";

      if (!reader) throw new Error("Response body is null");

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");

        if (lines.length > 0 && !buffer.endsWith("\n")) {
          buffer = lines.pop() || "";
        } else {
          buffer = "";
        }

        for (const line of lines) {
          if (!line.trim()) continue;

          if (line.startsWith("event:")) {
            eventType = line.substring(7).trim();
          } else if (line.startsWith("data:")) {
            const dataStr = line.substring(5).trim();
            if (!dataStr) continue;

            let data: any;
            try {
              data = JSON.parse(dataStr);
            } catch {
              continue;
            }

            if (eventType === "retrieval_complete") {
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
            } else if (eventType === "generation_delta") {
              fullContent += data.delta || "";
              setMessages((prev) =>
                prev.map((msg) =>
                  msg.id === assistantMessageId
                    ? { ...msg, content: fullContent }
                    : msg,
                ),
              );
            } else if (eventType === "generation_complete") {
              const metadata = data.metadata || {};
              const answer = data.answer || fullContent || "";

              setMessages((prev) =>
                prev.map((msg) =>
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
                ),
              );
            } else if (eventType === "error") {
              throw new Error(data.detail || data.error || "Unknown error");
            }
          }
        }
      }
    } catch (error) {
      if ((error as Error).name === "AbortError") return;
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
      abortRef.current = null;
    }
  }, [inputValue, isLoading, sessionId]);

  return {
    messages,
    inputValue,
    setInputValue,
    isLoading,
    sendMessage,
    clearChat,
    deduplicateCitations,
  };
}
