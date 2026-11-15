---
name: 更新晨興聖言網頁
description: >-
  執行《晨興聖言》自動化更新管線（pipeline.py），從淡水會所來源網站擷取最新週次內容、清洗資料並生成每週獨立子目錄網頁與總覽首頁，接著自動將變更同步推送至 GitHub，最後將最新一週的公開網址進行短網址處理並貼出。當使用者告知「來源網站已經更新」、「更新晨興聖言」或要求執行晨興聖言更新流程時啟用此技能。
---

# 更新晨興聖言網頁

此技能定義 `morning-revival` 專案的標準自動化更新、GitHub 同步部署與最新週次短網址產出流程。

---

## 標準作業流程 (Workflow)

### 步驟 1：執行自動化更新與驗證管線
在 `morning-revival` 目錄下執行自動化更新腳本：
```bash
python3 scripts/pipeline.py
```
- 確認腳本成功從來源網站（`https://churchintamsui.wixsite.com/index/morning-revival`）擷取最新週次（如 `<第X週>`）。
- 確認成功生成 `output/<第X週>/` 下的 8 個頁面（`index.html`, `綱目.html`, `週一.html` ～ `週六.html`）並更新根目錄 `output/index.html`。
- 確認所有週次子目錄與總覽首頁皆通過 SRS 品管驗證（`✔️ [第X週] 8 個頁面全數通過驗證`）。

### 步驟 2：同步推送至 GitHub
確認 `output/` 與專案檔案變更無誤後，將 `morning-revival` 的更新提交並推送至遠端 GitHub 儲存庫：
```bash
git add output/
git commit -m "update"
git push origin main
```
*(若同時有修改規格或腳本，請一併納入提交)*

### 步驟 3：產生最新一週短網址並貼出
1. 根據步驟 1 解析出的最新週次名稱（例如 `第五週`），組合公開部署網址（需對中文週次名稱進行 URL Encode）：
   - 原始網址格式：`https://www.blowing-in-the-wind.net/morning-revival/output/<第X週>/index.html`
2. 呼叫 `is.gd` API 產生短網址：
   ```bash
   python3 -c 'import urllib.parse, urllib.request; week="第X週"; url=f"https://www.blowing-in-the-wind.net/morning-revival/output/{urllib.parse.quote(week)}/index.html"; req=urllib.request.urlopen(f"https://is.gd/create.php?format=simple&url={urllib.parse.quote(url, safe=\"\")}"); print(req.read().decode("utf-8"))'
   ```
3. 在回覆中清楚貼出：
   - **最新週次與篇題名稱**
   - **短網址**
   - **原始公開連結**与 **總覽首頁連結**（`https://www.blowing-in-the-wind.net/morning-revival/output/`）
