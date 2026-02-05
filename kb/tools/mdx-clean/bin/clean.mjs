#!/usr/bin/env node
import { cleanDocuments } from '../src/cleaner.js';

const args = parseArgs(process.argv.slice(2));
const repoRoot = process.cwd();

const rootsArg = args.roots || 'docs,blog';
const includeArg = args.include || '.mdx,.md';
const excludeArg = args.exclude || 'docs/plans/**,build/**,node_modules/**,kb/**';
const output = args.output || 'kb/data/cleaned/docs.jsonl';
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

console.error(`🧹 Cleaning MDX documents...`);
console.error(`📂 Roots: ${roots.map(r => r.dir).join(', ')}`);
console.error(`📤 Output: ${output}`);
console.error(``);

const records = await cleanDocuments({
  roots,
  include,
  exclude,
  output,
  defaultVersion,
  noiseFilter,
  repoRoot,
});

// Print summary
const errorCount = records.filter(r => r.frontmatter.parseError).length;
const successCount = records.length - errorCount;

console.error(``);
console.error(`✅ Done!`);
console.error(`📊 Total records: ${records.length}`);
console.error(`✓ Success: ${successCount}`);
if (errorCount > 0) {
  console.error(`✗ Errors: ${errorCount}`);
}
console.error(`💾 Saved to: ${output}`);

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
