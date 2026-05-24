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
// Sources expand inline on click — no nested <details>.
function KbSearchToolRender({
  args,
  result,
  status,
}: KbSearchToolRenderProps): JSX.Element {
  const [sourcesOpen, setSourcesOpen] = useState(false);
  const running = status?.type === "running";
  const chunks = dedupeChunks(result?.chunks ?? []);

  return (
    <div className="my-0.5 text-xs">
      <div className="inline-flex items-center gap-1.5 rounded-full border border-neutral-200 bg-white px-2.5 py-1 text-neutral-600 dark:border-neutral-800 dark:bg-neutral-900 dark:text-neutral-300">
        {running ? (
          <LoaderIcon className="size-3.5 animate-spin text-indigo-500" />
        ) : (
          <CheckCircle2Icon className="size-3.5 text-emerald-500" />
        )}
        <span className="font-medium">{running ? "Searching" : "Searched"}</span>
        {args?.query && (
          <span className="max-w-[180px] truncate text-neutral-500 dark:text-neutral-400">
            &middot; &ldquo;{args.query}&rdquo;
          </span>
        )}
        {!running && chunks.length > 0 && (
          <button
            type="button"
            onClick={() => setSourcesOpen((prev) => !prev)}
            className="ml-0.5 flex items-center gap-0.5 text-indigo-500 hover:text-indigo-700 dark:text-indigo-400 dark:hover:text-indigo-300"
          >
            <ChevronRightIcon
              className={`size-3 transition-transform duration-150 ${sourcesOpen ? "rotate-90" : ""}`}
            />
            {chunks.length} {chunks.length === 1 ? "source" : "sources"}
          </button>
        )}
      </div>

      {sourcesOpen && chunks.length > 0 && (
        <ul className="mt-1 space-y-0.5 pl-2">
          {chunks.map((c) => (
            <li key={c.chunk_id}>
              <a
                href={toDocLink(c.path)}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-1.5 rounded px-1.5 py-1 text-neutral-600 hover:bg-neutral-50 hover:text-neutral-900 dark:text-neutral-400 dark:hover:bg-neutral-800 dark:hover:text-neutral-100"
              >
                <ExternalLinkIcon className="size-3 shrink-0 text-neutral-400" />
                <span className="truncate">{c.title ?? c.path}</span>
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
