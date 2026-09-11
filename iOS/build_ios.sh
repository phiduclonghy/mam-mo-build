#!/bin/sh
set -eu
cd "$(dirname "$0")"
if ! command -v xcodebuild >/dev/null 2>&1; then
  echo 'Cần macOS và Xcode. Chưa có IPA được tạo.'
  exit 1
fi
xcodebuild -project MamMo.xcodeproj -scheme MamMo -configuration Debug -sdk iphonesimulator -derivedDataPath build CODE_SIGNING_ALLOWED=NO build
echo 'Ứng dụng simulator: build/Build/Products/Debug-iphonesimulator/MamMo.app'
echo 'Để xuất IPA cho iPhone thật: mở Xcode, chọn Signing Team, Product > Archive > Distribute App.'
