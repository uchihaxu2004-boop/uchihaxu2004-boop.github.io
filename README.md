# 大軍的個人網站 · dajcxun

> 暗黑銀色奢華風的個人網站（Life Archive）。純手寫 HTML / CSS / JS，無框架、無建置工具，直接開檔即可運作。

---

## 1. 專案簡介

- **品牌名**：dajcxun（網域 `dajcxun.com`）
- **風格**：純黑（`#0a0a0a`）＋ 白／銀字、襯線標題（Playfair Display）、留白克制、不加彩色
- **語言**：介面英文（`lang="en"`），少量中文與漢字點綴
- **技術**：靜態網站，每頁一個 `.html`（CSS 與 JS 內嵌在各檔），另有兩個共用檔（搜尋）

---

## 2. 檔案結構

```
.
├── index.html          首頁：問候標題 + 搜尋框 + 選單（自己內嵌一套搜尋）
├── log.html            照片日誌（依「月份」篩選）
├── adventures.html     旅遊相簿（依「國家／地區」篩選）
├── craft.html          作品集（平面列表，已移除分類）
├── reach.html          聯絡頁（社群連結）
├── join.html           訂閱／會員頁
├── site-search.css     共用底部懸浮搜尋框 — 樣式（log/adventures/craft/reach/join 共用）
├── site-search.js      共用底部懸浮搜尋框 — 邏輯
├── favicon.svg         網站圖示
├── ui.md               設計系統與元件手冊（給人／AI 讀的規範）
├── CLAUDE.md           個人與互動偏好設定
├── images/
│   ├── log/            日常照片（log 頁讀這裡）
│   └── adventures/     旅遊照片（adventures 頁讀這裡）
└── files/
    └── craft/          作品檔案（craft 頁讀這裡，如 PDF）
```

---

## 3. 頁面說明

| 頁面 | 角色 | 篩選 | 現況 |
|---|---|---|---|
| `index.html` | 門面 | — | `Welcome to 大軍's Life Archive` + 搜尋框（左側 `+` 開選單，可跳各頁）|
| `log.html` | 日常照片 | 月份 | 已有 1 張範例照片（2026-02-22）|
| `adventures.html` | 旅遊照片 | 國家／地區 | 內容待填（已內建 Taiwan/HongKong/Japan/USA/Indonesia）|
| `craft.html` | 作品 | 無（已移除分類）| 平面列表「年份｜名稱｜箭頭」，內容待填 |
| `reach.html` | 聯絡 | — | 5 個社群圓鈕（Email/IG/GitHub/X/LinkedIn）|
| `join.html` | 訂閱 | — | 表單**目前是假的**（見第 7 節）|

- **頂部導覽列已全部移除**，改由首頁搜尋框／各頁底部懸浮搜尋框導覽。

---

## 4. 設計系統（重點）

CSS 變數（各頁 `:root` 一致）：

```css
--color-bg:        #0a0a0a;   /* 頁底 */
--color-bg-alt:    #111111;
--color-white:     #ffffff;   /* 主字、強調 */
--color-silver:    #c0c0c0;   /* 次字 */
--color-silver-dim:#8a8a8a;   /* 提示字 */
--font-display: 'Playfair Display', serif;  /* 標題＋所有英文/數字/UI 標籤 */
--font-body:    'Inter', sans-serif;
--font-cn:      'Noto Serif TC', serif;      /* 中文 */
```

慣例：標籤一律大寫 + 寬字距（`letter-spacing: 0.15em`）；數字／英文用 Playfair；維持黑／白／銀單色。完整規範見 [`ui.md`](ui.md)。

---

## 5. 如何新增內容（最常用）

每種內容都是「**① 把檔案放進對應資料夾 → ② 在該頁的陣列加一行**」。
⚠️ 檔名**不要有空格**（多字用 `-` 連接）。

### 5.1 日常照片（log.html）
- 檔案放 `images/log/`，檔名格式 **`年-月-日-號碼.jpg`**（程式靠檔名讀日期）
- 在 `log.html` 的 `PHOTOS` 陣列加一行：

```js
const PHOTOS = [
    photo('2026-2-22-1', false),   // false = 橫式，true = 直式
];
```

### 5.2 旅遊照片（adventures.html）
- 檔案放 `images/adventures/`，檔名格式 **`國家-地區-號碼.jpg`**
- 國家須為已內建者（`Taiwan` / `HongKong` / `Japan` / `USA` / `Indonesia`，要新增國家再擴充資料）

```js
photo('Japan-Kyoto-1', true),
```

### 5.3 作品（craft.html）
- 檔案放 `files/craft/`，檔名 **`作品名.副檔名`**（多字用 `-`，會顯示成空格）
- **已移除分類**，不用再寫 `-project` 等後綴

```js
const WORKS = [
    work('OptionPricing', '2026', 'pdf'),   // 有副檔名 → 可點擊下載
    work('MyWebsite', '2026'),               // 不填副檔名 → 純列表項
];
```

---

## 6. 共用底部搜尋（site-search）

- 由 `site-search.css` + `site-search.js` 提供，被 **log / adventures / craft / reach / join** 五頁引入。
- 行為：**固定懸浮在視窗最底部置中**，捲動時不動；左側 `+` 開選單（Home/Log/Adventures/Craft/Reach/Join），點選自動填入，按 Enter 或 `→` 跳轉。
- 首頁 `index.html` **沒有**用這個共用檔，它自己內嵌一套相同行為的搜尋。
- ⚠️ 改 `site-search.css/js` 後，瀏覽器會快取；本機看不到更新時按 **Cmd+Shift+R** 強制重新整理。

---

## 7. 本機預覽

ES module 與相對路徑需要透過伺服器（不能用 `file://` 直接開）：

```bash
cd /Users/uchihamac/Desktop/D
python3 -m http.server 8000
# 瀏覽器開 http://localhost:8000/
```

---

## 8. 已知事項 / 待辦

- **`og:image` 圖尚未建立**：各頁 `<head>` 指向 `https://dajcxun.com/og-image.jpg`，但檔案還沒做 → 分享到社群暫無縮圖。需放一張 1200×630 圖到根目錄並命名 `og-image.jpg`。
- **`join.html` 表單是假的**：送出只顯示成功訊息，**不會真的收到訂閱者**。要嘛接真服務（Formspree／Mailchimp…），要嘛先拿掉。
- **死依賴 / 死碼**：log / adventures / craft 的 `<head>` 仍載入 GSAP + Flip，但篩選已改為純 CSS 切換、用不到了，可移除；另有少量舊版 nav／分類的 CSS 死碼。
- **照片懶載入**：圖片用 `IntersectionObserver` 進視窗才載入；屬正常行為。

---

## 9. 維護慣例

- 任何**設計／元件**變更，先更新 [`ui.md`](ui.md)，再讓各頁同步。
- 新增內容只動各頁的資料陣列（`PHOTOS` / `WORKS`），不需碰其他程式碼。

*最後更新：2026-06-24*
