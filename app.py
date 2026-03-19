# ---------------------------------------------------
# 你的第十一台 RFIRE 财富推演机 (V9.0 真实人生风控版)
# ---------------------------------------------------

import streamlit as st
import pandas as pd

st.set_page_config(page_title="RFIRE 财富推演系统", page_icon="🔥", layout="wide")

st.sidebar.header("👤 0. 定制你的专属计划")
user_name = st.sidebar.text_input("请输入你的称呼：", value="探索者")
st.title(f"🔥 {user_name} 的 RFIRE 财务路径推演系统 (V9.0 风控版)")

with st.expander("💡 点击阅读：这套系统背后的硬核量化逻辑", expanded=False):
    st.markdown("""
    * **🛡️ 购买力平价：** 强制扣除通胀磨损资金，寻找真实的永续 FIRE 奇点。
    * **⚙️ 剥离 FI 与 RE：** 财务自由(FI)和提前退休(RE)是两码事。打工时的开支按当前标准算，彻底辞职后才切换为退休开支标准。
    * **⚠️ 黑天鹅压力测试：** 引入大额意外开支频率模拟。经得起意外冲击的 FIRE，才是真金不怕火炼的系统。
    """)

# --- 左侧边栏参数 ---
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

# 【V9.0 新增核心模块】：意外开支模拟器
st.sidebar.header("⚠️ 4. 黑天鹅与压力测试")
unexpected_amount = st.sidebar.number_input("单次大额意外开支 (元)", value=100000, step=10000, help="例如大病医疗、房屋大修等")
unexpected_freq = st.sidebar.number_input("意外发生频率 (每 X 年)", value=5, min_value=1, max_value=30, help="设定每隔多少年遭遇一次上述意外支出")

# --- 主界面：未来收入设定 (沿用 V8.0 的终极状态管理) ---
st.subheader("💼 设定你的未来收入路径")

income_mode = st.radio(
    "请选择你的收入预测模式：",
    ("🚀 智能预填并支持微调 (输入参数后，在下方表格手动修改特例)", "✍️ 纯手动逐年填入")
)

table_years = int(max_working_years)

if "智能预填" in income_mode:
    col1, col2, col3 = st.columns(3)
    with col1:
        base_monthly = st.number_input("当前月收入 (元)", value=20000, step=1000)
    with col2:
        raise_rate = st.number_input("预计每年涨薪比例 (%)", value=5.0, step=0.5) / 100
    with col3:
        base_bonus = st.number_input("预计年终奖 (元/年)", value=50000, step=5000)
    current_params = f"{base_monthly}_{raise_rate}_{base_bonus}"
else:
    base_monthly, raise_rate, base_bonus = 20000.0, 0.05, 50000.0
    current_params = "manual"

def get_default_df(mode, years, b_m, r_r, b_b):
    data = []
    if "智能预填" in mode:
        c_m = b_m
        for i in range(years):
            data.append({"工作年份": f"第 {i+1} 年", "预期月收入(元)": round(c_m, 2), "预期年终奖(元)": b_b})
            c_m *= (1 + r_r)
    else:
        for i in range(years):
            data.append({"工作年份": f"第 {i+1} 年", "预期月收入(元)": 20000.0, "预期年终奖(元)": 50000.0})
    return pd.DataFrame(data)

if "base_df" not in st.session_state:
    st.session_state.base_df = get_default_df(income_mode, table_years, base_monthly, raise_rate, base_bonus)
    st.session_state.latest_edited_df = st.session_state.base_df.copy()
    st.session_state.last_mode = income_mode
    st.session_state.last_params = current_params
    st.session_state.last_years = table_years

mode_changed = (st.session_state.last_mode != income_mode)
params_changed = (st.session_state.last_params != current_params)
years_changed = (st.session_state.last_years != table_years)

if mode_changed or params_changed:
    st.session_state.base_df = get_default_df(income_mode, table_years, base_monthly, raise_rate, base_bonus)
    if "income_table" in st.session_state:
        del st.session_state["income_table"]
elif years_changed:
    current_df = st.session_state.latest_edited_df
    current_len = len(current_df)
    if table_years > current_len:
        last_income = current_df.iloc[-1]["预期月收入(元)"] if current_len > 0 else 20000.0
        last_bonus = current_df.iloc[-1]["预期年终奖(元)"] if current_len > 0 else 50000.0
        new_rows = [{"工作年份": f"第 {i+1} 年", "预期月收入(元)": last_income, "预期年终奖(元)": last_bonus} for i in range(current_len, table_years)]
        st.session_state.base_df = pd.concat([current_df, pd.DataFrame(new_rows)], ignore_index=True)
    elif table_years < current_len:
        st.session_state.base_df = current_df.head(table_years)
    if "income_table" in st.session_state:
        del st.session_state["income_table"]

st.session_state.last_mode = income_mode
st.session_state.last_params = current_params
st.session_state.last_years = table_years

st.markdown(f"👇 **你的打工生涯预计还有 {table_years} 年。你可以双击任意数字进行修改：**")
edited_df = st.data_editor(st.session_state.base_df, key="income_table", use_container_width=True, hide_index=True)
st.session_state.latest_edited_df = edited_df

yearly_total_income_list = []
for index, row in edited_df.iterrows():
    total_annual = (row["预期月收入(元)"] * 12) + row["预期年终奖(元)"]
    yearly_total_income_list.append(total_annual)

st.divider()

# --- 核心推演逻辑 (V9.0 重构：行为与财富剥离) ---
data_records = []
current_assets = initial_assets
current_monthly_expense = monthly_expense
current_fire_expense = fire_monthly_expense 
# 意外开支也会随通胀变大
current_unexpected_amount = unexpected_amount 

for year in range(1, target_years + 1):
    
    # 判定 1：当前行为状态（还在打工还是已经退休辞职？）
    is_working = year <= max_working_years
    current_annual_income = yearly_total_income_list[year - 1] if is_working else 0

    # 【修复重点】：开支标准由行为状态决定，只要还在打工，就按当前支出水平生活
    base_annual_expense = (current_monthly_expense * 12) if is_working else (current_fire_expense * 12)
    
    # 【V9.0 意外开支判定】：今年是倒霉的“黑天鹅年份”吗？
    actual_annual_expense = base_annual_expense
    had_black_swan = False
    if year % unexpected_freq == 0:
        actual_annual_expense += current_unexpected_amount
        had_black_swan = True

    # 判定 2：当前财富状态（算算投资赚了多少）
    investment_profit = current_assets * annual_return_rate
    capital_preservation_need = current_assets * annual_inflation_rate
    real_passive_income = investment_profit - capital_preservation_need
    
    # 判定 3：是否达到 FI（财务独立）境界？（用退休后的预期开支来衡量底气）
    is_fi = real_passive_income >= (current_fire_expense * 12)
    
    # 状态栏文本生成：将行为状态与财富状态组合
    if is_working:
        status_text = "👑 财务自由 (继续打工)" if is_fi else "💼 资本积累期"
    else:
        status_text = "🌴 永续 FIRE (已退休)" if is_fi else "⚠️ 退休但消耗本金"
        
    if had_black_swan:
        status_text += " 🏥[触发意外开支]"
            
    # 年度结算
    yearly_savings = current_annual_income - actual_annual_expense 
    current_assets = current_assets + investment_profit + yearly_savings
    
    data_records.append({
        "推演年份": year, 
        "生命周期": status_text,
        "当年实际总收入(元)": round(current_annual_income, 2),
        "总资产(元)": round(current_assets, 2),
        "抗通胀后真实收益(元)": round(real_passive_income, 2),
        "年度实际支出(元)": round(actual_annual_expense, 2)
    })
    
    # 通胀更新
    current_monthly_expense *= (1 + annual_inflation_rate)
    current_fire_expense *= (1 + annual_inflation_rate)
    current_unexpected_amount *= (1 + annual_inflation_rate)

# --- 结果展示与下载 ---
df_result = pd.DataFrame(data_records)

st.subheader(f"📈 {user_name} 的永续 RFIRE 交叉点分析图")
# 【V9.0 图表小优化】：为了看清意外开支的毛刺，使用柱状图+折线图的组合会更好，但这里保持极简折线
st.line_chart(df_result, x="推演年份", y=["抗通胀后真实收益(元)", "年度实际支出(元)"], color=["#00FF00", "#FF0000"])

st.subheader("📋 详细推演数据大表")
df_result_display = df_result.copy()
df_result_display["推演年份"] = df_result_display["推演年份"].apply(lambda x: f"第 {x} 年")
st.dataframe(df_result_display, use_container_width=True)

st.divider()
st.markdown("### 💾 保存你的推演计划")
csv_data = df_result_display.to_csv(index=False).encode('utf-8-sig')

st.download_button(
    label=f"📥 一键下载【{user_name}的RFIRE推演计划.csv】",
    data=csv_data,
    file_name=f"{user_name}的RFIRE推演计划.csv",
    mime="text/csv",
    type="primary"
)
