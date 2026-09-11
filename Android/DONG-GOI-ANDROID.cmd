@echo off
chcp 65001 >nul
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (
  python build_apk.py
) else (
  py -3 build_apk.py
)
if errorlevel 1 (
  echo Chua tao duoc APK. Xem thong bao thieu cong cu o tren va README.md.
) else (
  echo Da tao Mam-Mo-Android-debug.apk va kiem tra chu ky.
)
pause
