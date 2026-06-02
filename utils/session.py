"""
Streamlit Session State 管理模块

统一管理会话状态的初始化、更新和清理，
避免在各页面中直接操作 st.session_state 导致的键名不一致问题。
"""
import streamlit as st

# 会话状态键名常量
_KEY_AUTHENTICATED = "authenticated"
_KEY_USER_INFO = "user_info"
_KEY_ROLE = "role"
_KEY_OAUTH_STATE = "oauth_state"
_KEY_DEMO_MODE = "demo_mode"


def init_session() -> None:
    """
    初始化所有会话状态键（仅在键不存在时设置默认值）
    应在 app.py 的最顶部调用。
    """
    defaults = {
        _KEY_AUTHENTICATED: False,
        _KEY_USER_INFO: {},
        _KEY_ROLE: "guest",
        _KEY_OAUTH_STATE: None,
        _KEY_DEMO_MODE: False,
    }
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value


def set_user(user_info: dict, role: str) -> None:
    """
    将用户信息和角色写入会话状态（登录成功后调用）

    Args:
        user_info: 用户信息字典（来自 MS Graph 或演示数据）
        role:      用户角色字符串（admin/manager/user/guest）
    """
    st.session_state[_KEY_AUTHENTICATED] = True
    st.session_state[_KEY_USER_INFO] = user_info
    st.session_state[_KEY_ROLE] = role


def clear_session() -> None:
    """
    清除用户会话（登出操作）
    重置认证状态，保留其他非认证状态。
    """
    st.session_state[_KEY_AUTHENTICATED] = False
    st.session_state[_KEY_USER_INFO] = {}
    st.session_state[_KEY_ROLE] = "guest"
    st.session_state[_KEY_OAUTH_STATE] = None


def is_authenticated() -> bool:
    """
    检查用户是否已通过认证

    Returns:
        True 表示已登录，False 表示未登录
    """
    return bool(st.session_state.get(_KEY_AUTHENTICATED, False))


def get_role() -> str:
    """
    获取当前用户角色

    Returns:
        角色字符串（默认为 "guest"）
    """
    return st.session_state.get(_KEY_ROLE, "guest")


def get_user_info() -> dict:
    """
    获取当前用户完整信息字典

    Returns:
        用户信息字典（未登录时返回空字典）
    """
    return st.session_state.get(_KEY_USER_INFO, {})


def get_display_name() -> str:
    """
    获取用户显示名称

    Returns:
        用户姓名字符串（未登录时返回 "未登录"）
    """
    user_info = get_user_info()
    return user_info.get("displayName", user_info.get("mail", "未登录"))


def set_oauth_state(state: str) -> None:
    """保存 OAuth state 参数（用于 CSRF 保护）"""
    st.session_state[_KEY_OAUTH_STATE] = state


def get_oauth_state() -> str | None:
    """获取保存的 OAuth state 参数"""
    return st.session_state.get(_KEY_OAUTH_STATE)
