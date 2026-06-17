#!/bin/bash
# Azure Entra ID 登入驗證（.env 由 python-dotenv 自動載入）
cd "$(dirname "$0")"
python scripts/verify_entra.py
