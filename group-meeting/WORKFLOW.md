# 職事文摘 圖片轉 HTML 網頁處理流程 (方案 B 簡化版 SOP)

本文件記錄「連續圖片轉文字 ➔ 生成單一完整 Markdown 備份 ➔ 更新至 index.html」的簡化處理流程。

---

## 📋 簡化處理流程 (Workflow Steps)

### 1. 跨頁識別與直接合成完整 Markdown (Direct Full MD Generation)
- **輸入**：連續頁面圖片（例如 `page 50.png`, `page 51.png`, ...）
- **輸出檔案**：`[文章標題]_完整文章.md` （僅保留這 1 個完整備份檔，不再產生單頁 `.md` 檔）
- **處理**：
  - 一次性讀取所有連續頁面圖片。
  - AI 在記憶體中直接跨頁比對、校對與自動拼接斷句。
  - 保留標題層級（大標題 `#` / 分段標題 `##`）、引言 `>` 與引用經節。

### 2. 更新/生成網頁 (`index.html`)
- **輸出檔案**：`index.html`（作為首頁預設展示）
- **核心設計規範**：
  - **主題系統 (Themes)**：支援明亮 (Light) 與深色 (Dark) 雙態動態切換模式（單一按鈕切換）。
  - **字級控制 (Font Size)**：預設 24px，支援 24px ~ 32px 預設按鈕與循環切換按鈕，並記憶於 `localStorage`。
  - **閱讀輔助**：頂部閱讀進度條 (Progress Bar)、右下角懸浮導航與回到頂部按鈕 (FAB)。
  - **排版細節**：
    - 主標題 `<h1>` 與欄位 `meta-tag`
    - 引言/摘要卡片 `.lead-quote`
    - 文章小標 `##` 帶有 ❖ 圖示裝飾線
    - 引文塊 `blockquote` 與末尾參考資料盒 `.reference-box`

---

> 💡 Future Instructions for Assistant:
> 當使用者上傳新一組連續頁面圖片時，請直接執行方案 B：在記憶體中一次拼接完成，僅輸出 `[文章標題]_完整文章.md` 作為純文字備份，並同步更新/覆蓋 [index.html](file:///d:/AGY代理/職事文摘/index.html)。
