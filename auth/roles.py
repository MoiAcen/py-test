"""
角色与权限定义模块

角色层级:
    admin   > manager > user > guest
    管理员  > 经理    > 用户 > 访客
"""
from config.settings import settings

# 角色权限映射表
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

# 角色显示名称（用于 UI）
ROLE_LABELS: dict[str, str] = {
    "admin":   "管理员 Admin",
    "manager": "经理 Manager",
    "user":    "用户 User",
    "guest":   "访客 Guest",
}

# 角色对应徽章颜色（Streamlit markdown 样式）
ROLE_COLORS: dict[str, str] = {
    "admin":   "#e74c3c",  # 红色
    "manager": "#e67e22",  # 橙色
    "user":    "#2ecc71",  # 绿色
    "guest":   "#95a5a6",  # 灰色
}


def has_permission(role: str, permission: str) -> bool:
    """
    检查给定角色是否拥有指定权限

    Args:
        role:       角色名称（admin/manager/user/guest）
        permission: 权限名称

    Returns:
        True 表示有权限，False 表示无权限
    """
    permissions = ROLES.get(role, [])
    return permission in permissions


def get_role_from_groups(groups: list[str]) -> str:
    """
    根据用户所属的 Azure AD 群组 ID 列表映射到应用角色

    优先级: admin > manager > user > guest

    Args:
        groups: 用户所属群组 ID 列表（来自 MS Graph /me/memberOf）

    Returns:
        角色字符串（"admin"/"manager"/"user"/"guest"）
    """
    group_role_map = settings.get_group_role_map()

    # 按优先级顺序检查
    priority_order = ["admin", "manager", "user"]

    # 收集用户所有匹配到的角色
    matched_roles: set[str] = set()
    for group_id in groups:
        role = group_role_map.get(group_id)
        if role and role in ROLES:
            matched_roles.add(role)

    # 返回最高优先级角色
    for role in priority_order:
        if role in matched_roles:
            return role

    # 没有匹配到任何群组，默认为访客
    return "guest"


def get_role_badge_html(role: str) -> str:
    """生成角色徽章 HTML 字符串（用于 st.markdown unsafe_allow_html）"""
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
