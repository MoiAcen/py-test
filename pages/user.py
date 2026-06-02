"""
普通用户页面 - 个人仪表盘与数据查询
权限: view_user
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random

from utils.session import get_user_info, get_display_name


def _mock_personal_data() -> pd.DataFrame:
    """生成模拟的个人工作数据"""
    today = datetime.today()
    records = []
    for i in range(10):
        date = today - timedelta(days=i)
        records.append(
            {
                "日期": date.strftime("%Y-%m-%d"),
                "任务名称": random.choice(
                    ["数据整理", "报表生成", "客户跟进", "会议记录", "文档撰写"]
                ),
                "状态": random.choice(["已完成", "进行中", "待处理"]),
                "优先级": random.choice(["高", "中", "低"]),
                "耗时(h)": round(random.uniform(0.5, 8.0), 1),
            }
        )
    return pd.DataFrame(records)


def render() -> None:
    """渲染普通用户页面"""
    user_info = get_user_info()
    display_name = get_display_name()

    st.title(f"个人仪表盘")
    st.markdown(f"欢迎回来，**{display_name}**！")

    # 个人信息卡片
    with st.expander("个人信息", expanded=False):
        info_col1, info_col2 = st.columns(2)
        with info_col1:
            st.markdown(f"**邮箱:** {user_info.get('mail', 'N/A')}")
            st.markdown(f"**职位:** {user_info.get('jobTitle', 'N/A')}")
        with info_col2:
            st.markdown(f"**部门:** {user_info.get('department', 'N/A')}")
            st.markdown(f"**UPN:** {user_info.get('userPrincipalName', 'N/A')}")

    st.divider()

    # 个人统计指标
    st.subheader("本周工作概览")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("已完成任务", "12", "+3")
    m2.metric("进行中", "4", "-1")
    m3.metric("本周工时(h)", "38.5", "+2.5")
    m4.metric("待处理事项", "7", "+2")

    st.divider()

    # 数据查询表单
    st.subheader("数据查询")
    with st.form("query_form"):
        q_col1, q_col2 = st.columns(2)
        with q_col1:
            start_date = st.date_input(
                "开始日期",
                value=datetime.today() - timedelta(days=7),
            )
        with q_col2:
            end_date = st.date_input("结束日期", value=datetime.today())

        status_filter = st.multiselect(
            "状态筛选",
            options=["已完成", "进行中", "待处理"],
            default=["已完成", "进行中", "待处理"],
        )
        submitted = st.form_submit_button("查询", use_container_width=True)

    # 显示查询结果
    if submitted or True:  # 默认展示数据
        df = _mock_personal_data()
        if status_filter:
            df = df[df["状态"].isin(status_filter)]

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "优先级": st.column_config.SelectboxColumn(
                    options=["高", "中", "低"]
                ),
                "耗时(h)": st.column_config.NumberColumn(format="%.1f h"),
            },
        )
        st.caption(f"共 {len(df)} 条记录（演示数据）")
