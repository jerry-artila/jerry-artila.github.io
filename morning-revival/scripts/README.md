# 《晨興聖言》自動化更新管線說明 (Update Pipeline)

本工具遵循 [`專案規格.md`](../專案規格.md) (SRS 2.0) 規範設計，提供一鍵式從淡水會所來源網站擷取、清洗、渲染與品管驗證之全自動工作流程。

---

## 🚀 快速開始 (Quick Start)

在專案根目錄下直接執行：

```bash
# 一鍵更新 (直接從來源網站抓取最新週次、清洗、生成 output/ 並進行品質驗證)
python3 scripts/pipeline.py
```

---

## 🛠️ 命令列參數 (CLI Options)

| 參數 | 預設值 | 說明 |
| :--- | :--- | :--- |
| *(無參數)* | 淡水會所晨興網址 | 連線來源網站、清洗資料、更新 `output/` 檔案並自動驗證 |
| `--dry-run` | `False` | 僅連線與解析測試，不寫入任何檔案 |
| `--verify-only` | `False` | 僅針對現有 `output/` 進行 SRS 品質規範驗證 (檢查引文與標籤) |
| `--url <URL>` | 官方預設網址 | 自訂抓取的來源網頁 URL |
| `--input-file <PATH>` | `None` | 使用本地 HTML 或文字快取檔更新 (離線測試或除錯用) |
| `--output-dir <DIR>` | `output` | 指定輸出的部署目錄 |

### 範例：

```bash
# 1. 僅檢查目前的 output 是否完全合規 (無未清出處、無殘留參讀)
python3 scripts/pipeline.py --verify-only

# 2. 測試抓取與解析，不覆寫檔案
python3 scripts/pipeline.py --dry-run

# 3. 使用本地 HTML 快取檔案進行離線測試
python3 scripts/pipeline.py --input-file /path/to/cache.html
```

---

## 🔄 管線自動化架構 (Pipeline Architecture)

```
[淡水會所來源網站] ➔ fetch_source_html() (SSL & User-Agent 適配)
        ↓
  HTML 文字流提取 ➔ VisibleTextExtractor
        ↓
   結構化資料解析 ➔ parse_morning_revival_data()
        ↓ 
  資料清洗與截除 ➔ clean_paragraph_text()
     • 清除段落尾端書籍出處引文（如李常受文集、新約總論、生命讀經等）
     • 截除信息選讀末尾之「--參讀...」與「📚 參讀：...」推薦區塊
     • 結構化三層綱目提取（大點、中點、小點，過濾 4~5 層）
        ↓
   模組化模板渲染 ➔ render_index_html() / render_outline_html() / render_daily_html()
     • index.html (首頁兼全週經文匯總)
     • 綱目.html (結構化綱目檢視)
     • 週一.html ～ 週六.html (每日晨興餧養 + 信息選讀)
        ↓
   產出品管自動驗證 ➔ validate_output_directory()
     • 零引文洩漏驗證
     • 零參讀殘留驗證
     • 徽章與導覽列完整性檢查
```
