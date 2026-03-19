# ---------------------------------------------------
# 你的第九台 RFIRE 财富推演机 (V7.0 记忆胶囊与下载版)
# ---------------------------------------------------

import streamlit as st
import pandas as pd

st.set_page_config(page_title="RFIRE 财富推演系统", page_icon="🔥", layout="wide")

st.sidebar.header("👤 0. 定制你的专属计划")
user_name = st.sidebar.text_input("请输入你的称呼：", value="探索者")
st.title(f"🔥 {user_name} 的 RFIRE 财务路径推演系统")

with st.expander("💡 点击阅读：这套系统背后的硬核量化逻辑（新手必看）", expanded=False):
    st.markdown("""
    ### 欢迎来到真实世界的财务沙盘
    这不仅仅是一个复利计算器，而是一套严谨的**全生命周期财富推演系统**。传统的 FIRE（提前退休）理论往往忽略了真实世界的摩擦成本，本系统通过三大核心引擎，帮你寻找最坚固的安全边际：

    * **🛡️ 引擎一：购买力平价 (真正的抗通胀)**
        系统强制扣除【通胀磨损资金】。只有当你扣除通胀后，剩下的“真实被动收益”依然能覆盖日常开销，才算真正的永续 FIRE。
    * **⚙️ 引擎二：生命周期状态机 (动态的人生阶段)**
        到达“最多工作年限”后，系统会自动切断打工收入；触发 FIRE 状态后，自动切换至“退休后开支”。
    * **🧠 引擎三：智能预填与精细微调 (颗粒度管控)**
        支持基础参数一键预填，并随时双击表格修改特定年份的超额收益或空窗期。
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

if "智能预填" in income_mode:
    col1, col2, col3 = st.columns(3)
    with col1:
        base_monthly = st.number_input("当前月收入 (元)", value=20000, step=1000)
    with col2:
        raise_rate = st.number_input("预计每年涨薪比例 (%)", value=5.0, step=0.5) / 100
    with col3:
        base_bonus = st.number_input("预计年终奖 (元/年)", value=50000, step=5000)
    # 把当前设置打包成一个“参数指纹”，用于判断用户是否修改了基础设定
    current_params = f"{base_monthly}_{raise_rate}_{base_bonus}"
else:
    current_params = "manual"

# ==========================================
# 【V7.0 黑科技：记忆胶囊 Session State】
# ==========================================
# 1. 如果这是用户刚打开网页，初始化保险箱
if "income_df" not in st.session_state:
    st.session_state.income_df = pd.DataFrame()
    st.session_state.last_years = 0
    st.session_state.last_params = ""
    st.session_state.last_mode = ""

# 2. 触发条件 A：用户切换了模式，或者修改了“当前月薪/涨薪率”等基础设定 -> 重新生成整张表
if st.session_state.last_mode != income_mode or st.session_state.last_params != current_params:
    default_data = []
    if "智能预填" in income_mode:
        c_m = base_monthly
        for i in range(table_years):
            default_data.append({"工作年份": f"第 {i+1} 年", "预期月收入(元)": round(c_m, 2), "预期年终奖(元)": base_bonus})
            c_m *= (1 + raise_rate)
    else:
        for i in range(table_years):
            default_data.append({"工作年份": f"第 {i+1} 年", "预期月收入(元)": 20000.0, "预期年终奖(元)": 50000.0})
    st.session_state.income_df = pd.DataFrame(default_data)

# 3. 触发条件 B：基础设定没变，只是拖动了【工作年限】 -> 继承记忆，多退少补
elif st.session_state.last_years != table_years:
    current_df = st.session_state.income_df
    current_len = len(current_df)
    
    if table_years > current_len:
        # 增加年限：补齐背后的空白行（极其人性化的设计：直接复制最后一年的收入作为后续的默认值）
        last_income = current_df.iloc[-1]["预期月收入(元)"] if current_len > 0 else 20000.0
        last_bonus = current_df.iloc[-1]["预期年终奖(元)"] if current_len > 0 else 50000.0
        new_rows = []
        for i in range(current_len, table_years):
            new_rows.append({"工作年份": f"第 {i+1} 年", "预期月收入(元)": last_income, "预期年终奖(元)": last_bonus})
        st.session_state.income_df = pd.concat([current_df, pd.DataFrame(new_rows)], ignore_index=True)
        
    elif table_years < current_len:
        # 减少年限：直接砍掉多出的行数
        st.session_state.income_df = current_df.head(table_years)

# 4. 把当前状态存入保险箱，供下次对比使用
st.session_state.last_mode = income_mode
st.session_state.last_params = current_params
st.session_state.last_years = table_years

# 5. 展示表格，并把用户在网页上敲入的最新修改，实时存回保险箱
st.markdown(f"👇 **你的打工生涯预计还有 {table_years} 年。你可以双击任意数字进行修改：**")
edited_df = st.data_editor(st.session_state.income_df, use_container_width=True, hide_index=True)
st.session_state.income_df = edited_df

# 提取表格数据进入系统核心引擎
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

# 【V7.0 新增功能：一键导出 CSV】
st.divider()
st.markdown("### 💾 保存你的推演计划")
# utf-8-sig 编码是为了保证国内用户用 Excel 打开时不出现中文乱码
csv_data = df_result_display.to_csv(index=False).encode('utf-8-sig')

st.download_button(
    label=f"📥 一键下载【{user_name}的RFIRE推演计划.csv】",
    data=csv_data,
    file_name=f"{user_name}的RFIRE推演计划.csv",
    mime="text/csv",
    type="primary" # 把按钮变成显眼的红色/主色调
)
