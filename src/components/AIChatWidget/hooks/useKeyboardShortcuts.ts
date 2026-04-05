import { useEffect } from "react";

export default function useKeyboardShortcuts(callbacks: {
  onEscape: () => void;
  onToggle: () => void;
}) {
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      // Escape closes the panel
      if (e.key === "Escape") {
        callbacks.onEscape();
        return;
      }
      // Cmd/Ctrl + K toggles the panel
      if (e.key === "k" && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        callbacks.onToggle();
      }
    };

    document.addEventListener("keydown", handler);
    return () => document.removeEventListener("keydown", handler);
  }, [callbacks]);
}
