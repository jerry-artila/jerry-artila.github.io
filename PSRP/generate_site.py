import sys, os, json, re, html
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
from parse_pdf import THEMES_CONFIG, make_page_reader, parse_lesson, BASE_DIR

# 1. CSS template
css_content = """/* PSRP 適合年長者手機閱讀樣式 */
:root {
  --bg-color: #FBF9F5;
  --text-main: #1F2328;
  --title-color: #0F2A4A;
  --num-color: #8C2D19;
  --scripture-bg: #F4EFEB;
  --scripture-border: #CBBCAE;
  --scripture-ref: #5B3924;
  --scripture-text: #2D2A26;
  --header-bg: rgba(251, 249, 245, 0.96);
  --border-light: #E8E0D5;
  --btn-bg: #FFFFFF;
  --btn-border: #D8CEC2;
  --btn-text: #1F2328;
  --btn-active-bg: #EAE2D7;
  
  /* 預設：中 (標準舒適大字) */
  --font-x: 24px;
  --font-y: 20px;
  --font-z: 17px;
  --line-height: 1.75;
}

/* 大字檔位 */
body.font-lg {
  --font-x: 28px;
  --font-y: 23px;
  --font-z: 20px;
}

/* 特大字檔位 */
body.font-xl {
  --font-x: 32px;
  --font-y: 26px;
  --font-z: 23px;
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
  -webkit-tap-highlight-color: transparent;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, "PingFang TC", "Microsoft JhengHei", "Noto Sans TC", sans-serif;
  background-color: var(--bg-color);
  color: var(--text-main);
  line-height: var(--line-height);
  padding: 0 0 60px 0;
  -webkit-font-smoothing: antialiased;
}

/* 頂部固定導覽列 */
.top-nav {
  position: sticky;
  top: 0;
  z-index: 999;
  background-color: var(--header-bg);
  backdrop-filter: blur(8px);
  border-bottom: 1px solid var(--border-light);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  gap: 8px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.03);
}

.nav-left, .nav-right {
  display: flex;
  align-items: center;
  gap: 6px;
}

.nav-center {
  font-size: 16px;
  font-weight: 700;
  color: var(--title-color);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 140px;
}

.nav-btn {
  background: var(--btn-bg);
  border: 1px solid var(--btn-border);
  color: var(--btn-text);
  font-size: 15px;
  font-weight: 600;
  padding: 8px 14px;
  border-radius: 8px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 44px;
  min-width: 44px;
  text-decoration: none;
  box-shadow: 0 1px 2px rgba(0,0,0,0.04);
  transition: all 0.15s ease;
}

.nav-btn:active {
  background-color: var(--btn-active-bg);
  transform: scale(0.97);
}

/* 內容主要容器 */
.container {
  max-width: 720px;
  margin: 0 auto;
  padding: 16px 16px 32px 16px;
}

/* 篇題標題區：僅保留篇號與篇題 */
.lesson-header {
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 2px solid var(--num-color);
}

.lesson-title {
  font-size: calc(var(--font-x) * 1.15);
  line-height: 1.4;
  color: var(--title-color);
  font-weight: 800;
  word-break: break-word;
}

/* 綱目容器 */
.outline-list {
  display: flex;
  flex-direction: column;
}

/* 每一條綱目 (懸掛縮排) */
.outline-item {
  display: flex;
  align-items: flex-start;
  margin-top: 14px;
  word-break: break-word;
}

/* 編號樣式 */
.outline-item .num {
  flex-shrink: 0;
  font-weight: 700;
  color: var(--num-color);
  font-variant-numeric: tabular-nums;
  padding-top: 1px;
}

/* 內文主體 */
.outline-item .item-content {
  flex-grow: 1;
  min-width: 0;
}

.outline-item .text {
  font-size: var(--font-y);
  line-height: var(--line-height);
  color: var(--text-main);
}

/* 各級階層規格 */
/* 第一級：壹、貳、參 (字體 X，文字加大粗體，編號不縮小) */
.level-1 {
  margin-top: 30px;
  padding-top: 14px;
  border-top: 1px dashed var(--border-light);
  margin-left: 0;
}
.level-1:first-child {
  margin-top: 10px;
  border-top: none;
  padding-top: 0;
}
.level-1 .num {
  font-size: var(--font-x);
  font-weight: 800;
  margin-right: 10px;
  color: var(--title-color);
}
.level-1 .text {
  font-size: var(--font-x);
  font-weight: 700;
  color: var(--title-color);
}

/* 第二級：一、二、三 (內文 Y，編號縮小 0.95 Y) */
.level-2 {
  margin-left: 12px;
}
.level-2 .num {
  font-size: calc(var(--font-y) * 0.95);
  margin-right: 8px;
}

/* 第三級：1、2、3 (內文 Y，編號縮小 0.90 Y) */
.level-3 {
  margin-left: 24px;
}
.level-3 .num {
  font-size: calc(var(--font-y) * 0.90);
  margin-right: 8px;
}

/* 第四級：a、b、c (內文 Y，編號縮小 0.85 Y) */
.level-4 {
  margin-left: 36px;
}
.level-4 .num {
  font-size: calc(var(--font-y) * 0.85);
  margin-right: 8px;
}

/* 第五級：㈠、㈡、㈢ (內文 Y，編號縮小 0.80 Y) */
.level-5 {
  margin-left: 48px;
}
.level-5 .num {
  font-size: calc(var(--font-y) * 0.80);
  margin-right: 8px;
}

/* 個別項目引經控制按鈕 (緊跟在文字之後) */
.scripture-toggle-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 3px;
  vertical-align: middle;
  margin-left: 8px;
  margin-top: -2px;
  padding: 3px 10px;
  font-size: calc(var(--font-y) * 0.72);
  font-weight: 700;
  color: var(--num-color);
  background-color: #F2ECE4;
  border: 1px solid #D3C5B5;
  border-radius: 14px;
  cursor: pointer;
  min-height: 32px;
  user-select: none;
  touch-action: manipulation;
  transition: all 0.18s ease;
  box-shadow: 0 1px 2px rgba(0,0,0,0.03);
}

.scripture-toggle-btn:hover {
  background-color: #E8DEC3;
}

.scripture-toggle-btn:active {
  transform: scale(0.95);
}

.scripture-toggle-btn.expanded {
  background-color: var(--num-color);
  color: #FFFFFF;
  border-color: var(--num-color);
}

/* 引經 (經文) 區塊：字體比 Y 小一級，為 Z */
.scriptures {
  list-style: none;
  margin-top: 10px;
  margin-bottom: 6px;
  display: none; /* 預設收合 */
  flex-direction: column;
  gap: 8px;
  animation: fadeIn 0.2s ease-in-out;
}

.scriptures.expanded {
  display: flex; /* 點擊後展開 */
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-4px); }
  to { opacity: 1; transform: translateY(0); }
}

.scripture-item {
  background-color: var(--scripture-bg);
  border-left: 3px solid var(--scripture-border);
  border-radius: 6px;
  padding: 10px 14px;
  font-size: var(--font-z);
  line-height: 1.65;
  color: var(--scripture-text);
  box-shadow: 0 1px 2px rgba(0,0,0,0.02);
}

/* 無序 bullet 符號 */
.scripture-item .bullet {
  color: var(--num-color);
  font-weight: bold;
  margin-right: 6px;
  user-select: none;
}

/* 經文章節號加粗 */
.scripture-item .ref {
  font-weight: 700;
  color: var(--scripture-ref);
  margin-right: 6px;
  letter-spacing: 0.5px;
}

/* 底部導覽大卡片 */
.bottom-nav {
  margin-top: 40px;
  padding-top: 24px;
  border-top: 1px solid var(--border-light);
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.nav-page-btn {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #FFFFFF;
  border: 1px solid var(--btn-border);
  padding: 14px 16px;
  border-radius: 12px;
  text-decoration: none;
  color: var(--text-main);
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
  min-height: 54px;
  transition: all 0.15s ease;
}

.nav-page-btn:active {
  background: var(--btn-active-bg);
  transform: scale(0.98);
}

.nav-page-btn .label {
  font-size: 15px;
  font-weight: 600;
  color: #6C757D;
}

.nav-page-btn .page-title {
  font-size: 17px;
  font-weight: 700;
  color: var(--title-color);
  text-align: right;
  max-width: 70%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.nav-home-btn {
  text-align: center;
  justify-content: center;
  background: #FAF3E8;
  border-color: #D9C3A5;
  color: var(--title-color);
  font-size: 18px;
  font-weight: 700;
}

/* 主題目錄頁樣式 (Cards) */
.theme-header {
  text-align: center;
  margin: 20px 0 28px 0;
  padding-bottom: 20px;
  border-bottom: 2px solid var(--num-color);
}

.theme-sub {
  font-size: 17px;
  font-weight: 600;
  color: var(--num-color);
  margin-bottom: 6px;
}

.theme-title {
  font-size: 28px;
  font-weight: 800;
  color: var(--title-color);
  line-height: 1.35;
}

.lesson-card-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.lesson-card {
  display: flex;
  align-items: center;
  gap: 14px;
  background: #FFFFFF;
  border: 1px solid var(--btn-border);
  border-radius: 14px;
  padding: 16px 18px;
  text-decoration: none;
  color: var(--text-main);
  box-shadow: 0 2px 4px rgba(0,0,0,0.03);
  min-height: 64px;
  transition: all 0.15s ease;
}

.lesson-card:active {
  background-color: var(--btn-active-bg);
  transform: scale(0.98);
}

.lesson-badge {
  flex-shrink: 0;
  background: #EBF3FA;
  color: #1A5488;
  font-size: 16px;
  font-weight: 800;
  padding: 6px 12px;
  border-radius: 8px;
}

.lesson-card-title {
  font-size: 19px;
  font-weight: 700;
  color: var(--title-color);
  line-height: 1.45;
}
"""

# 2. JS template
js_content = """// PSRP 字體切換與個別項目引經展開/收合控制
(function() {
  const FONT_LEVELS = ['md', 'lg', 'xl']; // 中、大、特大
  const FONT_LABELS = {
    'md': '字體: 中',
    'lg': '字體: 大',
    'xl': '字體: 特'
  };

  function init() {
    // 1. 初始化字體大小
    const savedFont = localStorage.getItem('psrp_font_size') || 'md';
    applyFont(savedFont);

    // 2. 頂部字體切換按鈕事件
    const fontBtn = document.getElementById('btn-font-toggle');
    if (fontBtn) {
      fontBtn.addEventListener('click', toggleFontSize);
    }

    // 3. 綱目項目後方的個別引經按鈕事件
    document.querySelectorAll('.scripture-toggle-btn').forEach(btn => {
      btn.addEventListener('click', function(e) {
        e.stopPropagation();
        const contentBox = this.closest('.item-content');
        if (!contentBox) return;
        const scripturesList = contentBox.querySelector('.scriptures');
        if (!scripturesList) return;

        const isCurrentlyExpanded = scripturesList.classList.contains('expanded');
        if (isCurrentlyExpanded) {
          scripturesList.classList.remove('expanded');
          this.classList.remove('expanded');
          this.setAttribute('aria-expanded', 'false');
          this.innerHTML = '經文 ▾';
        } else {
          scripturesList.classList.add('expanded');
          this.classList.add('expanded');
          this.setAttribute('aria-expanded', 'true');
          this.innerHTML = '經文 ▴';
        }
      });
    });
  }

  function applyFont(level) {
    const body = document.body;
    body.classList.remove('font-lg', 'font-xl');
    if (level === 'lg') {
      body.classList.add('font-lg');
    } else if (level === 'xl') {
      body.classList.add('font-xl');
    }
    localStorage.setItem('psrp_font_size', level);

    const fontBtn = document.getElementById('btn-font-toggle');
    if (fontBtn) {
      fontBtn.textContent = FONT_LABELS[level] || '字體: 中';
    }
  }

  function toggleFontSize() {
    const current = localStorage.getItem('psrp_font_size') || 'md';
    const nextIdx = (FONT_LEVELS.indexOf(current) + 1) % FONT_LEVELS.length;
    const nextLevel = FONT_LEVELS[nextIdx];
    applyFont(nextLevel);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
"""

# Helper to format items to HTML with individual scripture toggle button
def render_outline_html(items):
    out = ['<div class="outline-list">']
    for it in items:
        lvl = it["level"]
        num_str = html.escape(it["num"])
        text_str = html.escape(it["text"])
        has_scriptures = bool(it.get("scriptures"))
        
        out.append(f'  <div class="outline-item level-{lvl}">')
        if num_str:
            out.append(f'    <span class="num">{num_str}</span>')
        out.append('    <div class="item-content">')
        
        # 內文 + 個別引經切換按鈕（在項目文字後面）
        toggle_btn_html = ''
        if has_scriptures:
            toggle_btn_html = ' <button class="scripture-toggle-btn" aria-expanded="false" type="button" title="展開/收合引經">經文 ▾</button>'
            
        if text_str:
            out.append(f'      <div class="text">{text_str}{toggle_btn_html}</div>')
        elif toggle_btn_html:
            out.append(f'      <div class="text">{toggle_btn_html}</div>')
            
        if has_scriptures:
            out.append('      <ul class="scriptures">')
            for s in it["scriptures"]:
                ref = html.escape(s["ref"])
                stext = html.escape(s["text"])
                out.append('        <li class="scripture-item">')
                out.append(f'          <span class="bullet">•</span><span class="ref">{ref}</span><span class="stext">{stext}</span>')
                out.append('        </li>')
            out.append('      </ul>')
            
        out.append('    </div>')
        out.append('  </div>')
    out.append('</div>')
    return "\n".join(out)


def generate_theme(theme_cfg):
    theme_name = theme_cfg["theme_name"]
    pdf_file = theme_cfg["pdf_file"]
    lessons_config = theme_cfg["lessons"]
    theme_dir = os.path.join(BASE_DIR, theme_name)
    os.makedirs(theme_dir, exist_ok=True)

    with open(os.path.join(theme_dir, "style.css"), "w", encoding="utf-8") as f:
        f.write(css_content.strip())
    with open(os.path.join(theme_dir, "script.js"), "w", encoding="utf-8") as f:
        f.write(js_content.strip())
    print(f"[{theme_name}] style.css and script.js generated.")

    page_reader = make_page_reader(theme_dir, pdf_file)
    all_parsed_lessons = []
    for cfg in lessons_config:
        items = parse_lesson(cfg, page_reader=page_reader, legacy_mode=(theme_name == "亞伯拉罕以撒雅各的神"))
        all_parsed_lessons.append({
            "cfg": cfg,
            "items": items
        })

    for idx, ldata in enumerate(all_parsed_lessons):
        cfg = ldata["cfg"]
        items = ldata["items"]
        outline_html = render_outline_html(items)
        
        prev_cfg = lessons_config[idx - 1] if idx > 0 else None
        next_cfg = lessons_config[idx + 1] if idx < len(lessons_config) - 1 else None
        
        bottom_nav = ['<div class="bottom-nav">']
        if prev_cfg:
            bottom_nav.append(f'  <a href="{prev_cfg["code"]}.html" class="nav-page-btn">')
            bottom_nav.append(f'    <span class="label">‹ 上一篇</span>')
            bottom_nav.append(f'    <span class="page-title">{html.escape(prev_cfg["title"])}</span>')
            bottom_nav.append('  </a>')
            
        bottom_nav.append('  <a href="index.html" class="nav-page-btn nav-home-btn">返回篇題目錄</a>')
        
        if next_cfg:
            bottom_nav.append(f'  <a href="{next_cfg["code"]}.html" class="nav-page-btn">')
            bottom_nav.append(f'    <span class="label">下一篇 ›</span>')
            bottom_nav.append(f'    <span class="page-title">{html.escape(next_cfg["title"])}</span>')
            bottom_nav.append('  </a>')
        bottom_nav.append('</div>')
        bottom_nav_html = "\n".join(bottom_nav)
        
        page_html = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=3.0, user-scalable=yes">
  <title>{html.escape(cfg["title"])} - PSRP</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <!-- 頂部固定導覽列 -->
  <header class="top-nav">
    <div class="nav-left">
      <a href="index.html" class="nav-btn" aria-label="返回目錄">‹ 目錄</a>
    </div>
    <div class="nav-center">第 {cfg["num"]} 篇</div>
    <div class="nav-right">
      <button id="btn-font-toggle" class="nav-btn" aria-label="切換字體大小">字體: 中</button>
    </div>
  </header>

  <main class="container">
    <!-- 篇題資訊：僅保留篇號與篇題 -->
    <div class="lesson-header">
      <h1 class="lesson-title">{html.escape(cfg["title"])}</h1>
    </div>

    <!-- 綱目與經文 -->
    {outline_html}

    <!-- 頁尾導覽 -->
    {bottom_nav_html}
  </main>

  <script src="script.js"></script>
</body>
</html>
"""
        out_file = os.path.join(theme_dir, f"{cfg['code']}.html")
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(page_html.strip())
        print(f"Generated {out_file}")

    theme_cards = []
    for cfg in lessons_config:
        theme_cards.append(f"""    <a href="{cfg["code"]}.html" class="lesson-card">
      <div class="lesson-badge">第 {cfg["num"]} 篇</div>
      <div class="lesson-card-title">{html.escape(cfg["short_title"])}</div>
    </a>""")
    theme_cards_html = "\n".join(theme_cards)

    theme_index_html = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=3.0, user-scalable=yes">
  <title>{theme_name} - 篇題目錄</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <!-- 頂部導覽列 -->
  <header class="top-nav">
    <div class="nav-left">
      <a href="../index.html" class="nav-btn" aria-label="返回主首頁">‹ 首頁</a>
    </div>
    <div class="nav-center">{theme_name}</div>
    <div class="nav-right">
      <button id="btn-font-toggle" class="nav-btn" aria-label="切換字體大小">字體: 中</button>
    </div>
  </header>

  <main class="container">
    <div class="theme-header">
      <div class="theme-sub">總題</div>
      <h1 class="theme-title">{theme_name}</h1>
    </div>

    <div class="lesson-card-list">
{theme_cards_html}
    </div>

    <div class="bottom-nav">
      <a href="../index.html" class="nav-page-btn nav-home-btn">返回 PSRP 主目錄</a>
    </div>
  </main>

  <script src="script.js"></script>
</body>
</html>
"""

    with open(os.path.join(theme_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(theme_index_html.strip())
    print(f"[{theme_name}] index.html generated.")


# Generate all themes
for t_cfg in THEMES_CONFIG:
    generate_theme(t_cfg)

# Generate root index.html with all themes
first_theme = THEMES_CONFIG[0]["theme_name"]
root_cards = []
for t_cfg in THEMES_CONFIG:
    t_name = t_cfg["theme_name"]
    t_count = len(t_cfg["lessons"])
    root_cards.append(f"""      <a href="{t_name}/index.html" class="lesson-card">
        <div class="lesson-badge">主題</div>
        <div class="lesson-card-title">{t_name}（共 {t_count} 篇）</div>
      </a>""")
root_cards_html = "\n".join(root_cards)

root_index_html = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=3.0, user-scalable=yes">
  <title>禱研背講 PSRP - 手機版</title>
  <link rel="stylesheet" href="{first_theme}/style.css">
  <style>
    .home-banner {{
      text-align: center;
      margin: 30px 0 36px 0;
      padding-bottom: 24px;
      border-bottom: 2px solid var(--num-color);
    }}
    .home-app-title {{
      font-size: 32px;
      font-weight: 800;
      color: var(--title-color);
      margin-bottom: 8px;
    }}
    .home-app-desc {{
      font-size: 18px;
      color: #6C757D;
      font-weight: 600;
    }}
  </style>
</head>
<body>
  <header class="top-nav">
    <div class="nav-left">
      <span style="font-weight: 800; color: var(--num-color); font-size: 18px;">PSRP</span>
    </div>
    <div class="nav-center">主題目錄</div>
    <div class="nav-right">
      <button id="btn-font-toggle" class="nav-btn" aria-label="切換字體大小">字體: 中</button>
    </div>
  </header>

  <main class="container">
    <div class="home-banner">
      <h1 class="home-app-title">禱研背講 PSRP</h1>
      <div class="home-app-desc">Pray • Study • Recite • Prophesy</div>
    </div>

    <div class="lesson-card-list">
{root_cards_html}
    </div>
  </main>

  <script src="{first_theme}/script.js"></script>
</body>
</html>
"""

with open(os.path.join(BASE_DIR, "index.html"), "w", encoding="utf-8") as f:
    f.write(root_index_html.strip())
print("Root index.html generated.")
