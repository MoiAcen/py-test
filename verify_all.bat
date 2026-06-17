@echo off
chcp 65001 >nul
REM 完整系統驗證（.env 由 python-dotenv 自動載入）
cd /d "%~dp0"
python scripts\verify_all.py
