"""
Oracle 資料庫連線驗證腳本
執行方式: python scripts/verify_db.py
"""
import sys
import os

# Windows cmd 預設 cp950，強制 UTF-8 輸出避免繁體中文亂碼
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

# 將專案根目錄加入 path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from config.settings import settings
from config.crypto import decrypt_password


def check_config() -> list[str]:
    """檢查必要設定是否齊全"""
    missing = []
    if not settings.FERNET_KEY:
        missing.append("FERNET_KEY")
    if not settings.ORACLE_PASSWORD_ENCRYPTED:
        missing.append("ORACLE_PASSWORD_ENCRYPTED")
    if not settings.ORACLE_HOST or settings.ORACLE_HOST == "localhost":
        missing.append("ORACLE_HOST（目前為預設值 localhost）")
    if not settings.ORACLE_USER or settings.ORACLE_USER == "system":
        missing.append("ORACLE_USER（目前為預設值 system）")
    return missing


def verify_decrypt() -> tuple[bool, str]:
    """驗證金鑰與密文是否匹配"""
    try:
        plain = decrypt_password(settings.ORACLE_PASSWORD_ENCRYPTED, settings.FERNET_KEY)
        return True, f"解密成功（密碼長度: {len(plain)} 字元）"
    except Exception as e:
        return False, f"解密失敗: {e}"


def verify_connection() -> tuple[bool, str]:
    """實際測試資料庫連線"""
    try:
        import oracledb
        from db.oracle import test_connection
        ok, msg = test_connection()
        return ok, msg
    except ImportError:
        return False, "oracledb 套件未安裝，請執行 pip install -r requirements.txt"
    except Exception as e:
        return False, f"連線例外: {e}"


def verify_query() -> tuple[bool, str]:
    """執行簡單查詢驗證讀取權限"""
    try:
        from db.oracle import execute_query
        cols, rows = execute_query("SELECT SYSDATE, USER FROM DUAL")
        if rows:
            return True, f"查詢成功 | 資料庫時間: {rows[0][0]} | 使用者: {rows[0][1]}"
        return False, "查詢無回傳結果"
    except Exception as e:
        return False, f"查詢失敗: {e}"


def main():
    print("=" * 56)
    print("  Oracle 資料庫連線驗證")
    print("=" * 56)

    # 1. 設定檢查
    print("\n[1/4] 檢查環境變數設定...")
    missing = check_config()
    if missing:
        print(f"  ⚠  以下設定未完整:")
        for m in missing:
            print(f"     - {m}")
        if "FERNET_KEY" in missing or "ORACLE_PASSWORD_ENCRYPTED" in missing:
            print("\n  請先執行 keygen.bat / keygen.sh 產生金鑰並加密密碼")
            sys.exit(1)
    else:
        print("  ✓  所有必要設定已齊全")
    print(f"     主機: {settings.ORACLE_HOST}:{settings.ORACLE_PORT}/{settings.ORACLE_SERVICE}")
    print(f"     用戶: {settings.ORACLE_USER}")

    # 2. 解密驗證
    print("\n[2/4] 驗證金鑰與密碼解密...")
    ok, msg = verify_decrypt()
    status = "✓" if ok else "✗"
    print(f"  {status}  {msg}")
    if not ok:
        sys.exit(1)

    # 3. 連線測試
    print("\n[3/4] 測試資料庫連線...")
    ok, msg = verify_connection()
    status = "✓" if ok else "✗"
    print(f"  {status}  {msg}")
    if not ok:
        print("\n  常見原因:")
        print("  - Oracle 主機無法連線（防火牆/網路）")
        print("  - 服務名稱或埠號錯誤")
        print("  - 帳號密碼錯誤")
        sys.exit(1)

    # 4. 查詢驗證
    print("\n[4/4] 執行驗證查詢（SELECT SYSDATE FROM DUAL）...")
    ok, msg = verify_query()
    status = "✓" if ok else "✗"
    print(f"  {status}  {msg}")

    print("\n" + "=" * 56)
    if ok:
        print("  ✓  Oracle 資料庫驗證全部通過")
    else:
        print("  ✗  部分驗證未通過，請檢查上方訊息")
        sys.exit(1)
    print("=" * 56)


if __name__ == "__main__":
    main()
