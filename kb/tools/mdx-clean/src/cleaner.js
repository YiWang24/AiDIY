import crypto from "node:crypto";
import fs from "node:fs/promises";
import path from "node:path";

import fg from "fast-glob";
import matter from "gray-matter";
import { unified } from "unified";
import remarkParse from "remark-parse";
import remarkMdx from "remark-mdx";
import remarkStringify from "remark-stringify";
import { toString as mdastToString } from "mdast-util-to-string";
import { visit } from "unist-util-visit";

const DEFAULT_EXCLUDES = ["docs/plans/**", "build/**", "node_modules/**"];
const DEFAULT_INCLUDES = [".mdx", ".md"];

// Internal: MDX AST transformation logic
const noisePatterns = [
  /^\*\*Previous\*\*:/i,
  /^\*\*Next\*\*:/i,
  /^Previous:/i,
  /^Next:/i,
  /^Next Chapter/i,
];

const transformMdxTree = (tree, noiseFilter) => {
  const transformNode = (node) => {
    const runtimeTypes = [
      "mdxjsEsm",
      "mdxTextExpression",
      "mdxFlowExpression",
      "import",
      "export",
    ];
    if (runtimeTypes.includes(node.type)) return [];

    const isJsxElement =
      node.type === "mdxJsxFlowElement" || node.type === "mdxJsxTextElement";
    if (isJsxElement) {
      const children = (node.children || []).flatMap(transformNode);
      if (node.name === "TabItem") {
        const getAttr = (name) => {
          if (!node.attributes) return null;
          const attr = node.attributes.find(
            (e) => e.type === "mdxJsxAttribute" && e.name === name,
          );
          return attr && typeof attr.value === "string"
            ? attr.value.trim()
            : null;
        };
        const label = getAttr("label") || getAttr("value");
        const heading = label
          ? [
              {
                type: "heading",
                depth: 4,
                children: [{ type: "text", value: label }],
              },
            ]
          : [];
        return [...heading, ...children];
      }
      return children;
    }

    if (node.children) {
      return [{ ...node, children: node.children.flatMap(transformNode) }];
    }
    return [node];
  };

  let children = (tree.children || []).flatMap(transformNode);
  if (noiseFilter) {
    children = children.filter((node) => {
      if (node.type !== "paragraph") return true;
      const text = mdastToString(node).trim();
      if (!text) return true;
      return !noisePatterns.some((pattern) => pattern.test(text));
    });
  }
  return { ...tree, children };
};

export async function cleanDocuments(options) {
  const records = await collectRecords(options);
  if (options?.output) {
    await writeJsonl(records, options.output);
  }
  return records;
}

export async function collectRecords(options) {
  const {
    roots,
    include = DEFAULT_INCLUDES,
    exclude = DEFAULT_EXCLUDES,
    defaultVersion = "latest",
    noiseFilter = false,
    repoRoot = process.cwd(),
  } = options || {};

  if (!roots || roots.length === 0) {
    throw new Error("collectRecords requires at least one root");
  }

  const rootConfigs = roots.map((root) => {
    const dir = path.resolve(repoRoot, root.dir);
    return {
      dir,
      dirRel: path.relative(repoRoot, dir).split(path.sep).join("/"),
      prefix: root.prefix,
    };
  });

  const patterns = rootConfigs.flatMap((root) =>
    include.map((ext) => `${root.dirRel}/**/*${ext}`),
  );

  const files = await fg(patterns, {
    cwd: repoRoot,
    absolute: true,
    onlyFiles: true,
    dot: false,
    ignore: exclude,
  });

  const sortedFiles = files
    .map((filePath) => ({
      filePath,
      relPath: path.relative(repoRoot, filePath).split(path.sep).join("/"),
    }))
    .sort((a, b) => a.relPath.localeCompare(b.relPath));

  const records = [];

  for (const { filePath, relPath } of sortedFiles) {
    // Find matching root config (longest path match wins)
    const normalizedPath = path.resolve(filePath);
    let rootConfig = null;
    for (const root of rootConfigs) {
      const rootPath = path.resolve(root.dir);
      if (normalizedPath.startsWith(rootPath)) {
        if (
          !rootConfig ||
          rootPath.length > path.resolve(rootConfig.dir).length
        ) {
          rootConfig = root;
        }
      }
    }

    const sourcePrefix = rootConfig
      ? rootConfig.prefix
      : relPath.startsWith("docs/")
        ? "docs"
        : relPath.startsWith("blog/")
          ? "blog"
          : "docs";
    const idFallback = rootConfig
      ? path.relative(rootConfig.dir, filePath).split(path.sep).join("/")
      : relPath;

    const raw = await fs.readFile(filePath, "utf8");

    let frontmatter = {};
    let body = raw;
    try {
      const parsed = matter(raw);
      frontmatter = parsed.data || {};
      body = parsed.content || "";
    } catch (error) {
      frontmatter = { parseError: error?.message || String(error) };
      body = raw;
    }

    let cleaned = "";
    let cleanedTree = null;
    try {
      const processor = unified().use(remarkParse).use(remarkMdx);
      const tree = processor.parse(body);
      const transformedTree = transformMdxTree(tree, noiseFilter);

      cleaned = unified()
        .use(remarkStringify, { bullet: "-", listItemIndent: "one" })
        .stringify(transformedTree)
        .trim();
      cleanedTree = transformedTree;
    } catch (error) {
      cleaned = "";
      frontmatter = {
        ...frontmatter,
        parseError: error?.message || String(error),
      };
    }

    // Title: frontmatter > first h1 > filename
    const title = frontmatter.title?.trim() || null;
    const treeTitle = cleanedTree
      ? (() => {
          let found = null;
          visit(cleanedTree, "heading", (node) => {
            if (!found && node.depth === 1) {
              const text = mdastToString(node).trim();
              if (text) found = text;
            }
          });
          return found;
        })()
      : null;
    const finalTitle =
      title ||
      treeTitle ||
      path.basename(relPath, path.extname(relPath)) ||
      relPath;

    const version = frontmatter.version || defaultVersion;

    // Build ID: priority slug > id > fallback path
    const normalizeId = (v) =>
      v ? String(v).trim().replace(/^\/+/, "") || null : null;
    const slug = normalizeId(frontmatter?.slug);
    const id = normalizeId(frontmatter?.id);
    const fallback = normalizeId(idFallback);
    const docId = `${sourcePrefix}:${slug || id || fallback}`;

    const record = {
      id: docId,
      path: relPath,
      title: finalTitle,
      version,
      frontmatter,
      content: cleaned,
    };

    const checksumPayload = {
      id: record.id,
      title: record.title,
      version: record.version,
      frontmatter: record.frontmatter,
      content: record.content,
    };

    // Stable stringify for checksum
    const sortValue = (v) => {
      if (Array.isArray(v)) return v.map(sortValue);
      if (v && typeof v === "object") {
        const sorted = {};
        for (const key of Object.keys(v).sort())
          sorted[key] = sortValue(v[key]);
        return sorted;
      }
      return v;
    };
    record.checksum = crypto
      .createHash("sha256")
      .update(JSON.stringify(sortValue(checksumPayload)))
      .digest("hex");

    records.push(record);
  }

  return records;
}

export function cleanContentToMarkdown(content, options = {}) {
  const { noiseFilter = false } = options;

  const processor = unified().use(remarkParse).use(remarkMdx);
  const tree = processor.parse(content);
  const transformedTree = transformMdxTree(tree, noiseFilter);

  return unified()
    .use(remarkStringify, { bullet: "-", listItemIndent: "one" })
    .stringify(transformedTree)
    .trim();
}

export function stableStringify(value) {
  const sortValue = (v) => {
    if (Array.isArray(v)) return v.map(sortValue);
    if (v && typeof v === "object") {
      const sorted = {};
      for (const key of Object.keys(v).sort()) sorted[key] = sortValue(v[key]);
      return sorted;
    }
    return v;
  };
  return JSON.stringify(sortValue(value));
}

export async function writeJsonl(records, outputPath) {
  const dir = path.dirname(outputPath);
  await fs.mkdir(dir, { recursive: true });

  const sortValue = (v) => {
    if (Array.isArray(v)) return v.map(sortValue);
    if (v && typeof v === "object") {
      const sorted = {};
      for (const key of Object.keys(v).sort()) sorted[key] = sortValue(v[key]);
      return sorted;
    }
    return v;
  };

  const lines = records.map((record) => JSON.stringify(sortValue(record)));
  await fs.writeFile(outputPath, `${lines.join("\n")}\n`, "utf8");
}
