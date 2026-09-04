const fs = require('fs');
const path = require('path');

const root = __dirname;
const dir = path.join(root, 'regenerated_from_source');
const days = ['週一', '週二', '週三', '週四', '週五', '週六'];
const scriptureCounts = { 週一: 1, 週二: 1, 週三: 1, 週四: 2, 週五: 2, 週六: 1 };

function addScriptureLink(nav) {
  if (nav.includes('href="經文.html"')) return nav;
  return nav.replace('<a href="綱目.html">綱目</a>', '<a href="綱目.html">綱目</a><a href="經文.html">經文</a>');
}

function addControls(header) {
  if (header.includes('font-size-btn')) return header;
  return header.replace('</header>', '<div class="header-controls"><button id="font-size-btn" type="button" aria-label="切換字體大小"><span aria-hidden="true">A</span><span id="font-size-label">20px</span></button></div></header>');
}

for (const day of days) {
  const file = path.join(dir, `${day}.html`);
  let html = fs.readFileSync(file, 'utf8');
  html = html.replace(/<header>[\s\S]*?<\/header>/, h => addControls(addScriptureLink(h)));
  html = html.replace('<main>', '<main class="daily-main"><article class="daily-article">');
  html = html.replace('</main>', '</article></main>');
  html = html.replace(`<h2>第六週 • ${day}</h2>`, `<h2 class="daily-title">第六週・${day}</h2>`);
  html = html.replace('<p>信息選讀</p>', '<h3 class="section-title">信息選讀</h3>');

  const marker = '<h3 id="morning-nourishment">晨興餧養</h3>';
  const markerAt = html.indexOf(marker);
  if (markerAt < 0) throw new Error(`${day} 找不到晨興餧養錨點。`);
  const afterMarker = markerAt + marker.length;
  const tail = html.slice(afterMarker);
  const paragraphPattern = /\s*<p>[\s\S]*?<\/p>/y;
  let cursor = 0;
  const verses = [];
  for (let i = 0; i < scriptureCounts[day]; i++) {
    paragraphPattern.lastIndex = cursor;
    const match = paragraphPattern.exec(tail);
    if (!match) throw new Error(`${day} 無法取得第 ${i + 1} 段引經。`);
    verses.push(match[0].trim());
    cursor = paragraphPattern.lastIndex;
  }
  const scriptureCard = `${marker}\n<section class="scripture-card" aria-label="${day}晨興餧養引經">\n${verses.join('\n')}\n</section>`;
  html = html.slice(0, markerAt) + scriptureCard + tail.slice(cursor);
  if (!html.includes('<script src="app.js"></script>')) {
    html = html.replace('</body>', '  <script src="app.js"></script>\n</body>');
  }
  fs.writeFileSync(file, html, 'utf8');
}

// Add the Scripture page to the home navigation and make the font control
// available from the home page as well.
const indexFile = path.join(dir, 'index.html');
let index = fs.readFileSync(indexFile, 'utf8');
index = index.replace(/<header>[\s\S]*?<\/header>/, h => addControls(addScriptureLink(h)));
if (!index.includes('<script src="app.js"></script>')) {
  index = index.replace('</body>', '  <script src="app.js"></script>\n</body>');
}
fs.writeFileSync(indexFile, index, 'utf8');

// Add the shared font control to the Scripture page without changing its cards.
const scriptureFile = path.join(dir, '經文.html');
let scripture = fs.readFileSync(scriptureFile, 'utf8');
scripture = scripture.replace(/<header>[\s\S]*?<\/header>/, addControls);
if (!scripture.includes('<script src="app.js"></script>')) {
  scripture = scripture.replace('</body>', '  <script src="app.js"></script>\n</body>');
}
fs.writeFileSync(scriptureFile, scripture, 'utf8');

console.log('Updated:', [...days.map(d => `${d}.html`), 'index.html', '經文.html'].join(', '));
