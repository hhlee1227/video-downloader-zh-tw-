# GitHub 上傳與官方雲端簽署結果

2026-10-24 已完成 GitHub 上傳，儲存庫為使用者提供的公開專案：

https://github.com/hhlee1227/video-downloader-zh-tw-

完整成果位於 `feature/shortcuts-zh-tw-v1`，原始捷徑與候選版分別保存。首次上傳 53 個檔案，逐一以本機 Git blob SHA 與遠端 tree 比對，一致；上傳 commit 為 `97b4ab48ecb02324307f1dea35e9356ba08cdc99`，tree 為 `ffb3b399e64cf5c50ed2ffc7aae4a40c9005cc57`。後續文件更新另有 commit，不改動此初次上傳證據。

草稿 PR：https://github.com/hhlee1227/video-downloader-zh-tw-/pull/1 。尚未合併 main。

## 真實雲端執行

- Run：https://github.com/hhlee1227/video-downloader-zh-tw-/actions/runs/40055691370
- Job ID：120758058105。
- 執行時間：2026-10-24 02:48 UTC。
- Runner：macOS 15.7.9、macos-15-arm64。
- 已找到 `/usr/bin/shortcuts`、`/usr/bin/aea`、`/usr/bin/aa`。
- 官方命令：`shortcuts sign --mode anyone --input dist/Video-Downloader-V1.0.unsigned.shortcut --output dist/Video-Downloader-V1.0.signed.shortcut`。
- 結果：失敗，exit code 1。
- 直接原因：`Error: In order to do this, you must be signed into iCloud.`
- 解碼驗證及 signed artifact 上傳步驟因此跳過；沒有產生成功的簽署成果，不能將候選檔標為可直接匯入。

原始 job 日誌可從上方 run 查閱。檢查到的 Objective-C debugDescription 訊息不是此處認定的主要原因；阻擋簽署的是官方明確的 iCloud 登入要求。這是環境條件，沒有透過改腳本忽略 exit code、重命名檔案或第三方簽署服務掩蓋。

## 只有 iPhone 的實際限制與下一步

無人登入 iCloud 的 GitHub macOS runner 無法完成本次官方簽署。這次失敗不是需要重複按「重新執行」就可解決的問題。沒有把 Apple 帳號密碼存入 GitHub Secrets，也不要求使用者這樣做。

目前可行的路徑為：

1. 在 iPhone「捷徑」App 內複製已安裝的原捷徑，再依原始碼逐項修改。這是手動編輯路徑，不能直接自動套用本次 117 動作候選檔，也尚未替使用者在手機上完成。修改完可用 App 的原生分享功能產生 iCloud 連結。
2. 若日後有能登入 iCloud 的可信任 Mac，可執行專案中的 Apple 官方簽署腳本，簽署與比對成功後再傳至 iPhone；不必購買 Mac，但目前沒有提供這種環境。

無論哪條路徑，仍須解決原下載 API 回傳更新導引的相容性問題，並完成 iPhone 單片／多媒體／音訊／取消／儲存驗收。**目前不能提供已完成、可直接匯入且下載功能已證實的 V1.0。**
