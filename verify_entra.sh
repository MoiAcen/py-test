#!/bin/bash
# Azure Entra ID 登入驗證
cd "$(dirname "$0")"
if [ -f ".env" ]; then export $(grep -v '^#' .env | grep -v '^$' | xargs); fi
python scripts/verify_entra.py
