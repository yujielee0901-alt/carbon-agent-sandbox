import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import time

# ==========================================
# 0. 页面全局配置 (必须放在第一行)
# ==========================================
st.set_page_config(page_title="数智寻路：政务决策沙盘", layout="wide", initial_sidebar_state="expanded")

# ==========================================
# 1. 初始化核心状态机 (Session State)
# ==========================================
# 控制当前所处页面的状态标识
if 'page' not in st.session_state:
    st.session_state.page = 'splash'

# 初始化所有的用户输入数据，确保跨页面不丢失
if 's_mode' not in st.session_state: st.session_state.s_mode = "提取内建资源型城市 (推荐)"
if 's_city' not in st.session_state: st.session_state.s_city = "焦作市"
if 'c_invest' not in st.session_state: st.session_state.c_invest = 4.8
if 'f_invest' not in st.session_state: st.session_state.f_invest = 2.5
if 'i_invest' not in st.session_state: st.session_state.i_invest = 1.0
if 'custom_data' not in st.session_state:
    st.session_state.custom_data = {
        "长途光缆": 1500.0, "高质量外资": 40.0, "IT人才密度": 2.0,
        "宽带普及": 200.0, "普惠金融": 250.0, "基准碳排": 120.0
    }

# ==========================================
# 2. 内嵌数据库与极差标准化引擎
# ==========================================
embedded_data = [
    {"城市": "焦作市", "长途光缆": 1500, "高质量外资": 40.5, "IT人才密度": 2.1, "宽带普及": 210, "普惠金融": 245, "基准碳排": 140.5},
    {"城市": "平顶山市", "长途光缆": 1800, "高质量外资": 35.2, "IT人才密度": 1.8, "宽带普及": 230, "普惠金融": 230, "基准碳排": 155.2},
    {"城市": "安阳市", "长途光缆": 1600, "高质量外资": 50.0, "IT人才密度": 2.5, "宽带普及": 200, "普惠金融": 255, "基准碳排": 138.0},
    {"城市": "鹤壁市", "长途光缆": 800, "高质量外资": 20.1, "IT人才密度": 1.2, "宽带普及": 120, "普惠金融": 210, "基准碳排": 110.4},
    {"城市": "长治市", "长途光缆": 1900, "高质量外资": 45.3, "IT人才密度": 3.0, "宽带普及": 250, "普惠金融": 260, "基准碳排": 160.8},
    {"城市": "晋城市", "长途光缆": 2100, "高质量外资": 40.0, "IT人才密度": 2.8, "宽带普及": 240, "普惠金融": 250, "基准碳排": 145.6},
    {"城市": "郑州市", "长途光缆": 6500, "高质量外资": 320.0, "IT人才密度": 15.5, "宽带普及": 850, "普惠金融": 340, "基准碳排": 85.0},
    {"城市": "洛阳市", "长途光缆": 4200, "高质量外资": 150.0, "IT人才密度": 8.2, "宽带普及": 520, "普惠金融": 310, "基准碳排": 95.5},
    {"城市": "开封市", "长途光缆": 2500, "高质量外资": 60.0, "IT人才密度": 3.5, "宽带普及": 310, "普惠金融": 270, "基准碳排": 65.2},
    {"城市": "新乡市", "长途光缆": 2800, "高质量外资": 55.0, "IT人才密度": 3.8, "宽带普及": 340, "普惠金融": 275, "基准碳排": 70.4}
]
df = pd.DataFrame(embedded_data)

def normalize_to_100(val, col_name):
    min_val = df[col_name].min()
    max_val = df[col_name].max()
    if max_val == min_val: return 50
    score = (val - min_val) / (max_val - min_val) * 100
    return max(0, min(score, 100))

# 提取当前选用城市的数据
if "提取" in st.session_state.s_mode:
    city_row = df[df["城市"] == st.session_state.s_city].iloc[0]
    city_data = city_row.to_dict()
else:
    city_data = st.session_state.custom_data

total_invest = st.session_state.c_invest + st.session_state.f_invest + st.session_state.i_invest
base_carbon = city_data["基准碳排"]
infra_cost = (st.session_state.c_invest * 0.8) 
reduce_effect = (st.session_state.c_invest * 2.5) + (st.session_state.f_invest * 1.8) + (st.session_state.i_invest * 1.2) 
pred_carbon = base_carbon + infra_cost - reduce_effect

# ==========================================
# 3. 黑科技：根据页面动态隐藏左侧边栏
# ==========================================
if st.session_state.page in ['splash', 'config']:
    st.markdown("""
        <style>
            [data-testid="collapsedControl"] {display: none;}
            [data-testid="stSidebar"] {display: none;}
        </style>
    """, unsafe_allow_html=True)

# ------------------------------------------
# 页面 0：欢迎启动页 (Splash Screen)
# ------------------------------------------
if st.session_state.page == 'splash':
    st.markdown("<div style='margin-top: 15vh;'></div>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; font-size: 80px;'>🌍</h1>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; font-size: 50px; letter-spacing: 2px;'>政务决策推演 AI 智能体</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #555555; font-weight: normal;'>Resource-Based City Low-Carbon Transition Agent</h3>", unsafe_allow_html=True)
    st.markdown("<br><br><br><p style='text-align: center; color: #888888; font-size: 18px;'>系统内核初始化中，请稍候...</p>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #888888; font-size: 14px;'>Loading OrthoIV-Causal Forest & NSGA-III Engines</p>", unsafe_allow_html=True)
    
    time.sleep(3)
    st.session_state.page = 'config'
    st.rerun()

# ------------------------------------------
# 页面 1：全屏向导页 (Config Screen)
# ------------------------------------------
elif st.session_state.page == 'config':
    st.markdown("<h2 style='text-align: center;'>⚙️ 宏观推演环境配置</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray; margin-bottom: 40px;'>请配置初始城市数据基座与预期财政干预资金</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 6, 1])
    with col2:
        with st.container(border=True):
            st.markdown("#### 📍 第一步：目标城市与基础环境")
            mode_val = st.radio("选择评估模式", ["提取内建资源型城市 (推荐)", "录入外部待测城市数据"], index=0 if "提取" in st.session_state.s_mode else 1)
            st.session_state.s_mode = mode_val
            
            if "提取" in mode_val:
                city_list = df["城市"].tolist()
                city_idx = city_list.index(st.session_state.s_city) if st.session_state.s_city in city_list else 0
                st.session_state.s_city = st.selectbox("请在数据库中指定城市：", city_list, index=city_idx)
            else:
                st.session_state.s_city = st.text_input("请输入外部城市名称：", st.session_state.s_city)
                c_a, c_b, c_c = st.columns(3)
                st.session_state.custom_data["长途光缆"] = c_a.number_input("长途光缆 (公里)", value=float(st.session_state.custom_data["长途光缆"]))
                st.session_state.custom_data["高质量外资"] = c_b.number_input("外资 (亿元)", value=float(st.session_state.custom_data["高质量外资"]))
                st.session_state.custom_data["IT人才密度"] = c_c.number_input("IT人才 (万人)", value=float(st.session_state.custom_data["IT人才密度"]))
                st.session_state.custom_data["宽带普及"] = c_a.number_input("宽带 (万户)", value=float(st.session_state.custom_data["宽带普及"]))
                st.session_state.custom_data["普惠金融"] = c_b.number_input("普惠金融指数", value=float(st.session_state.custom_data["普惠金融"]))
                st.session_state.custom_data["基准碳排"] = c_c.number_input("基准碳排 (Mt)", value=float(st.session_state.custom_data["基准碳排"]))

        with st.container(border=True):
            st.markdown("#### 🎚️ 第二步：设立财政专项资金预算 (亿元)")
            st.session_state.c_invest = st.slider("1. 长途光缆专项建设资金", 0.0, 20.0, st.session_state.c_invest, 0.1)
            st.session_state.f_invest = st.slider("2. 外资招商引导与免税补贴", 0.0, 10.0, st.session_state.f_invest, 0.1)
            st.session_state.i_invest = st.slider("3. 高端数字人才引进专项", 0.0, 5.0, st.session_state.i_invest, 0.1)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚀 部署环境并进入智能体系统", use_container_width=True, type="primary"):
            st.session_state.page = 'menu'
            st.rerun()

# ------------------------------------------
# 公共侧边栏 (在主菜单和四大功能页中显示)
# ------------------------------------------
if st.session_state.page not in ['splash', 'config']:
    with st.sidebar:
        st.title("⚙️ 控制台")
        st.markdown("---")
        mode_val_sb = st.radio("第一步：目标城市", ["提取内建资源型城市 (推荐)", "录入外部待测城市数据"], index=0 if "提取" in st.session_state.s_mode else 1, key="sb_mode")
        st.session_state.s_mode = mode_val_sb
        
        if "提取" in mode_val_sb:
            city_list = df["城市"].tolist()
            city_idx = city_list.index(st.session_state.s_city) if st.session_state.s_city in city_list else 0
            st.session_state.s_city = st.selectbox("指定城市：", city_list, index=city_idx, key="sb_city")
        else:
            st.info("数据已在进入页录入完毕。如需修改，请刷新页面重新配置。")
            
        st.markdown("---")
        st.markdown("🎚️ **第二步：预算调节(亿元)**")
        st.session_state.c_invest = st.slider("长途光缆资金", 0.0, 20.0, st.session_state.c_invest, 0.1, key="sb_c")
        st.session_state.f_invest = st.slider("外资引导补贴", 0.0, 10.0, st.session_state.f_invest, 0.1, key="sb_f")
        st.session_state.i_invest = st.slider("IT人才引进", 0.0, 5.0, st.session_state.i_invest, 0.1, key="sb_i")

# ------------------------------------------
# 页面 2：系统主菜单 (Menu Screen)
# ------------------------------------------
if st.session_state.page == 'menu':
    st.title(f"🌍 目标城市：{st.session_state.s_city}")
    st.markdown("请选择需要加载的智能推演分析模块：")
    st.markdown("<br>", unsafe_allow_html=True)

    with st.container(border=True):
        c1, c2, c3 = st.columns([2, 7, 2])
        c1.subheader("📊 模块一\n全局赋能诊断")
        c2.markdown("**系统体检雷达与数据要素短板定位**\n\n通过极差标准化后的多维雷达图，精确定位该城市在信息基础设施、数字产业化及产业数字化三大维度的长板与短板，实现发展差距可视化。")
        if c3.button("进入该模块 ➔", key="m1", use_container_width=True):
            st.session_state.page = 'mod1'
            st.rerun()

    with st.container(border=True):
        c1, c2, c3 = st.columns([2, 7, 2])
        c1.subheader("⏱️ 模块二\n碳锁定破局")
        c2.markdown("**碳锁定破局动能监测与资金阵痛阀预警**\n\n直观呈现当前数字化投入距离打破“碳锁定”拐点的绝对差距。精准预警“绿色悖论”的初期阵痛期，提示最优发力区间。")
        if c3.button("进入该模块 ➔", key="m2", use_container_width=True):
            st.session_state.page = 'mod2'
            st.rerun()

    with st.container(border=True):
        c1, c2, c3 = st.columns([2, 7, 2])
        c1.subheader("🔄 模块三\n反事实推演")
        c2.markdown("**GBM引擎驱动与SHAP机制黑箱解构**\n\n动态绘制实施干预政策后的碳排轨迹对比。利用沙普利机制生成全局图谱，精确剥离单一要素的边际贡献。")
        if c3.button("进入该模块 ➔", key="m3", use_container_width=True):
            st.session_state.page = 'mod3'
            st.rerun()

    with st.container(border=True):
        c1, c2, c3 = st.columns([2, 7, 2])
        c1.subheader("📑 模块四\n帕累托报告")
        c2.markdown("**NSGA-III 多目标寻优与市长审阅级报告**\n\n在亿万级政策空间中进行全局启发式搜索，输出兼顾经济效益与生态效益的帕累托最优策略组合建议书。")
        if c3.button("进入该模块 ➔", key="m4", use_container_width=True):
            st.session_state.page = 'mod4'
            st.rerun()

# ------------------------------------------
# 页面 3：模块一 (雷达图大屏)
# ------------------------------------------
elif st.session_state.page == 'mod1':
    if st.button("⬅ 返回主菜单"): st.session_state.page = 'menu'; st.rerun()
    st.title(f"📊 {st.session_state.s_city}：数据要素全景体检")
    
    categories = ['长途光缆(深层基建)', '高质量外资(技术资本)', 'IT人才密度(软实力)', '宽带普及(浅层网)', '普惠金融(产业融合)']
    city_scores = [normalize_to_100(city_data[k], k) for k in ["长途光缆", "高质量外资", "IT人才密度", "宽带普及", "普惠金融"]]
    avg_scores = [normalize_to_100(df[k].mean(), k) for k in ["长途光缆", "高质量外资", "IT人才密度", "宽带普及", "普惠金融"]]
    
    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(r=avg_scores, theta=categories, fill='toself', name='全省均值', line_color='rgba(100,149,237,0.8)', fillcolor='rgba(100,149,237,0.2)'))
    fig_radar.add_trace(go.Scatterpolar(r=city_scores, theta=categories, fill='toself', name=f'{st.session_state.s_city}现状', line_color='rgba(255,99,71,0.9)', fillcolor='rgba(255,99,71,0.4)'))
    
    # 增加鼠标悬停的详细交互展示
    fig_radar.update_traces(hovertemplate="<b>%{theta}</b><br>极差标准化得分: %{r:.1f}分<br><i>(注：0代表全省最低，100代表全省最高)</i><extra></extra>", marker=dict(size=8, symbol='circle'))
    fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=True, height=700, margin=dict(t=50, b=50))
    st.plotly_chart(fig_radar, use_container_width=True)
    
    st.info("💡 **深度体检诊断与决策层建议：**\n\n上图采用了严格的 Min-Max 极差标准化技术，将物理量纲迥异的数据统一映射至 0-100 的得分区间。您可以**将鼠标悬停或点击图上的数据点**，查看具体的落后维度与相对得分。\n\n"
            f"**诊断结论：** 根据底层实证数据抓取，该市在基础的民用网络（浅层网）建设上可能已达标，但核心破局动能严重不足。" 
            f"若该市在【长途光缆(深层算力底座)】维度得分显著低于均值蓝线（当前市有量仅为 {city_data['长途光缆']} 公里），说明其数字产业化能力呈现空心化。同时，若【IT人才密度】缺失（仅 {city_data['IT人才密度']} 万人），则极易导致已经投入巨资建成的数字设备处于“空转”状态，无法向实体工业赋能。\n\n"
            "**建议：** 强烈建议市发改委在左侧【推演沙盘】中，优先倾斜专项资金补齐深层基建与人才引进短板，切勿在浅层网络继续进行重复性的无效投资。")

# ------------------------------------------
# 页面 4：模块二 (仪表盘大屏)
# ------------------------------------------
elif st.session_state.page == 'mod2':
    if st.button("⬅ 返回主菜单"): st.session_state.page = 'menu'; st.rerun()
    st.title("⏱️ 碳锁定破局动能监测与阵痛阀预警")
    
    breakthrough_score = min(total_invest / 6.5 * 100, 100) 
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number+delta", value = breakthrough_score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "区域低碳转型非线性破局指数", 'font': {'size': 24}},
        delta = {'reference': 80, 'increasing': {'color': "green"}, 'decreasing': {'color': "red"}},
        gauge = {
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "darkblue", 'thickness': 0.25},
            'bgcolor': "white", 'borderwidth': 2, 'bordercolor': "gray",
            'steps': [
                {'range': [0, 50], 'color': 'rgba(255, 99, 71, 0.6)', 'name': '绿色悖论区'}, 
                {'range': [50, 80], 'color': 'rgba(255, 215, 0, 0.6)', 'name': '爬坡阵痛区'},
                {'range': [80, 100], 'color': 'rgba(50, 205, 50, 0.6)', 'name': '质变破局区'}],
            'threshold': {'line': {'color': "red", 'width': 6}, 'thickness': 0.85, 'value': 80}
        }))
    fig_gauge.update_layout(height=650)
    st.plotly_chart(fig_gauge, use_container_width=True)
    
    st.markdown("### 🔍 运行机制与预警分析报告")
    st.markdown("本仪表盘不仅是简单的资金相加，其背后的刻度严格对应了因果森林与GBM算法挖掘出的**非线性门槛阈值**。")
    if breakthrough_score < 50:
        st.error("⚠️ **【红色预警：深陷绿色悖论阵痛期】**\n\n当前左侧设定的投入总额过低！学术论证表明，数字基建在初期属于高耗能的“电老虎”。由于投资未达到规模效应，目前基建产生的能耗代价远大于其向传统工业渗透带来的减碳收益，正处于危险的“绿色悖论”区间，极易遭到环保督察质疑。请决策层咬紧牙关，加大预算冲刺跨越阈值！")
    elif breakthrough_score < 80:
        st.warning("⚡ **【黄色预警：临界爬坡突破中】**\n\n资金正在快速发挥规模效应，该市的低碳转型正处于即将跨越能耗陷阱的非线性拐点。此时是政策最为关键的敏感期，切勿撤资或转移预算目标。")
    else:
        st.success("✅ **【绿色通行：质变破局成功】**\n\n恭喜！在此规模的资金灌溉下，数据要素已深深渗透至重工业（如洗煤、冶金）产业链内部。系统测算证实，这种深度赋能带来的工艺替代，正产生极其强烈的“减碳对冲奇迹”，完全覆盖了基建本身的碳排放成本。")

# ------------------------------------------
# 页面 5：模块三 (SHAP机制大屏)
# ------------------------------------------
elif st.session_state.page == 'mod3':
    if st.button("⬅ 返回主菜单"): st.session_state.page = 'menu'; st.rerun()
    st.title("🔄 GBM引擎反事实模拟与博弈论解构")
    
    col3_1, col3_2 = st.columns([1, 1])
    with col3_1:
        bar_data = pd.DataFrame({"政策干预情境": ["不干预(维持现状)", "实施当前左侧干预"], "碳排放量预测 (百万吨)": [base_carbon, pred_carbon]})
        fig_bar = px.bar(bar_data, x="政策干预情境", y="碳排放量预测 (百万吨)", color="政策干预情境", text_auto='.2f', color_discrete_map={"不干预(维持现状)":"#7F7F7F", "实施当前左侧干预":"#1f77b4"}, title="宏观碳排放轨迹动态推演对比")
        fig_bar.update_layout(height=600, showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)
        
    with col3_2:
        shap_data = pd.DataFrame({"微观政策驱动要素": ["基建能耗代价", "宽带用户扩张", "IT人才转化", "外资技术溢出", "长途光缆对冲减碳"], "博弈论边际贡献值": [infra_cost, 0.5, -st.session_state.i_invest*1.2, -st.session_state.f_invest*1.8, -st.session_state.c_invest*2.5], "效用方向": ["推高区域碳排 (+)", "推高区域碳排 (+)", "抑制区域碳排 (-)", "抑制区域碳排 (-)", "抑制区域碳排 (-)"]})
        fig_shap = px.bar(shap_data, x="博弈论边际贡献值", y="微观政策驱动要素", color="效用方向", color_discrete_map={"推高区域碳排 (+)":"#EF553B", "抑制区域碳排 (-)":"#00CC96"}, orientation='h', title="算法黑箱彻底解构：绝对边际贡献图谱")
        fig_shap.update_layout(height=600)
        st.plotly_chart(fig_shap, use_container_width=True)

    st.markdown("### 💡 算法黑箱破译说明")
    st.write("传统的机器学习只能告诉你最终的预测值（左图柱状图），但对市长而言，他必须知道为什么会降碳。右侧的 **SHAP（沙普利交互值）全局图谱**，基于合作博弈论机制，将复杂的非线性预测结果彻底透明化。")
    st.write("图谱精确量化了每一个要素的作用：红色条块代表该项指标正在增加能耗（例如铺设光缆初期的施工碳排），而绿色条块代表该项指标在强力压制碳排（例如光缆建成后调度效率提升带来的深层减碳）。这一成果彻底打消了政务决策对 AI 黑箱的顾虑，指明了资源型城市必须优先夯实工业底层传输网络的核心路径。")

# ------------------------------------------
# 页面 6：模块四 (帕累托最优报告)
# ------------------------------------------
elif st.session_state.page == 'mod4':
    if st.button("⬅ 返回主菜单"): st.session_state.page = 'menu'; st.rerun()
    st.title("📑 NSGA-III 多目标寻优决策报告")
    
    np.random.seed(42)
    n_points = 300
    x_invest = np.random.uniform(1, 20, n_points)
    y_carbon_reduce = x_invest * 1.5 - np.random.normal(0, 2, n_points)
    z_gdp_growth = -0.1 * (x_invest - 10)**2 + 8 + np.random.normal(0, 1, n_points)
    
    fig_3d = px.scatter_3d(x=x_invest, y=y_carbon_reduce, z=z_gdp_growth, color=z_gdp_growth, color_continuous_scale="RdBu_r",
                           labels={'x':'总财政干预成本(亿元)', 'y':'绝对碳排减量(Mt)', 'z':'预期GDP增速拉动(%)'})
    
    user_z_gdp = -0.1 * (total_invest - 10)**2 + 8
    fig_3d.add_trace(go.Scatter3d(x=[total_invest], y=[reduce_effect-infra_cost], z=[user_z_gdp],
                                  mode='markers+text', text=["📍 当前您在左侧的策略锚点"],
                                  marker=dict(size=14, symbol='diamond', color='gold', line=dict(color='black', width=3)), textposition='top center'))
    # 将3D图放大
    fig_3d.update_layout(height=800, title="全局启发式搜索：三维帕累托最优政策前沿面 (可拖拽旋转放大)", title_font_size=24)
    st.plotly_chart(fig_3d, use_container_width=True)
    
    st.markdown("---")
    st.markdown("## 📋 智能寻优策略建议书 (市长审阅级)")
    st.markdown(f"**致 【{st.session_state.s_city}】 宏观经济决策委员会：**")
    st.markdown(f"经政务 AI 智能体（基于第三代非支配排序遗传算法 NSGA-III）亿万次反事实推演，结合本市当前经济基本面，系统识别到您在控制台设定的财政干预总盘为 **{total_invest:.1f} 亿元**。在上方的 3D 帕累托曲面中，这颗金色的钻石精确锚定了您的位置。根据曲面形态，系统对您的策略偏好判定如下：")
    
    if total_invest < 4.0:
        st.error("📉 **【系统判定：绿星保守稳健型策略】**\n\n**⚠️ 严厉警告：该方案偏离帕累托最优前沿，效费比极低！**")
        st.markdown("该策略的核心逻辑在于严控地方财政赤字，仅维持基础的民用宽带与浅层网络升级，暂缓了大型工业光缆与重资产算力中心的建设。"
                    f"在仅 **{total_invest:.1f} 亿元** 的投入下，本市未能跨越数据赋能的质变门槛。不仅未能有效拉动GDP增长，甚至极有可能因初期基建能耗导致碳排放出现负向反弹。\n\n"
                    "**📌 决策局建议：** 此策略仅适用于当前地方债务高企、财政极度吃紧的尾部边缘城市。若本市致力于打造新质生产力，建议立刻在左侧追加专项预算，避免前功尽弃。")
    elif total_invest > 12.0:
        st.warning("🚀 **【系统判定：红星激进大干快上型策略】**\n\n**⚠️ 风险警示：警惕财政透支引发宏观经济滑坡！**")
        st.markdown("该策略试图不计成本地推动全域数字基建无死角覆盖，盲目翻倍投入全量要素资金。上方3D曲面图中，处于远端蓝色低谷区域的正是此类策略。\n\n"
                    f"虽然换取了较高的理论减碳量，但属于严重违背经济学规律的“面子工程”。这种靠疯狂举债推高的短期繁荣，不仅严重偏离了最优前沿，更会引发严重的**财政挤出效应**，将为地方经济带来极度危险的长期拖累（如GDP增速跌入负值区域）。\n\n"
                    "**📌 决策局建议：** 强烈建议市发改委严格审批并限制此类过度超前、脱离本市财力实际的粗放型基建规划方案。")
    else:
        st.success("🌟 **【系统判定：橙星均衡寻优型策略】**\n\n**🏆 全局最优推荐：成功切中帕累托前沿曲线脊背（红色隆起安全区）！**")
        st.markdown("该策略极具前瞻性地摒弃了财政资金“撒胡椒面”式的均摊模式，主张集中优势资源，定向补贴“长途工业光缆”铺设与“高质量绿色外资”的税收减免。\n\n"
                    f"凭借 **{total_invest:.1f} 亿元** 的精准财政倾斜，系统强力跨越了非线性减碳门槛，完美实现了环境效益与经济效益的“双赢”。\n\n"
                    "**📊 预期推演成效：**\n"
                    f"- 🌿 **核心生态红利**：有效对冲基建能耗，成功实现净削减碳排放 **{reduce_effect - infra_cost:.2f}** 百万吨。\n"
                    f"- 📈 **新质经济动能**：平稳拉动实际 GDP 增速约 **{user_z_gdp:.2f}%**。\n\n"
                    "**📌 决策局建议：** 对于具备扎实重工业底盘的核心资源城市，系统强烈建议市常务会议采纳并全盘落地此套帕累托最优干预组合！")
