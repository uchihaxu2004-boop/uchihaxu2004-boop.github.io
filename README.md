# 大軍的個人網站 | Life Archive

A personal life documentation website blending American retro aesthetics with Japanese minimalism.

## 網站結構

```
根目錄/
├── index.html          # 主頁面（HTML + CSS + JS 已整合）
└── assets/
    ├── fonts/          # 自訂字體（如需使用）
    └── images/
        ├── daily/      # 日常生活照片
        └── adventure/  # 出遊冒險照片
```

## 部署到 GitHub Pages

1. 將所有檔案 push 到你的 GitHub repository
2. 進入 Settings → Pages
3. Source 選擇 "Deploy from a branch"
4. Branch 選擇 `main`，資料夾選 `/ (root)`
5. 點擊 Save，等待幾分鐘即可

## 之後新增照片的方式

### 日常生活照片
將照片放入 `assets/images/daily/`，然後修改 `index.html` 中的 placeholder card，替換為：

```html
<div class="photo-card" data-tilt>
    <img src="assets/images/daily/your-photo.jpg" alt="描述">
    <div class="card-glare"></div>
</div>
```

### 出遊冒險照片
同樣方式，放入 `assets/images/adventure/`

## 會員資料處理

目前表單會在 console 輸出資料。要實際儲存，可接：
- Google Sheets API
- Airtable
- 自己的後端伺服器

## 技術特色

| 功能 | 說明 |
|:---|:---|
| 客製化滑鼠游標 | 跟隨滑鼠的圓點與外圈 |
| 3D 卡片傾斜效果 | 滑鼠移動時卡片立體傾斜 |
| 視差滾動 | 背景形狀隨滾動移動 |
| 文字解碼動畫 | 標題 hover 時的隨機字母效果 |
| 粒子爆炸 | 表單提交時的慶祝動畫 |
| 滾動顯示動畫 | 元素進入視窗時的漸入效果 |

## 設計特色

| 元素 | 美式復古 | 日系簡約 |
|:---|:---|:---|
| 字體 | Playfair Display 襯線體 | Inter 無襯線 + 思源宋體 |
| 配色 | 高對比黑白 | 極簡色調，銀色點綴 |
| 動態 | 流暢誇張的動畫 | 精緻細膩的互動 |
| 排版 | 大膽的標題層次 | 大量留白、呼吸感 |
| 質感 | 噪點紋理覆蓋 | 玻璃擬態、微光效果 |

---

網站已準備好部署到你的 GitHub repository，之後只需替換 placeholder 為實際照片即可！
