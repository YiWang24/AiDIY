import crypto from "node:crypto";

export interface Chunk {
  chunk_id: string;
  chunk_index: number;
  heading_path: string[];
  content: string;
}

interface SplitOptions {
  maxChars?: number;
  overlapChars?: number;
}

const DEFAULT_MAX = 1500;
const DEFAULT_OVERLAP = 200;

export function chunkMarkdown(
  docId: string,
  markdown: string,
  opts: SplitOptions = {},
): Chunk[] {
  const maxChars = opts.maxChars ?? DEFAULT_MAX;
  const overlap = opts.overlapChars ?? DEFAULT_OVERLAP;

  const lines = markdown.split(/\r?\n/);
  const sections: { headingPath: string[]; body: string }[] = [];
  const stack: string[] = [];
  let buffer: string[] = [];

  const flush = () => {
    const body = buffer.join("\n").trim();
    if (body) sections.push({ headingPath: [...stack], body });
    buffer = [];
  };

  for (const line of lines) {
    const m = /^(#{1,3})\s+(.+?)\s*$/.exec(line);
    if (m) {
      flush();
      const depth = m[1].length;
      const title = m[2].trim();
      stack.length = depth - 1;
      stack[depth - 1] = title;
      continue;
    }
    buffer.push(line);
  }
  flush();

  const chunks: Chunk[] = [];
  let idx = 0;
  for (const section of sections) {
    const pieces = splitBySize(section.body, maxChars, overlap);
    for (const piece of pieces) {
      const content = piece.trim();
      if (!content) continue;
      chunks.push({
        chunk_id: chunkId(docId, idx, content),
        chunk_index: idx,
        heading_path: section.headingPath,
        content,
      });
      idx += 1;
    }
  }
  return chunks;
}

function splitBySize(text: string, maxChars: number, overlap: number): string[] {
  if (text.length <= maxChars) return [text];

  const out: string[] = [];
  const paragraphs = text.split(/\n\n+/);
  let current = "";

  for (const p of paragraphs) {
    if ((current + "\n\n" + p).length <= maxChars) {
      current = current ? current + "\n\n" + p : p;
      continue;
    }
    if (current) {
      out.push(current);
      const tail = current.slice(Math.max(0, current.length - overlap));
      current = tail + (tail ? "\n\n" : "") + p;
    } else {
      for (let i = 0; i < p.length; i += maxChars - overlap) {
        out.push(p.slice(i, i + maxChars));
      }
      current = "";
    }
  }
  if (current) out.push(current);
  return out;
}

function chunkId(docId: string, index: number, content: string): string {
  const h = crypto.createHash("sha256");
  h.update(`${docId}|${index}|${content}`);
  return h.digest("hex").slice(0, 32);
}
