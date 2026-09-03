const fs = require('fs');
const path = require('path');

const root = __dirname;
const sourceFile = path.join(root, 'source_snapshot.html');
const outputFile = path.join(root, 'regenerated_from_source', '綱目.html');
const source = fs.readFileSync(sourceFile, 'utf8');

const titleText = '2026年六月-半年度訓練';
const firstDailyText = '第六週 &bull; 週一';
const titleAt = source.indexOf(titleText);
const dailyAt = source.indexOf(firstDailyText, titleAt);

if (titleAt < 0 || dailyAt < 0) {
  throw new Error('無法在來源快照中定位第六週綱目的完整範圍。');
}

// Take the complete source elements: the section heading through the element
// immediately before the first daily-reading heading. Keeping the source
// fragment intact preserves its nested ul/ol/li hierarchy and inline text.
const fragmentStart = source.lastIndexOf('<h2', titleAt);
const fragmentEnd = source.lastIndexOf('<p', dailyAt);
if (fragmentStart < 0 || fragmentEnd <= fragmentStart) {
  throw new Error('來源綱目元素邊界不完整。');
}
const outlineFragment = source.slice(fragmentStart, fragmentEnd);

const document = `<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>第六週・綱目｜晨興聖言</title>
  <style>
    :root { color-scheme: light dark; font-family: "Noto Sans TC", "Microsoft JhengHei", sans-serif; }
    body { margin: 0; background: #f7f3ec; color: #302820; }
    header { position: sticky; top: 0; z-index: 2; padding: .8rem 1rem; background: #fffdf9; border-bottom: 1px solid #d8cfc2; }
    header a { color: inherit; }
    main { box-sizing: border-box; max-width: 920px; margin: 0 auto; padding: 1.5rem 1rem 4rem; font-size: 20px; line-height: 1.75; }
    h2 { line-height: 1.45; }
    p { margin: .65rem 0; }
    ul, ol { margin: .4rem 0 .75rem; padding-left: 1.7rem; }
    li { margin: .35rem 0; }
    @media (prefers-color-scheme: dark) {
      body { background: #181614; color: #eee7df; }
      header { background: #24211e; border-color: #514940; }
    }
  </style>
</head>
<body>
  <header><a href="index.html">首頁</a>　<strong>晨興聖言・第六週綱目</strong></header>
  <main id="source-outline">
${outlineFragment}
  </main>
</body>
</html>
`;

fs.mkdirSync(path.dirname(outputFile), { recursive: true });
fs.writeFileSync(outputFile, document, 'utf8');

function count(pattern, text) {
  return [...text.matchAll(pattern)].length;
}

const checks = {
  outputFile,
  fragmentCharacters: outlineFragment.length,
  paragraphs: count(/<p\b/gi, outlineFragment),
  unorderedLists: count(/<ul\b/gi, outlineFragment),
  orderedLists: count(/<ol\b/gi, outlineFragment),
  listItems: count(/<li\b/gi, outlineFragment),
  weekMarkers: count(/【週(?:&nbsp;|\s)*[^】]+】/g, outlineFragment),
  startsWithExpectedHeading: outlineFragment.includes(titleText),
  excludesDailyReading: !outlineFragment.includes(firstDailyText)
};
fs.writeFileSync(
  path.join(path.dirname(outputFile), 'outline-extraction-check.json'),
  JSON.stringify(checks, null, 2),
  'utf8'
);
console.log(JSON.stringify(checks, null, 2));
