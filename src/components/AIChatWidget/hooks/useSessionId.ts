import { useState, useCallback } from "react";

const STORAGE_KEY = "aidiy.chat.sessionId";

function generateId(): string {
  const rand = Math.random().toString(36).slice(2, 10);
  return `s-${Date.now()}-${rand}`;
}

// Reads localStorage synchronously via lazy useState initializer.
// Safe because this component is always wrapped in <BrowserOnly> — no SSR.
export default function useSessionId(): {
  sessionId: string;
  startNew: () => string;
  setSessionId: (id: string) => void;
} {
  const [sessionId, setSessionIdState] = useState<string>(() => {
    const stored = localStorage.getItem(STORAGE_KEY);
    const id = stored ?? generateId();
    if (!stored) localStorage.setItem(STORAGE_KEY, id);
    return id;
  });

  const setSessionId = useCallback((id: string) => {
    setSessionIdState(id);
    localStorage.setItem(STORAGE_KEY, id);
  }, []);

  const startNew = useCallback(() => {
    const id = generateId();
    setSessionId(id);
    return id;
  }, [setSessionId]);

  return { sessionId, startNew, setSessionId };
}
