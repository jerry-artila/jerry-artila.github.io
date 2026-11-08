---
name: 生成小排信息網頁
description: >-
  將排聚會（group-meeting）新增子目錄中的屬靈信息圖片（如《職事文摘》掃描/截圖）完整擷取文字，產生 Markdown 檔與手機友善的響應式 HTML 閱讀網頁，並同步更新總目錄與前後篇導航連結。當使用者提及新增小排信息子目錄、整理屬靈信息圖片成網頁、或執行「生成小排信息網頁」時啟用此技能。
---

# 生成小排信息網頁

此技能定義將 `group-meeting` 子目錄中的屬靈信息圖片（通常為《職事文摘》共 8 頁直排截圖）轉換為標準 Markdown 與響應式 HTML 網頁的完整規範與流程。

---

## 標準作業流程 (Workflow)

### 步驟 1：檢視子目錄與讀取圖片
1. 確認目標子目錄路徑（例如 `group-meeting/<子目錄名稱>/`）內的所有圖片檔案（`.png`, `.PNG`, `.jpg`, `.jpeg`）。
2. 依檔名順序使用 `read_file` 檢視每一張圖片，辨識以下資訊：
   - **篇題名稱**（以首頁大標題為準；若子目錄名稱因打字或符號簡化略有差異，**請保留子目錄名稱不變**，但文章內文與網頁標題使用圖片上的正確篇題）。
   - **專欄類別**：圖片頁眉右上角標示（如：`真理`、`生命`、`事奉`、`福音` 等）。
   - **卷期與頁碼**：圖片頁尾標示（如：`第十一卷．第三期`）。
   - **完整內文**：注意原文為**繁體中文直排（由右至左、由上至下）**，且常分為上下兩欄。請逐字精確轉錄，保留完整標點符號（如『』、「」、—、…）與經節括號出處，以及最後一頁的「參讀」書目。
   - **異體字規範**：維持原文用字習慣（如：`裏`、`纔`、`彀`、`豫`、`喫`、`題` 等）。

### 步驟 2：建立 Markdown 檔案 (`<篇題名稱>.md`)
在該子目錄下建立 `<篇題名稱>.md`，結構如下：
```markdown
# <篇題名稱>

<引言段落 1>

<引言段落 2（若有）>

## <小標題一>

<內文段落...>

## <小標題二>

<內文段落...>

---

> （參讀：<參讀書目內容>。）
```

### 步驟 3：建立文章網頁 (`<子目錄名稱>/index.html`)
1. 讀取 HTML 範本：[article-template.html](./references/article-template.html)（內建支援 `22px / 26px / 30px` 三級字體大小循環切換、Sepia / Light / Dark 主題模式切換、以及側邊欄漢堡選單目錄導航）。
2. 根據文章所屬**專欄類別**套用對應的主題色（Accent Colors）：

| 專欄類別 | `--accent-color` (Sepia) | `--accent-light` (Sepia) | `--accent-color` (Light) | `--accent-light` (Light) | `--accent-color` (Dark) | `--accent-light` (Dark) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **生命篇** | `#215a36` | `rgba(33, 90, 54, 0.08)` | `#27673e` | `rgba(39, 103, 62, 0.08)` | `#68b984` | `rgba(104, 185, 132, 0.16)` |
| **真理篇** | `#1a5276` | `rgba(26, 82, 118, 0.08)` | `#1f618d` | `rgba(31, 97, 141, 0.08)` | `#5dade2` | `rgba(93, 173, 226, 0.16)` |
| **事奉篇** | `#8c281f` | `rgba(140, 40, 31, 0.08)` | `#9c2720` | `rgba(156, 39, 32, 0.08)` | `#e5534b` | `rgba(229, 83, 75, 0.16)` |

3. 填入章節目錄 (`drawer-toc-list`) 與內文區塊 (`<section id="sec-...">`)：
   - 第一個區塊為 `#sec-intro`，將引言段落包在 `<div class="lead-box">` 內，並在側邊欄目錄列為 `引言：<簡短引言主題>`。
   - 每個小標題使用 `<section id="sec-xxx"><h2 class="section-title">...</h2><p>...</p></section>`，並在側邊欄目錄依序標示 `一、...`、`二、...`。
   - 最後為 `#sec-reference`（`<div class="reference-box">📖 參讀：...</div>`），並在側邊欄目錄列為 `參讀書目`。
4. 設定頁尾導航 (`.footer-nav`)：
   - 左側按鈕連結至目前總目錄中的上一篇文章（`../<上一篇子目錄>/index.html`）。
   - 右側按鈕連結回總目錄（`../index.html`，顯示「返回目錄：聚會文章列表 →」）。

### 步驟 4：更新上一篇文章的頁尾導航與根目錄 `group-meeting/index.html`
1. **更新上一篇文章的 `index.html`**：
   - 將原本指向 `../index.html`（返回目錄）的右側導航按鈕，改為指向新文章 `../<新子目錄名稱>/index.html`：
     ```html
     <a href="../<新子目錄名稱>/index.html" class="nav-card-btn" style="text-align: right;">
       <span class="nav-card-sub">下一篇</span>
       <span class="nav-card-title"><新篇題名稱> →</span>
     </a>
     ```
2. **更新總目錄 `group-meeting/index.html`**：
   - 在 `<meta name="description">` 中加入新篇題名稱。
   - 在 `.article-list` 最下方新增一張 `.article-card`：
     ```html
     <a href="<新子目錄名稱>/index.html" class="article-card">
       <span class="card-badge"><類別>篇 · 職事文摘 <卷期></span>
       <h2 class="card-title"><新篇題名稱></h2>
       <p class="card-desc">
         <2～3 句精煉摘要，概述本篇信息核心負擔>
       </p>
       <div class="card-meta">
         <span><頁數> 頁內容完整擷取</span>
         <span>含 <引言+小標題總數> 個段落目錄導航</span>
         <span class="card-arrow">閱讀全文 →</span>
       </div>
     </a>
     ```

### 步驟 5：驗證檢查
- 確認 `group-meeting/.gitignore` 已忽略圖片檔（`*.jpg`, `*.jpeg`, `*.png`, `*.PNG`），不會將圖片加入 Git 追蹤。
- 確認所有內部錨點 (`#sec-...`) 與側邊欄目錄連結 (`href="#sec-..."`) 完全對應。
- 確認總目錄與前後篇的相對路徑連結正確無誤。
