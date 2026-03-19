# ---------------------------------------------------
# 你的第六台 RFIRE 财富推演机 (V5.0 精准收入引擎版)
# ---------------------------------------------------

import streamlit as st
import pandas as pd

st.set_page_config(page_title="我的 RFIRE 计算器", page_icon="🔥", layout="wide")
st.title("🔥 个人 RFIRE 财务路径推演系统 (V5.0 精准收入版)")

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

# --- 主界面：【V5.0 收入引擎升级】 ---
st.subheader("💼 设定你的未来收入路径")

income_mode = st.radio(
    "请选择你的收入预测模式：",
    ("简略模式 (基础工资 + 每年固定涨薪 + 年终奖)", "逐年手动填入模式 (精准模拟薪资与奖金起伏)")
)

# 我们准备一个列表，用来装系统算出的【当年实际总收入】（月薪*12 + 年终奖）
yearly_total_income_list = []

if income_mode == "简略模式":
    # 使用列排版，让三个输入框并排，UI更清爽
    col1, col2, col3 = st.columns(3)
    with col1:
        base_monthly = st.number_input("当前月收入 (元)", value=20000, step=1000)
    with col2:
        raise_rate = st.number_input("预计每年涨薪比例 (%)", value=5.0, step=0.5) / 100
    with col3:
        base_bonus = st.number_input("预计年终奖 (元/年, 选填)", value=50000, step=5000)
    
    # 系统开始自动推算
    st.markdown("👇 **系统自动推算的未来收入明细如下（仅展示工作期）：**")
    projection_data = []
    current_m_income = base_monthly
    
    for i in range(target_years):
        # 核心算法：当年实际总收入 = 推算月薪 * 12 + 年终奖
        total_annual = (current_m_income * 12) + base_bonus
        yearly_total_income_list.append(total_annual) # 存入后台列表供核心循环使用
        
        # 把推算过程记录下来，准备展示给用户看
        projection_data.append({
            "年份": f"第 {i+1} 年",
            "推算月收入(元)": round(current_m_income, 2), # round()用于保留两位小数
            "预期年终奖(元)": base_bonus,
            "✨ 当年实际总收入(元)": round(total_annual, 2)
        })
        # 明年涨薪（年终奖我们假设保持不变，你也可以日后升级为随工资涨）
        current_m_income = current_m_income * (1 + raise_rate)
        
    # st.dataframe 会生成一个不可编辑的展示表格
    st.dataframe(pd.DataFrame(projection_data), use_container_width=True)

else:
    # 逐年手动填入模式
    st.write("请在下方的表格中，直接双击修改你未来每一年的【月收入】和【年终奖】：")
    
    # 准备默认数据框架，包含月收入和年终奖两列
    default_income_data = [
        {"年份": f"第 {i+1} 年", "预期月收入(元)": 20000, "预期年终奖(元)": 50000} 
        for i in range(target_years)
    ]
    df_input = pd.DataFrame(default_income_data)
    
    # 这是一个可编辑表格，用户修改后的数据会存入 edited_df
    edited_df = st.data_editor(df_input, use_container_width=True, hide_index=True)
    
    # 遍历用户填好的表格，系统在后台计算每年的总收入
    for index, row in edited_df.iterrows():
        total_annual = (row["预期月收入(元)"] * 12) + row["预期年终奖(元)"]
        yearly_total_income_list.append(total_annual)

st.divider()

# --- 核心推演逻辑 (保持 V4.0 的抗通胀严谨性) ---
data_records = []
current_assets = initial_assets
current_monthly_expense = monthly_expense
current_fire_expense = fire_monthly_expense 
is_fired = False 

for year in range(1, target_years + 1):
    
    # 获取这辈子的“当年总收入”
    if year > max_working_years:
        current_annual_income = 0 # 退休或干不动了，主动收入断绝
    else:
        current_annual_income = yearly_total_income_list[year - 1]

    # 1. 计算名义理财收益与抗通胀真实收益
    investment_profit = current_assets * annual_return_rate
    capital_preservation_need = current_assets * annual_inflation_rate
    real_passive_income = investment_profit - capital_preservation_need
    
    # 2. 严谨的 FIRE 判断
    if real_passive_income >= (current_fire_expense * 12):
        is_fired = True
        
    # 3. 算账 (注意：这里用的是刚刚算出来的 current_annual_income 总收入)
    if is_fired:
        yearly_savings = 0 
        annual_expense = current_fire_expense * 12
        status_text = "🌴 永续 FIRE"
    else:
        annual_expense = current_monthly_expense * 12
        # 当年结余 = 当年总收入 - 当年总开支
        yearly_savings = current_annual_income - annual_expense 
        
        if yearly_savings < 0:
            status_text = "⚠️ 消耗本金中"
        else:
            status_text = "💼 资本积累期"
            
    # 4. 资产更新
    current_assets = current_assets + investment_profit + yearly_savings
    
    data_records.append({
        "年份": f"第 {year} 年",
        "生命周期": status_text,
        "当年实际总收入": current_annual_income, # 最终大表里也能看到当年的打工总收入
        "总资产": current_assets,
        "抗通胀后真实收益": real_passive_income,
        "年度实际支出": annual_expense
    })
    
    # 5. 通胀计算
    current_monthly_expense *= (1 + annual_inflation_rate)
    current_fire_expense *= (1 + annual_inflation_rate)

# --- 结果展示 ---
df_result = pd.DataFrame(data_records)

st.subheader("📈 永续 RFIRE 交叉点分析图 (已扣除通胀磨损)")
st.line_chart(df_result, x="年份", y=["抗通胀后真实收益", "年度实际支出"], color=["#00FF00", "#FF0000"])

st.subheader("📋 详细推演数据大表")
st.dataframe(df_result, use_container_width=True)
