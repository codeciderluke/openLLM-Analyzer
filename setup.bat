@echo off
REM ============================================================
REM  Ollama Model ^& RAG Inspector - environment setup
REM  Creates a local .venv and installs the app + dev tools.
REM ============================================================
setlocal
cd /d "%~dp0"

echo [1/3] Checking Python...
where py >nul 2>nul
if %errorlevel%==0 (
    set "PY=py -3"
) else (
    set "PY=python"
)
%PY% --version
if %errorlevel% neq 0 (
    echo [ERROR] Python 3.11+ not found. Install from https://www.python.org
    goto :fail
)

echo.
echo [2/3] Creating virtual environment (.venv)...
if not exist ".venv\Scripts\python.exe" (
    %PY% -m venv .venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        goto :fail
    )
) else (
    echo   Reusing existing .venv
)

echo.
echo [3/3] Installing dependencies...
call ".venv\Scripts\python.exe" -m pip install --upgrade pip
call ".venv\Scripts\python.exe" -m pip install -e ".[dev]"
if %errorlevel% neq 0 (
    echo [ERROR] Dependency installation failed.
    goto :fail
)

echo.
echo ============================================================
echo  Setup complete.  Run: run.bat    Test: test.bat
echo ============================================================
endlocal
exit /b 0

:fail
echo.
echo Setup aborted.
endlocal
exit /b 1
