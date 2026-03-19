# ---------------------------------------------------
# 你的第十六台 RFIRE 财富推演机 (V14.0 双图表与精准除错版)
# ---------------------------------------------------

import streamlit as st
import pandas as pd

st.set_page_config(page_title="RFIRE 财富推演系统", page_icon="🔥", layout="wide")

st.sidebar.header("👤 0. 定制你的专属计划")
user_name = st.sidebar.text_input("请输入你的称呼：", value="探索者")
st.title(f"🔥 {user_name} 的 RFIRE 财务路径推演系统 (V14.0)")

with st.expander("💡 点击阅读：这套系统背后的硬核量化逻辑", expanded=False):
    st.markdown("""
    * **🛡️ 购买力平价：** 强制扣除通胀磨损，寻找真实的永续 FIRE 奇点。
    * **⚙️ 动态生命周期：** 引入真实年龄轴。彻底辞职后切换退休开支标准。
    * **⚖️ 命运平衡双轨：** 独立定制未来的黑天鹅(意外开支)与正向期权(意外收入)。
    * **🌉 养老底座与双轨资产：** 引入法定养老金。分离“名义资产”与“真实购买力资产”，打破金钱的数字幻觉。
    """)

# --- 左侧边栏参数 ---
st.sidebar.header("📊 1. 个人与财富参数")
current_age = st.sidebar.number_input("你的当前年龄 (岁)", value=30, min_value=18, max_value=100)
retire_age = st.sidebar.number_input("计划退休年龄 (岁)", value=40, min_value=current_age, max_value=100)
target_age = st.sidebar.number_input("推演至多少岁？ (岁)", value=85, min_value=retire_age, max_value=120)
initial_assets = st.sidebar.number_input("初始资产 (元)", value=500000, step=50000)
monthly_expense = st.sidebar.number_input("当前打工期月支出 (元)", value=8000, step=1000)

max_working_years = retire_age - current_age
target_years = target_age - current_age

st.sidebar.header("🎯 2. FIRE 退休期参数")
fire_monthly_expense = st.sidebar.number_input("RFIRE后月预计开支 (元)", value=12000, step=1000)

st.sidebar.header("📈 3. 市场与环境假设")
annual_return_rate = st.sidebar.number_input("预期名义年化收益率 (%)", value=8.0, step=0.5) / 100
annual_inflation_rate = st.sidebar.number_input("预计年通胀率 (%)", value=3.0, step=0.5) / 100

st.sidebar.header("🛡️ 4. 养老金底座")
monthly_pension = st.sidebar.number_input("预计退休金 (元/月, 当前物价)", value=3000, step=500)
pension_age = st.sidebar.number_input("法定领养老金年龄 (岁)", value=60, min_value=current_age, max_value=100)

# --- 主界面：未来主业收入设定 ---
st.subheader("💼 1. 设定你的未来【主业】收入路径")

income_mode = st.radio("请选择你的收入预测模式：", ("🚀 智能预填并支持微调", "✍️ 纯手动逐年填入"))
table_years = max_working_years

if "智能预填" in income_mode:
    col1, col2, col3 = st.columns(3)
    with col1: base_monthly = st.number_input("当前月收入 (元)", value=20000, step=1000)
    with col2: raise_rate = st.number_input("预计每年涨薪比例 (%)", value=5.0, step=0.5) / 100
    with col3: base_bonus = st.number_input("预计年终奖 (元/年)", value=50000, step=5000)
    current_params = f"{base_monthly}_{raise_rate}_{base_bonus}"
else:
    base_monthly, raise_rate, base_bonus = 20000.0, 0.05, 50000.0
    current_params = "manual"

def get_default_df(mode, years, b_m, r_r, b_b, start_age):
    data = []
    if "智能预填" in mode:
        c_m = b_m
        for i in range(years):
            data.append({"未来年份": f"第 {i+1} 年 ({start_age + i + 1}岁)", "主业月收入(元)": round(c_m, 2), "主业年终奖(元)": b_b})
            c_m *= (1 + r_r)
    else:
        for i in range(years):
            data.append({"未来年份": f"第 {i+1} 年 ({start_age + i + 1}岁)", "主业月收入(元)": 20000.0, "主业年终奖(元)": 50000.0})
    return pd.DataFrame(data)

if "base_df" not in st.session_state:
    st.session_state.base_df = get_default_df(income_mode, table_years, base_monthly, raise_rate, base_bonus, current_age)
    st.session_state.latest_edited_df = st.session_state.base_df.copy()
    st.session_state.last_mode = income_mode
    st.session_state.last_params = current_params
    st.session_state.last_years = table_years
    st.session_state.last_age = current_age

mode_changed = (st.session_state.last_mode != income_mode)
params_changed = (st.session_state.last_params != current_params)
years_changed = (st.session_state.last_years != table_years)
age_changed = (st.session_state.last_age != current_age)

if mode_changed or params_changed or age_changed:
    st.session_state.base_df = get_default_df(income_mode, table_years, base_monthly, raise_rate, base_bonus, current_age)
    if "income_table" in st.session_state: del st.session_state["income_table"]
elif years_changed:
    current_df = st.session_state.latest_edited_df
    current_len = len(current_df)
    if table_years > current_len:
        last_income = current_df.iloc[-1]["主业月收入(元)"] if current_len > 0 else 20000.0
        last_bonus = current_df.iloc[-1]["主业年终奖(元)"] if current_len > 0 else 50000.0
        new_rows = [{"未来年份": f"第 {i+1} 年 ({current_age + i + 1}岁)", "主业月收入(元)": last_income, "主业年终奖(元)": last_bonus} for i in range(current_len, table_years)]
        st.session_state.base_df = pd.concat([current_df, pd.DataFrame(new_rows)], ignore_index=True)
    elif table_years < current_len:
        st.session_state.base_df = current_df.head(table_years)
    if "income_table" in st.session_state: del st.session_state["income_table"]

st.session_state.last_mode = income_mode
st.session_state.last_params = current_params
st.session_state.last_years = table_years
