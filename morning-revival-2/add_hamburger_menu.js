const fs = require('fs');
const path = require('path');
const dir = path.join(__dirname, 'regenerated_from_source');
const files = ['index.html', '經文.html', '週一.html', '週二.html', '週三.html', '週四.html', '週五.html', '週六.html'];

for (const name of files) {
  const file = path.join(dir, name);
  let html = fs.readFileSync(file, 'utf8');
  if (!html.includes('href="styles.css"')) {
    html = html.replace('</head>', '  <link rel="stylesheet" href="styles.css">\n</head>');
  }
  html = html.replace('<nav>', '<nav id="site-nav" aria-label="主要導覽">');
  if (!html.includes('id="menu-btn"')) {
    html = html.replace(/<header>/, `<header>
    <button id="menu-btn" class="menu-btn" type="button" aria-label="開啟導覽選單" aria-controls="site-nav" aria-expanded="false">
      <span></span><span></span><span></span>
    </button>`);
  }
  if (!html.includes('class="nav-overlay"')) {
    html = html.replace('</header>', '</header><button class="nav-overlay" type="button" aria-label="關閉導覽選單" tabindex="-1"></button>');
  }
  fs.writeFileSync(file, html, 'utf8');
}
console.log(`Hamburger menu added to ${files.length} pages.`);
