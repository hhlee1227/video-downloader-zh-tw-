#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ "$(uname -s)" != Darwin ]] || ! command -v shortcuts >/dev/null; then
  echo '需要 macOS 與 Apple 官方 shortcuts 工具。' >&2
  exit 1
fi
input='dist/Video-Downloader-V1.0.unsigned.shortcut'
output='dist/Video-Downloader-V1.0.signed.shortcut'
[[ ! -e "$output" ]] || { echo '簽署後檔案已存在；請先另行保留。' >&2; exit 1; }
shasum -a 256 "$input" > reports/signing-before.sha256
shortcuts sign --mode anyone --input "$input" --output "$output"
[[ -s "$output" ]]
shasum -a 256 "$input" "$output" > reports/signing-after.sha256
echo '官方簽署命令成功；請再解碼比對內容並進行 iPhone 匯入及下載測試。'
