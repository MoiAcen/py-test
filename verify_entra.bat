@echo off
chcp 65001 >nul
REM Azure Entra ID 登入驗證（.env 由 python-dotenv 自動載入）
cd /d "%~dp0"
python scripts\verify_entra.py
