@echo off
REM 完整系統驗證（DB + Entra + 基礎環境）
setlocal enabledelayedexpansion
cd /d "%~dp0"
if exist ".env" (
    for /f "usebackq tokens=1,* delims==" %%A in (".env") do (
        set "ln=%%A"
        if not "!ln:~0,1!"=="#" if not "%%A"=="" set "%%A=%%B"
    )
)
python scripts\verify_all.py
endlocal
