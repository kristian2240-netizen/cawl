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

echo [CAWL] starting from %CAWL_DIR%
cd /d "%CAWL_DIR%"
uv run python -m test_project.main %*

endlocal
