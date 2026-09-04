const fs = require('fs');
const path = require('path');

const root = __dirname;
const outDir = path.join(root, 'regenerated_from_source');
const days = ['週一', '週二', '週三', '週四', '週五', '週六'];
const scriptureCounts = { 週一: 1, 週二: 1, 週三: 1, 週四: 2, 週五: 2, 週六: 1 };

function decodeEntities(value) {
  const named = { amp: '&', lt: '<', gt: '>', quot: '"', apos: "'", nbsp: ' ', hellip: '…', mdash: '—', ndash: '–', bull: '•' };
  return value
    .replace(/&#(x[0-9a-f]+|\d+);/gi, (_, code) => String.fromCodePoint(code[0].toLowerCase() === 'x' ? parseInt(code.slice(1), 16) : parseInt(code, 10)))
    .replace(/&([a-z]+);/gi, (match, name) => named[name.toLowerCase()] ?? match);
}

function textOf(fragment) {
  return decodeEntities(fragment.replace(/<[^>]*>/g, ''))
    .replace(/[\u200b\ufeff]/g, '')
    .replace(/\s+/g, ' ')
    .trim();
}

function esc(value) {
  return value.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

const cards = [];
for (const day of days) {
  const file = path.join(outDir, `${day}.html`);
  let html = fs.readFileSync(file, 'utf8');
  const paragraphs = [...html.matchAll(/<p\b[^>]*>([\s\S]*?)<\/p>/gi)].map(m => textOf(m[1]));
  const headingAt = paragraphs.findIndex(p => p === '晨興餧養');
  if (headingAt < 0) throw new Error(`${day} 找不到「晨興餧養」。`);
  const scriptures = paragraphs.slice(headingAt + 1, headingAt + 1 + scriptureCounts[day]);
  if (scriptures.length !== scriptureCounts[day] || scriptures.some(x => !x)) {
    throw new Error(`${day} 的引經數量不完整。`);
  }
  cards.push({ day, scriptures });

  if (!html.includes('id="morning-nourishment"')) {
    html = html.replace(/<p>晨興餧養<\/p>/, '<h3 id="morning-nourishment">晨興餧養</h3>');
    fs.writeFileSync(file, html, 'utf8');
  }
}

const cardHtml = cards.map(({ day, scriptures }) => `
    <article class="scripture-card">
      <div class="card-heading">
        <h2>${day}</h2>
        <a class="day-link" href="${day}.html#morning-nourishment" aria-label="前往${day}晨興餧養">前往${day}信息 →</a>
      </div>
      <div class="verses">
${scriptures.map(s => `        <p>${esc(s)}</p>`).join('\n')}
      </div>
    </article>`).join('\n');

const document = `<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>第六週・晨興餧養引經｜晨興聖言</title>
  <style>
    :root { color-scheme: light dark; font-family: "Noto Sans TC", "Microsoft JhengHei", sans-serif; }
    * { box-sizing: border-box; }
    body { margin: 0; color: #302820; background: #f4efe7; }
    header { position: sticky; top: 0; z-index: 2; padding: .85rem 1rem; background: rgba(255,253,249,.96); border-bottom: 1px solid #d8cfc2; backdrop-filter: blur(8px); }
    header a { color: inherit; }
    main { width: min(1040px, 100%); margin: 0 auto; padding: 2rem 1rem 4rem; }
    .page-title { margin: 0 0 .4rem; font-size: clamp(1.6rem, 4vw, 2.25rem); }
    .intro { margin: 0 0 1.5rem; color: #6f6255; }
    .card-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 1rem; }
    .scripture-card { padding: 1.25rem; background: #fffdf9; border: 1px solid #ded4c7; border-radius: 16px; box-shadow: 0 5px 18px rgba(65,45,25,.07); }
    .card-heading { display: flex; align-items: center; justify-content: space-between; gap: 1rem; padding-bottom: .75rem; border-bottom: 1px solid #e8e0d6; }
    .card-heading h2 { margin: 0; font-size: 1.25rem; }
    .day-link { color: #80572c; font-weight: 700; text-decoration: none; white-space: nowrap; }
    .day-link:hover, .day-link:focus-visible { text-decoration: underline; }
    .verses p { margin: 1rem 0 0; font-size: 1.1rem; line-height: 1.85; }
    @media (max-width: 700px) { .card-grid { grid-template-columns: 1fr; } }
    @media (prefers-color-scheme: dark) {
      body { color: #eee7df; background: #181614; }
      header, .scripture-card { background: #24211e; border-color: #514940; }
      .intro { color: #bdb2a7; }
      .card-heading { border-color: #514940; }
      .day-link { color: #e8bc86; }
    }
  </style>
</head>
<body>
  <header><a href="index.html">首頁</a>　<a href="綱目.html">綱目</a>　<strong>經文</strong></header>
  <main>
    <h1 class="page-title">第六週・晨興餧養引經</h1>
    <p class="intro">神長子基督的眾弟兄</p>
    <section class="card-grid" aria-label="週一至週六晨興餧養引經">
${cardHtml}
    </section>
  </main>
</body>
</html>
`;

fs.writeFileSync(path.join(outDir, '經文.html'), document, 'utf8');
fs.writeFileSync(path.join(outDir, 'scripture-extraction-check.json'), JSON.stringify(cards, null, 2), 'utf8');
console.log(JSON.stringify(cards, null, 2));
