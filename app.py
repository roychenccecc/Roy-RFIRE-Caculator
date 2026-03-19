# ---------------------------------------------------
# 你的第五台 RFIRE 财富推演机 (V4.0 真实通胀抵抗版)
# ---------------------------------------------------

import streamlit as st
import pandas as pd

st.set_page_config(page_title="我的 RFIRE 计算器", page_icon="🔥", layout="wide")
st.title("🔥 个人 RFIRE 财务路径推演系统 (V4.0 严谨抗通胀版)")

# --- 左侧边栏：参数输入区 ---
st.sidebar.header("📊 1. 财富与工作参数")
initial_assets = st.sidebar.number_input("初始资产 (元)", value=500000, step=50000)
max_working_years = st.sidebar.number_input("预计最多还能工作多少年？", value=20, min_value=1, max_value=50)
monthly_expense = st.sidebar.number_input("当前月支出 (元)", value=8000, step=1000)

st.sidebar.header("🎯 2. FIRE 退休期参数")
fire_monthly_expense = st.sidebar.number_input("RFIRE后月预计开支 (元)", value=12000, step=1000)

st.sidebar.header("📈 3. 市场与环境假设")
annual_return_rate = st.sidebar.number_input("预期名义年化收益率 (%)", value=8.0, step=0.5) / 100
annual_inflation_rate = st.sidebar.number_input("预计年通胀率 (%)", value=3.0, step=0.5) / 100
target_years = st.sidebar.slider("推演未来多少年？", min_value=10, max_value=50, value=30)

# --- 主界面：收入模式选择 ---
st.subheader("💼 设定你的未来收入路径")

income_mode = st.radio(
    "请选择你的收入预测模式：",
    ("简略模式 (基础工资 + 每年固定比例涨薪)", "逐年手动填入模式 (精准模拟薪资起伏)")
)

yearly_income_list = []

if income_mode == "简略模式":
    col1, col2 = st.columns(2) # 把输入框并排成两列，更美观
    with col1:
        simple_monthly_income = st.number_input("当前月收入 (元)", value=20000, step=1000)
    with col2:
        # 【V4.0 新增】：工资增长率输入
        income_growth_rate = st.number_input("预期每年工资增长率 (%)", value=5.0, step=0.5) / 100
    
    # 按照复利计算未来的预期工资
    current_calc_income = simple_monthly_income
    for y in range(target_years):
        yearly_income_list.append(current_calc_income)
        current_calc_income = current_calc_income * (1 + income_growth_rate) # 明年涨薪
        
else:
    st.write("请在下方的表格中，直接双击修改你未来每一年的预期【月收入】：")
    default_income_data = [{"年份": f"第 {i+1} 年", "预期月收入(元)": 20000} for i in range(target_years)]
    df_input = pd.DataFrame(default_income_data)
    edited_df = st.data_editor(df_input, use_container_width=True, hide_index=True)
    yearly_income_list = edited_df["预期月收入(元)"].tolist()

st.divider()

# --- 核心推演逻辑 ---
data_records = []
current_assets = initial_assets
current_monthly_expense = monthly_expense
current_fire_expense = fire_monthly_expense 
is_fired = False 

for year in range(1, target_years + 1):
    
    if year > max_working_years:
        current_monthly_income = 0
    else:
        current_monthly_income = yearly_income_list[year - 1]

    # 1. 计算名义理财收益
    investment_profit = current_assets * annual_return_rate
    
    # 【V4.0 核心逻辑升级】：计算对抗通胀所需的“护城河”资金
    # 这部分钱必须留在本金里滚存，不能花掉，否则本金购买力会缩水
    capital_preservation_need = current_assets * annual_inflation_rate
    
    # 真实可自由支配的被动收益
    real_passive_income = investment_profit - capital_preservation_need
    
    # 2. 严谨的 FIRE 判断：真实被动收益 >= 当年实际开支
    if real_passive_income >= (current_fire_expense * 12):
        is_fired = True
        
    # 3. 根据状态算账
    if is_fired:
        yearly_savings = 0 
        annual_expense = current_fire_expense * 12
        status_text = "🌴 永续 FIRE"
    else:
        yearly_savings = (current_monthly_income - current_monthly_expense) * 12
        if yearly_savings < 0:
            status_text = "⚠️ 消耗本金中"
        else:
            status_text = "💼 资本积累期"
        annual_expense = current_monthly_expense * 12
        
    # 4. 资产更新 (注意：总资产的增长依然是用 名义收益 + 结余)
    current_assets = current_assets + investment_profit + yearly_savings
    
    data_records.append({
        "年份": f"第 {year} 年",
        "生命周期": status_text,
        "总资产": current_assets,
        "抗通胀后真实收益": real_passive_income, # 记录严谨的真实收益
        "年度实际支出": annual_expense
    })
    
    # 5. 通胀计算：开支依然会随着通胀变大
    current_monthly_expense *= (1 + annual_inflation_rate)
    current_fire_expense *= (1 + annual_inflation_rate)

# --- 结果展示 ---
df_result = pd.DataFrame(data_records)

st.subheader("📈 永续 RFIRE 交叉点分析图 (已扣除通胀磨损)")
# 【V4.0 图表修复】：现在对比的是“真实收益”和“实际支出”
st.line_chart(df_result, x="年份", y=["抗通胀后真实收益", "年度实际支出"], color=["#00FF00", "#FF0000"])

st.subheader("📋 详细推演数据表")
st.dataframe(df_result)
