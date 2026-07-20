@echo off
REM ============================================================
REM  Ollama Model ^& RAG Inspector - tests + lint
REM ============================================================
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo [INFO] No virtual environment found. Running setup.bat first...
    call "%~dp0setup.bat"
    if %errorlevel% neq 0 exit /b 1
)

REM Run UI tests headless (no display required)
set "QT_QPA_PLATFORM=offscreen"

echo === pytest ===
call ".venv\Scripts\python.exe" -m pytest -q
set "RC=%errorlevel%"

echo.
echo === ruff ===
call ".venv\Scripts\python.exe" -m ruff check src tests

echo.
if "%RC%"=="0" (
    echo Tests passed.
) else (
    echo Tests failed ^(code %RC%^).
)
endlocal
exit /b %RC%
