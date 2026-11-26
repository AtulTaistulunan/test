# 教檢研習室（新版，開發中）

不使用框架與建置步驟：原生 ES 模組讀取 `data/` 的 JSON。

- `css/tokens.css`：Design Tokens；`css/app.css`：版面與元件
- `js/app.js`：路由與各頁面；`js/store.js`：本機紀錄；`js/repo.js`：資料讀取；`js/mastery.js`：掌握狀態的暫定規則
- `data/index.json`：考科與 63 個單元；`data/units/<代碼>.json`：各單元的筆記、練習題、情境考點

本機預覽：在這個資料夾執行 `python3 -m http.server`，再開啟 http://localhost:8000 。
- `data/scholars.json`：學者索引；`data/search.json`：全站搜尋用的索引（第一次搜尋時才載入）

資料流程：`../tools/migrate.py`（舊版 → JSON）→ `../tools/phase2.py`（抽出概念、建立題目與概念連結、學者索引）→ `../tools/validate.py`（逐題比對新舊版，並檢查連結完整性）。
概念與連結只加上錨點與對照資料，不更動筆記文字、題目與答案。
題庫全部是 AI 生成的練習題，不是官方歷屆試題。
