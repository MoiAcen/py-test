"""經理頁面 - 團隊概覽、資料報表"""
import streamlit as st
import pandas as pd
import random

# 模擬團隊績效資料
_MOCK_TEAM = [
    {"員工": "王用戶", "部門": "運營部", "本月完成件數": 42, "目標達成率": "95%", "狀態": "🟢 正常"},
    {"員工": "陳用戶", "部門": "行銷部", "本月完成件數": 28, "目標達成率": "70%", "狀態": "🟡 關注"},
    {"員工": "黃用戶", "部門": "運營部", "本月完成件數": 55, "目標達成率": "110%", "狀態": "🟢 超標"},
    {"員工": "林用戶", "部門": "行銷部", "本月完成件數": 15, "目標達成率": "38%", "狀態": "🔴 異常"},
    {"員工": "蔡用戶", "部門": "客服部", "本月完成件數": 38, "目標達成率": "85%", "狀態": "🟢 正常"},
]


def render():
    st.title("📊 經理儀表板")
    st.markdown("---")

    # 團隊指標
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("團隊人數", "5", "0")
    col2.metric("平均達成率", "79.6%", "-3.2%")
    col3.metric("本月總件數", "178", "+12")
    col4.metric("異常人員", "1", "+1", delta_color="inverse")

    st.markdown("---")

    tab1, tab2 = st.tabs(["👥 團隊績效", "📈 資料查詢"])

    with tab1:
        st.subheader("本月團隊績效")
        df = pd.DataFrame(_MOCK_TEAM)
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.markdown("#### 📤 匯出報表")
        col_e1, col_e2, col_e3 = st.columns(3)
        with col_e1:
            st.button("匯出 Excel", disabled=True, help="需要連線正式環境")
        with col_e2:
            st.button("匯出 PDF", disabled=True, help="需要連線正式環境")
        with col_e3:
            st.button("寄送報表", disabled=True, help="需要連線正式環境")

    with tab2:
        st.subheader("資料篩選查詢")
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            dept_filter = st.multiselect(
                "選擇部門",
                ["運營部", "行銷部", "客服部"],
                default=["運營部", "行銷部", "客服部"],
            )
        with col_f2:
            status_filter = st.selectbox("狀態篩選", ["全部", "🟢 正常", "🟡 關注", "🔴 異常"])

        df_filtered = pd.DataFrame(_MOCK_TEAM)
        if dept_filter:
            df_filtered = df_filtered[df_filtered["部門"].isin(dept_filter)]
        if status_filter != "全部":
            df_filtered = df_filtered[df_filtered["狀態"] == status_filter]

        st.dataframe(df_filtered, use_container_width=True, hide_index=True)
        st.caption(f"共 {len(df_filtered)} 筆記錄")
