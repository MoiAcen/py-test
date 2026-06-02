@echo off
REM Azure Entra ID 登入驗證
setlocal enabledelayedexpansion
cd /d "%~dp0"
if exist ".env" (
    for /f "usebackq tokens=1,* delims==" %%A in (".env") do (
        set "ln=%%A"
        if not "!ln:~0,1!"=="#" if not "%%A"=="" set "%%A=%%B"
    )
)
python scripts\verify_entra.py
endlocal
