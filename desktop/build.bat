@echo off
rem Builds dist\Receptor Fixer.exe (single file) from index.html and desktop\app.py.
rem Needs Python 3.9+ on PATH. The first run creates .venv and installs pywebview + PyInstaller.
setlocal
cd /d "%~dp0.."

if not exist ".venv\Scripts\python.exe" (
    python -m venv .venv || goto :error
)
".venv\Scripts\python.exe" -m pip install --quiet --upgrade pip || goto :error
".venv\Scripts\python.exe" -m pip install --quiet -r desktop\requirements.txt || goto :error

".venv\Scripts\python.exe" -m PyInstaller --noconfirm --clean --onefile --windowed ^
    --name "Receptor Fixer" ^
    --icon "%CD%\icons\icon.ico" ^
    --distpath dist --workpath build --specpath build ^
    --add-data "%CD%\index.html;web" ^
    --add-data "%CD%\manifest.webmanifest;web" ^
    --add-data "%CD%\sw.js;web" ^
    --add-data "%CD%\icons;web\icons" ^
    --add-data "%CD%\vendor;web\vendor" ^
    desktop\app.py || goto :error

echo.
echo Built: %CD%\dist\Receptor Fixer.exe
exit /b 0

:error
echo Build failed.
exit /b 1
