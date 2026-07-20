@echo off
REM ============================================================
REM  Ollama Model ^& RAG Inspector - build a standalone .exe
REM  Output: dist\OllamaInspector.exe  (onefile, windowed)
REM ============================================================
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo [INFO] No virtual environment found. Running setup.bat first...
    call "%~dp0setup.bat"
    if %errorlevel% neq 0 exit /b 1
)

set "PY=.venv\Scripts\python.exe"

echo [1/3] Installing PyInstaller...
call "%PY%" -m pip install --upgrade pyinstaller
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install PyInstaller.
    goto :fail
)

echo.
echo [2/3] Generating application icon (packaging\icon.ico)...
call "%PY%" packaging\gen_icon.py
if %errorlevel% neq 0 (
    echo [ERROR] Icon generation failed.
    goto :fail
)

echo.
echo [3/3] Building executable with PyInstaller...
call "%PY%" -m PyInstaller --noconfirm --clean OllamaInspector.spec
if %errorlevel% neq 0 (
    echo [ERROR] PyInstaller build failed.
    goto :fail
)

echo.
echo ============================================================
echo  Build complete:  dist\OllamaInspector.exe
echo ============================================================
endlocal
exit /b 0

:fail
echo.
echo Build aborted.
endlocal
exit /b 1
