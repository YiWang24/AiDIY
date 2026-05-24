import { useEffect, useState } from "react";
import type { UIMessage } from "ai";

const PREFIX = "aidiy.messages.";
const MAX_MSGS = 30;

function cacheKey(sessionId: string): string {
  return `${PREFIX}${sessionId}`;
}

function readCache(sessionId: string): UIMessage[] {
  try {
    const raw = localStorage.getItem(cacheKey(sessionId));
    if (!raw) return [];
    const data = JSON.parse(raw) as unknown;
    return Array.isArray(data) ? (data as UIMessage[]) : [];
  } catch {
    return [];
  }
}

function writeCache(sessionId: string, messages: UIMessage[]): void {
  try {
    localStorage.setItem(
      cacheKey(sessionId),
      JSON.stringify(messages.slice(-MAX_MSGS)),
    );
  } catch {
    // localStorage quota exceeded or unavailable — ignore
  }
}

export function clearSessionCache(sessionId: string): void {
  try {
    localStorage.removeItem(cacheKey(sessionId));
  } catch {
    // ignore
  }
}

/**
 * Returns cached messages from localStorage immediately (never null).
 * Fetches from /api/messages in background to keep cache fresh for the
 * NEXT page load. Does NOT remount the runtime — only updates storage.
 */
export function useSessionMessages(sessionId: string): UIMessage[] {
  const [messages] = useState<UIMessage[]>(() => readCache(sessionId));

  useEffect(() => {
    let cancelled = false;
    void (async () => {
      try {
        const res = await fetch(
          `/api/messages?sessionId=${encodeURIComponent(sessionId)}`,
        );
        if (cancelled || !res.ok) return;
        const data = (await res.json()) as { messages: UIMessage[] };
        if (!cancelled && Array.isArray(data.messages)) {
          writeCache(sessionId, data.messages);
        }
      } catch {
        // network error — use cache silently
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [sessionId]);

  return messages;
}
