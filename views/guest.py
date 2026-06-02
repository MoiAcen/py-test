"""
訪客頁面 - 公開資訊展示與登入引導
未登入用戶或 guest 角色用戶看到此頁面
"""
import streamlit as st


def render() -> None:
    """渲染訪客頁面"""
    # 歡迎橫幅
    st.markdown(
        """
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 40px;
            border-radius: 16px;
            text-align: center;
            margin-bottom: 30px;
        ">
            <h1 style="color: white; margin: 0; font-size: 2.5em;">歡迎使用企業資料平台</h1>
            <p style="color: rgba(255,255,255,0.85); font-size: 1.1em; margin-top: 10px;">
                Enterprise Data Platform powered by Azure Entra &amp; Oracle
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 功能介紹卡片
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
            <div style="
                background: #f8f9fa;
                border-left: 4px solid #667eea;
                padding: 20px;
                border-radius: 8px;
                height: 160px;
            ">
                <h3 style="margin-top:0; color:#667eea;">安全認證</h3>
                <p style="color:#555; font-size:0.9em;">
                    整合 Azure Entra ID (Azure AD) 單一登入，
                    企業級身份驗證保障資料安全。
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
            <div style="
                background: #f8f9fa;
                border-left: 4px solid #764ba2;
                padding: 20px;
                border-radius: 8px;
                height: 160px;
            ">
                <h3 style="margin-top:0; color:#764ba2;">角色管控</h3>
                <p style="color:#555; font-size:0.9em;">
                    基於角色的存取控制 (RBAC)，
                    管理員、經理、普通用戶權限分級管理。
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            """
            <div style="
                background: #f8f9fa;
                border-left: 4px solid #2ecc71;
                padding: 20px;
                border-radius: 8px;
                height: 160px;
            ">
                <h3 style="margin-top:0; color:#2ecc71;">加密連線</h3>
                <p style="color:#555; font-size:0.9em;">
                    Oracle 資料庫密碼使用 Fernet 對稱加密儲存，
                    保障資料庫憑證安全。
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.divider()

    # 登入引導
    col_left, col_center, col_right = st.columns([1, 2, 1])
    with col_center:
        st.markdown("### 請先登入以存取完整功能")
        st.info(
            "點擊左側邊欄的 **登入** 按鈕，透過 Azure Entra ID 進行身份驗證。\n\n"
            "示範模式下，可在頂部選擇角色直接體驗各功能頁面。",
            icon="ℹ️",
        )

    st.divider()

    # 系統資訊
    st.subheader("系統資訊")
    info_col1, info_col2 = st.columns(2)
    with info_col1:
        st.markdown(
            """
            **技術棧**
            - Streamlit >= 1.35
            - MSAL (Microsoft Authentication Library)
            - oracledb (thin mode)
            - Fernet 加密 (cryptography)
            """
        )
    with info_col2:
        st.markdown(
            """
            **支援角色**
            - Admin（管理員）- 全功能存取
            - Manager（經理）- 資料與團隊管理
            - User（普通用戶）- 個人儀表板
            - Guest（訪客）- 本頁面
            """
        )
