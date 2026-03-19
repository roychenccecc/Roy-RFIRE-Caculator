# ---------------------------------------------------
# 你的第十台 RFIRE 财富推演机 (V8.0 终极交互修复版)
# ---------------------------------------------------

import streamlit as st
import pandas as pd

st.set_page_config(page_title="RFIRE 财富推演系统", page_icon="🔥", layout="wide")

st.sidebar.header("👤 0. 定制你的专属计划")
user_name = st.sidebar.text_input("请输入你的称呼：", value="探索者")
st.title(f"🔥 {user_name} 的 RFIRE 财务路径推演系统")

with st.expander("💡 点击阅读：这套系统背后的硬核量化逻辑", expanded=False):
    st.markdown("""
    * **🛡️ 购买力平价：** 强制扣除通胀磨损资金，寻找真实的永续 FIRE 奇点。
    * **⚙️ 动态生命周期：** 到达设定工作年限后，主动收入自动断绝，开支切换至退休标准。
    * **🧠 智能底表：** 基础参数一键生成未来 30 年现金流，支持双击表格微调特定年份特殊收入。
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

# --- 主界面：未来收入设定 ---
st.subheader("💼 设定你的未来收入路径")

income_mode = st.radio(
    "请选择你的收入预测模式：",
    ("🚀 智能预填并支持微调 (输入参数后，在下方表格手动修改特例)", "✍️ 纯手动逐年填入")
)

table_years = int(max_working_years)

# 提取参数，防止未定义错误
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
    base_monthly, raise_rate, base_bonus = 20000.0, 0.05, 50000.0 # 占位符
    current_params = "manual"

# 辅助函数：生成默认白板表格
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

# ==========================================
# 【V8.0 终极状态管理机制】
# ==========================================
# 1. 首次打开网页，初始化核心记忆
if "base_df" not in st.session_state:
    st.session_state.base_df = get_default_df(income_mode, table_years, base_monthly, raise_rate, base_bonus)
    st.session_state.latest_edited_df = st.session_state.base_df.copy() # 记录最新被编辑过的状态
    st.session_state.last_mode = income_mode
    st.session_state.last_params = current_params
    st.session_state.last_years = table_years

# 2. 检查你是否修改了影响“基本盘”的参数
mode_changed = (st.session_state.last_mode != income_mode)
params_changed = (st.session_state.last_params != current_params)
years_changed = (st.session_state.last_years != table_years)

if mode_changed or params_changed:
    # 如果切换了模式或修改了基础工资，直接重置全新表格
    st.session_state.base_df = get_default_df(income_mode, table_years, base_monthly, raise_rate, base_bonus)
    # 【核心】：清空底层编辑器的缓存记录，防止幽灵数据
    if "income_table" in st.session_state:
        del st.session_state["income_table"]
        
elif years_changed:
    # 【修复重点】：如果只改了工作年限，从你“最后一次编辑过的表格”里去多退少补！
    current_df = st.session_state.latest_edited_df
    current_len = len(current_df)
    
    if table_years > current_len:
        # 加长年限：贴心地复制最后一年的收入填进去
        last_income = current_df.iloc[-1]["预期月收入(元)"] if current_len > 0 else 20000.0
        last_bonus = current_df.iloc[-1]["预期年终奖(元)"] if current_len > 0 else 50000.0
        new_rows = [{"工作年份": f"第 {i+1} 年", "预期月收入(元)": last_income, "预期年终奖(元)": last_bonus} for i in range(current_len, table_years)]
        st.session_state.base_df = pd.concat([current_df, pd.DataFrame(new_rows)], ignore_index=True)
    elif table_years < current_len:
        # 缩短年限：直接裁掉尾巴
        st.session_state.base_df = current_df.head(table_years)
        
    # 把最新的合成表当做新的底座，清空缓存准备迎接新编辑
    if "income_table" in st.session_state:
        del st.session_state["income_table"]

# 更新记忆锚点
st.session_state.last_mode = income_mode
st.session_state.last_params = current_params
st.session_state.last_years = table_years

# 3. 呼出终极形态的数据表格（注意 key="income_table" 这个灵魂参数）
st.markdown(f"👇 **你的打工生涯预计还有 {table_years} 年。你可以双击任意数字进行修改：**")
edited_df = st.data_editor(
    st.session_state.base_df, 
    key="income_table", # 绑定身份证，绝不再丢失焦点
    use_container_width=True, 
    hide_index=True
)

# 4. 把用户最后改好的表格死死记住，给上面的 elif 备用
st.session_state.latest_edited_df = edited_df

# 5. 提取数据进入发动机引擎
yearly_total_income_list = []
for index, row in edited_df.iterrows():
    total_annual = (row["预期月收入(元)"] * 12) + row["预期年终奖(元)"]
    yearly_total_income_list.append(total_annual)
# ==========================================


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
        "当年实际总收入(元)": round(current_annual_income, 2),
        "总资产(元)": round(current_assets, 2),
        "抗通胀后真实收益(元)": round(real_passive_income, 2),
        "年度实际支出(元)": round(annual_expense, 2)
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
