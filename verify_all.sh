#!/bin/bash
# 完整系統驗證（DB + Entra + 基礎環境）
cd "$(dirname "$0")"
if [ -f ".env" ]; then export $(grep -v '^#' .env | grep -v '^$' | xargs); fi
python scripts/verify_all.py
