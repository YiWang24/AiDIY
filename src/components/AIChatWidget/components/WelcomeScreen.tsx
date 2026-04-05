import React from "react";
import Translate from "@docusaurus/Translate";
import BotIcon from "../icons/BotIcon";
import styles from "../AIChatWidget.module.css";

const SUGGESTIONS = [
  {
    id: "suggestion.1",
    label: <Translate id="chatbot.suggestion.1">What is AgentOps and how does it work?</Translate>,
    query: "What is AgentOps and how does it work?",
  },
  {
    id: "suggestion.2",
    label: <Translate id="chatbot.suggestion.2">Explain the agent loop architecture</Translate>,
    query: "Explain the agent loop architecture",
  },
  {
    id: "suggestion.3",
    label: <Translate id="chatbot.suggestion.3">What are the patterns of agent orchestration?</Translate>,
    query: "What are the patterns of agent orchestration?",
  },
];

const CAPABILITIES = [
  { icon: "search", label: <Translate id="chatbot.capability.search">Search docs</Translate> },
  { icon: "code", label: <Translate id="chatbot.capability.code">Explain code</Translate> },
  { icon: "file", label: <Translate id="chatbot.capability.file">Find examples</Translate> },
];

function CapabilityIcon({ icon }: { icon: string }) {
  if (icon === "search") {
    return (
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <circle cx="11" cy="11" r="8" />
        <path d="M21 21l-4.35-4.35" />
      </svg>
    );
  }
  if (icon === "code") {
    return (
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M16 18l6-6-6-6M8 6l-6 6 6 6" />
      </svg>
    );
  }
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" />
      <path d="M14 2v6h6M16 13H8M16 17H8M10 9H8" />
    </svg>
  );
}

export default function WelcomeScreen({
  onSelectSuggestion,
}: {
  onSelectSuggestion: (query: string) => void;
}): JSX.Element {
  return (
    <div className={styles.welcomeRoot}>
      {/* Zone A — Brand Hero */}
      <div className={styles.welcomeHero}>
        <div className={styles.welcomeIconWrap}>
          <BotIcon size={56} />
        </div>
        <h2 className={styles.welcomeTitle}>
          <Translate id="chatbot.title">AiDIY Assistant</Translate>
        </h2>
        <p className={styles.welcomeSubtitle}>
          <Translate id="chatbot.welcomeSubtitle">
            Ask questions about CS, AI, and engineering docs
          </Translate>
        </p>
      </div>

      {/* Zone B — Capability Chips */}
      <div className={styles.welcomeCapabilities}>
        {CAPABILITIES.map((cap) => (
          <span key={cap.icon} className={styles.capabilityChip}>
            <CapabilityIcon icon={cap.icon} />
            {cap.label}
          </span>
        ))}
      </div>

      {/* Zone C — Quick Suggestions */}
      <div className={styles.welcomeSuggestions}>
        <p className={styles.suggestionsLabel}>
          <Translate id="chatbot.tryAsking">Try asking</Translate>
        </p>
        {SUGGESTIONS.map((s) => (
          <button
            key={s.id}
            className={styles.suggestionButton}
            onClick={() => onSelectSuggestion(s.query)}
          >
            <span>{s.label}</span>
            <svg
              width="14"
              height="14"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
            >
              <path d="M5 12h14M12 5l7 7-7 7" />
            </svg>
          </button>
        ))}
      </div>
    </div>
  );
}
