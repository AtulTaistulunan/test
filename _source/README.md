# 原始資料與產生工具（Phase 0 備份）

`index.html` 是由這裡的資料與腳本產生的單一檔案。重構前的狀態保存在分支 `backup-v0-before-refactor`。

- `data/`：題庫與筆記的結構化資料。`counseling_600q_original.json` 是整理前的原始版本，`_edited` 是統一譯名、精簡正解後的版本。
- `tools/`：解析、清理與產生網頁的 Python 腳本，以及 CSS、JS。腳本內的路徑指向當時的工作目錄，需調整後才能重新執行。

題庫全部為 AI 生成的練習題，不是官方歷屆試題。
