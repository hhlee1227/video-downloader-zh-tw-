# 原始檔解析與改造記錄

## 格式與完整性

原檔 31,063 bytes，AEA1 profile 0（簽署、未加密），認證區為 bplist，含 SigningCertificateChain。`python-aea` 以內嵌葉憑證公鑰成功驗證 AEA ECDSA、HMAC 與區段校驗；這不等同驗證 Apple 根憑證信任鏈、撤銷狀態或 iOS 匯入資格。結果見 `original/signature-check.json`。

解碼結果為 AA01，包含目錄與 Shortcut.wflow，後者是 binary plist，共 85 動作；完整原始結構見 `original/workflow.plist`。解碼範圍依 AA DATA 長度界定，沒有依賴截斷的文字輸出重建捷徑。

## 控制流程與變數

原始動作索引採 0 起算：0–2 設定與註解；3–8 建立 API 請求；9–84 最多 100 次迴圈；12 取得遠端內容；13–18 判斷 JSON 及 reload；19–31 僅第一次建立選擇清單；32–38 建立媒體請求；39–52 貼上連結／重跑；53–59 處理 open-url 指令；60–70 第二次起儲存上一次的媒體；71–83 完成選單與結束。

主要變數：`main_json`（請求設定）、`url_fetch`（下一次請求）、`api_result`（原下載服務資料／本地化副本）、`selected_item`（選擇結果）、`label_now`（當前媒體 metadata）、`m_album`／`m_file`／`menu_done`（原完成選單狀態）。原動作 32 引用稍後動作 36 的輸出；候選版改為取得 metadata 後立即保存 label_now，避免迴圈首次使用前向引用。既有變數名稱、API key 與媒體欄位不翻譯。

`*-dependencies.mmd` 展示動作輸出依賴，實線僅為詞法順序；`*-control-flow.mmd` 展示分支／迴圈的靜態流程。圖不代表模擬執行成功；詳細 GroupingIdentifier 與參數見完整動作清單。尚未完成所有分支的型別與變數支配性證明。

## 外部資料範圍

1. `https://api.phimtat.vn/json/snapvideo.json`：GET，既有 `api-key`、`lang`、`ver=8`、`ask_format`、`show_menu`、`skip_update`、`b64`。候選版固定 `lang=zh-TW`、`skip_update=true`；影音網址以 Base64 傳送，Base64 **不是加密**。
2. `https://api.phimtat.vn/snapvideo/red64.php?url=`：接收下一個完整 URL 的 Base64，含內層 API 參數或媒體網址；服務可能重新導向至媒體 CDN。保留原 User-Agent。遠端會看到來源 IP、HTTP 層資訊及其日誌中的 query。
3. 媒體目的地由 API 回傳，無法離線列出所有網域。既有設計允許外部 URL 與重新導向，未建立 CDN 白名單；需實機檢查實際傳輸目的地與個別平台授權行為。
4. 候選版只將擷取的第一個有效 HTTP(S) 網址送入主解析器。手動輸入預設值可讀剪貼簿；原重新執行分支仍可能讀剪貼簿，但重新進入後仍只擷取第一個網址。沒有新增照片、檔案或通訊錄上傳動作。照片與檔案動作用於本機保存。
5. 原始捷徑已內含 API key；未將其當成新取得的個人憑證。原始證據及完整原始碼保留它，報告不另外印出。公開專案前宜確認原作者授權與此 key 的公開用途。

本次唯一 API 探測採空白 b64，不送使用者影音連結或剪貼簿，未追蹤回應內的圖片網址。HTTP 200、application/json，證據 `api-empty-input-response.bin`。回應 labels 為英文更新指南與關閉，medias 值為字串；原流程期望的媒體 metadata（url/ext/file）不在此回應中。因此不能確認實際下載流程相容，不能把 HTTP 200 視為下載成功。本地化層會辨識觀察到的更新回應並提示停止。

## JavaScript、Base64 與更新

原動作 4 是 `data:text/html,<script>…</script>`，先以 Base64 保護輸入插值，再用本地網頁轉文字執行 JavaScript，輸出 JSON。它擷取 HTTP(S) 網址、偵測語言、讀設定並組裝 URL；不是遠端 JavaScript。原 3、10 動作執行 Base64 編碼。完整腳本保留在原始 plist，沒有隱藏解碼內容。新增同一種橋接機制處理遠端 JSON；此 WebKit／內容轉換相容性待 iPhone 驗證。

更新防護有三層：請求 skip_update=true、本地化層移除 reload 並拒絕已觀察的更新導引、原 reload 與 open-url 自動執行分支改為說明後停止。沒有安裝捷徑或直接開啟遠端更新頁面的動作。一般 API URL 回傳仍受服務控制，服務行為的後續變更不能由離線測試保證。

## 實作範圍與待驗證

新增本地網址輸入與格式檢查（接受有點分隔網域的 HTTP(S)，僅取第一個；不支援 IP、localhost、原生 Unicode 網域、URL 內空白），保留 API 格式與多媒體選擇。已知音訊 `file` 路徑直接選擇檔案位置；其他媒體提供照片／檔案選擇。移除原 iPhone deviceSpecific 儲存位置與完成後不必要選單，改以儲存後通知。取消採系統原生取消，不攔截。

目前只能處理已取得回應的格式錯誤、無媒體、更新要求及迴圈上限；網路逾時、HTTP 錯誤、照片權限不足或儲存空間不足仍可能由捷徑系統直接顯示錯誤，未宣稱已有完整通用 try/catch。選單的未知遠端文字與平台動態內容保留原樣，不能宣稱全部 API 文案已完成繁體中文化。新增 list／notification／regex 等動作參數及新本地化 HTML 橋接需 Apple 匯入與實機確認；靜態 plist 有效不等於 Apple 動作 schema 已驗證。

## 依賴來源

從 PyPI 安裝鎖定版本 python-aea 1.1.0（上游 https://github.com/kinnay/AEA）、cryptography、lz4、pyliblzfse 及其依賴，版本見 requirements.txt。已檢閱 AEA 上游核心來源：本機解析、密碼學驗證與解壓縮，沒有呼叫簽署服務；未對套件供應鏈做完整安全稽核。參考工具來源與 PyPI metadata 保存在 tools，未執行下載的第三方 EXE，未使用第三方簽署。
