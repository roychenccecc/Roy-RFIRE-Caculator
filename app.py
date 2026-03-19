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
st.session_state.last_age = current_age

edited_df = st.data_editor(st.session_state.base_df, key="income_table", use_container_width=True, hide_index=True)
st.session_state.latest_edited_df = edited_df

yearly_total_income_list = []
for index, row in edited_df.iterrows():
    total_annual = (row["主业月收入(元)"] * 12) + row["主业年终奖(元)"]
    yearly_total_income_list.append(total_annual)

st.divider()

# --- 命运平衡面板 (V14.0：完美修复缺失的金额列) ---
st.subheader("⚖️ 2. 命运平衡控制台 (意外开支 vs 额外收入)")
col_risk, col_opp = st.columns(2)

with col_risk:
    st.markdown("#### 🌪️ 黑天鹅事件 (意外支出)")
    # 修复点：将金额列重新加入默认 DataFrame 中
    default_bs_df = pd.DataFrame({"发生时的年龄 (数字)": [45], "金额 (当前物价/元)": [100000.0]})
    edited_black_swans = st.data_editor(default_bs_df, num_rows="dynamic", use_container_width=True, hide_index=True, key="black_swan_table")
    black_swan_dict = {int(row["发生时的年龄 (数字)"]): float(row["金额 (当前物价/元)"]) for i, row in edited_black_swans.iterrows() if pd.notnull(row["发生时的年龄 (数字)"])}

with col_opp:
    st.markdown("#### 🎁 正向期权 (额外收入)")
    # 修复点：将金额列重新加入默认 DataFrame 中
    default_wf_df = pd.DataFrame({"发生时的年龄 (数字)": [38], "金额 (当前物价/元)": [30000.0]})
    edited_windfalls = st.data_editor(default_wf_df, num_rows="dynamic", use_container_width=True, hide_index=True, key="windfall_table")
    windfall_dict = {int(row["发生时的年龄 (数字)"]): float(row["金额 (当前物价/元)"]) for i, row in edited_windfalls.iterrows() if pd.notnull(row["发生时的年龄 (数字)"])}

st.divider()

# --- 核心推演逻辑 ---
data_records = []
current_assets = initial_assets
current_monthly_expense = monthly_expense
current_fire_expense = fire_monthly_expense 
current_pension = monthly_pension 

for year in range(1, target_years + 1):
    
    this_year_age = current_age + year
    
    is_working = this_year_age <= retire_age
    current_annual_income = yearly_total_income_list[year - 1] if is_working else 0
    base_annual_expense = (current_monthly_expense * 12) if is_working else (current_fire_expense * 12)
    actual_annual_expense = base_annual_expense
    
    had_black_swan, had_windfall, getting_pension = False, False, False
    
    if this_year_age in black_swan_dict:
        actual_annual_expense += black_swan_dict[this_year_age] * ((1 + annual_inflation_rate) ** year)
        had_black_swan = True
    if this_year_age in windfall_dict:
        current_annual_income += windfall_dict[this_year_age] * ((1 + annual_inflation_rate) ** year)
        had_windfall = True

    annual_pension_income = 0
    if this_year_age >= pension_age:
        annual_pension_income = current_pension * 12
        current_annual_income += annual_pension_income
        getting_pension = True

    investment_profit = current_assets * annual_return_rate
    capital_preservation_need = current_assets * annual_inflation_rate
    real_passive_income = investment_profit - capital_preservation_need
    
    max_disposable_income = real_passive_income + current_annual_income

    is_fi = max_disposable_income >= (current_fire_expense * 12)
    
    if is_working:
        status_text = "👑 财务自由(打工中)" if is_fi else "💼 资本积累期"
    else:
        status_text = "🌴 永续 FIRE" if is_fi else "⚠️ 消耗本金中"
        
    if had_black_swan: status_text += " 🏥[暴击]"
    if had_windfall: status_text += " 💰[外财]"
    if getting_pension: status_text += " 💳[领养老金]"
            
    yearly_savings = current_annual_income - actual_annual_expense 
    current_assets = current_assets + investment_profit + yearly_savings
    
    # 【V14.0 核心逻辑】：计算“实际购买力资产”（剔除通胀水分后的真实价值）
    # 假设你第 30 年有 1000 万，如果通胀是 3%，那这 1000 万只相当于今天的 411 万。
    real_purchasing_power_assets = current_assets / ((1 + annual_inflation_rate) ** year)
    
    data_records.append({
        "推演年份": year, 
        "当年年龄": f"{this_year_age} 岁",
        "生命周期": status_text,
        "当年实际总收入(元)": round(current_annual_income, 2), 
        "最大可支配收入(不伤本金)": round(max_disposable_income, 2), 
        "年度实际支出(元)": round(actual_annual_expense, 2),
        "抗通胀真实理财收益(元)": round(real_passive_income, 2),
        "期末名义总资产(元)": round(current_assets, 2),
        "实际购买力资产(今日价值)": round(real_purchasing_power_assets, 2) # 【新增的真实资产列】
    })
    
    current_monthly_expense *= (1 + annual_inflation_rate)
    current_fire_expense *= (1 + annual_inflation_rate)
    current_pension *= (1 + annual_inflation_rate) 

# --- 结果展示与下载 ---
df_result = pd.DataFrame(data_records)

# 【V14.0 UI 升级】：双图表并行展示
st.subheader(f"📈 {user_name} 的 FIRE 路径深度解析")
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.markdown("#### 📊 1. 现金流与 FIRE 交叉点")
    st.markdown("当绿线（最大可支配收入）在红线（实际支出）上方时，你的财富在永续增长。")
    st.line_chart(df_result, x="推演年份", y=["最大可支配收入(不伤本金)", "年度实际支出(元)"], color=["#00FF00", "#FF0000"])

with col_chart2:
    st.markdown("#### 🏦 2. 资产雪球效应 (名义 vs 真实)")
    st.markdown("打破复利幻觉：蓝线是你账户上的钱，黄线是这笔钱在**今天**到底能买多少东西。")
    st.line_chart(df_result, x="推演年份", y=["期末名义总资产(元)", "实际购买力资产(今日价值)"], color=["#4285F4", "#F4B400"])

st.subheader("📋 详细推演数据大表")
st.dataframe(df_result, use_container_width=True)

st.divider()
st.markdown("### 💾 保存你的推演计划")
csv_data = df_result.to_csv(index=False).encode('utf-8-sig')
st.download_button("📥 一键下载【推演计划.csv】", data=csv_data, file_name=f"{user_name}的推演计划.csv", mime="text/csv", type="primary")
