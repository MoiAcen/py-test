@echo off
REM Oracle 資料庫連線驗證（.env 由 python-dotenv 自動載入）
cd /d "%~dp0"
python scripts\verify_db.py
