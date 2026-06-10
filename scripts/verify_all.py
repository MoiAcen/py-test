"""
完整系統驗證腳本 — 整合 DB + Entra + 應用程式設定
執行方式: python scripts/verify_all.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from config.settings import settings

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))


def run_check(label: str, fn):
    """執行單項檢查並回傳結果"""
    try:
        ok, msg = fn()
        return ok, msg
    except Exception as e:
        return False, str(e)


def check_python_version() -> tuple[bool, str]:
    v = sys.version_info
    ok = v >= (3, 11)
    return ok, f"Python {v.major}.{v.minor}.{v.micro}（{'✓ 符合需求 >= 3.11' if ok else '✗ 需要 3.11+'}）"


def check_packages() -> tuple[bool, str]:
    required = ["streamlit", "msal", "oracledb", "cryptography", "dotenv", "requests", "jwt", "pandas"]
    missing = []
    for pkg in required:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)
    if missing:
        return False, f"缺少套件: {', '.join(missing)}（請執行 pip install -r requirements.txt）"
    return True, f"所有套件已安裝（{len(required)} 個）"


def check_env_file() -> tuple[bool, str]:
    if os.path.exists(".env"):
        return True, ".env 檔案存在"
    if os.path.exists(".env.tokens"):
        return True, ".env.tokens 存在（部署環境）"
    return False, ".env 檔案不存在，請複製 .env.example 並填入設定"


def check_app_mode() -> tuple[bool, str]:
    mode = settings.APP_MODE
    return True, f"應用模式: {mode}（{'Demo — 適用開發測試' if mode == 'demo' else 'Production — 需完整設定'}）"


def check_fernet_key() -> tuple[bool, str]:
    if not settings.FERNET_KEY:
        return False, "FERNET_KEY 未設定（執行 keygen.bat / keygen.sh 產生）"
    try:
        from cryptography.fernet import Fernet
        Fernet(settings.FERNET_KEY.encode())
        return True, f"FERNET_KEY 格式有效（長度: {len(settings.FERNET_KEY)} 字元）"
    except Exception as e:
        return False, f"FERNET_KEY 格式無效: {e}"


def check_db_decrypt() -> tuple[bool, str]:
    if not settings.ORACLE_PASSWORD_ENCRYPTED:
        return False, "ORACLE_PASSWORD_ENCRYPTED 未設定"
    if not settings.FERNET_KEY:
        return False, "FERNET_KEY 未設定，無法解密"
    try:
        from config.crypto import decrypt_password
        plain = decrypt_password(settings.ORACLE_PASSWORD_ENCRYPTED, settings.FERNET_KEY)
        return True, f"資料庫密碼解密成功（長度: {len(plain)} 字元）"
    except Exception as e:
        return False, f"解密失敗: {e}"


def check_db_connection() -> tuple[bool, str]:
    try:
        from db.oracle import test_connection
        return test_connection()
    except Exception as e:
        return False, str(e)


def check_entra_config() -> tuple[bool, str]:
    missing = [k for k, v in {
        "AZURE_CLIENT_ID":     settings.AZURE_CLIENT_ID,
        "AZURE_CLIENT_SECRET": settings.AZURE_CLIENT_SECRET,
        "AZURE_TENANT_ID":     settings.AZURE_TENANT_ID,
    }.items() if not v]
    if missing:
        return False, f"缺少: {', '.join(missing)}"
    return True, "Azure AD 設定齊全"


def check_entra_authority() -> tuple[bool, str]:
    if not settings.AZURE_TENANT_ID:
        return False, "AZURE_TENANT_ID 未設定，跳過"
    try:
        import requests
        url = f"{settings.AZURE_AUTHORITY}/.well-known/openid-configuration"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        return True, f"Authority 端點可連線"
    except Exception as e:
        return False, f"Authority 端點連線失敗: {e}"


def check_entra_credentials() -> tuple[bool, str]:
    if not all([settings.AZURE_CLIENT_ID, settings.AZURE_CLIENT_SECRET, settings.AZURE_TENANT_ID]):
        return False, "Azure AD 設定不完整，跳過"
    try:
        import msal
        app = msal.ConfidentialClientApplication(
            client_id=settings.AZURE_CLIENT_ID,
            client_credential=settings.AZURE_CLIENT_SECRET,
            authority=settings.AZURE_AUTHORITY,
        )
        result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
        if "access_token" in result:
            return True, "Client Credentials 驗證成功"
        return False, result.get("error_description", result.get("error", "未知錯誤"))
    except Exception as e:
        return False, str(e)


def print_section(title: str):
    print(f"\n{'─' * 56}")
    print(f"  {title}")
    print(f"{'─' * 56}")


def print_result(step: str, ok: bool, msg: str):
    icon = "✓" if ok else "✗"
    print(f"  {icon}  {step}")
    print(f"     {msg}")


def main():
    print("=" * 56)
    print("  企業資料平台 — 完整系統驗證")
    print("=" * 56)

    results = []

    # ── 基礎環境 ──────────────────────────────────────
    print_section("基礎環境")

    checks = [
        ("Python 版本",    check_python_version),
        ("套件安裝",        check_packages),
        (".env 檔案",      check_env_file),
        ("應用模式",        check_app_mode),
    ]
    for label, fn in checks:
        ok, msg = run_check(label, fn)
        print_result(label, ok, msg)
        results.append((label, ok))

    # ── 加密金鑰 ──────────────────────────────────────
    print_section("加密金鑰")

    checks = [
        ("FERNET_KEY 設定",    check_fernet_key),
        ("資料庫密碼解密",      check_db_decrypt),
    ]
    for label, fn in checks:
        ok, msg = run_check(label, fn)
        print_result(label, ok, msg)
        results.append((label, ok))

    # ── Oracle 資料庫 ──────────────────────────────────
    print_section("Oracle 資料庫")

    if settings.is_demo_mode():
        print("  ─  Demo 模式，跳過實際資料庫連線測試")
        print(f"     主機設定: {settings.ORACLE_HOST}:{settings.ORACLE_PORT}/{settings.ORACLE_SERVICE}")
    else:
        ok, msg = run_check("資料庫連線", check_db_connection)
        print_result("資料庫連線", ok, msg)
        results.append(("資料庫連線", ok))

    # ── Azure Entra ID ────────────────────────────────
    print_section("Azure Entra ID")

    if settings.is_demo_mode() and not settings.AZURE_CLIENT_ID:
        print("  ─  Demo 模式且未設定 Azure AD，跳過 Entra 驗證")
    else:
        checks = [
            ("Entra 設定",           check_entra_config),
            ("Authority 端點",        check_entra_authority),
            ("Client Credentials",    check_entra_credentials),
        ]
        for label, fn in checks:
            ok, msg = run_check(label, fn)
            print_result(label, ok, msg)
            results.append((label, ok))

    # ── 總結 ──────────────────────────────────────────
    passed = sum(1 for _, ok in results if ok)
    failed = [label for label, ok in results if not ok]

    print("\n" + "=" * 56)
    print(f"  驗證結果: {passed}/{len(results)} 通過")
    if failed:
        print(f"  ✗  未通過項目:")
        for f in failed:
            print(f"     - {f}")
        print("=" * 56)
        sys.exit(1)
    else:
        print("  ✓  所有驗證項目通過")
        print("=" * 56)


if __name__ == "__main__":
    main()
