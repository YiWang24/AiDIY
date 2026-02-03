import crypto from 'node:crypto';
import fs from 'node:fs/promises';
import path from 'node:path';

import fg from 'fast-glob';
import matter from 'gray-matter';
import { unified } from 'unified';
import remarkParse from 'remark-parse';
import remarkMdx from 'remark-mdx';
import remarkStringify from 'remark-stringify';
import { toString as mdastToString } from 'mdast-util-to-string';
import { visit } from 'unist-util-visit';

const DEFAULT_EXCLUDES = ['docs/plans/**', 'build/**', 'node_modules/**'];
const DEFAULT_INCLUDES = ['.mdx', '.md'];

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
    defaultVersion = 'latest',
    noiseFilter = false,
    repoRoot = process.cwd(),
  } = options || {};

  if (!roots || roots.length === 0) {
    throw new Error('collectRecords requires at least one root');
  }

  const rootConfigs = roots.map((root) => {
    const dir = path.resolve(repoRoot, root.dir);
    return {
      dir,
      dirRel: normalizePath(path.relative(repoRoot, dir)),
      prefix: root.prefix,
    };
  });

  const patterns = rootConfigs.flatMap((root) =>
    include.map((ext) => `${root.dirRel}/**/*${ext}`)
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
      relPath: normalizePath(path.relative(repoRoot, filePath)),
    }))
    .sort((a, b) => a.relPath.localeCompare(b.relPath));

  const records = [];

  for (const { filePath, relPath } of sortedFiles) {
    const rootConfig = findRootConfig(rootConfigs, filePath);
    const sourcePrefix = rootConfig ? rootConfig.prefix : guessPrefix(relPath);
    const idFallback = rootConfig
      ? normalizePath(path.relative(rootConfig.dir, filePath))
      : relPath;

    const raw = await fs.readFile(filePath, 'utf8');

    let frontmatter = {};
    let body = raw;
    try {
      const parsed = matter(raw);
      frontmatter = parsed.data || {};
      body = parsed.content || '';
    } catch (error) {
      frontmatter = { parseError: error?.message || String(error) };
      body = raw;
    }

    let cleaned = '';
    let cleanedTree = null;
    try {
      const cleanedResult = cleanContent(body, { noiseFilter });
      cleaned = cleanedResult.content;
      cleanedTree = cleanedResult.tree;
    } catch (error) {
      cleaned = '';
      frontmatter = {
        ...frontmatter,
        parseError: error?.message || String(error),
      };
    }

    const title =
      normalizeTitle(frontmatter.title) ||
      (cleanedTree ? extractTitleFromTree(cleanedTree) : null) ||
      filenameTitle(relPath);

    const version = frontmatter.version || defaultVersion;

    const id = buildDocId({ frontmatter, fallbackPath: idFallback, prefix: sourcePrefix });

    const record = {
      id,
      path: relPath,
      title,
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

    record.checksum = sha256(stableStringify(checksumPayload));

    records.push(record);
  }

  return records;
}

export function cleanContentToMarkdown(content, options = {}) {
  return cleanContent(content, options).content;
}

export function stableStringify(value) {
  return JSON.stringify(sortValue(value));
}

export async function writeJsonl(records, outputPath) {
  const dir = path.dirname(outputPath);
  await fs.mkdir(dir, { recursive: true });

  const lines = records.map((record) => stableStringify(record));
  await fs.writeFile(outputPath, `${lines.join('\n')}\n`, 'utf8');
}

function cleanContent(content, { noiseFilter }) {
  const processor = unified().use(remarkParse).use(remarkMdx);
  const tree = processor.parse(content);
  const cleanedTree = transformTree(tree, { noiseFilter });
  const markdown = unified()
    .use(remarkStringify, {
      bullet: '-',
      fence: '```',
      listItemIndent: 'one',
    })
    .stringify(cleanedTree)
    .trim();

  return {
    content: markdown,
    tree: cleanedTree,
  };
}

function transformTree(tree, { noiseFilter }) {
  const children = transformNodes(tree.children || []);
  const filtered = noiseFilter ? filterNoise(children) : children;
  return { ...tree, children: filtered };
}

function transformNodes(nodes) {
  return nodes.flatMap((node) => transformNode(node));
}

function transformNode(node) {
  if (isRuntimeNode(node)) {
    return [];
  }

  if (isMdxJsxNode(node)) {
    const children = transformNodes(node.children || []);
    if (isTabItem(node)) {
      const label = getAttributeValue(node, 'label') || getAttributeValue(node, 'value');
      const heading = label ? [createHeading(label, 4)] : [];
      return [...heading, ...children];
    }
    return children;
  }

  if (node.children) {
    return [{ ...node, children: transformNodes(node.children) }];
  }

  return [node];
}

function isRuntimeNode(node) {
  return (
    node.type === 'mdxjsEsm' ||
    node.type === 'mdxTextExpression' ||
    node.type === 'mdxFlowExpression' ||
    node.type === 'import' ||
    node.type === 'export'
  );
}

function isMdxJsxNode(node) {
  return node.type === 'mdxJsxFlowElement' || node.type === 'mdxJsxTextElement';
}

function isTabItem(node) {
  return node.name === 'TabItem';
}

function getAttributeValue(node, name) {
  if (!node.attributes) return null;
  const attr = node.attributes.find(
    (entry) => entry.type === 'mdxJsxAttribute' && entry.name === name
  );
  if (!attr) return null;
  if (typeof attr.value === 'string') return attr.value.trim();
  return null;
}

function createHeading(text, depth) {
  return {
    type: 'heading',
    depth,
    children: [{ type: 'text', value: text }],
  };
}

function filterNoise(nodes) {
  return nodes.filter((node) => !isNoiseParagraph(node));
}

function isNoiseParagraph(node) {
  if (node.type !== 'paragraph') return false;
  const text = mdastToString(node).trim();
  if (!text) return false;

  const patterns = [
    /^\*\*Previous\*\*:/i,
    /^\*\*Next\*\*:/i,
    /^Previous:/i,
    /^Next:/i,
    /^Next Chapter/i,
  ];

  return patterns.some((pattern) => pattern.test(text));
}

function extractTitleFromTree(tree) {
  let title = null;
  visit(tree, 'heading', (node) => {
    if (title) return;
    if (node.depth === 1) {
      const text = mdastToString(node).trim();
      if (text) {
        title = text;
      }
    }
  });
  return title;
}

function normalizeTitle(value) {
  if (!value) return null;
  const text = String(value).trim();
  return text.length ? text : null;
}

function filenameTitle(relPath) {
  const base = path.basename(relPath, path.extname(relPath));
  return base || relPath;
}

function buildDocId({ frontmatter, fallbackPath, prefix }) {
  const slug = normalizeIdValue(frontmatter?.slug);
  const id = normalizeIdValue(frontmatter?.id);
  const fallback = normalizeIdValue(fallbackPath);
  const chosen = slug || id || fallback;
  return `${prefix}:${chosen}`;
}

function normalizeIdValue(value) {
  if (!value) return null;
  const text = String(value).trim();
  if (!text) return null;
  return text.replace(/^\/+/, '');
}

function findRootConfig(roots, filePath) {
  const normalized = path.resolve(filePath);
  let match = null;
  for (const root of roots) {
    const rootPath = path.resolve(root.dir);
    if (normalized.startsWith(rootPath)) {
      if (!match || rootPath.length > path.resolve(match.dir).length) {
        match = root;
      }
    }
  }
  return match;
}

function guessPrefix(relPath) {
  if (relPath.startsWith('docs/')) return 'docs';
  if (relPath.startsWith('blog/')) return 'blog';
  return 'docs';
}

function sha256(value) {
  return crypto.createHash('sha256').update(value).digest('hex');
}

function sortValue(value) {
  if (Array.isArray(value)) {
    return value.map((entry) => sortValue(entry));
  }
  if (value && typeof value === 'object') {
    const sorted = {};
    for (const key of Object.keys(value).sort()) {
      sorted[key] = sortValue(value[key]);
    }
    return sorted;
  }
  return value;
}

function normalizePath(value) {
  return value.split(path.sep).join('/');
}
