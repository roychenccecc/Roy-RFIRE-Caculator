# ---------------------------------------------------
# 你的第八台 RFIRE 财富推演机 (V6.0 专属定制与产品化版)
# ---------------------------------------------------

import streamlit as st
import pandas as pd

st.set_page_config(page_title="RFIRE 财富推演系统", page_icon="🔥", layout="wide")

# --- 左侧边栏：【V6.0 新增个性化命名】 ---
st.sidebar.header("👤 0. 定制你的专属计划")
user_name = st.sidebar.text_input("请输入你的称呼：", value="探索者")

# 动态主标题：根据用户输入的名字自动变化！
st.title(f"🔥 {user_name} 的 RFIRE 财务路径推演系统")

# --- 主界面：【V6.0 新增：可收起的产品逻辑说明书】 ---
with st.expander("💡 点击阅读：这套系统背后的硬核量化逻辑（新手必看）", expanded=False):
    st.markdown("""
    ### 欢迎来到真实世界的财务沙盘
    这不仅仅是一个复利计算器，而是一套严谨的**全生命周期财富推演系统**。传统的 FIRE（提前退休）理论往往忽略了真实世界的摩擦成本，本系统通过三大核心引擎，帮你寻找最坚固的安全边际：

    * **🛡️ 引擎一：购买力平价 (真正的抗通胀)**
        * **痛点：** 很多人以为“理财收益 > 支出”就能退休，却忽略了本金的购买力正在被通胀蚕食。
        * **我们的逻辑：** 系统强制扣除【通胀磨损资金】。只有当你扣除通胀后，剩下的**“真实被动收益”**依然能覆盖你的日常开销时，才算达到真正的“永续 FIRE”。
    * **⚙️ 引擎二：生命周期状态机 (动态的人生阶段)**
        * **痛点：** 人的收入不会一直涨，人也会老去。
        * **我们的逻辑：** 你可以设定“最多工作年限”。到达年限后，系统会自动切断打工收入；一旦触发 FIRE 状态，系统会自动将生活标准切换至你设定的“退休后开支”，并停止滚存工资结余。
    * **🧠 引擎三：智能预填与精细微调 (颗粒度管控)**
        * **痛点：** 未来 30 年的收入很难笔笔算清，但特殊年份的奖金又极其重要。
        * **我们的逻辑：** 你只需输入基础工资和涨薪率，系统瞬间生成未来几十年的财务底表。你可以直接在底表上双击修改任意一年的特殊收入（如跳槽、大额年终奖），系统会实时重算全局。
        
    **👉 使用指南：** 依次调节左侧参数，在下方确认你的收入路径，观察底部图表中的【绿线（真实收益）】何时穿透【红线（年度支出）】！
    """)

# --- 左侧边栏：参数输入区 ---
st.sidebar.header("📊 1. 财富与工作参数")
initial_assets = st.sidebar.number_input("初始资产 (元)", value=500000, step=50000)
max_working_years = st.sidebar.number_input("预计最多还能工作多少年？", value=15, min_value=1, max_value=50)
monthly_expense = st.sidebar.number_input("当前月支出 (元)", value=8000, step=1000)

st.sidebar.header("🎯 2. FIRE 退休期参数")
fire_monthly_expense = st.sidebar.number_input("RFIRE后月预计开支 (元)", value=12000, step=1000)

st.sidebar.header("📈 3. 市场与环境假设")
annual_return_rate = st.sidebar.number_input("预期名义年化收益率 (%)", value=8.0, step=0.5) / 100
annual_inflation_rate = st.sidebar.number_input("预计年通胀率 (%)", value=3.0, step=0.5) / 100
target_years = st.sidebar.slider("推演未来多少年？", min_value=10, max_value=50, value=30)

# --- 主界面：未来收入路径设定 ---
st.subheader("💼 设定你的未来收入路径")

income_mode = st.radio(
    "请选择你的收入预测模式：",
    ("🚀 智能预填并支持微调 (输入参数后，在下方表格手动修改特例)", "✍️ 纯手动逐年填入")
)

table_years = int(max_working_years)
default_income_data = []

if "智能预填" in income_mode:
    col1, col2, col3 = st.columns(3)
    with col1:
        base_monthly = st.number_input("当前月收入 (元)", value=20000, step=1000)
    with col2:
        raise_rate = st.number_input("预计每年涨薪比例 (%)", value=5.0, step=0.5) / 100
    with col3:
        base_bonus = st.number_input("预计年终奖 (元/年)", value=50000, step=5000)
    
    current_m_income = base_monthly
    for i in range(table_years):
        default_income_data.append({
            "工作年份": f"第 {i+1} 年",
            "预期月收入(元)": round(current_m_income, 2),
            "预期年终奖(元)": base_bonus
        })
        current_m_income = current_m_income * (1 + raise_rate)
else:
    for i in range(table_years):
        default_income_data.append({
            "工作年份": f"第 {i+1} 年",
            "预期月收入(元)": 20000,
            "预期年终奖(元)": 50000
        })

st.markdown(f"👇 **你的打工生涯预计还有 {table_years} 年。你可以在下方表格双击任意数字进行修改：**")
df_input = pd.DataFrame(default_income_data)
edited_df = st.data_editor(df_input, use_container_width=True, hide_index=True)

yearly_total_income_list = []
for index, row in edited_df.iterrows():
    total_annual = (row["预期月收入(元)"] * 12) + row["预期年终奖(元)"]
    yearly_total_income_list.append(total_annual)

st.divider()

# --- 核心推演逻辑 ---
data_records = []
current_assets = initial_assets
current_monthly_expense = monthly_expense
current_fire_expense = fire_monthly_expense 
is_fired = False 

for year in range(1, target_years + 1):
    
    if year > max_working_years:
        current_annual_income = 0
    else:
        current_annual_income = yearly_total_income_list[year - 1]

    investment_profit = current_assets * annual_return_rate
    capital_preservation_need = current_assets * annual_inflation_rate
    real_passive_income = investment_profit - capital_preservation_need
    
    if real_passive_income >= (current_fire_expense * 12):
        is_fired = True
        
    if is_fired:
        yearly_savings = 0 
        annual_expense = current_fire_expense * 12
        status_text = "🌴 永续 FIRE"
    else:
        annual_expense = current_monthly_expense * 12
        yearly_savings = current_annual_income - annual_expense 
        if yearly_savings < 0:
            status_text = "⚠️ 消耗本金"
        else:
            status_text = "💼 资本积累"
            
    current_assets = current_assets + investment_profit + yearly_savings
    
    data_records.append({
        "推演年份": year, 
        "生命周期": status_text,
        "当年实际总收入": round(current_annual_income, 2),
        "总资产": round(current_assets, 2),
        "抗通胀后真实收益": round(real_passive_income, 2),
        "年度实际支出": round(annual_expense, 2)
    })
    
    current_monthly_expense *= (1 + annual_inflation_rate)
    current_fire_expense *= (1 + annual_inflation_rate)

# --- 结果展示 ---
df_result = pd.DataFrame(data_records)

st.subheader(f"📈 {user_name} 的永续 RFIRE 交叉点分析图")
st.line_chart(df_result, x="推演年份", y=["抗通胀后真实收益", "年度实际支出"], color=["#00FF00", "#FF0000"])

st.subheader("📋 详细推演数据大表")
df_result_display = df_result.copy()
df_result_display["推演年份"] = df_result_display["推演年份"].apply(lambda x: f"第 {x} 年")
st.dataframe(df_result_display, use_container_width=True)
