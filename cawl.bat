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
echo   C.A.W.L. — Belisarius Cawl, Archmagos Dominus
echo.
echo   Usage:  cawl [command]
echo.
echo   Commands:
echo     start     Launch the Electron app (default)
echo     serve     Start the server only (browser at localhost:8123)
echo     doctor    Run diagnostics and auto-fix
echo     help      Show this help
echo.
echo   Examples:
echo     cawl              Launch the app
echo     cawl doctor       Check for problems
echo     cawl serve        Run server without GUI
echo.
exit /b

endlocal
