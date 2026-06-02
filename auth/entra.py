"""
Azure Entra (Azure AD) 认证模块 - 基于 MSAL 的 OAuth2 授权码流程

生产模式: 使用真实 MSAL 认证
演示模式: 返回模拟用户数据，无需真实 Azure AD 配置
"""
import secrets
import requests
from typing import Optional
import msal

from config.settings import settings
from auth.roles import get_role_from_groups

# MS Graph API 端点
GRAPH_BASE = "https://graph.microsoft.com/v1.0"

# 演示模式下的模拟用户数据
DEMO_USERS: dict[str, dict] = {
    "admin": {
        "id": "demo-admin-001",
        "displayName": "张管理员 (Demo Admin)",
        "mail": "admin@demo.local",
        "userPrincipalName": "admin@demo.local",
        "jobTitle": "系统管理员",
        "department": "IT部门",
        "groups": [],           # 演示模式下角色直接指定，不走群组映射
        "_demo_role": "admin",
    },
    "manager": {
        "id": "demo-manager-001",
        "displayName": "李经理 (Demo Manager)",
        "mail": "manager@demo.local",
        "userPrincipalName": "manager@demo.local",
        "jobTitle": "部门经理",
        "department": "销售部",
        "groups": [],
        "_demo_role": "manager",
    },
    "user": {
        "id": "demo-user-001",
        "displayName": "王用户 (Demo User)",
        "mail": "user@demo.local",
        "userPrincipalName": "user@demo.local",
        "jobTitle": "业务专员",
        "department": "运营部",
        "groups": [],
        "_demo_role": "user",
    },
    "guest": {
        "id": "demo-guest-001",
        "displayName": "访客 (Demo Guest)",
        "mail": "guest@demo.local",
        "userPrincipalName": "guest@demo.local",
        "jobTitle": "",
        "department": "",
        "groups": [],
        "_demo_role": "guest",
    },
}


def _build_msal_app() -> msal.ConfidentialClientApplication:
    """构建 MSAL 机密客户端应用实例"""
    return msal.ConfidentialClientApplication(
        client_id=settings.AZURE_CLIENT_ID,
        client_credential=settings.AZURE_CLIENT_SECRET,
        authority=settings.AZURE_AUTHORITY,
    )


def get_auth_url(state: Optional[str] = None) -> tuple[str, str]:
    """
    构建 Azure AD OAuth2 授权 URL

    Args:
        state: CSRF 保护状态参数（若为 None 则自动生成）

    Returns:
        (auth_url, state) 元组
    """
    if settings.is_demo_mode():
        # 演示模式：返回占位符 URL（实际上不会跳转）
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
    用授权码换取访问令牌

    Args:
        code:  OAuth2 授权码（来自回调 URL 参数 ?code=...）
        state: 状态参数（用于 CSRF 验证）

    Returns:
        包含 access_token 的令牌字典

    Raises:
        ValueError: 令牌交换失败
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
            f"令牌获取失败: {result.get('error')} - {result.get('error_description')}"
        )
    return result


def get_user_info(access_token: str) -> dict:
    """
    调用 MS Graph API 获取用户信息和所属群组

    Args:
        access_token: 有效的访问令牌

    Returns:
        用户信息字典（包含 groups 列表和 _role 字段）

    Raises:
        requests.HTTPError: API 调用失败
    """
    if settings.is_demo_mode():
        # 演示模式：返回空占位符（实际角色由 session 直接设置）
        return DEMO_USERS["guest"].copy()

    headers = {"Authorization": f"Bearer {access_token}"}

    # 获取基本用户信息
    me_resp = requests.get(f"{GRAPH_BASE}/me", headers=headers, timeout=10)
    me_resp.raise_for_status()
    user_info = me_resp.json()

    # 获取用户所属群组 ID
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
    演示模式：根据角色获取模拟用户信息

    Args:
        role: 目标角色（admin/manager/user/guest）

    Returns:
        模拟用户信息字典
    """
    return DEMO_USERS.get(role, DEMO_USERS["guest"]).copy()
