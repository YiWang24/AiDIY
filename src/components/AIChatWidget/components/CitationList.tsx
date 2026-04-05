import React from "react";
import Translate from "@docusaurus/Translate";
import { Citation } from "../hooks/useChatSession";
import styles from "../AIChatWidget.module.css";

export default function CitationList({
  citations,
  deduplicate,
}: {
  citations: Citation[];
  deduplicate: (citations: Citation[]) => Citation[];
}): JSX.Element | null {
  const unique = deduplicate(citations);
  if (unique.length === 0) return null;

  return (
    <div className={styles.citations}>
      <p className={styles.citationsTitle}>
        <Translate id="chatbot.sources">Sources</Translate>
      </p>
      <ul className={styles.citationsList}>
        {unique.map((citation) => (
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
              ({(citation.score * 100).toFixed(0)}%{" "}
              <Translate id="chatbot.match">match</Translate>)
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}
