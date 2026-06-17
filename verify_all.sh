#!/bin/bash
# 完整系統驗證（.env 由 python-dotenv 自動載入）
cd "$(dirname "$0")"
python scripts/verify_all.py
