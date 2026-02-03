@echo off
setlocal
set SCRIPT_DIR=%~dp0
set FFPLAY_PATH=%SCRIPT_DIR%ffplay.exe

if not exist "%FFPLAY_PATH%" (
  echo ffplay.exe not found next to this script: %FFPLAY_PATH%
  exit /b 1
)

where pyinstaller >nul 2>&1
if errorlevel 1 (
  echo pyinstaller not found. Install with: pip install pyinstaller
  exit /b 1
)

pyinstaller --noconfirm --onefile --windowed --name audiobook-player --add-binary "%FFPLAY_PATH%;." gui.py
if errorlevel 1 (
  exit /b 1
)

echo Build complete. Output: dist\audiobook-player.exe
endlocal
