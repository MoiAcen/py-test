"""管理員頁面 - 系統管理、用戶管理、資料庫連線測試"""
import streamlit as st
import pandas as pd
from db.oracle import test_connection

# 模擬用戶資料【範本擴充點】placeholder，接手時請改為從資料庫/Graph API 取得
_MOCK_USERS = [
    {"ID": "U001", "姓名": "張管理員", "部門": "IT部門", "角色": "admin", "狀態": "✅ 啟用"},
    {"ID": "U002", "姓名": "李經理", "部門": "銷售部", "角色": "manager", "狀態": "✅ 啟用"},
    {"ID": "U003", "姓名": "王用戶", "部門": "運營部", "角色": "user", "狀態": "✅ 啟用"},
    {"ID": "U004", "姓名": "陳用戶", "部門": "行銷部", "角色": "user", "狀態": "⛔ 停用"},
    {"ID": "U005", "姓名": "林訪客", "部門": "-", "角色": "guest", "狀態": "✅ 啟用"},
]


def render():
    st.title("🛡️ 管理員控制台")
    st.markdown("---")

    # 概覽指標
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("總用戶數", "5", "+1")
    col2.metric("啟用用戶", "4", "0")
    col3.metric("角色數", "4", "0")
    col4.metric("系統狀態", "正常", "")

    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["👥 用戶管理", "🗄️ 資料庫", "⚙️ 系統設定"])

    with tab1:
        st.subheader("用戶列表")
        df = pd.DataFrame(_MOCK_USERS)
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.markdown("#### 新增用戶")
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            new_name = st.text_input("姓名")
        with col_b:
            new_dept = st.text_input("部門")
        with col_c:
            new_role = st.selectbox("角色", ["user", "manager", "admin", "guest"])
        if st.button("➕ 新增用戶", type="primary"):
            if new_name:
                st.success(f"用戶 {new_name} 已新增（模擬）")
            else:
                st.warning("請輸入姓名")

    with tab2:
        st.subheader("Oracle 資料庫連線測試")
        st.info("點擊下方按鈕測試與 Oracle 資料庫的連線狀態")

        if st.button("🔌 測試資料庫連線", type="primary"):
            with st.spinner("連線中..."):
                success, message = test_connection()
            if success:
                st.success(f"✅ {message}")
            else:
                st.error(f"❌ {message}")
                st.code(
                    "# 設定資料庫連線，請在 .env 設定以下環境變數:\n"
                    "ORACLE_HOST=your-host\n"
                    "ORACLE_PORT=1521\n"
                    "ORACLE_SERVICE=your-service\n"
                    "ORACLE_USER=your-user\n"
                    "ORACLE_PASSWORD_ENCRYPTED=<加密後的密碼>\n"
                    "FERNET_KEY=<執行 python -m config.crypto 產生>",
                    language="bash",
                )

        st.markdown("#### 執行查詢（示範）")
        query = st.text_area("SQL 查詢", value="SELECT 1 FROM DUAL", height=80)
        if st.button("▶️ 執行", disabled=True):
            st.warning("需要真實資料庫連線")

    with tab3:
        st.subheader("系統設定")

        col_s1, col_s2 = st.columns(2)
        with col_s1:
            st.markdown("**應用程式設定**")
            st.toggle("維護模式", value=False)
            st.toggle("詳細日誌", value=True)
            st.selectbox("預設語言", ["繁體中文", "简体中文", "English"])

        with col_s2:
            st.markdown("**安全設定**")
            st.toggle("強制 MFA", value=True, disabled=True)
            st.number_input("Session 逾時（分鐘）", min_value=5, max_value=480, value=60)
            st.number_input("最大登入失敗次數", min_value=3, max_value=10, value=5)

        if st.button("💾 儲存設定", type="primary"):
            st.success("設定已儲存（模擬）")
