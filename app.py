# ---------------------------------------------------
# 你的第四台 RFIRE 财富推演机 (V3.0 动态收入与年限版)
# ---------------------------------------------------

import streamlit as st
import pandas as pd

st.set_page_config(page_title="我的 RFIRE 计算器", page_icon="🔥", layout="wide") # layout="wide" 让网页变宽，方便显示表格
st.title("🔥 个人 RFIRE 财务路径推演系统 (V3.0)")

# --- 左侧边栏：参数输入区 ---
st.sidebar.header("📊 1. 财富与工作参数")
initial_assets = st.sidebar.number_input("初始资产 (元)", value=500000, step=50000)

# 【V3.0 新增】：工作年限限制
max_working_years = st.sidebar.number_input("预计最多还能工作多少年？", value=20, min_value=1, max_value=50)

monthly_expense = st.sidebar.number_input("当前月支出 (元)", value=8000, step=1000)

st.sidebar.header("🎯 2. FIRE 退休期参数")
fire_monthly_expense = st.sidebar.number_input("RFIRE后月预计开支 (元)", value=12000, step=1000)

st.sidebar.header("📈 3. 市场与环境假设")
annual_return_rate = st.sidebar.number_input("预期年化收益率 (%)", value=8.0, step=0.5) / 100
annual_inflation_rate = st.sidebar.number_input("预计年通胀率 (%)", value=3.0, step=0.5) / 100
target_years = st.sidebar.slider("推演未来多少年？", min_value=10, max_value=50, value=30)

# --- 主界面：收入模式选择与推演 ---
st.subheader("💼 设定你的未来收入路径")

# 【V3.0 新增】：使用 st.radio 让用户选择收入模式
income_mode = st.radio(
    "请选择你的收入预测模式：",
    ("简略模式 (假设每月工资固定)", "逐年手动填入模式 (精准模拟薪资起伏)")
)

# 准备一个列表，用来装每一年的具体收入
yearly_income_list = []

if income_mode == "简略模式":
    # 简略模式下，只显示一个输入框
    simple_monthly_income = st.number_input("当前月收入 (元)", value=20000, step=1000)
    # 把每年的收入都设定为这个固定值
    for y in range(target_years):
        yearly_income_list.append(simple_monthly_income)
        
else:
    # 逐年手动填入模式下，我们给用户生成一个可编辑的 Excel 表格
    st.write("请在下方的表格中，直接双击修改你未来每一年的预期【月收入】（只需填打工的这些年）：")
    
    # 1. 先造一个默认的数据表 (默认初始工资20000)
    default_income_data = [{"年份": f"第 {i+1} 年", "预期月收入(元)": 20000} for i in range(target_years)]
    df_input = pd.DataFrame(default_income_data)
    
    # 2. st.data_editor 会在网页上显示表格，并把用户修改后的新表格存入 edited_df
    edited_df = st.data_editor(df_input, use_container_width=True, hide_index=True)
    
    # 3. 把用户修改后的数据，提取成列表供后续计算使用
    yearly_income_list = edited_df["预期月收入(元)"].tolist()


st.divider() # 画一条华丽的分割线

# --- 核心推演逻辑 ---
data_records = []
current_assets = initial_assets
current_monthly_expense = monthly_expense
current_fire_expense = fire_monthly_expense 
is_fired = False 

for year in range(1, target_years + 1):
    
    # 【V3.0 新增核心逻辑】：判断今年还能不能拿到工资？
    # 如果已经超过了你设定的“最多工作年限”，那么月收入强制归 0
    if year > max_working_years:
        current_monthly_income = 0
    else:
        # 否则，从我们刚才准备好的收入列表里，把今年的预期收入拿出来 (计算机从0开始数数，所以是 year - 1)
        current_monthly_income = yearly_income_list[year - 1]

    # 1. 计算理财收益
    investment_profit = current_assets * annual_return_rate
    
    # 2. 判断是否触发 FIRE
    if investment_profit >= (current_fire_expense * 12):
        is_fired = True
        
    # 3. 根据状态算账
    if is_fired:
        yearly_savings = 0 # 财务自由，不再存钱
        annual_expense = current_fire_expense * 12
        status_text = "🌴 已FIRE"
    else:
        # 还没自由，继续打工。结余 = (今年预期的月收入 - 今年的月开支) * 12
        yearly_savings = (current_monthly_income - current_monthly_expense) * 12
        
        # 如果结余是负数（比如工作年限到了，没工资了，又没FIRE），那就得消耗本金
        if yearly_savings < 0:
            status_text = "⚠️ 消耗本金中"
        else:
            status_text = "💼 积累期"
            
        annual_expense = current_monthly_expense * 12
        
    # 4. 资产更新
    current_assets = current_assets + investment_profit + yearly_savings
    
    data_records.append({
        "年份": f"第 {year} 年",
        "生命周期": status_text,
        "当年月收入": current_monthly_income, # 把当年的预期收入也记录进表格
        "总资产": current_assets,
        "年度被动收益": investment_profit,
        "年度实际支出": annual_expense
    })
    
    # 5. 通胀计算
    current_monthly_expense *= (1 + annual_inflation_rate)
    current_fire_expense *= (1 + annual_inflation_rate)

# --- 结果展示 ---
df_result = pd.DataFrame(data_records)

st.subheader("📈 RFIRE 交叉点分析图")
st.line_chart(df_result, x="年份", y=["年度被动收益", "年度实际支出"], color=["#00FF00", "#FF0000"])

st.subheader("📋 详细推演数据表")
st.dataframe(df_result)
