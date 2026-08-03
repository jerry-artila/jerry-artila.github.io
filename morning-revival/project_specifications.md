# 晨興聖言第二週 專案需求與規格細節說明書

本文檔彙整本專案（2026年六月半年度訓練《信徒（一）》第二週）所有維護、補齊與樣式優化之規格細節。

---

## 📌 一、 專案基本資訊與部署規範

1. **專案主題**：
   - 2026年六月 半年度訓練《信徒（一）》第二週：
     **《永遠的生命—神的生命帶着神聖的性情；三一神乃是聖經的結構；以及隱藏的神，自隱的神》**
2. **資料來源網頁**：
   - `https://churchintamsui.wixsite.com/index/morning-revival`
3. **部署與版控規則**：
   - 僅對本地端檔案進行修改與維護。
   - **禁止** 執行 `git commit` 或 `git push`。

---

## 📖 二、 內容完整性與對照標準

1. **100% 忠實還原來源網頁**：
   - [`週一.html`](file:///D:/myGit/jerry-artila.github.io/morning-revival/%E9%80%B1%E4%B8%80.html) 至 [`週六.html`](file:///D:/myGit/jerry-artila.github.io/morning-revival/%E9%80%B1%E5%85%AD.html) 每日內容必須與淡水會所來源網頁文字完全一致。
2. **完整收錄項目**：
   - **晨興餧養**：收錄完整段落文字，包含文中書目頁碼引用（例如：`（李常受文集一九三二至一九四九年第三冊，二九七至二九八頁）`）。
   - **信息選讀**：收錄完整段落文字與相關書目頁碼引用。
   - **參讀指引**：每日內文最下方需完整保留來源網頁之 `📚 參讀：...` 書目及篇章。

---

## 📐 三、 綱目層級與符號規格 ([`綱目.html`](file:///D:/myGit/jerry-artila.github.io/morning-revival/%E7%B6%B1%E7%9B%AE.html))

| 層級 | 說明 | 符號 / 編號格式 | 範例 |
| :--- | :--- | :--- | :--- |
| **第 1 層級** | 大點 | 中文大寫數字 | `第壹大點`～`第肆大點` |
| **第 2 層級** | 中點 | 國字數字 + 頓號 | `一、`, `二、`, `三、` |
| **第 3 層級** | 小點 | 阿拉伯數字 + 句點 | `1.`, `2.`, `3.` |
| **第 4 層級** | 子點 | 小寫英文字母 + 句點 | `a.`, `b.`, `c.`, `d.`, `e.`, `f.` |
| **第 5 層級** | 細點 | 括號國字數字 | `(一)`, `(二)`, `(三)` |

> [!NOTE]
> 來源網頁第 4 層級原為黑圓點 `•`，在本專案中已依規範全數替換為小寫英文字母 `a.`, `b.`, `c.` 等。

---

## 🎨 四、 縮排與字體大小規範

1. **螢幕親和縮排 (Screen-Friendly Indentation)**：
   - 避免過深內縮影響閱讀體驗，層級清單內縮設定為小幅精緻間距（`padding-left: 0.85rem`）。
2. **第 5 層級排列方式**：
   - 第 5 層級（`(一)`, `(二)`, `(三)`）視為第 4 層級平鋪排列，**與第 4 層級對齊，無額外內縮**（`padding-left: 0`）。
3. **字體大小規則 (Font Size Rules)**：
   - **內文段落**：內文文字大小與層級無關，全站保持標準一致字號（並可切換 20px / 22px / 24px）。
   - **第 5 層級編號符號**：僅第 5 層級編號符號 `(一)`, `(二)`, `(三)` 獨立縮小為 **`0.7em`**（CSS class: `.sub-num-level-5`）。

---

> [!TIP]
> 專案樣式維護檔為 [`styles.css`](file:///D:/myGit/jerry-artila.github.io/morning-revival/styles.css)，結構內容維護檔為 [`綱目.html`](file:///D:/myGit/jerry-artila.github.io/morning-revival/%E7%B6%B1%E7%9B%AE.html) 與 [`週一.html`](file:///D:/myGit/jerry-artila.github.io/morning-revival/%E9%80%B1%E4%B8%80.html)～[`週六.html`](file:///D:/myGit/jerry-artila.github.io/morning-revival/%E9%80%B1%E5%85%AD.html)。
