const fs = require('fs');
const path = require('path');

const root = __dirname;
const sourcePath = path.join(root, 'source_snapshot.html');
const outDir = path.join(root, 'regenerated_from_source');
const sourceHtml = fs.readFileSync(sourcePath, 'utf8');

function decodeEntities(value) {
  const named = {
    amp: '&', lt: '<', gt: '>', quot: '"', apos: "'", nbsp: ' ',
    hellip: '…', mdash: '—', ndash: '–', bull: '•', middot: '·'
  };
  return value
    .replace(/&#(x[0-9a-f]+|\d+);/gi, (_, code) =>
      String.fromCodePoint(code[0].toLowerCase() === 'x' ? parseInt(code.slice(1), 16) : parseInt(code, 10)))
    .replace(/&([a-z]+);/gi, (match, name) => named[name.toLowerCase()] ?? match);
}

function visibleText(fragment) {
  return decodeEntities(fragment)
    .replace(/<br\s*\/?>/gi, '\n')
    .replace(/<[^>]*>/g, '')
    .replace(/[\u200b\ufeff]/g, '')
    .replace(/\u00a0/g, ' ')
    .replace(/[ \t]+/g, ' ')
    .replace(/\s*\n\s*/g, '\n')
    .trim();
}

function esc(value) {
  return value.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

const start = sourceHtml.indexOf('2026年六月-半年度訓練');
const endMarker = '李常受文集一九九三年第一冊，一五一至一五二頁。';
const end = sourceHtml.indexOf(endMarker, start);
if (start < 0 || end < 0) throw new Error('找不到第六週內容範圍。');
const slice = sourceHtml.slice(Math.max(0, start - 2000), end + endMarker.length + 500);
const blocks = [];
for (const match of slice.matchAll(/<(h[1-6]|p)\b[^>]*>([\s\S]*?)<\/\1>/gi)) {
  const text = visibleText(match[2]);
  if (text) blocks.push(text);
}

const titleIndex = blocks.findIndex(x => x.includes('2026年六月-半年度訓練'));
if (titleIndex < 0) throw new Error('找不到第六週標題區塊。');
const content = blocks.slice(titleIndex);
const dayNames = ['週一', '週二', '週三', '週四', '週五', '週六'];
const dayStart = name => content.findIndex(x => new RegExp(`第六週\\s*[•·]\\s*${name}`).test(x));
const firstDay = dayStart('週一');
if (firstDay < 0) throw new Error('找不到每日內容起點。');

const outline = content.slice(0, firstDay);
const days = {};
for (let i = 0; i < dayNames.length; i++) {
  const from = dayStart(dayNames[i]);
  const to = i + 1 < dayNames.length ? dayStart(dayNames[i + 1]) : content.length;
  days[dayNames[i]] = content.slice(from, to);
}

const nav = ['index.html', '綱目.html', ...dayNames.map(x => `${x}.html`)]
  .map((href, i) => `<a href="${href}">${i === 0 ? '首頁' : i === 1 ? '綱目' : dayNames[i - 2]}</a>`)
  .join('');

function render(title, pageBlocks) {
  return `<!doctype html>\n<html lang="zh-Hant">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1">\n<title>${esc(title)}</title>\n<link rel="stylesheet" href="styles.css">\n</head>\n<body>\n<header><h1>晨興聖言</h1><nav>${nav}</nav></header>\n<main>${pageBlocks.map((x, i) => i === 0 ? `<h2>${esc(x)}</h2>` : `<p>${esc(x)}</p>`).join('\n')}</main>\n</body>\n</html>\n`;
}

fs.mkdirSync(outDir, { recursive: true });
fs.writeFileSync(path.join(outDir, 'index.html'), render('第六週・首頁', outline.slice(0, 3)), 'utf8');
fs.writeFileSync(path.join(outDir, '綱目.html'), render('第六週・綱目', outline), 'utf8');
for (const name of dayNames) {
  fs.writeFileSync(path.join(outDir, `${name}.html`), render(`第六週・${name}`, days[name]), 'utf8');
}
fs.writeFileSync(path.join(outDir, 'styles.css'), `:root{font-family:"Noto Sans TC",sans-serif;color:#302a25;background:#f8f5ef}body{margin:0}header{position:sticky;top:0;background:#fff;border-bottom:1px solid #ddd;padding:1rem}h1{margin:0 0 .7rem}nav{display:flex;gap:.8rem;flex-wrap:wrap}main{max-width:850px;margin:auto;padding:2rem 1rem;line-height:1.85;font-size:20px}p{white-space:pre-wrap}@media(prefers-color-scheme:dark){:root{color:#eee;background:#181818}header{background:#222;border-color:#444}a{color:#9bc5ff}}\n`, 'utf8');

function normalizedFile(file) {
  return visibleText(fs.readFileSync(file, 'utf8')).replace(/\s+/g, '');
}
function normalizedBlock(text) {
  return text.replace(/^--(?=參讀)/, '').replace(/\s+/g, '');
}

const comparisons = [];
const targets = [['綱目.html', outline], ...dayNames.map(name => [`${name}.html`, days[name]])];
for (const [file, sourceBlocks] of targets) {
  const existing = normalizedFile(path.join(root, file));
  const missing = sourceBlocks.filter(x => !existing.includes(normalizedBlock(x)));
  comparisons.push({ file, sourceBlockCount: sourceBlocks.length, matchedBlocks: sourceBlocks.length - missing.length, missing });
}

const report = {
  generatedAt: new Date().toISOString(),
  sourceUrl: 'https://churchintamsui.wixsite.com/index/morning-revival',
  sourceSnapshot: path.basename(sourcePath),
  extractedBlockCount: content.length,
  note: '逐段比較會忽略 HTML 標籤及空白；檔案本身因模板不同，不預期位元組完全相同。',
  comparisons
};
fs.writeFileSync(path.join(outDir, 'comparison-report.json'), JSON.stringify(report, null, 2), 'utf8');
console.log(JSON.stringify(report, null, 2));

