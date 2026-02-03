#!/usr/bin/env node
import path from 'node:path';
import { cleanDocuments } from '../src/cleaner.js';

const args = parseArgs(process.argv.slice(2));
const repoRoot = process.cwd();

const rootsArg = args.roots || 'docs,blog';
const includeArg = args.include || '.mdx,.md';
const excludeArg = args.exclude || 'docs/plans/**,build/**,node_modules/**';
const output = args.output || path.join('kb', 'data', 'cleaned', 'docs_blog.jsonl');
const defaultVersion = args.version || 'latest';
const noiseFilter = Boolean(args['noise-filter']);

const roots = rootsArg
  .split(',')
  .map((entry) => entry.trim())
  .filter(Boolean)
  .map((entry) => ({ dir: entry, prefix: entry }));

const include = includeArg
  .split(',')
  .map((entry) => entry.trim())
  .filter(Boolean)
  .map((ext) => (ext.startsWith('.') ? ext : `.${ext}`));

const exclude = excludeArg
  .split(',')
  .map((entry) => entry.trim())
  .filter(Boolean);

await cleanDocuments({
  roots,
  include,
  exclude,
  output,
  defaultVersion,
  noiseFilter,
  repoRoot,
});

function parseArgs(argv) {
  const result = {};
  for (let i = 0; i < argv.length; i += 1) {
    const token = argv[i];
    if (!token.startsWith('--')) {
      continue;
    }
    const key = token.slice(2);
    const next = argv[i + 1];
    if (!next || next.startsWith('--')) {
      result[key] = true;
    } else {
      result[key] = next;
      i += 1;
    }
  }
  return result;
}
