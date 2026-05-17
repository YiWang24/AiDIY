import React from "react";
import Translate from "@docusaurus/Translate";
import type { RetrievedChunk } from "../types";
import styles from "../AIChatWidget.module.css";

function deduplicate(chunks: RetrievedChunk[]): RetrievedChunk[] {
  const seen = new Set<string>();
  return chunks.filter((c) => {
    const key = `${c.doc_id}::${c.path}`;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

function toDocLink(rawPath: string): string {
  // rawPath looks like "docs/cs/algorithms/index.md" — normalize to a Docusaurus
  // route by stripping extension and any /index suffix.
  const noExt = rawPath.replace(/\.(mdx?|MDX?)$/i, "");
  const noIndex = noExt.replace(/\/index$/i, "");
  return "/" + noIndex.replace(/^\/+/, "");
}

interface Props {
  chunks: RetrievedChunk[];
}

export default function CitationList({ chunks }: Props): JSX.Element | null {
  const unique = deduplicate(chunks);
  if (unique.length === 0) return null;

  return (
    <div className={styles.citations}>
      <p className={styles.citationsTitle}>
        <Translate id="chatbot.sources">Sources</Translate>
      </p>
      <ul className={styles.citationsList}>
        {unique.map((c) => (
          <li key={c.chunk_id}>
            <a
              href={toDocLink(c.path)}
              target="_blank"
              rel="noopener noreferrer"
              className={styles.citationLink}
            >
              {c.title ?? c.path}
            </a>
            <span className={styles.citationScore}>
              ({(c.score * 100).toFixed(0)}%{" "}
              <Translate id="chatbot.match">match</Translate>)
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}
