import { useState } from "react";
import {
  CheckCircle2Icon,
  ChevronRightIcon,
  ExternalLinkIcon,
  LoaderIcon,
} from "lucide-react";
import { makeAssistantToolUI } from "@assistant-ui/react";

import type { RetrievalToolOutput, RetrievedChunk } from "../AIChatWidget/types";

// docs/cs/algorithms/index.md → /docs/cs/algorithms
function toDocLink(rawPath: string): string {
  const noExt = rawPath.replace(/\.(mdx?|MDX?)$/i, "");
  const noIndex = noExt.replace(/\/index$/i, "");
  return "/" + noIndex.replace(/^\/+/, "");
}

function dedupeChunks(chunks: RetrievedChunk[]): RetrievedChunk[] {
  const seen = new Set<string>();
  return chunks.filter((c) => {
    const key = `${c.doc_id}::${c.path}`;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

interface KbSearchToolRenderProps {
  args?: { query: string; top_k?: number };
  result?: RetrievalToolOutput;
  status?: { type: string };
}

// Compact single-row pill:
//   [spinner] Searching · "query"
//   [check]   Searched  · "query"  ▸ N sources
function KbSearchToolRender({
  args,
  result,
  status,
}: KbSearchToolRenderProps): JSX.Element {
  const [sourcesOpen, setSourcesOpen] = useState(false);
  const running = status?.type === "running";
  const chunks = dedupeChunks(result?.chunks ?? []);

  return (
    <div style={{ margin: "4px 0" }}>
      <div className="aidiy-kb-pill">
        {running ? (
          <LoaderIcon size={13} className="aidiy-kb-pill-icon-running" />
        ) : (
          <CheckCircle2Icon size={13} className="aidiy-kb-pill-icon-done" />
        )}
        <span className="aidiy-kb-pill-label">
          {running ? "Searching" : "Searched"}
        </span>
        {args?.query && (
          <span className="aidiy-kb-pill-query">
            · &ldquo;{args.query}&rdquo;
          </span>
        )}
        {!running && chunks.length > 0 && (
          <button
            type="button"
            onClick={() => setSourcesOpen((prev) => !prev)}
            className="aidiy-kb-pill-toggle"
          >
            <ChevronRightIcon
              size={12}
              style={{
                transition: "transform 0.15s ease",
                transform: sourcesOpen ? "rotate(90deg)" : "rotate(0deg)",
              }}
            />
            {chunks.length} {chunks.length === 1 ? "source" : "sources"}
          </button>
        )}
      </div>

      {sourcesOpen && chunks.length > 0 && (
        <ul className="aidiy-kb-sources">
          {chunks.map((c) => (
            <li key={c.chunk_id}>
              <a
                href={toDocLink(c.path)}
                target="_blank"
                rel="noopener noreferrer"
                className="aidiy-kb-source"
              >
                <ExternalLinkIcon className="aidiy-kb-source-icon" />
                <span className="aidiy-kb-source-text">{c.title ?? c.path}</span>
              </a>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

// Renders the kb_search tool call using a named inner component so that
// React hooks (useState) can be used inside makeAssistantToolUI.
export const KbSearchToolUI = makeAssistantToolUI<
  { query: string; top_k?: number },
  RetrievalToolOutput
>({
  toolName: "kb_search",
  render: (props) => <KbSearchToolRender {...props} />,
});
