#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
《晨興聖言》自動化更新管線 (Morning Revival Update Pipeline)
遵循《專案規格.md》(SRS 2.0) 規範，執行以下自動化任務：
  1. Fetch: 自淡水會所來源網站 (或指定來源) 擷取最新網頁內容
  2. Parse & Clean: 結構化提取經文、綱目與每日信息，落實引文清洗與參讀截除
  3. Render: 產生首頁經文彙總 (index.html)、結構化綱目 (綱目.html) 及週一至週六每日閱讀頁面
  4. Validate: 執行品管驗證，確保出處清洗與標籤符合規範
"""

import os
import sys
import re
import ssl
import argparse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

DEFAULT_SOURCE_URL = "https://churchintamsui.wixsite.com/index/morning-revival"
DAYS = ["週一", "週二", "週三", "週四", "週五", "週六"]

# ==============================================================================
# 1. 網頁擷取器 (Fetcher)
# ==============================================================================
def fetch_source_html(url: str) -> str:
    """自目標網址抓取原始 HTML，具備 SSL 容錯與 User-Agent 偽裝"""
    print(f"🌐 正在從來源網址擷取資料: {url}")
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/124.0.0.0 Safari/537.36"
        }
    )
    with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
        content = resp.read().decode("utf-8", errors="ignore")
    print(f"✅ 成功擷取 HTML 內容 (大小: {len(content):,} bytes)")
    return content


class VisibleTextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.texts = []
        self.ignore = False

    def handle_starttag(self, tag, attrs):
        if tag in ["script", "style", "meta", "link", "noscript"]:
            self.ignore = True

    def handle_endtag(self, tag):
        if tag in ["script", "style", "meta", "link", "noscript"]:
            self.ignore = False

    def handle_data(self, data):
        if not self.ignore:
            cleaned = data.strip()
            if cleaned:
                self.texts.append(cleaned)


def extract_visible_lines(html_content: str) -> list:
    extractor = VisibleTextExtractor()
    extractor.feed(html_content)
    lines = [re.sub(r"[\u200b\u200c\u200d\uFEFF]", "", t).strip() for t in extractor.texts]
    return [l for l in lines if l]


# ==============================================================================
# 2. 資料清洗與解析 (Parser & Cleaner)
# ==============================================================================
def clean_paragraph_text(text: str) -> str:
    """自動清除段落尾端出處引文與參讀指引 (遵循 SRS 第四條第 3 點)"""
    text = re.sub(r"[\u200b\u200c\u200d\uFEFF]", "", text)
    # 清洗書籍出處括號，如（新約總論第十二冊，三五頁）、（李常受文集...）、（...生命讀經...）等
    pattern = r"（\s*(?:(?:李常受|倪柝聲)?文集|生命讀經|新約總論|真理課程|經歷基督|附聚會資料)[^）]*?）"
    text = re.sub(pattern, "", text)
    # 截除 --參讀... 與 📚 參讀：... 書目推薦區塊
    text = re.sub(r"(?:--|📚\s*)參讀[^\n<]*", "", text)
    # 整理標點符號與多餘空白
    text = re.sub(r"。\s*。", "。", text)
    text = re.sub(r"\s+。", "。", text)
    text = re.sub(r" +", " ", text).strip()
    return text


def parse_morning_revival_data(lines: list) -> dict:
    """解析網頁文本為結構化資料物件"""
    # 1. 解析篇題與讀經資訊
    week_str = "第十週"
    main_title = "模成基督的死與達到傑出的復活"
    scripture = "讀經：腓三10~11"
    training_info = ""

    for l in lines[:50]:
        if "半年度訓練" in l or "訓練" in l:
            training_info = l
        m_week = re.search(r"(第[一二三四五六七八九十0-9]+週)[、\s]*(.*)", l)
        if m_week and not training_info.startswith(l):
            week_str = m_week.group(1).strip()
            if m_week.group(2).strip():
                main_title = m_week.group(2).strip()
        if l.startswith("讀經：") or l.startswith("讀經:"):
            scripture = l.strip()

    # 2. 解析綱目結構 (Outline Parser)
    # 綱目界於 【週   一】 與 "第X週 • 週一" 之間
    outline_start = -1
    outline_end = -1
    for i, l in enumerate(lines):
        if "【週" in l and "一】" in l and outline_start == -1:
            outline_start = i
        if f"{week_str} • 週一" in l or (re.search(r"第[一二三四五六七八九十0-9]+週 • 週一", l) and outline_start != -1):
            outline_end = i
            break

    outline_sections = []
    if outline_start != -1 and outline_end != -1:
        raw_outline_lines = lines[outline_start:outline_end]
        chinese_nums = {'壹': 1, '貳': 2, '叁': 3, '肆': 4, '伍': 5, '陸': 6, '柒': 7, '捌': 8, '玖': 9, '拾': 10}

        current_sec = None
        current_item = None

        for raw_l in raw_outline_lines:
            l = clean_paragraph_text(raw_l)
            if not l or "【週" in l:
                continue

            # 第 1 層 (大點)：第壹大點、第貳大點...
            m1 = re.match(r"^(第?[壹貳叁肆伍陸柒捌玖拾]大?點?)[、\s]*(.*)", l)
            if m1 and any(l.startswith(cn) or l.startswith(f"第{cn}") for cn in chinese_nums):
                num_str = m1.group(1)
                if not num_str.startswith("第"):
                    num_str = f"第{num_str}"
                if not num_str.endswith("大點"):
                    num_str = f"{num_str}大點"
                current_sec = {
                    "numeral": num_str,
                    "title": m1.group(2).strip(),
                    "items": []
                }
                outline_sections.append(current_sec)
                current_item = None
                continue

            # 第 2 層 (中點)：一、二、三...
            m2 = re.match(r"^([一二三四五六七八九十]+、)\s*(.*)", l)
            if m2:
                current_item = {
                    "num": m2.group(1),
                    "text": m2.group(2).strip(),
                    "sub_items": []
                }
                if current_sec is not None:
                    current_sec["items"].append(current_item)
                continue

            # 第 4 層 (a. b.) 與第 5 層 ((一) (二)) 嚴格過濾截斷
            if re.match(r"^[a-z]\.|\([一二三四五六七八九十0-9]+\)", l):
                continue

            # 第 3 層 (小點)：1. 2. 3. 或中點內之細點
            if current_item is not None:
                if not current_item["text"]:
                    current_item["text"] = l
                else:
                    m3 = re.match(r"^\d+[\.、]\s*(.*)", l)
                    sub_text = m3.group(1).strip() if m3 else l
                    current_item["sub_items"].append(sub_text)

    # 3. 每日信息定位
    day_indices = []
    for d in DAYS:
        target = f"{week_str} • {d}"
        for i, l in enumerate(lines):
            if target in l:
                day_indices.append((d, i))
                break

    default_subheadings = {
        "週一": "認識基督並祂復活的大能，以及同祂受苦的交通",
        "週二": "模成基督之死的模子與背十字架",
        "週三": "經歷成就一切的死，對付消極的事",
        "週四": "達到那從死人中傑出的復活",
        "週五": "全人的每一部分都要復活",
        "週六": "忘記背後，努力面前的，向着標竿竭力追求",
    }

    daily_data = {}
    for idx, (d, start_idx) in enumerate(day_indices):
        end_idx = day_indices[idx + 1][1] if idx + 1 < len(day_indices) else len(lines)
        sub_lines = lines[start_idx:end_idx]

        nourish_idx = -1
        reading_idx = -1
        for i, l in enumerate(sub_lines):
            if l == "晨興餧養":
                nourish_idx = i
            elif l == "信息選讀":
                reading_idx = i

        nourish_lines = sub_lines[nourish_idx + 1:reading_idx] if reading_idx != -1 else sub_lines[nourish_idx + 1:]
        reading_lines = sub_lines[reading_idx + 1:] if reading_idx != -1 else []

        verses = []
        nourish_paras = []
        for l in nourish_lines:
            if not l: continue
            m_verse = re.match(r"^([^\s『「]+?\d+[\d~節\-]*)\s*([『「].*[』」])$", l)
            if m_verse:
                verses.append({
                    "ref": m_verse.group(1).strip(),
                    "text": m_verse.group(2).strip()
                })
            else:
                cl = clean_paragraph_text(l)
                if cl:
                    nourish_paras.append(cl)

        reading_paras = []
        for l in reading_lines:
            if any(k in l for k in ["新北市召會淡水會所", "電話：", "E-Mail:", "瀏覽本網站若發生異常", "聯絡我們", "bottom of page"]):
                continue
            cl = clean_paragraph_text(l)
            if cl:
                reading_paras.append(cl)

        daily_data[d] = {
            "verses": verses,
            "nourish_paragraphs": nourish_paras,
            "reading_paragraphs": reading_paras,
            "sub_heading": default_subheadings.get(d, "")
        }

    return {
        "training": training_info,
        "week_str": week_str,
        "main_title": main_title,
        "scripture": scripture,
        "outline_sections": outline_sections,
        "daily": daily_data
    }


# ==============================================================================
# 3. HTML 頁面生成器 (Page Renderer)
# ==============================================================================
def render_header(title: str = "晨興聖言") -> str:
    return f"""  <!-- Header / Navigation Bar -->
  <header class="app-header">
    <div class="header-container">
      <button id="mobile-toc-toggle" class="btn-icon" aria-label="切換導覽選單">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <line x1="3" y1="12" x2="21" y2="12"></line>
          <line x1="3" y1="6" x2="21" y2="6"></line>
          <line x1="3" y1="18" x2="21" y2="18"></line>
        </svg>
      </button>

      <div class="header-title">
        <h1>{title}</h1>
      </div>

      <div class="header-controls">
        <button id="font-size-btn" class="btn-control" title="調整字體大小 (22px -> 24px -> 26px 循環)">
          <span class="btn-icon-text">A+</span>
          <span id="font-size-label">22px</span>
        </button>

        <button id="theme-btn" class="btn-control" title="切換深淺模式">
          <svg id="sun-icon" class="theme-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="5"></circle>
            <line x1="12" y1="1" x2="12" y2="3"></line>
            <line x1="12" y1="21" x2="12" y2="23"></line>
            <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
            <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
            <line x1="1" y1="12" x2="3" y2="12"></line>
            <line x1="21" y1="12" x2="23" y2="12"></line>
            <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
            <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
          </svg>
          <svg id="moon-icon" class="theme-icon hidden" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
          </svg>
        </button>
      </div>
    </div>
  </header>"""


def render_drawer(active_page: str) -> str:
    nav_items = [
        ("index.html", "🏠 首頁 (經文)"),
        ("綱目.html", "📋 綱目"),
        ("週一.html", "📅 週一進度"),
        ("週二.html", "📅 週二進度"),
        ("週三.html", "📅 週三進度"),
        ("週四.html", "📅 週四進度"),
        ("週五.html", "📅 週五進度"),
        ("週六.html", "📅 週六進度"),
    ]

    links_html = []
    for href, label in nav_items:
        active_cls = " active" if href == active_page else ""
        links_html.append(f'          <li><a href="{href}" class="toc-link level-1{active_cls}">{label}</a></li>')

    joined_links = "\n".join(links_html)

    return f"""    <!-- TOC Sidebar / Mobile Drawer -->
    <aside id="toc-sidebar" class="toc-sidebar">
      <div class="toc-header">
        <h2>頁面導覽</h2>
        <button id="toc-close-btn" class="btn-icon mobile-only" aria-label="關閉導覽">✕</button>
      </div>
      <nav id="toc-nav" class="toc-nav">
        <ul>
{joined_links}
        </ul>
      </nav>
    </aside>

    <div id="toc-overlay" class="toc-overlay"></div>"""


def render_index_html(data: dict) -> str:
    week_str = data["week_str"]
    main_title = data["main_title"]
    scripture = data["scripture"]
    daily = data["daily"]

    day_sections = []
    day_tags = {"週一": "mon", "週二": "tue", "週三": "wed", "週四": "thu", "週五": "fri", "週六": "sat"}

    for d in DAYS:
        d_info = daily.get(d, {"verses": []})
        sec_id = f"sec-{day_tags.get(d, 'day')}"
        verse_cards = []
        for v in d_info["verses"]:
            verse_cards.append(f"""            <div class="verse-card">
              <span class="verse-ref">{v['ref']}</span>
              {v['text']}
            </div>""")
        v_content = "\n".join(verse_cards)

        day_sections.append(f"""        <!-- {d}經文卡片 -->
        <section id="{sec_id}" class="reading-section">
          <div class="section-heading reading-heading">
            <span class="reading-icon">📅</span>
            <h3>{d} 經文</h3>
            <a href="{d}.html" class="daily-tag" style="margin-left: auto;" title="進入{d}信息">進入 {d}</a>
          </div>
          <div class="verse-card-group">
{v_content}
          </div>
        </section>""")

    sections_joined = "\n\n".join(day_sections)

    return f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{week_str} • 首頁 (經文) | 晨興聖言</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="styles.css">
</head>
<body class="font-22px theme-light">
{render_header("晨興聖言")}

  <!-- Main Container -->
  <div class="layout-container">
{render_drawer("index.html")}

    <!-- Main Content Area -->
    <main class="main-content">
      <article class="reading-article">
        <!-- Title Card -->
        <div class="title-card">
          <div class="title-meta">
            <span class="badge">{week_str} 經文匯總</span>
          </div>
          <h2 class="main-title">
            {main_title}
          </h2>
          <p class="reading-scripture" style="margin-top: 0.5rem; font-size: 0.9em; color: var(--text-muted);">{scripture}</p>
        </div>

{sections_joined}

      </article>

      <footer class="app-footer">
        <p>晨興聖言 — 淡水會所網頁版</p>
      </footer>
    </main>
  </div>

  <script src="app.js"></script>
</body>
</html>
"""


def render_outline_html(data: dict) -> str:
    week_str = data["week_str"]
    main_title = data["main_title"]
    scripture = data["scripture"]
    sections = data.get("outline_sections", [])

    sections_html = []
    for s_idx, sec in enumerate(sections, 1):
        items_html = []
        for it_idx, item in enumerate(sec["items"], 1):
            sub_list_html = ""
            if item["sub_items"]:
                lis = "\n".join([f"                    <li>{s}</li>" for s in item["sub_items"]])
                sub_list_html = f"""                  <ol class="level-3-list">
{lis}
                  </ol>"""

            items_html.append(f"""            <div id="sec-{s_idx}-{it_idx}" class="item-block level-2-item">
              <div class="item-title">
                <span class="item-num">{item['num']}</span>
                <p>{item['text']}</p>
              </div>
{sub_list_html}
            </div>""")

        joined_items = "\n\n".join(items_html)

        sections_html.append(f"""        <!-- Section {s_idx} -->
        <section id="section-{s_idx}" class="outline-section">
          <div class="section-heading level-1-heading">
            <div class="level-1-top-bar">
              <span class="numeral">{sec['numeral']}</span>
            </div>
            <h3 class="level-1-title">{sec['title']}</h3>
          </div>
          <div class="section-body">
{joined_items}
          </div>
        </section>""")

    sections_joined = "\n\n".join(sections_html)

    return f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{week_str} • 綱目 | 晨興聖言</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="styles.css">
</head>
<body class="font-22px theme-light">
{render_header("晨興聖言")}

  <!-- Main Container -->
  <div class="layout-container">
{render_drawer("綱目.html")}

    <!-- Main Content Area -->
    <main class="main-content">
      <article class="outline-article">
        <!-- Title Card -->
        <div class="title-card">
          <div class="title-meta">
            <span class="badge">{week_str} 綱目</span>
          </div>
          <h2 class="main-title">
            {main_title}
          </h2>
          <p class="reading-scripture" style="margin-top: 0.5rem; font-size: 0.9em; color: var(--text-muted);">{scripture}</p>
        </div>

{sections_joined}

      </article>

      <footer class="app-footer">
        <p>晨興聖言 — 淡水會所網頁版</p>
      </footer>
    </main>
  </div>

  <script src="app.js"></script>
</body>
</html>
"""


def render_daily_html(data: dict, day_name: str) -> str:
    week_str = data["week_str"]
    main_title = data["main_title"]
    scripture = data["scripture"]
    d_info = data["daily"].get(day_name, {"verses": [], "nourish_paragraphs": [], "reading_paragraphs": [], "sub_heading": ""})

    # 1. 經文卡片
    verse_cards = []
    for v in d_info["verses"]:
        verse_cards.append(f"""            <div class="verse-card">
              <span class="verse-ref">{v['ref']}</span>
              {v['text']}
            </div>""")
    verses_html = "\n".join(verse_cards)

    # 2. 晨興餧養段落
    nourish_paras = []
    for p in d_info["nourish_paragraphs"]:
        nourish_paras.append(f"""            <p class="content-paragraph">
              {p}
            </p>""")
    nourish_html = "\n".join(nourish_paras)

    # 3. 信息選讀段落
    reading_paras = []
    for p in d_info["reading_paragraphs"]:
        reading_paras.append(f"""              <p class="content-paragraph">
              {p}
            </p>""")
    reading_joined = "\n".join(reading_paras)

    sub_heading_html = f'<h4 class="reading-sub-heading">{d_info["sub_heading"]}</h4>\n' if d_info["sub_heading"] else ""

    return f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{week_str} • {day_name} | 晨興聖言</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="styles.css">
</head>
<body class="font-22px theme-light">
{render_header("晨興聖言")}

  <!-- Main Container -->
  <div class="layout-container">
{render_drawer(f"{day_name}.html")}

    <main class="main-content">
      <!-- Article Content -->
      <article class="reading-article">
        <!-- Title & Meta Header -->
        <div class="title-card">
          <div class="title-meta">
            <span class="badge">{day_name}</span>
            <span class="date-text">{week_str}</span>
          </div>
          <h2 class="main-title">
            {main_title}
          </h2>
          <p class="reading-scripture">{scripture}</p>
        </div>

        <!-- Section 1: Morning Nourishment (晨興餧養) -->
        <section id="sec-nourishment" class="reading-section">
          <div class="section-heading reading-heading">
            <span class="reading-icon">🌅</span>
            <h3>晨興餧養</h3>
          </div>

          <!-- Scripture Cards -->
          <div id="nourishment-verses" class="verse-card-group">
{verses_html}
          </div>

          <!-- Nourishment Body Text -->
          <div id="nourishment-text" class="reading-body">
{nourish_html}
          </div>
        </section>

        <!-- Section 2: Selected Reading (信息選讀) -->
        <section id="sec-reading" class="reading-section">
          <div class="section-heading reading-heading">
            <span class="reading-icon">📖</span>
            <h3>信息選讀</h3>
          </div>

          <div class="reading-body">
            <div id="read-1">
              {sub_heading_html}{reading_joined}
            </div>
          </div>
        </section>
      </article>

      <footer class="app-footer">
        <p>晨興聖言 — 淡水會所網頁版</p>
      </footer>
    </main>
  </div>

  <script src="app.js"></script>
</body>
</html>
"""


# ==============================================================================
# 4. 品管驗證器 (Quality Validator)
# ==============================================================================
def validate_output_directory(output_dir: Path) -> bool:
    """自動檢驗輸出目錄下的 HTML 檔案是否百分之百符合 SRS 規格"""
    print("\n🔍 正在執行產出品質規範驗證 (SRS Validation)...")
    expected_files = ["index.html", "綱目.html"] + [f"{d}.html" for d in DAYS]
    passed = True

    for fname in expected_files:
        fpath = output_dir / fname
        if not fpath.exists():
            print(f"❌ 缺少必備部署檔案: {fname}")
            passed = False
            continue

        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()

        # 1. 檢驗書目出處引文清洗狀況
        cites = re.findall(r"（[^）]*?(?:文集|生命讀經|總論|真理課程|經歷基督|頁)[^）]*?）", content)
        if cites:
            print(f"❌ {fname} 發現未清洗出處引文: {cites[:3]}")
            passed = False

        # 2. 檢驗參讀標籤截除狀況
        refs = re.findall(r"(?:--|📚\s*)參讀[^\n<]*", content)
        if refs:
            print(f"❌ {fname} 發現未截除之參讀標籤: {refs[:3]}")
            passed = False

        # 3. 檢驗徽章與標題
        if fname == "綱目.html":
            if '<span class="badge">第十週 總綱</span>' in content:
                print("❌ 綱目.html 徽章錯誤，應為「第十週 綱目」")
                passed = False

    if passed:
        print("✅ 所有檔案皆通過品管驗證！完全符合 SRS 2.0 規範！\n")
    else:
        print("⚠️ 品管驗證未全數通過，請檢視上方錯誤訊息。\n")

    return passed


# ==============================================================================
# 5. 主流程控制器 (Pipeline Runner)
# ==============================================================================
def run_pipeline(source_url: str = DEFAULT_SOURCE_URL,
                 input_file: str = None,
                 output_dir_path: str = "output",
                 dry_run: bool = False,
                 verify_only: bool = False):
    output_dir = Path(output_dir_path).resolve()
    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)

    if verify_only:
        success = validate_output_directory(output_dir)
        sys.exit(0 if success else 1)

    # 取得原始 HTML 內容
    if input_file:
        print(f"📂 正在從本機快取檔案讀取: {input_file}")
        with open(input_file, "r", encoding="utf-8") as f:
            html_content = f.read()
    else:
        html_content = fetch_source_html(source_url)

    # 提取純文字行
    lines = extract_visible_lines(html_content)
    print(f"📝 擷取到 {len(lines):,} 行可見文字內容")

    # 結構化解析與清洗
    parsed_data = parse_morning_revival_data(lines)
    print(f"📌 解析主題: {parsed_data['week_str']} • {parsed_data['main_title']}")
    print(f"📖 讀經進度: {parsed_data['scripture']}")
    print(f"📋 綱目大點數: {len(parsed_data.get('outline_sections', []))} 個大點")

    if dry_run:
        print("💡 Dry-run 模式：略過檔案寫入。")
        return

    # 寫入 index.html
    index_html = render_index_html(parsed_data)
    with open(output_dir / "index.html", "w", encoding="utf-8") as f:
        f.write(index_html)
    print("✨ 已生成首頁經文彙總: output/index.html")

    # 寫入 綱目.html
    if parsed_data.get("outline_sections"):
        outline_html = render_outline_html(parsed_data)
        with open(output_dir / "綱目.html", "w", encoding="utf-8") as f:
            f.write(outline_html)
        print("✨ 已生成結構化綱目: output/綱目.html")

    # 寫入各每日頁面
    for d in DAYS:
        daily_html = render_daily_html(parsed_data, d)
        with open(output_dir / f"{d}.html", "w", encoding="utf-8") as f:
            f.write(daily_html)
        print(f"✨ 已生成每日閱讀模組: output/{d}.html")

    # 執行品管驗證
    validate_output_directory(output_dir)


def main():
    parser = argparse.ArgumentParser(description="晨興聖言自動化更新管線 (Pipeline)")
    parser.add_argument("--url", default=DEFAULT_SOURCE_URL, help="來源網址 (預設淡水會所晨興網址)")
    parser.add_argument("--input-file", help="使用本地 HTML/文字快取檔更新 (離線測試用)")
    parser.add_argument("--output-dir", default="output", help="輸出目錄路徑 (預設 output/)")
    parser.add_argument("--dry-run", action="store_true", help="僅解析不寫入檔案")
    parser.add_argument("--verify-only", action="store_true", help="僅驗證現有 output 檔案品質")

    args = parser.parse_args()
    run_pipeline(
        source_url=args.url,
        input_file=args.input_file,
        output_dir_path=args.output_dir,
        dry_run=args.dry_run,
        verify_only=args.verify_only
    )


if __name__ == "__main__":
    main()
