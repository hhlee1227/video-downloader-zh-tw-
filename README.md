# 🎞️ 影音下載器 V1.0

這是由使用者提供的 Snap Video 2026-10.shortcut 改造的**未簽署候選版本**，尚不可標示為可直接匯入。Windows 環境沒有 Apple 官方 `shortcuts` 簽署工具，也無法執行 iOS 捷徑。

只有 iPhone 的使用者請先看 [iPhone 專用後續步驟](reports/IPHONE-ONLY.md)。已準備 GitHub 雲端 macOS 官方簽署 workflow，首次上傳功能分支時會嘗試執行，不能保證簽署成功。最新執行結果以 GitHub Actions 為準。

原下載引擎與 API 協定保留；目前原 API 的空白輸入探測卻回傳「更新原版捷徑」導引，中文版會明確停止該導引。**沒有實際影片或音訊下載成功的證據，下載服務相容性尚未確認。**

## 成果

- `original/`：完整原始簽署檔、AEA 認證資料、解碼後 Apple Archive、原始 binary/XML plist 與 JSON。原檔 SHA-256：`96360b959801fa76bb6dc3820c1a44115bda0a77bea4cd217d68036f8dac7be8`。
- `dist/Video-Downloader-V1.0.unsigned.shortcut`：117 動作的未簽署候選檔。
- `src/workflow.zh-TW.plist`：完整可編輯捷徑原始碼。
- `src/build.py`、`src/decode.py`、`src/localize.js`：可重現建置、驗簽解碼與本地化層。
- `reports/`：動作清單、全部文字路徑清單、依賴圖、流程圖、中文化對照與測試證據。
- `tools/sign-macos.sh`：只使用 Apple 官方工具簽署，保留簽署前後檔案與雜湊。

## 建置與測試

在專案根目錄執行，需 Python 3.11 以上及 Node.js（本次 Python 3.14.7、Node.js 24.19.0）：

```sh
python -m pip install -r requirements.txt
python src/decode.py
python src/build.py
python tools/audit.py
```

解碼器僅支援本次已驗證的 AA01 目錄／單一 Shortcut.wflow 結構，遇到其他結構會失敗，不會猜測或建立假資料。JSON 內 bytes 以 Base64 物件保存；binary plist 是完整資料的主要依據。建置採固定 UUID，可重現相同候選檔。

## macOS 簽署

```sh
bash tools/sign-macos.sh
```

等價官方命令：

```sh
shortcuts sign --mode anyone --input dist/Video-Downloader-V1.0.unsigned.shortcut --output dist/Video-Downloader-V1.0.signed.shortcut
```

Apple 會收到捷徑副本進行驗證，見 [Apple 官方說明](https://support.apple.com/guide/shortcuts-mac/run-shortcuts-from-the-command-line-apd455c82f02/mac)。本次未執行簽署，未使用第三方簽署服務。腳本成功只代表官方命令成功，仍須比對內容並實機驗證。可用：

```sh
python src/decode.py dist/Video-Downloader-V1.0.signed.shortcut --output-dir reports/signed-decoded
python tools/compare-signed.py
```

完成後在 iPhone 匯入簽署檔，依 `reports/TEST-REPORT.md` 驗收。

## GitHub

專案：https://github.com/hhlee1227/video-downloader-zh-tw- （使用者建立的公開儲存庫，名稱末尾有連字號）。完整成果分支：`feature/shortcuts-zh-tw-v1`。目標初始為空白倉庫，main 僅初始化導覽首頁；捷徑原檔與修改版分別保存，不覆寫原始捷徑。
