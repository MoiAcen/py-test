"""
角色與權限定義模組

角色層級:
    admin   > manager > user > guest
    管理員  > 經理    > 用戶 > 訪客
"""
from config.settings import settings

# 角色權限對應表
ROLES: dict[str, list[str]] = {
    "admin": [
        "view_admin",
        "view_manager",
        "view_user",
        "manage_users",
        "view_db",
    ],
    "manager": [
        "view_manager",
        "view_user",
        "view_db",
    ],
    "user": [
        "view_user",
    ],
    "guest": [],
}

# 所有合法角色
ALL_ROLES: list[str] = list(ROLES.keys())

# 角色顯示名稱（用於 UI）
ROLE_LABELS: dict[str, str] = {
    "admin":   "管理員 Admin",
    "manager": "經理 Manager",
    "user":    "用戶 User",
    "guest":   "訪客 Guest",
}

# 角色對應徽章顏色（Streamlit markdown 樣式）
ROLE_COLORS: dict[str, str] = {
    "admin":   "#e74c3c",  # 紅色
    "manager": "#e67e22",  # 橙色
    "user":    "#2ecc71",  # 綠色
    "guest":   "#95a5a6",  # 灰色
}


def has_permission(role: str, permission: str) -> bool:
    """
    檢查給定角色是否擁有指定權限

    Args:
        role:       角色名稱（admin/manager/user/guest）
        permission: 權限名稱

    Returns:
        True 表示有權限，False 表示無權限
    """
    permissions = ROLES.get(role, [])
    return permission in permissions


def get_role_from_groups(groups: list[str]) -> str:
    """
    依據用戶所屬的 Azure AD 群組 ID 清單對應至應用角色

    優先等級: admin > manager > user > guest

    Args:
        groups: 用戶所屬群組 ID 清單（來自 MS Graph /me/memberOf）

    Returns:
        角色字串（"admin"/"manager"/"user"/"guest"）
    """
    group_role_map = settings.get_group_role_map()

    # 按優先等級順序檢查
    priority_order = ["admin", "manager", "user"]

    # 收集用戶所有匹配到的角色
    matched_roles: set[str] = set()
    for group_id in groups:
        role = group_role_map.get(group_id)
        if role and role in ROLES:
            matched_roles.add(role)

    # 回傳最高優先等級角色
    for role in priority_order:
        if role in matched_roles:
            return role

    # 沒有匹配到任何群組，預設為訪客
    return "guest"


def get_role_badge_html(role: str) -> str:
    """產生角色徽章 HTML 字串（用於 st.markdown unsafe_allow_html）"""
    label = ROLE_LABELS.get(role, role)
    color = ROLE_COLORS.get(role, "#95a5a6")
    return (
        f'<span style="'
        f"background-color:{color};"
        f"color:white;"
        f"padding:2px 10px;"
        f"border-radius:12px;"
        f"font-size:0.85em;"
        f"font-weight:600;"
        f'">{label}</span>'
    )
