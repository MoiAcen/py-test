"""
普通用戶頁面 - 個人儀表板與資料查詢
權限: view_user
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random

from utils.session import get_user_info, get_display_name


def _mock_personal_data() -> pd.DataFrame:
    """
    產生模擬的個人工作資料

    【範本擴充點】這是 placeholder。接手時請改為呼叫
    db.oracle.execute_query(...) 取得真實資料並回傳 DataFrame。
    """
    today = datetime.today()
    records = []
    for i in range(10):
        date = today - timedelta(days=i)
        records.append(
            {
                "日期": date.strftime("%Y-%m-%d"),
                "任務名稱": random.choice(
                    ["資料整理", "報表產生", "客戶跟進", "會議記錄", "文件撰寫"]
                ),
                "狀態": random.choice(["已完成", "進行中", "待處理"]),
                "優先等級": random.choice(["高", "中", "低"]),
                "工時(h)": round(random.uniform(0.5, 8.0), 1),
            }
        )
    return pd.DataFrame(records)


def render() -> None:
    """渲染普通用戶頁面"""
    user_info = get_user_info()
    display_name = get_display_name()

    st.title("個人儀表板")
    st.markdown(f"歡迎回來，**{display_name}**！")

    # 個人資訊卡片
    with st.expander("個人資訊", expanded=False):
        info_col1, info_col2 = st.columns(2)
        with info_col1:
            st.markdown(f"**郵箱:** {user_info.get('mail', 'N/A')}")
            st.markdown(f"**職位:** {user_info.get('jobTitle', 'N/A')}")
        with info_col2:
            st.markdown(f"**部門:** {user_info.get('department', 'N/A')}")
            st.markdown(f"**UPN:** {user_info.get('userPrincipalName', 'N/A')}")

    st.divider()

    # 個人統計指標
    st.subheader("本週工作概覽")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("已完成任務", "12", "+3")
    m2.metric("進行中", "4", "-1")
    m3.metric("本週工時(h)", "38.5", "+2.5")
    m4.metric("待處理事項", "7", "+2")

    st.divider()

    # 資料查詢表單
    st.subheader("資料查詢")
    with st.form("query_form"):
        q_col1, q_col2 = st.columns(2)
        with q_col1:
            # 【擴充點】日期區間欄位。實務上請將 start_date 帶入 DB 查詢條件，
            # 例如 db.oracle.execute_query 的 WHERE 子句參數。
            start_date = st.date_input(
                "開始日期",
                value=datetime.today() - timedelta(days=7),
            )
        with q_col2:
            # 【擴充點】結束日期，同上。
            end_date = st.date_input("結束日期", value=datetime.today())

        status_filter = st.multiselect(
            "狀態篩選",
            options=["已完成", "進行中", "待處理"],
            default=["已完成", "進行中", "待處理"],
        )
        submitted = st.form_submit_button("查詢", use_container_width=True)

    # 顯示查詢結果
    # 【範本說明】此處固定顯示模擬資料，submitted 與日期區間尚未實際套用查詢。
    # 接手時請依 submitted 觸發真實查詢，並用 start_date / end_date 過濾。
    if submitted:
        st.toast("已送出查詢（範本目前回傳模擬資料）", icon="🔍")

    df = _mock_personal_data()
    if status_filter:
        df = df[df["狀態"].isin(status_filter)]

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "優先等級": st.column_config.SelectboxColumn(
                options=["高", "中", "低"]
            ),
            "工時(h)": st.column_config.NumberColumn(format="%.1f h"),
        },
    )
    st.caption(f"共 {len(df)} 筆記錄（示範資料）")
