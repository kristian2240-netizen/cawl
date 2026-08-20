@echo off
setlocal
set "CAWL_DIR=C:\Users\Kristian\Documents\Test Project"

where uv >nul 2>&1
if errorlevel 1 (
    where "%USERPROFILE%\.local\bin\uv.exe" >nul 2>&1
    if errorlevel 1 (
        echo [CAWL] uv not found — install: powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
        exit /b 1
    )
    set "PATH=%USERPROFILE%\.local\bin;%PATH%"
)

cd /d "%CAWL_DIR%"

if "%1"=="" goto :start
if "%1"=="start" goto :start
if "%1"=="doctor" goto :doctor
if "%1"=="serve" goto :serve
if "%1"=="help" goto :help
if "%1"=="--help" goto :help
if "%1"=="-h" goto :help

echo [CAWL] Unknown command: %1
echo [CAWL] Run 'cawl help' for usage.
exit /b 1

:start
echo [CAWL] launching Electron app...
where node >nul 2>&1
if errorlevel 1 (
    echo [CAWL] node not found — falling back to browser mode
    uv run python -m test_project.main
    exit /b
)
where npx >nul 2>&1
if errorlevel 1 (
    echo [CAWL] npx not found — falling back to browser mode
    uv run python -m test_project.main
    exit /b
)
if not exist "node_modules\electron" (
    echo [CAWL] Electron not installed — run: npm install
    echo [CAWL] falling back to browser mode
    uv run python -m test_project.main
    exit /b
)
npx electron . %*
exit /b

:doctor
echo [CAWL] running diagnostics...
uv run python -m test_project.doctor %*
exit /b %errorlevel%

:serve
echo [CAWL] starting server only (no GUI)...
uv run python -m test_project.main %*
exit /b

:help
echo.
echo   ================================================
echo     C.A.W.L. v1.0 — Archmagos Dominus
echo     Belisarius Cawl, in service to the Void Dragon
echo   ================================================
echo.
echo   Commands:
echo.
echo     cawl              Launch the Electron app (default)
echo     cawl start        Launch the Electron app
echo     cawl serve        Start server only, no GUI (localhost:8123)
echo     cawl doctor       Run 38 diagnostic checks + auto-fix
echo     cawl help         Show this help
echo.
echo   Skills:
echo.
echo     /watch            Analyze any video (YouTube, TikTok, local)
echo     /wwv              Query WorldWideView geospatial globe
echo     DeepThink         Step-by-step reasoning (toggle in UI)
echo     WebFetch          Verify from web before answering
echo     Verify            Re-check every claim with confidence labels
echo.
echo   Config:
echo.
echo     cawl serve        then open http://localhost:8123
echo     CONFIG button     in-app settings for providers, voice, WWV
echo     cawl doctor       check for problems and auto-fix
echo.
echo   Docs:  https://github.com/kristian2240-netizen/cawl
echo.
exit /b

endlocal
