# ---------------------------------------------------
# 你的第十三台 RFIRE 财富推演机 (V11.0 双轨命运旗舰版)
# ---------------------------------------------------

import streamlit as st
import pandas as pd

st.set_page_config(page_title="RFIRE 财富推演系统", page_icon="🔥", layout="wide")

st.sidebar.header("👤 0. 定制你的专属计划")
user_name = st.sidebar.text_input("请输入你的称呼：", value="探索者")
st.title(f"🔥 {user_name} 的 RFIRE 财务路径推演系统 (V11.0)")

with st.expander("💡 点击阅读：这套系统背后的硬核量化逻辑", expanded=False):
    st.markdown("""
    * **🛡️ 购买力平价：** 强制扣除通胀磨损资金，寻找真实的永续 FIRE 奇点。
    * **⚙️ 剥离 FI 与 RE：** 财务自由(FI)和提前退休(RE)是两码事。彻底辞职后才切换为退休开支标准。
    * **⚖️ 命运平衡双轨：** 独立定制未来的“黑天鹅支出”与“意外之财/副业收入”，系统自动执行跨期通胀折算。
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

# --- 主界面：未来主业收入设定 (沿用极致稳定的 V8 记忆机制) ---
st.subheader("💼 1. 设定你的未来【主业】收入路径")

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
            data.append({"工作年份": f"第 {i+1} 年", "主业月收入(元)": round(c_m, 2), "主业年终奖(元)": b_b})
            c_m *= (1 + r_r)
    else:
        for i in range(years):
            data.append({"工作年份": f"第 {i+1} 年", "主业月收入(元)": 20000.0, "主业年终奖(元)": 50000.0})
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
        last_income = current_df.iloc[-1]["主业月收入(元)"] if current_len > 0 else 20000.0
        last_bonus = current_df.iloc[-1]["主业年终奖(元)"] if current_len > 0 else 50000.0
        new_rows = [{"工作年份": f"第 {i+1} 年", "主业月收入(元)": last_income, "主业年终奖(元)": last_bonus} for i in range(current_len, table_years)]
        st.session_state.base_df = pd.concat([current_df, pd.DataFrame(new_rows)], ignore_index=True)
    elif table_years < current_len:
        st.session_state.base_df = current_df.head(table_years)
    if "income_table" in st.session_state:
        del st.session_state["income_table"]

st.session_state.last_mode = income_mode
st.session_state.last_params = current_params
st.session_state.last_years = table_years

edited_df = st.data_editor(st.session_state.base_df, key="income_table", use_container_width=True, hide_index=True)
st.session_state.latest_edited_df = edited_df

yearly_total_income_list = []
for index, row in edited_df.iterrows():
    total_annual = (row["主业月收入(元)"] * 12) + row["主业年终奖(元)"]
    yearly_total_income_list.append(total_annual)

st.divider()

# ==========================================
# 【V11.0 新增：双轨命运面板 (左右分栏布局)】
# ==========================================
st.subheader("⚖️ 2. 命运平衡控制台 (意外开支 vs 额外收入)")
st.markdown("系统将自动把下方填入的金额（按当前物价）通过复利折算为发生那一年的真实价值。点击表格底部 `+` 号可无限新增。")

# 将屏幕分为左右两列
col_risk, col_opp = st.columns(2)

# 左侧：深渊（黑天鹅支出）
with col_risk:
    st.markdown("#### 🌪️ 黑天鹅事件 (意外支出)")
    default_black_swans = pd.DataFrame({"发生年份 (数字)": [5], "意外支出金额 (当前物价)": [100000.0]})
    edited_black_swans = st.data_editor(default_black_swans, num_rows="dynamic", use_container_width=True, hide_index=True, key="black_swan_table")
    
    black_swan_dict = {}
    for index, row in edited_black_swans.iterrows():
        try:
            y, amt = int(row["发生年份 (数字)"]), float(row["意外支出金额 (当前物价)"])
            black_swan_dict[y] = black_swan_dict.get(y, 0) + amt 
        except: pass

# 右侧：金矿（副业/意外收入）
with col_opp:
    st.markdown("#### 🎁 正向期权 (额外收入/副业)")
    default_windfalls = pd.DataFrame({"发生年份 (数字)": [3, 8], "额外收入金额 (当前物价)": [30000.0, 150000.0]})
    edited_windfalls = st.data_editor(default_windfalls, num_rows="dynamic", use_container_width=True, hide_index=True, key="windfall_table")
    
    windfall_dict = {}
    for index, row in edited_windfalls.iterrows():
        try:
            y, amt = int(row["发生年份 (数字)"]), float(row["额外收入金额 (当前物价)"])
            windfall_dict[y] = windfall_dict.get(y, 0) + amt 
        except: pass

st.divider()

# --- 核心推演逻辑 ---
data_records = []
current_assets = initial_assets
current_monthly_expense = monthly_expense
current_fire_expense = fire_monthly_expense 

for year in range(1, target_years + 1):
    
    is_working = year <= max_working_years
    
    # 【V11.0 逻辑升级：提取主业收入】
    current_annual_income = yearly_total_income_list[year - 1] if is_working else 0
    base_annual_expense = (current_monthly_expense * 12) if is_working else (current_fire_expense * 12)
    actual_annual_expense = base_annual_expense
    
    had_black_swan = False
    had_windfall = False
    
    # 1. 结算意外开支
    if year in black_swan_dict:
        inflated_black_swan_cost = black_swan_dict[year] * ((1 + annual_inflation_rate) ** year)
        actual_annual_expense += inflated_black_swan_cost
        had_black_swan = True

    # 2. 结算额外收入（通胀让副业收入/意外之财的名义数值也随之水涨船高）
    if year in windfall_dict:
        inflated_windfall_income = windfall_dict[year] * ((1 + annual_inflation_rate) ** year)
        current_annual_income += inflated_windfall_income
        had_windfall = True

    investment_profit = current_assets * annual_return_rate
    capital_preservation_need = current_assets * annual_inflation_rate
    real_passive_income = investment_profit - capital_preservation_need
    
    is_fi = real_passive_income >= (current_fire_expense * 12)
    
    if is_working:
        status_text = "👑 财务自由(打工中)" if is_fi else "💼 资本积累期"
    else:
        status_text = "🌴 永续 FIRE" if is_fi else "⚠️ 消耗本金中"
        
    # 状态标签拼接显示
    if had_black_swan: status_text += " 🏥[支出激增]"
    if had_windfall: status_text += " 💰[天降外财]"
            
    yearly_savings = current_annual_income - actual_annual_expense 
    current_assets = current_assets + investment_profit + yearly_savings
    
    data_records.append({
        "推演年份": year, 
        "生命周期": status_text,
        "当年实际总收入(元)": round(current_annual_income, 2), # 此时的总收入已包含副业
        "总资产(元)": round(current_assets, 2),
        "抗通胀后真实收益(元)": round(real_passive_income, 2),
        "年度实际支出(元)": round(actual_annual_expense, 2)
    })
    
    current_monthly_expense *= (1 + annual_inflation_rate)
    current_fire_expense *= (1 + annual_inflation_rate)

# --- 结果展示与下载 ---
df_result = pd.DataFrame(data_records)

st.subheader(f"📈 {user_name} 的永续 RFIRE 交叉点分析图")
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
