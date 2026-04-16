@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

echo.
echo ============================================================
echo   Lian Company - Setup Script
echo ============================================================
echo.

:: Detect current directory
set "REPO_DIR=%~dp0"
set "REPO_DIR=!REPO_DIR:~0,-1!"
echo   Path: !REPO_DIR!
echo.

:: Node.js check
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js not found.
    echo         Install LTS from https://nodejs.org and run again.
    start https://nodejs.org
    pause
    exit /b 1
)
echo [1/6] Node.js OK

:: Python check
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found.
    echo         Install Python 3.11+ from https://www.python.org
    echo         Check "Add Python to PATH" during install!
    start https://www.python.org/downloads/
    pause
    exit /b 1
)
echo [2/6] Python OK

:: Claude Code install
where claude >nul 2>&1
if errorlevel 1 (
    echo [3/6] Installing Claude Code...
    call npm install -g @anthropic/claude-code
    if errorlevel 1 (
        echo.
        echo [ERROR] Claude Code install failed.
        echo         Try: npm install -g @anthropic/claude-code
        pause
        exit /b 1
    )
    echo       Done
) else (
    echo [3/6] Claude Code already installed - skip
)

:: venv + packages
if not exist "!REPO_DIR!\company\venv" (
    echo [4/6] Creating Python venv...
    python -m venv "!REPO_DIR!\company\venv"
) else (
    echo [4/6] venv already exists - skip
)
echo       Installing packages...
"!REPO_DIR!\company\venv\Scripts\python.exe" -m pip install --upgrade pip -q
"!REPO_DIR!\company\venv\Scripts\python.exe" -m pip install -r "!REPO_DIR!\company\requirements.txt" -q
echo       Done

:: Update config paths
echo [5/6] Updating config paths...
"!REPO_DIR!\company\venv\Scripts\python.exe" "!REPO_DIR!\setup_paths.py" "!REPO_DIR!"
echo       Done

:: API keys
echo [6/6] API Key Setup
echo.

if not exist "!REPO_DIR!\company\.env" goto :setup_env
echo   .env already exists. Overwrite? (y/n, default=n):
set /p OVERWRITE=  Choice:
if /i "!OVERWRITE!"=="y" goto :setup_env
goto :done

:setup_env

echo.
echo   Anthropic key is required. Others are optional (press Enter to skip).
echo.

set /p OWNER=  Your name (e.g. Lian):
set /p ANTHROPIC=  Anthropic API key (required, sk-ant-...):

if "!ANTHROPIC!"=="" (
    echo.
    echo [ERROR] Anthropic API key is required. Run again.
    pause
    exit /b 1
)

set /p OPENAI=  OpenAI API key (optional):
set /p GOOGLE=  Google API key (optional):
set /p PERPLEXITY=  Perplexity API key (optional):
set /p DISCORD=  Discord Webhook URL (optional):

(
    echo OWNER_NAME=!OWNER!
    echo.
    echo ANTHROPIC_API_KEY=!ANTHROPIC!
    echo OPENAI_API_KEY=!OPENAI!
    echo GOOGLE_API_KEY=!GOOGLE!
    echo PERPLEXITY_API_KEY=!PERPLEXITY!
    echo.
    echo DISCORD_WEBHOOK_URL=!DISCORD!
    echo.
    echo CLOUDFLARE_API_TOKEN=
    echo CLOUDFLARE_ACCOUNT_ID=
    echo CF_PROJECT_NAME=
    echo PROJECT_URL=
    echo STITCH_API_KEY=
) > "!REPO_DIR!\company\.env"

echo.
echo   .env saved

:done
echo.
echo ============================================================
echo   Setup complete!
echo.
echo   How to run:
echo     1. Open terminal in this folder
echo     2. Type: claude
echo ============================================================
echo.
pause
