# 只有 iPhone 的處理方式

目前狀態：本機候選檔未簽署；Windows 無官方簽署工具。使用者已提供新建公開專案 https://github.com/hhlee1227/video-downloader-zh-tw- ，連接工具已確認可寫入。上傳及雲端簽署的最新結果以該專案功能分支與 Actions 頁面為準，不以本機檔案名稱推斷簽署成功。

## GitHub 專案已建立

不需要再建立儲存庫。既有目的地為 `hhlee1227/video-downloader-zh-tw-`，功能分支為 `feature/shortcuts-zh-tw-v1`。

若能操作已開啟的電腦瀏覽器，也可只完成 GitHub 登入，其餘交給 Codex。不要把密碼、一次性驗證碼或 Apple 帳號密碼貼到聊天。

## 嘗試雲端 Mac 官方簽署

已準備 `.github/workflows/official-sign.yml`，採 GitHub 的 macOS runner，執行 Apple 原生 `shortcuts sign --mode anyone`，成功後才解碼、驗簽並與候選內容逐項比較；全部通過才上傳 signed artifact。沒有第三方簽署服務、Apple 帳號密碼欄位或繞過簽章步驟。

此流程尚未執行，也無證據保證無 Apple 帳號登入的 GitHub runner 能成功簽署。若需要 Apple 個人帳號或雲端環境不支援，會失敗並保留 Actions 日誌，不會發布「可直接匯入」檔案。新格式 AA 無法由目前解碼器處理時也會停止，需診斷後再重試。

此 workflow 在指定功能分支的工作流程檔案更新時自動執行，不需要先合併 main。另保留 workflow_dispatch；這個手動介面須先將 workflow 納入預設分支才會顯示。使用 GitHub 公開專案標準 macOS runner，沒有設定付費大型 runner 或購買額度。

成功後，在 iPhone Safari 登入 GitHub → 專案 Actions → 該次成功執行 → Artifacts，下載壓縮檔，在「檔案」解壓縮後開啟 `.signed.shortcut`。這只是預定操作路徑，尚未在 iPhone 驗證，實際介面與匯入結果待測。匯入後仍須驗證下載服務，目前 API 曾回傳原版更新導引。

## 不使用 Mac／雲端簽署的替代方式

在 iPhone 捷徑 App 內保留並複製已安裝的原 Snap Video，將副本重新命名為「🎞️ 影音下載器 V1.0」，再依原始碼與對照表手動修改。這是 App 內編輯路徑，不是把這份未簽署檔改副檔名匯入；本次完整 117 動作候選版也不會自動套用到該副本。主要文字來自 API，單純改名稱不能完成中文化。

完成 App 內修改後，可以使用 App 的分享功能產生 iCloud 連結。Apple 官方說明： https://support.apple.com/guide/shortcuts/share-shortcuts-apdf01f8c054/ios 。

官方 Mac 簽署說明： https://support.apple.com/guide/shortcuts-mac/run-shortcuts-from-the-command-line-apd455c82f02/mac 。GitHub macOS runner 說明： https://docs.github.com/en/actions/reference/runners/github-hosted-runners 。
