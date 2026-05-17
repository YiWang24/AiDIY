import { useEffect, useState, useCallback } from "react";

const STORAGE_KEY = "aidiy.chat.sessionId";

function generateId(): string {
  const rand = Math.random().toString(36).slice(2, 10);
  return `s-${Date.now()}-${rand}`;
}

// Persists the current session id in localStorage so refresh keeps the same
// conversation. SSR-safe: returns null until mounted.
export default function useSessionId(): {
  sessionId: string | null;
  startNew: () => string;
  setSessionId: (id: string) => void;
} {
  const [sessionId, setSessionIdState] = useState<string | null>(null);

  useEffect(() => {
    if (typeof window === "undefined") return;
    const stored = window.localStorage.getItem(STORAGE_KEY);
    const id = stored ?? generateId();
    if (!stored) window.localStorage.setItem(STORAGE_KEY, id);
    setSessionIdState(id);
  }, []);

  const setSessionId = useCallback((id: string) => {
    setSessionIdState(id);
    if (typeof window !== "undefined") {
      window.localStorage.setItem(STORAGE_KEY, id);
    }
  }, []);

  const startNew = useCallback(() => {
    const id = generateId();
    setSessionId(id);
    return id;
  }, [setSessionId]);

  return { sessionId, startNew, setSessionId };
}
