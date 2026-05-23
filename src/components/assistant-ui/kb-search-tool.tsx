import {
  ChevronDownIcon,
  ExternalLinkIcon,
  LinkIcon,
  SearchCheckIcon,
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

// Renders the kb_search tool call:
// - while running: a small "Searching" pill with pulsing icon
// - after done: a collapsible "Used N sources" disclosure with doc links
export const KbSearchToolUI = makeAssistantToolUI<
  { query: string; top_k?: number },
  RetrievalToolOutput
>({
  toolName: "kb_search",
  render: ({ args, result, status }) => {
    const running = status?.type === "running";
    const chunks = dedupeChunks(result?.chunks ?? []);

    return (
      <div className="my-1 space-y-1.5 text-sm">
        <div className="inline-flex items-center gap-1.5 rounded-full border border-neutral-200 bg-white px-2.5 py-1 text-xs text-neutral-600 dark:border-neutral-800 dark:bg-neutral-900 dark:text-neutral-300">
          <SearchCheckIcon
            className={`size-3.5 ${running ? "animate-pulse text-indigo-500" : "text-emerald-500"}`}
          />
          <span className="font-medium">
            {running ? "Searching" : "Searched"}
          </span>
          {args?.query && (
            <span className="max-w-[180px] truncate text-neutral-500 dark:text-neutral-400">
              · &ldquo;{args.query}&rdquo;
            </span>
          )}
        </div>
        {chunks.length > 0 && (
          <details className="group rounded-lg border border-neutral-200 bg-white px-2 py-1.5 dark:border-neutral-800 dark:bg-neutral-900">
            <summary className="flex cursor-pointer list-none items-center gap-1.5 text-xs font-medium text-neutral-600 dark:text-neutral-300">
              <LinkIcon className="size-3.5" />
              Used {chunks.length}{" "}
              {chunks.length === 1 ? "source" : "sources"}
              <ChevronDownIcon className="ml-auto size-4 transition group-open:rotate-180" />
            </summary>
            <ul className="mt-1.5 space-y-0.5">
              {chunks.map((c) => (
                <li key={c.chunk_id}>
                  <a
                    href={toDocLink(c.path)}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-1.5 rounded px-1.5 py-1 text-xs text-neutral-600 hover:bg-neutral-50 hover:text-neutral-900 dark:text-neutral-400 dark:hover:bg-neutral-800 dark:hover:text-neutral-100"
                  >
                    <ExternalLinkIcon className="size-3 shrink-0 text-neutral-400" />
                    <span className="truncate">{c.title ?? c.path}</span>
                  </a>
                </li>
              ))}
            </ul>
          </details>
        )}
      </div>
    );
  },
});
