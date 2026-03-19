# ---------------------------------------------------
# 你的第三台 RFIRE 财富推演机 (V2.1 引入状态切换逻辑)
# ---------------------------------------------------

import streamlit as st
import pandas as pd

st.set_page_config(page_title="我的 RFIRE 计算器", page_icon="🔥")
st.title("🔥 个人 RFIRE 财务路径推演系统 (V2.1)")

st.sidebar.header("📊 1. 财富积累期参数")
initial_assets = st.sidebar.number_input("初始资产 (元)", value=500000, step=50000)
monthly_income = st.sidebar.number_input("当前月收入 (元)", value=20000, step=1000)
monthly_expense = st.sidebar.number_input("当前月支出 (元)", value=8000, step=1000)

# 【新增模块】：FIRE 后的目标设定
st.sidebar.header("🎯 2. FIRE 退休期参数")
# 假设退休后去旅居，开支可能比现在大
fire_monthly_expense = st.sidebar.number_input("RFIRE后月预计开支 (元)", value=12000, step=1000)

st.sidebar.header("📈 3. 市场与环境假设")
annual_return_rate = st.sidebar.number_input("预期年化收益率 (%)", value=8.0, step=0.5) / 100
annual_inflation_rate = st.sidebar.number_input("预计年通胀率 (%)", value=3.0, step=0.5) / 100
target_years = st.sidebar.slider("推演未来多少年？", min_value=10, max_value=50, value=30)

data_records = []
current_assets = initial_assets
current_monthly_expense = monthly_expense
# 我们需要一个独立的变量，来记录FIRE后的开支随通胀变化的情况
current_fire_expense = fire_monthly_expense 

# 新增一个“状态标签”，默认还没有FIRE
is_fired = False 

for year in range(1, target_years + 1):
    # 1. 先计算这一年的理财被动收益
    investment_profit = current_assets * annual_return_rate
    
    # 2. 核心逻辑分叉口：判断今年是否触发了 FIRE！
    # 如果被动收益 >= 你设定的FIRE后年度开支
    if investment_profit >= (current_fire_expense * 12):
        is_fired = True # 恭喜，状态切换为已退休！
    
    # 3. 根据状态，计算今年的结余和总开销
    if is_fired == True:
        # FIRE 状态下：不再赚工资，结余为 0（或者设为兼职收入，咱们先设为0）
        yearly_savings = 0
        annual_expense = current_fire_expense * 12
        status_text = "🌴 已FIRE"
    else:
        # 打工状态下：工资减去当前开支
        yearly_savings = (monthly_income - current_monthly_expense) * 12
        annual_expense = current_monthly_expense * 12
        status_text = "💼 积累期"
    
    # 4. 资产滚存（本金 + 收益 + 结余）
    current_assets = current_assets + investment_profit + yearly_savings
    
    data_records.append({
        "年份": f"第 {year} 年",
        "生命周期": status_text,
        "总资产": current_assets,
        "年度被动收益": investment_profit,
        "年度实际支出": annual_expense
    })
    
    # 5. 通胀的无差别攻击：无论是打工开支还是退休开支，明年都会变贵
    current_monthly_expense = current_monthly_expense * (1 + annual_inflation_rate)
    current_fire_expense = current_fire_expense * (1 + annual_inflation_rate)

df = pd.DataFrame(data_records)

st.subheader("📈 RFIRE 交叉点分析图")
# 注意这里，我们画图对比的是“年度被动收益” vs “年度实际支出”
st.line_chart(df, x="年份", y=["年度被动收益", "年度实际支出"], color=["#00FF00", "#FF0000"])

st.subheader("📋 详细数据推演表")
st.dataframe(df)
