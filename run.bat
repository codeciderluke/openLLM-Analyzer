@echo off
REM ============================================================
REM  Ollama Model ^& RAG Inspector - launcher
REM  Runs the GUI from the local .venv. Auto-sets up if missing.
REM ============================================================
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo [INFO] No virtual environment found. Running setup.bat first...
    call "%~dp0setup.bat"
    if %errorlevel% neq 0 exit /b 1
)

echo Starting Ollama Model ^& RAG Inspector...
call ".venv\Scripts\python.exe" -m ollama_inspector.main %*
set "RC=%errorlevel%"

if not "%RC%"=="0" (
    echo.
    echo [Exit code %RC%] The application exited with an error.
    pause
)
endlocal
exit /b %RC%
