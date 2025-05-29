@echo off
ECHO === 直接使用虛擬環境中的可執行檔 ===

REM 設定虛擬環境路徑
SET VENV_PATH=%CD%\music-env\Scripts
SET VENV_PYTHON=%VENV_PATH%\python.exe
SET VENV_PYINSTALLER=%VENV_PATH%\pyinstaller.exe

REM 檢查檔案是否存在
echo Checking if virtual env Python exists: %VENV_PYTHON%
if not exist "%VENV_PYTHON%" (
    echo ERROR: Virtual environment Python not found!
    goto :END
)

REM 顯示正在使用的 Python 路徑
echo Using virtual environment Python:
"%VENV_PYTHON%" -c "import sys; print('Python path:', sys.executable)"

REM 使用虛擬環境的 PyInstaller 執行打包
ECHO 開始使用虛擬環境打包...
"%VENV_PYINSTALLER%" --onefile ^
  --console ^
  --name "MoodComposer" ^
  --debug=all ^
  --add-data "screens;screens" ^
  --add-data "assets;assets" ^
  --add-data "MuseScorePortable;MuseScorePortable" ^
  --add-data "fluidsynth;fluidsynth" ^
  --add-data "tmp;tmp" ^
  main.py

ECHO === Success ===
:END
pause