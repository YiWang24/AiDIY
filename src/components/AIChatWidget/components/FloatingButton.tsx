import React from "react";
import clsx from "clsx";
import BotIcon from "../icons/BotIcon";
import styles from "../AIChatWidget.module.css";

export default function FloatingButton({
  isOpen,
  onClick,
}: {
  isOpen: boolean;
  onClick: () => void;
}): JSX.Element {
  return (
    <button
      className={clsx(styles.floatingButton, isOpen && styles.floatingButtonHidden)}
      onClick={onClick}
      aria-label={isOpen ? "Close chat" : "Open AiDIY chat"}
      aria-expanded={isOpen}
    >
      {isOpen ? (
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
      ) : (
        <BotIcon size={26} />
      )}
    </button>
  );
}
