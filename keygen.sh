#!/bin/bash
# 金鑰產生與密碼加密工具
# 用法:
#   bash keygen.sh              # 產生新的 Fernet 金鑰
#   bash keygen.sh encrypt      # 加密資料庫密碼（互動式）
#   bash keygen.sh decrypt      # 解密確認（互動式）

set -e

ACTION="${1:-keygen}"

# 讀取 .env（若存在）
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | grep -v '^$' | xargs)
fi

case "$ACTION" in
    keygen)
        echo "========================================"
        echo " Fernet 金鑰產生工具"
        echo "========================================"
        python -m config.crypto
        echo ""
        echo "[提示] 將上方 FERNET_KEY 與 ORACLE_PASSWORD_ENCRYPTED 填入 .env 檔案"
        ;;

    encrypt)
        echo "========================================"
        echo " 資料庫密碼加密工具"
        echo "========================================"
        if [ -z "$FERNET_KEY" ]; then
            echo "[錯誤] 未找到 FERNET_KEY，請先設定 .env 或執行: bash keygen.sh"
            exit 1
        fi
        read -rsp "請輸入要加密的資料庫密碼: " DB_PASS
        echo ""
        ENCRYPTED=$(python -m config.crypto encrypt "$DB_PASS")
        echo ""
        echo "[結果] 加密後密文:"
        echo "  ORACLE_PASSWORD_ENCRYPTED=${ENCRYPTED}"
        echo ""
        echo "[提示] 請將上方密文填入 .env 的 ORACLE_PASSWORD_ENCRYPTED"
        ;;

    decrypt)
        echo "========================================"
        echo " 密文解密確認工具"
        echo "========================================"
        if [ -z "$FERNET_KEY" ]; then
            echo "[錯誤] 未找到 FERNET_KEY，請先設定 .env"
            exit 1
        fi
        read -rp "請輸入要解密的密文: " CIPHER
        PLAIN=$(python -m config.crypto decrypt "$CIPHER")
        echo ""
        echo "[結果] 解密後明文: ${PLAIN}"
        ;;

    *)
        echo "用法:"
        echo "  bash keygen.sh              # 產生新的 Fernet 金鑰"
        echo "  bash keygen.sh encrypt      # 加密資料庫密碼"
        echo "  bash keygen.sh decrypt      # 解密確認"
        exit 1
        ;;
esac
