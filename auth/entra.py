"""
Azure Entra (Azure AD) 認證模組 - 基於 MSAL 的 OAuth2 授權碼流程

生產模式: 使用真實 MSAL 認證
示範模式: 回傳模擬用戶資料，無需真實 Azure AD 設定
"""
import secrets
import requests
from typing import Optional
import msal

from config.settings import settings
from auth.roles import get_role_from_groups

# MS Graph API 端點
GRAPH_BASE = "https://graph.microsoft.com/v1.0"

# 示範模式下的模擬用戶資料
# 註：`_demo_role` 欄位與字典 key 相同，刻意保留作為資料結構的自我說明
#     （讓接手者一眼看出每筆模擬用戶對應的角色）；實際角色由 app.py 明確傳入。
# 【範本擴充點】可在此調整模擬用戶屬性，或新增更多測試帳號。
DEMO_USERS: dict[str, dict] = {
    "admin": {
        "id": "demo-admin-001",
        "displayName": "張管理員 (Demo Admin)",
        "mail": "admin@demo.local",
        "userPrincipalName": "admin@demo.local",
        "jobTitle": "系統管理員",
        "department": "IT部門",
        "groups": [],           # 示範模式下角色直接指定，不走群組對應
        "_demo_role": "admin",
    },
    "manager": {
        "id": "demo-manager-001",
        "displayName": "李經理 (Demo Manager)",
        "mail": "manager@demo.local",
        "userPrincipalName": "manager@demo.local",
        "jobTitle": "部門經理",
        "department": "銷售部",
        "groups": [],
        "_demo_role": "manager",
    },
    "user": {
        "id": "demo-user-001",
        "displayName": "王用戶 (Demo User)",
        "mail": "user@demo.local",
        "userPrincipalName": "user@demo.local",
        "jobTitle": "業務專員",
        "department": "運營部",
        "groups": [],
        "_demo_role": "user",
    },
    "guest": {
        "id": "demo-guest-001",
        "displayName": "訪客 (Demo Guest)",
        "mail": "guest@demo.local",
        "userPrincipalName": "guest@demo.local",
        "jobTitle": "",
        "department": "",
        "groups": [],
        "_demo_role": "guest",
    },
}


def _build_msal_app() -> msal.ConfidentialClientApplication:
    """建立 MSAL 機密用戶端應用程式實例"""
    return msal.ConfidentialClientApplication(
        client_id=settings.AZURE_CLIENT_ID,
        client_credential=settings.AZURE_CLIENT_SECRET,
        authority=settings.AZURE_AUTHORITY,
    )


def get_auth_url(state: Optional[str] = None) -> tuple[str, str]:
    """
    建立 Azure AD OAuth2 授權 URL

    Args:
        state: CSRF 保護狀態參數（若為 None 則自動產生）

    Returns:
        (auth_url, state) 元組
    """
    if settings.is_demo_mode():
        # 示範模式：回傳占位符 URL（實際上不會跳轉）
        state = state or secrets.token_urlsafe(16)
        return ("#demo-mode", state)

    state = state or secrets.token_urlsafe(16)
    app = _build_msal_app()
    auth_url = app.get_authorization_request_url(
        scopes=settings.AZURE_SCOPES,
        state=state,
        redirect_uri=settings.AZURE_REDIRECT_URI,
    )
    return (auth_url, state)


def get_token_from_code(code: str, state: str) -> dict:
    """
    用授權碼換取存取權杖

    Args:
        code:  OAuth2 授權碼（來自回呼 URL 參數 ?code=...）
        state: 狀態參數（用於 CSRF 驗證）

    Returns:
        包含 access_token 的權杖字典

    Raises:
        ValueError: 權杖交換失敗
    """
    if settings.is_demo_mode():
        return {"access_token": "demo-token", "token_type": "Bearer"}

    app = _build_msal_app()
    result = app.acquire_token_by_authorization_code(
        code=code,
        scopes=settings.AZURE_SCOPES,
        redirect_uri=settings.AZURE_REDIRECT_URI,
    )
    if "error" in result:
        raise ValueError(
            f"權杖取得失敗: {result.get('error')} - {result.get('error_description')}"
        )
    return result


def get_user_info(access_token: str) -> dict:
    """
    呼叫 MS Graph API 取得用戶資訊和所屬群組

    Args:
        access_token: 有效的存取權杖

    Returns:
        用戶資訊字典（包含 groups 清單和 _role 欄位）

    Raises:
        requests.HTTPError: API 呼叫失敗
    """
    if settings.is_demo_mode():
        # 示範模式：回傳空占位符（實際角色由 session 直接設定）
        return DEMO_USERS["guest"].copy()

    headers = {"Authorization": f"Bearer {access_token}"}

    # 取得基本用戶資訊
    me_resp = requests.get(f"{GRAPH_BASE}/me", headers=headers, timeout=10)
    me_resp.raise_for_status()
    user_info = me_resp.json()

    # 取得用戶所屬群組 ID
    groups_resp = requests.get(
        f"{GRAPH_BASE}/me/memberOf?$select=id",
        headers=headers,
        timeout=10,
    )
    groups_resp.raise_for_status()
    groups_data = groups_resp.json()
    group_ids = [g["id"] for g in groups_data.get("value", [])]

    user_info["groups"] = group_ids
    user_info["_role"] = get_role_from_groups(group_ids)
    return user_info


def get_demo_user(role: str) -> dict:
    """
    示範模式：依角色取得模擬用戶資訊

    Args:
        role: 目標角色（admin/manager/user/guest）

    Returns:
        模擬用戶資訊字典
    """
    return DEMO_USERS.get(role, DEMO_USERS["guest"]).copy()
