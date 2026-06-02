#!/bin/bash
# Oracle 資料庫連線驗證
cd "$(dirname "$0")"
if [ -f ".env" ]; then export $(grep -v '^#' .env | grep -v '^$' | xargs); fi
python scripts/verify_db.py
