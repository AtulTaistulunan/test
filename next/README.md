# 教檢研習室（新版，開發中）

不使用框架與建置步驟：原生 ES 模組讀取 `data/` 的 JSON。

- `css/tokens.css`：Design Tokens；`css/app.css`：版面與元件
- `js/app.js`：路由與各頁面；`js/store.js`：本機紀錄；`js/repo.js`：資料讀取；`js/mastery.js`：掌握狀態的暫定規則
- `data/index.json`：考科與 63 個單元；`data/units/<代碼>.json`：各單元的筆記、練習題、情境考點

本機預覽：在這個資料夾執行 `python3 -m http.server`，再開啟 http://localhost:8000 。
資料由 `../tools/migrate.py` 產生，`../tools/validate.py` 會比對新舊版題目是否逐題一致。
題庫全部是 AI 生成的練習題，不是官方歷屆試題。
