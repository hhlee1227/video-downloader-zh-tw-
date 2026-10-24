# 只有 iPhone 的處理方式

目前狀態：成果已上傳 https://github.com/hhlee1227/video-downloader-zh-tw- 的功能分支。候選檔仍未簽署；雲端 Mac 已嘗試 Apple 官方工具，但因未登入 iCloud 而失敗。[實際日誌與後續限制](CLOUD-SIGNING.md)。

## GitHub 專案已建立

不需要再建立儲存庫。既有目的地為 `hhlee1227/video-downloader-zh-tw-`，功能分支為 `feature/shortcuts-zh-tw-v1`。

若能操作已開啟的電腦瀏覽器，也可只完成 GitHub 登入，其餘交給 Codex。不要把密碼、一次性驗證碼或 Apple 帳號密碼貼到聊天。

## 嘗試雲端 Mac 官方簽署

已準備 `.github/workflows/official-sign.yml`，採 GitHub 的 macOS runner，執行 Apple 原生 `shortcuts sign --mode anyone`，成功後才解碼、驗簽並與候選內容逐項比較；全部通過才上傳 signed artifact。沒有第三方簽署服務、Apple 帳號密碼欄位或繞過簽章步驟。

此流程已執行，官方工具明確回覆需要登入 iCloud，因而失敗。沒有發布「可直接匯入」檔案，也沒有透過新增帳號密碼到 CI 的方式重試。新格式 AA 無法由目前解碼器處理時也會停止，需診斷後再重試。

此 workflow 在指定功能分支的工作流程檔案更新時自動執行，不需要先合併 main。另保留 workflow_dispatch；這個手動介面須先將 workflow 納入預設分支才會顯示。使用 GitHub 公開專案標準 macOS runner，沒有設定付費大型 runner 或購買額度。

目前沒有可下載的 signed artifact。只有未來簽署、解碼驗簽與內容比對均成功後，才能在 iPhone Safari 從 GitHub Actions 下載 signed artifact，在「檔案」解壓縮後嘗試匯入；此手機下載／匯入路徑尚未實測。匯入後仍須驗證下載服務，目前 API 曾回傳原版更新導引。

## 不使用 Mac／雲端簽署的替代方式

在 iPhone 捷徑 App 內保留並複製已安裝的原 Snap Video，將副本重新命名為「🎞️ 影音下載器 V1.0」，再依原始碼與對照表手動修改。這是 App 內編輯路徑，不是把這份未簽署檔改副檔名匯入；本次完整 117 動作候選版也不會自動套用到該副本。主要文字來自 API，單純改名稱不能完成中文化。

完成 App 內修改後，可以使用 App 的分享功能產生 iCloud 連結。Apple 官方說明： https://support.apple.com/guide/shortcuts/share-shortcuts-apdf01f8c054/ios 。

官方 Mac 簽署說明： https://support.apple.com/guide/shortcuts-mac/run-shortcuts-from-the-command-line-apd455c82f02/mac 。GitHub macOS runner 說明： https://docs.github.com/en/actions/reference/runners/github-hosted-runners 。
