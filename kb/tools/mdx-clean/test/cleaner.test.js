import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';

import {
  cleanContentToMarkdown,
  collectRecords,
  stableStringify,
} from '../src/cleaner.js';

async function withTempDir(fn) {
  const dir = await fs.mkdtemp(path.join(os.tmpdir(), 'mdx-clean-'));
  try {
    await fn(dir);
  } finally {
    await fs.rm(dir, { recursive: true, force: true });
  }
}

test('removes mdx runtime nodes and unwraps components', () => {
  const mdx = [
    "import Tabs from '@theme/Tabs';",
    'export const foo = 1;',
    '',
    '# Title',
    '',
    '<Tabs>',
    '  <TabItem label="Variant A">',
    '    Hello **world**',
    '  </TabItem>',
    '</Tabs>',
    '',
    '<Badge>Beta</Badge>',
    '',
    '{1 + 2}',
  ].join('\n');

  const cleaned = cleanContentToMarkdown(mdx, { noiseFilter: false });

  assert.match(cleaned, /# Title/);
  assert.match(cleaned, /#### Variant A/);
  assert.match(cleaned, /Hello \*\*world\*\*/);
  assert.match(cleaned, /Beta/);
  assert.doesNotMatch(cleaned, /import Tabs/);
  assert.doesNotMatch(cleaned, /<Tabs>/);
  assert.doesNotMatch(cleaned, /<Badge>/);
  assert.doesNotMatch(cleaned, /\{1 \+ 2\}/);
});

test('deterministic records and id prefers slug over id over path', async () => {
  await withTempDir(async (dir) => {
    const docsDir = path.join(dir, 'docs');
    await fs.mkdir(docsDir, { recursive: true });
    const filePath = path.join(docsDir, 'example.mdx');

    const content = [
      '---',
      'title: Sample',
      'slug: sample-slug',
      'id: sample-id',
      '---',
      '',
      '# Sample',
      '',
      'Body text',
    ].join('\n');

    await fs.writeFile(filePath, content, 'utf8');

    const options = {
      roots: [{ dir: docsDir, prefix: 'docs' }],
      include: ['.mdx'],
      exclude: [],
      defaultVersion: 'latest',
      noiseFilter: false,
      repoRoot: dir,
    };

    const recordsA = await collectRecords(options);
    const recordsB = await collectRecords(options);

    assert.equal(recordsA.length, 1);
    assert.equal(recordsA[0].id, 'docs:sample-slug');
    assert.equal(stableStringify(recordsA[0]), stableStringify(recordsB[0]));
  });
});

test('invalid mdx produces empty content and parse error metadata', async () => {
  await withTempDir(async (dir) => {
    const docsDir = path.join(dir, 'docs');
    await fs.mkdir(docsDir, { recursive: true });
    const filePath = path.join(docsDir, 'broken.mdx');

    await fs.writeFile(filePath, '---\ntitle: Broken\n---\n\n<BadComponent {', 'utf8');

    const records = await collectRecords({
      roots: [{ dir: docsDir, prefix: 'docs' }],
      include: ['.mdx'],
      exclude: [],
      defaultVersion: 'latest',
      noiseFilter: false,
      repoRoot: dir,
    });

    assert.equal(records.length, 1);
    assert.equal(records[0].content, '');
    assert.ok(records[0].frontmatter.parseError);
  });
});
