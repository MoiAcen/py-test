"""
Streamlit Session State 管理模組

統一管理會話狀態的初始化、更新與清理，
避免在各頁面中直接操作 st.session_state 導致的鍵名不一致問題。
"""
import streamlit as st

# 會話狀態鍵名常數
_KEY_AUTHENTICATED = "authenticated"
_KEY_USER_INFO = "user_info"
_KEY_ROLE = "role"
_KEY_OAUTH_STATE = "oauth_state"
_KEY_DEMO_MODE = "demo_mode"


def init_session() -> None:
    """
    初始化所有會話狀態鍵（僅在鍵不存在時設定預設值）
    應在 app.py 的最頂部呼叫。
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
    將用戶資訊和角色寫入會話狀態（登入成功後呼叫）

    Args:
        user_info: 用戶資訊字典（來自 MS Graph 或示範資料）
        role:      用戶角色字串（admin/manager/user/guest）
    """
    st.session_state[_KEY_AUTHENTICATED] = True
    st.session_state[_KEY_USER_INFO] = user_info
    st.session_state[_KEY_ROLE] = role


def clear_session() -> None:
    """
    清除用戶會話（登出操作）
    重設認證狀態，保留其他非認證狀態。
    """
    st.session_state[_KEY_AUTHENTICATED] = False
    st.session_state[_KEY_USER_INFO] = {}
    st.session_state[_KEY_ROLE] = "guest"
    st.session_state[_KEY_OAUTH_STATE] = None


def is_authenticated() -> bool:
    """
    檢查用戶是否已通過認證

    Returns:
        True 表示已登入，False 表示未登入
    """
    return bool(st.session_state.get(_KEY_AUTHENTICATED, False))


def get_role() -> str:
    """
    取得當前用戶角色

    Returns:
        角色字串（預設為 "guest"）
    """
    return st.session_state.get(_KEY_ROLE, "guest")


def get_user_info() -> dict:
    """
    取得當前用戶完整資訊字典

    Returns:
        用戶資訊字典（未登入時回傳空字典）
    """
    return st.session_state.get(_KEY_USER_INFO, {})


def get_display_name() -> str:
    """
    取得用戶顯示名稱

    Returns:
        用戶姓名字串（未登入時回傳 "未登入"）
    """
    user_info = get_user_info()
    return user_info.get("displayName", user_info.get("mail", "未登入"))


def set_oauth_state(state: str) -> None:
    """儲存 OAuth state 參數（用於 CSRF 保護）"""
    st.session_state[_KEY_OAUTH_STATE] = state


def get_oauth_state() -> str | None:
    """取得已儲存的 OAuth state 參數"""
    return st.session_state.get(_KEY_OAUTH_STATE)
