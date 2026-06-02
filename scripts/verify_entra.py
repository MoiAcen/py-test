"""
Azure Entra ID 登入驗證腳本
執行方式: python scripts/verify_entra.py
"""
import sys
import os
import json
import webbrowser
import http.server
import threading
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from config.settings import settings

# OAuth2 本機回呼用
CALLBACK_PORT = 8502
CALLBACK_PATH = "/callback"
_auth_code: dict = {}


def check_config() -> list[str]:
    """檢查 Entra 必要設定"""
    missing = []
    if not settings.AZURE_CLIENT_ID:
        missing.append("AZURE_CLIENT_ID")
    if not settings.AZURE_CLIENT_SECRET:
        missing.append("AZURE_CLIENT_SECRET")
    if not settings.AZURE_TENANT_ID:
        missing.append("AZURE_TENANT_ID")
    return missing


def verify_msal_import() -> tuple[bool, str]:
    """驗證 MSAL 套件可正常匯入"""
    try:
        import msal
        return True, f"msal {msal.__version__} 載入成功"
    except ImportError:
        return False, "msal 套件未安裝，請執行 pip install -r requirements.txt"


def verify_authority() -> tuple[bool, str]:
    """驗證 Tenant ID 對應的 Authority 端點可連線"""
    try:
        import requests
        url = f"{settings.AZURE_AUTHORITY}/.well-known/openid-configuration"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        issuer = data.get("issuer", "")
        return True, f"Authority 端點可連線 | Issuer: {issuer}"
    except Exception as e:
        return False, f"Authority 端點連線失敗: {e}"


def verify_client_credentials() -> tuple[bool, str]:
    """用 Client Credentials 驗證 Client ID / Secret 是否有效（不需用戶互動）"""
    try:
        import msal
        app = msal.ConfidentialClientApplication(
            client_id=settings.AZURE_CLIENT_ID,
            client_credential=settings.AZURE_CLIENT_SECRET,
            authority=settings.AZURE_AUTHORITY,
        )
        result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
        if "access_token" in result:
            return True, "Client Credentials 驗證成功（Client ID / Secret 有效）"
        error = result.get("error", "unknown")
        desc = result.get("error_description", "")
        return False, f"驗證失敗: {error} — {desc}"
    except Exception as e:
        return False, f"MSAL 例外: {e}"


def verify_interactive_login() -> tuple[bool, str]:
    """
    互動式登入驗證：
    開啟瀏覽器讓使用者實際登入，驗證授權碼流程是否正常。
    需要 AZURE_REDIRECT_URI 設定為 http://localhost:8502
    """
    try:
        import msal
        import requests
        import secrets

        redirect_uri = f"http://localhost:{CALLBACK_PORT}"
        state = secrets.token_urlsafe(16)

        app = msal.ConfidentialClientApplication(
            client_id=settings.AZURE_CLIENT_ID,
            client_credential=settings.AZURE_CLIENT_SECRET,
            authority=settings.AZURE_AUTHORITY,
        )
        auth_url = app.get_authorization_request_url(
            scopes=["User.Read"],
            state=state,
            redirect_uri=redirect_uri,
        )

        # 啟動本機 HTTP server 接收回呼
        received = {}

        class CallbackHandler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                parsed = urllib.parse.urlparse(self.path)
                params = dict(urllib.parse.parse_qsl(parsed.query))
                received.update(params)
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(
                    "<html><body><h2>✓ 登入成功，請關閉此視窗並返回終端機。</h2></body></html>".encode()
                )

            def log_message(self, *args):
                pass  # 靜默 server log

        server = http.server.HTTPServer(("localhost", CALLBACK_PORT), CallbackHandler)
        thread = threading.Thread(target=server.handle_request)
        thread.start()

        print(f"\n  → 正在開啟瀏覽器，請完成 Azure AD 登入...")
        print(f"     （若瀏覽器未自動開啟，請手動前往以下網址）")
        print(f"     {auth_url[:80]}...")
        webbrowser.open(auth_url)
        thread.join(timeout=120)

        if "code" not in received:
            return False, "等待逾時（120秒）或使用者取消登入"
        if received.get("state") != state:
            return False, "CSRF state 不符，可能遭受攻擊"

        # 用授權碼換取 token
        result = app.acquire_token_by_authorization_code(
            code=received["code"],
            scopes=["User.Read"],
            redirect_uri=redirect_uri,
        )
        if "access_token" not in result:
            return False, f"Token 交換失敗: {result.get('error_description', '')}"

        # 呼叫 Graph API 取得用戶資訊
        headers = {"Authorization": f"Bearer {result['access_token']}"}
        me = requests.get("https://graph.microsoft.com/v1.0/me", headers=headers, timeout=10).json()
        name = me.get("displayName", "")
        mail = me.get("mail") or me.get("userPrincipalName", "")
        return True, f"互動式登入成功 | 用戶: {name} <{mail}>"

    except Exception as e:
        return False, f"互動式登入例外: {e}"


def main():
    is_demo = settings.is_demo_mode()

    print("=" * 56)
    print("  Azure Entra ID 登入驗證")
    print("=" * 56)
    if is_demo:
        print("  ⚠  目前為 Demo 模式（APP_MODE=demo）")
        print("     將跳過互動式登入，僅驗證套件與設定")
        print()

    # 1. 設定檢查
    print("[1/4] 檢查環境變數設定...")
    missing = check_config()
    if missing:
        for m in missing:
            print(f"  ✗  缺少: {m}")
        if not is_demo:
            print("\n  生產模式需要完整 Azure AD 設定")
            sys.exit(1)
        else:
            print("  ⚠  Demo 模式下跳過後續 Azure AD 驗證")
    else:
        print(f"  ✓  設定齊全")
        print(f"     Tenant : {settings.AZURE_TENANT_ID}")
        print(f"     Client : {settings.AZURE_CLIENT_ID}")

    # 2. 套件驗證
    print("\n[2/4] 驗證 MSAL 套件...")
    ok, msg = verify_msal_import()
    print(f"  {'✓' if ok else '✗'}  {msg}")
    if not ok:
        sys.exit(1)

    if missing and is_demo:
        print("\n[3/4] 跳過 Authority 端點驗證（設定未齊全）")
        print("[4/4] 跳過互動式登入驗證（Demo 模式 + 設定未齊全）")
        print("\n" + "=" * 56)
        print("  ⚠  部分驗證已跳過（Demo 模式）")
        print("     填入完整 Azure AD 設定後重新執行可進行完整驗證")
        print("=" * 56)
        return

    # 3. Authority 端點
    print("\n[3/4] 驗證 Azure AD Authority 端點...")
    ok, msg = verify_authority()
    print(f"  {'✓' if ok else '✗'}  {msg}")
    if not ok:
        sys.exit(1)

    # 4. Client Credentials 驗證（非互動）
    print("\n[4/4] 驗證 Client ID / Secret...")
    ok, msg = verify_client_credentials()
    print(f"  {'✓' if ok else '✗'}  {msg}")
    if not ok:
        sys.exit(1)

    # 5. 互動式登入（可選，非 demo 模式）
    print()
    ans = input("是否進行互動式登入驗證（開啟瀏覽器）？[y/N] ").strip().lower()
    if ans == "y":
        print("\n[選用] 互動式登入驗證...")
        ok, msg = verify_interactive_login()
        print(f"  {'✓' if ok else '✗'}  {msg}")

    print("\n" + "=" * 56)
    print("  ✓  Azure Entra ID 驗證完成")
    print("=" * 56)


if __name__ == "__main__":
    main()
