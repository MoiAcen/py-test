"""
访客页面 - 公开信息展示与登录引导
未登录用户或 guest 角色用户看到此页面
"""
import streamlit as st


def render() -> None:
    """渲染访客页面"""
    # 欢迎横幅
    st.markdown(
        """
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 40px;
            border-radius: 16px;
            text-align: center;
            margin-bottom: 30px;
        ">
            <h1 style="color: white; margin: 0; font-size: 2.5em;">欢迎使用企业数据平台</h1>
            <p style="color: rgba(255,255,255,0.85); font-size: 1.1em; margin-top: 10px;">
                Enterprise Data Platform powered by Azure Entra &amp; Oracle
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 功能介绍卡片
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
                <h3 style="margin-top:0; color:#667eea;">安全认证</h3>
                <p style="color:#555; font-size:0.9em;">
                    集成 Azure Entra ID (Azure AD) 单点登录，
                    企业级身份验证保障数据安全。
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
                    基于角色的访问控制 (RBAC)，
                    管理员、经理、普通用户权限分级管理。
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
                <h3 style="margin-top:0; color:#2ecc71;">加密连接</h3>
                <p style="color:#555; font-size:0.9em;">
                    Oracle 数据库密码使用 Fernet 对称加密存储，
                    保障数据库凭据安全。
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.divider()

    # 登录引导
    col_left, col_center, col_right = st.columns([1, 2, 1])
    with col_center:
        st.markdown("### 请先登录以访问完整功能")
        st.info(
            "点击左侧边栏的 **登录** 按钮，通过 Azure Entra ID 进行身份验证。\n\n"
            "演示模式下，可在顶部选择角色直接体验各功能页面。",
            icon="ℹ️",
        )

    st.divider()

    # 系统信息
    st.subheader("系统信息")
    info_col1, info_col2 = st.columns(2)
    with info_col1:
        st.markdown(
            """
            **技术栈**
            - Streamlit >= 1.35
            - MSAL (Microsoft Authentication Library)
            - oracledb (thin mode)
            - Fernet 加密 (cryptography)
            """
        )
    with info_col2:
        st.markdown(
            """
            **支持角色**
            - Admin（管理员）- 全功能访问
            - Manager（经理）- 数据与团队管理
            - User（普通用户）- 个人仪表盘
            - Guest（访客）- 本页面
            """
        )
