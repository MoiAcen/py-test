"""
企業資料平台 - Streamlit 主入口

功能:
- Azure Entra ID (MSAL) OAuth2 授權碼流程登入
- 角色型存取控制 (RBAC): admin / manager / user / guest
- Oracle 資料庫連線（Fernet 加密密碼）
- Demo 模式：無需真實 Azure AD，直接選角色測試
"""
import streamlit as st

# --- 頁面基本設定（必須是第一個 Streamlit 呼叫）---
st.set_page_config(
    page_title="企業資料平台",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
)

from config.settings import settings
from auth.entra import get_auth_url, get_token_from_code, get_user_info, get_demo_user
from auth.roles import get_role_badge_html, ROLE_LABELS
from utils.session import (
    init_session,
    set_user,
    clear_session,
    is_authenticated,
    get_role,
    get_display_name,
    set_oauth_state,
    get_oauth_state,
)
from pages import admin, manager, user, guest

# 初始化 session state
init_session()


def _handle_oauth_callback():
    """處理 Azure AD OAuth2 回呼（?code=...&state=...）"""
    params = st.query_params
    code = params.get("code")
    state = params.get("state")

    if not code:
        return

    # 清除 URL 參數，避免重複處理
    st.query_params.clear()

    # CSRF 驗證
    saved_state = get_oauth_state()
    if saved_state and state != saved_state:
        st.error("⚠️ 安全驗證失敗（state 不符），請重新登入。")
        return

    try:
        with st.spinner("正在驗證身份..."):
            token = get_token_from_code(code, state or "")
            user_info = get_user_info(token["access_token"])
            role = user_info.get("_role", "guest")
            set_user(user_info, role)
        st.success(f"✅ 登入成功！歡迎 {user_info.get('displayName', '')}")
        st.rerun()
    except Exception as e:
        st.error(f"❌ 登入失敗：{e}")


def _render_demo_role_selector():
    """Demo 模式頂部角色選擇器"""
    st.warning(
        "🧪 **Demo 模式** — 選擇角色直接體驗各功能頁面（不需要真實 Azure AD）",
        icon="🧪",
    )
    cols = st.columns([2, 1, 1])
    with cols[0]:
        role_options = list(ROLE_LABELS.keys())
        labels = [ROLE_LABELS[r] for r in role_options]
        current_role = get_role() if is_authenticated() else "guest"
        current_idx = role_options.index(current_role) if current_role in role_options else 3

        selected_label = st.selectbox(
            "選擇測試角色",
            labels,
            index=current_idx,
            key="demo_role_selector",
            label_visibility="collapsed",
        )
        selected_role = role_options[labels.index(selected_label)]

    with cols[1]:
        if st.button("🔑 以此角色登入", use_container_width=True, type="primary"):
            demo_user = get_demo_user(selected_role)
            set_user(demo_user, selected_role)
            st.rerun()

    with cols[2]:
        if is_authenticated() and st.button("🚪 登出", use_container_width=True):
            clear_session()
            st.rerun()


def _render_sidebar():
    """渲染側邊欄：用戶資訊、登入/登出按鈕"""
    with st.sidebar:
        st.markdown("## 🏢 企業資料平台")
        st.markdown("---")

        if is_authenticated():
            # 已登入：顯示用戶資訊
            role = get_role()
            name = get_display_name()

            st.markdown(f"**{name}**")
            st.markdown(
                get_role_badge_html(role),
                unsafe_allow_html=True,
            )
            st.markdown("")

            if st.button("🚪 登出", use_container_width=True):
                clear_session()
                st.rerun()
        else:
            # 未登入
            st.markdown("尚未登入")
            st.markdown("")

            if settings.is_demo_mode():
                st.info("目前為 Demo 模式\n請在頂部選擇角色")
            else:
                if st.button("🔑 Azure AD 登入", use_container_width=True, type="primary"):
                    auth_url, state = get_auth_url()
                    set_oauth_state(state)
                    st.markdown(
                        f'<meta http-equiv="refresh" content="0; url={auth_url}">',
                        unsafe_allow_html=True,
                    )

        st.markdown("---")

        # 導航說明
        st.markdown("#### 頁面導覽")
        role = get_role()
        nav_items = {
            "admin":   ["🛡️ 管理員控制台", "📊 經理儀表板", "👤 個人頁面"],
            "manager": ["📊 經理儀表板", "👤 個人頁面"],
            "user":    ["👤 個人頁面"],
            "guest":   ["🌐 訪客首頁"],
        }
        for item in nav_items.get(role, ["🌐 訪客首頁"]):
            st.markdown(f"- {item}")

        st.markdown("---")
        st.caption(f"模式: {'🧪 Demo' if settings.is_demo_mode() else '🔒 Production'}")


def _render_main_content():
    """根據當前角色渲染對應頁面"""
    if not is_authenticated():
        guest.render()
        return

    role = get_role()

    if role == "admin":
        admin.render()
    elif role == "manager":
        manager.render()
    elif role == "user":
        user.render()
    else:
        guest.render()


def main():
    # 1. 處理 OAuth 回呼
    _handle_oauth_callback()

    # 2. Demo 模式頂部角色選擇器
    if settings.is_demo_mode():
        _render_demo_role_selector()
        st.markdown("---")

    # 3. 側邊欄
    _render_sidebar()

    # 4. 主要內容
    _render_main_content()


if __name__ == "__main__":
    main()
