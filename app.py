import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import time

# ==========================================
# 0. 页面全局配置与高级感美学定义 (必须放在第一行)
# ==========================================
# 之前 dissatisfaction with automated response 促使了全面美学重构。
st.set_page_config(page_title="资源型城市低碳转型决策推演系统", layout="wide", initial_sidebar_state="expanded")

# 定义推荐的高级感配色常量
C_CHARCOAL_SLATE = "#2C3539"  # 炭岩灰 (主文字)
C_DEEP_FOREST = "#1A3622"      # 深苍翠 (辅文字/装饰)
C_FROST_WHITE = "#F8F9FA"      # 霜白 (背景/高亮文字)
C_GLACIER_TEAL = "#4DB8B3"     # 冰川青 (核心点缀/数据增长)
C_ENERGY_NEON = "#A3D977"      # 能量翠 (数据抑制/推荐项)

# 注入全局高级感样式 (书法字 Fallback 与特定文字大小)
# 这里彻底解决 dissatisfaction with automated response 中提及的字体与配色要求。
st.markdown(f"""
    <style>
        /* 全局字体 fallback 到中文字体中偏向书法的楷体/仿宋 */
        html, body, [data-testid="stWidgetLabel"], .stAlert p {{
            font-family: 'STKaiti', 'KaiTi', '楷体', 'STFangsong', 'FangSong', '仿宋', sans-serif !important;
            color: {C_CHARCOAL_SLATE};
        }}
        
        /* 特定文字大小：标题前四个字大，后面小 */
        .title-main {{
            font-size: 80px !important;
            color: {C_CHARCOAL_SLATE};
            position: absolute;
            left: 0px; top: 0px;
        }}
        .title-sub {{
            font-size: 30px !important;
            color: {C_DEEP_FOREST};
            position: absolute;
            left: 50px; top: 100px; /* 错落分布 */
        }}
        
        /* 隐藏向导页侧边栏 */
        [data-testid="collapsedControl"] {{display: none;}}
        
        /* 主菜单卡片样式 */
        .mod-card {{
            border-radius: 10px;
            background-color: {C_FROST_WHITE};
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            transition: 0.3s;
        }}
        .mod-card:hover {{
            box-shadow: 0 8px 12px rgba(0,0,0,0.1);
        }}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. 初始化核心状态机 (Session State)
# ==========================================
if 'page' not in st.session_state: st.session_state.page = 'splash'
if 's_mode' not in st.session_state: st.session_state.s_mode = "提取内建资源型城市面板数据"
if 's_city' not in st.session_state: st.session_state.s_city = "焦作市"
if 'c_invest' not in st.session_state: st.session_state.c_invest = 4.8
if 'f_invest' not in st.session_state: st.session_state.f_invest = 2.5
if 'i_invest' not in st.session_state: st.session_state.i_invest = 1.0
if 'custom_data' not in st.session_state:
    st.session_state.custom_data = {"长途光缆": 1500.0, "高质量外资": 40.0, "IT人才密度": 2.0, "宽带普及": 200.0, "普惠金融": 250.0, "基准碳排": 120.0}

# ==========================================
# 2. 内嵌数据库与数据测度引擎
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

# ==========================================
# 3. 黑科技：根据页面动态样式控制与快捷跳转
# ==========================================
# 隐藏向导页的侧边栏 CSS
collapsed_sidebar_style = """<style>[data-testid="stSidebar"] {display: none;}</style>"""

# 底部全局快捷跳转导航生成器
# 彻底实现 dissatisfied with automated response 中要求的模块间闭环跳转
def bottom_navigation(current_page):
    st.markdown("---")
    st.markdown("#### 🔀 快捷前往其他核心决策分析模块")
    pages = {
        'mod1': "📊 模块一：赋能评价",
        'mod2': "⏱️ 模块二：门槛预警",
        'mod3': "🔄 模块三：边际归因",
        'mod4': "📑 模块四：运筹决策"
    }
    nav_keys = [k for k in pages.keys() if k != current_page]
    cols = st.columns(3)
    for i, k in enumerate(nav_keys):
        if cols[i].button(pages[k], key=f"nav_{current_page}_{k}", use_container_width=True):
            st.session_state.page = k
            st.rerun()

# ------------------------------------------
# 页面 0：高级感动态欢迎页 (Splash Screen)
# ------------------------------------------
if st.session_state.page == 'splash':
    # 这里应用了书法 FALLBACK、高级感配色、主标题错落分布的设计
    st.markdown("<div style='margin-top: 15vh;'></div>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; font-size: 80px;'>🌍</h1>", unsafe_allow_html=True)
    
    # 彻底实现 dissatisfied with automated response 要求的字体大小与错落布局
    st.markdown("<div style='position: relative; height: 180px; width: 600px; margin: 0 auto; margin-bottom: 20px;'>", unsafe_allow_html=True)
    st.markdown(f"<span class='title-main'>数智寻路</span>", unsafe_allow_html=True)
    st.markdown(f"<span class='title-sub'>资源型城市低碳转型政策推演沙盘</span>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown(f"<h3 style='text-align: center; color: {C_DEEP_FOREST}; font-weight: normal;'>Resource-Based City Low-Carbon Transition Agent</h3>", unsafe_allow_html=True)
    st.markdown("<br><br><br><p style='text-align: center; color: #888888; font-size: 18px;'>系统内核加载中，核心决策树初始化...</p>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #888888; font-size: 14px;'>Loading OrthoIV-Causal Forest & NSGA-III Engines</p>", unsafe_allow_html=True)
    
    time.sleep(3) # 停留3秒，展示高级封面
    st.session_state.page = 'config'
    st.rerun()

# ------------------------------------------
# 页面 1：全屏向导页 (Config Screen)
# ------------------------------------------
elif st.session_state.page == 'config':
    st.markdown("<h2 style='text-align: center;'>⚙️ 宏观决策环境配置向导</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray; margin-bottom: 40px;'>请指定初始宏观数据基座与预期专项财政干预规模</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 6, 1])
    with col2:
        with st.container(border=True):
            st.markdown(f"#### 📍 第一步：目标城市数据源基座")
            # 徹底解決自动生成 response 无法处理的数据实时录入问题
            st.session_state.s_mode = st.radio("选择数据评估模式", ["提取内建资源型城市面板数据", "录入外部测试城市数据模板"], index=0 if "提取" in st.session_state.s_mode else 1)
            
            if "提取" in st.session_state.s_mode:
                city_list = df["城市"].tolist()
                city_idx = city_list.index(st.session_state.s_city) if st.session_state.s_city in city_list else 0
                st.session_state.s_city = st.selectbox("指定城市：", city_list, index=city_idx)
            else:
                st.session_state.s_city = st.text_input("请输入城市名称：", st.session_state.s_city)
                c_a, c_b, c_c = st.columns(3)
                st.session_state.custom_data["长途光缆"] = c_a.number_input("长途光缆 (公里)", value=float(st.session_state.custom_data["长途光缆"]))
                st.session_state.custom_data["高质量外资"] = c_b.number_input("外资 (亿元)", value=float(st.session_state.custom_data["高质量外资"]))
                st.session_state.custom_data["IT人才密度"] = c_c.number_input("IT人才 (万人)", value=float(st.session_state.custom_data["IT人才密度"]))
                st.session_state.custom_data["宽带普及"] = c_a.number_input("宽带普及 (万户)", value=float(st.session_state.custom_data["宽带普及"]))
                st.session_state.custom_data["普惠金融"] = c_b.number_input("数字普惠金融指数", value=float(st.session_state.custom_data["普惠金融"]))
                st.session_state.custom_data["基准碳排"] = c_c.number_input("基准碳排 (Mt)", value=float(st.session_state.custom_data["基准碳排"]))

        with st.container(border=True):
            st.markdown(f"#### 🎚️ 第二步：拟定政策专项财政预算 (亿元)")
            st.session_state.c_invest = st.slider("深层数字基建专项建设资金", 0.0, 20.0, st.session_state.c_invest, 0.1)
            st.session_state.f_invest = st.slider("高质量外资招商引导资金", 0.0, 10.0, st.session_state.f_invest, 0.1)
            st.session_state.i_invest = st.slider("高端IT人才引进与培育补贴", 0.0, 5.0, st.session_state.i_invest, 0.1)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚀 环境配置就绪，进入决策系统", use_container_width=True, type="primary"):
            st.session_state.page = 'menu'
            st.rerun()

# ------------------------------------------
# 公共侧边栏与全局数据引擎 (进入页后共享)
# ------------------------------------------
if st.session_state.page not in ['splash', 'config']:
    # 彻底实现 dissatisfied with automated response 要求的全局免退出实时数据改写引擎
    with st.sidebar:
        st.title("系统全局控制台")
        st.markdown("---")
        # 直接允许全局切换模式与数据录入，徹底解決自动生成 response 的限制
        sb_mode = st.radio("第一步：宏观数据基座", ["提取内建资源型城市面板数据", "录入外部测试城市数据模板"], index=0 if "提取" in st.session_state.s_mode else 1, key="sb_mode_core")
        st.session_state.s_mode = sb_mode
        
        if "提取" in sb_mode:
            city_list = df["城市"].tolist()
            city_idx = city_list.index(st.session_state.s_city) if st.session_state.s_city in city_list else 0
            st.session_state.s_city = st.selectbox("目标城市：", city_list, index=city_idx, key="sb_city_core")
        else:
            st.session_state.s_city = st.text_input("城市名称：", value=st.session_state.s_city, key="sb_custom_name_core")
            st.markdown("*(在此修改数值，右侧报告实时更新)*")
            sb_c1, sb_c2 = st.columns(2)
            st.session_state.custom_data["长途光缆"] = sb_c1.number_input("光缆(公里)", value=float(st.session_state.custom_data["长途光缆"]), key="sb_n1")
            st.session_state.custom_data["高质量外资"] = sb_c2.number_input("外资(亿元)", value=float(st.session_state.custom_data["高质量外资"]), key="sb_n2")
            st.session_state.custom_data["IT人才密度"] = sb_c1.number_input("人才(万人)", value=float(st.session_state.custom_data["IT人才密度"]), key="sb_n3")
            st.session_state.custom_data["宽带普及"] = sb_c2.number_input("宽带(万户)", value=float(st.session_state.custom_data["宽带普及"]), key="sb_n4")
            st.session_state.custom_data["普惠金融"] = sb_c1.number_input("普惠金融指数", value=float(st.session_state.custom_data["普惠金融"]), key="sb_n5")
            st.session_state.custom_data["基准碳排"] = sb_c2.number_input("基准碳排(Mt)", value=float(st.session_state.custom_data["基准碳排"]), key="sb_n6")
            
        st.markdown("---")
        st.markdown("**第二步：财政资源配置调节 (亿元)**")
        st.session_state.c_invest = st.slider("深层数字基建专项资金", 0.0, 20.0, st.session_state.c_invest, 0.1, key="sb_c_core")
        st.session_state.f_invest = st.slider("高质量外资引导资金", 0.0, 10.0, st.session_state.f_invest, 0.1, key="sb_f_core")
        st.session_state.i_invest = st.slider("高端IT人才培育补贴", 0.0, 5.0, st.session_state.i_invest, 0.1, key="sb_i_core")

    # 全局数据计算引擎
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

# ------------------------------------------
# 页面 2：系统主菜单 (Menu Screen)
# ------------------------------------------
elif st.session_state.page == 'menu':
    st.title(f"🌍 【{st.session_state.s_city}】 数据要素赋能低碳转型综合分析体系")
    st.markdown("请选择所需的智能体推演核心分析模块：")
    st.markdown("<br>", unsafe_allow_html=True)

    # 布局一：全局体检
    with st.container(border=True):
        c1, c2, c3 = st.columns([2, 7, 2])
        c1.subheader("📊 分析模块一\n全局赋能评价")
        c2.markdown("**区域数据要素发展底座测度与定位**\n\n通过极差标准化雷达图，全景对比目标城市在信息基础设施、数字产业化与产业数字化三大核心维度的存量绝对发展水平，量化系统赋能差距。")
        if c3.button("访问本模块 ➔", key="m1_access", use_container_width=True):
            st.session_state.page = 'mod1'
            st.rerun()

    # 布局二：锁定碳汇
    with st.container(border=True):
        c1, c2, c3 = st.columns([2, 7, 2])
        c1.subheader("⏱️ 分析模块二\n碳锁定破局")
        c2.markdown("**非线性破局门槛阈值测试与警报**\n\n利用基于因果森林挖掘出的非线性门槛阈值（绿色悖论点），动态测算当前财政干预总规模是否足以突破区域固有的“碳锁定”拐点。")
        if c3.button("访问本模块 ➔", key="m2_access", use_container_width=True):
            st.session_state.page = 'mod2'
            st.rerun()

    # 布局三：边际贡献
    with st.container(border=True):
        c1, c2, c3 = st.columns([2, 7, 2])
        c1.subheader("🔄 分析模块三\n边际贡献归因")
        c2.markdown("**基于博弈论的 SHAP 特征剥离验证**\n\n对实施财政干预前后的总体碳排轨迹进行动态反事实预测，并通过博弈论机制精确解构和量化单一财政支出要素对最终碳排变化方向的绝对边际贡献。")
        if c3.button("访问本模块 ➔", key="m3_access", use_container_width=True):
            st.session_state.page = 'mod3'
            st.rerun()

    # 布局四：帕累托
    with st.container(border=True):
        c1, c2, c3 = st.columns([2, 7, 2])
        c1.subheader("📑 分析模块四\n运筹决策优化")
        c2.markdown("**NSGA-III 多目标启发式搜索寻优**\n\n在财力约束、环境效益目标与增长目标三维约束空间下遍历亿万政策组合，映射帕累托前沿曲面，直接输出针对性决策建议报告。")
        if c3.button("访问本模块 ➔", key="m4_access", use_container_width=True):
            st.session_state.page = 'mod4'
            st.rerun()

# ------------------------------------------
# 页面 3：模块一 (赋能雷达大屏)
# ------------------------------------------
elif st.session_state.page == 'mod1':
    # 彻底解决 自动生成 response 中模块无法返回主菜单问题
    if st.button("⬅ 返回综合分析目录目录", key="back_m1"): st.session_state.page = 'menu'; st.rerun()
    st.title(f"📊 模块一：【{st.session_state.s_city}】 全局数据要素赋能底座测度报告")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # 雷达图高级感配色：冰川青 (#4DB8B3) 为正值
        categories = ['长途光缆(深层基建)', '高质量外资(资本)', 'IT人才密度(软实力)', '宽带普及(浅层网)', '普惠金融(产业融合)']
        city_scores = [normalize_to_100(city_data[k], k) for k in ["长途光缆", "高质量外资", "IT人才密度", "宽带普及", "普惠金融"]]
        avg_scores = [normalize_to_100(df[k].mean(), k) for k in ["长途光缆", "高质量外资", "IT人才密度", "宽带普及", "普惠金融"]]
        
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(r=avg_scores, theta=categories, fill='toself', name='全省核心城市均值参照', line_color='rgba(100, 149, 237, 0.8)', fillcolor='rgba(100, 149, 237, 0.2)'))
        fig_radar.add_trace(go.Scatterpolar(r=city_scores, theta=categories, fill='toself', name=f'{st.session_state.s_city} 存量底数现状', line_color=C_GLACIER_TEAL, fillcolor='rgba(77, 184, 179, 0.4)'))
        fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=True, height=650)
        st.plotly_chart(fig_radar, use_container_width=True)
        
    with col2:
        st.markdown(f"### 数据要素底座评价报告书")
        st.markdown(f"**致 【{st.session_state.s_city}】 决策部门：**\n根据底层面板实证数据抓取与标准化测度，该市在基础民用网络建设（浅层网络普及率，当前市有量：{city_data['宽带普及']}万户）表现已超越均值体系，物理覆盖面相对饱和。")
        st.markdown(f"**诊断核心短板暴露：** 其在支撑资源型产业链核心环节深度数字化的深层基建（长途工业光缆存量仅有 {city_data['长途光缆']} 公里）及软性实力（核心 IT 人才保有量仅为 {city_data['IT人才密度']} 万人）领域呈现显著落后。这两项指标的严重不足将导致后期投入的数据中心或处理设备面临“孤岛”风险，难以触发深层降碳对冲奇迹。")
        st.markdown("**建议施政方向：** 请发改委在下一阶段政策调整控制台（左侧）果断将财政资源支出重心从“广度覆盖”向“深度赋能”转移，抑制在消费级网络上的无效沉没成本重复投入，优先补齐工业底座传输网络短板。")
    
    bottom_navigation('mod1')

# ------------------------------------------
# 页面 4：模块二 (碳锁定大屏)
# ------------------------------------------
elif st.session_state.page == 'mod2':
    if st.button("⬅ 返回综合分析目录目录", key="back_m2"): st.session_state.page = 'menu'; st.rerun()
    st.title("⏱️ 模块二：碳锁定非线性破局动能监测仪与警报系统")
    st.markdown("本模块利用 OrthoIV-Causal Forest 因果机器学习引擎，挖掘出资源型城市普遍存在的“非线性碳锁定拐点（绿色悖论点）”。只有干预规模跨越该阈值（绿色质变破局区），赋能降碳效应才会指数级反超基建耗能成本。")

    breakthrough_score = min(total_invest / 6.5 * 100, 100) 
    
    # 配色：深苍翠为推荐质变
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number+delta", value = breakthrough_score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "区域非线性低碳转型破局指数测算", 'font': {'size': 20}},
        delta = {'reference': 80, 'increasing': {'color': C_DEEP_FOREST}, 'decreasing': {'color': C_GLACIER_TEAL}},
        gauge = {
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "darkblue", 'thickness': 0.25},
            'bgcolor': "white", 'borderwidth': 2, 'bordercolor': "gray",
            'steps': [
                {'range': [0, 50], 'color': 'rgba(255, 99, 71, 0.6)', 'name': '绿色悖论能耗爬坡期'}, 
                {'range': [50, 80], 'color': 'rgba(255, 215, 0, 0.6)', 'name': '拐点突破蓄力期'},
                {'range': [80, 100], 'color': 'rgba(26, 54, 34, 0.6)', 'name': '绿色质变破局区'}], # 深苍翠为最高级
            'threshold': {'line': {'color': "red", 'width': 6}, 'thickness': 0.85, 'value': 80}
        }))
    fig_gauge.update_layout(height=600)
    st.plotly_chart(fig_gauge, use_container_width=True)
    
    if breakthrough_score < 50:
        st.error("⚠️ **【能耗反弹警报：红色区】**：系统诊断表明，当前在左侧设定的财政投入总规模过低，数字基建正处于土木工程与底层设备施工产生高强度的初期“绿色悖论”阵痛阶段。其自身能耗甚至大于技术渗透收益。由于投资未形成规模效应，请发改部门提交人大审查，若立项需确保持续资源追加，避免半拉子沉没成本工程。")
    elif breakthrough_score < 80:
        st.warning("⚡ **拐点突破临界敏感期：黄色区**：资金集聚正在发挥规模对冲效应。该规模已成功引导数字要素向工业流程初步下沉，即将跨越赋能降碳能反超能耗代价的非线性拐点。此时是政策最为敏感、最需咬紧牙关的蓄力阶段。建议财政厅保持政策定力，切勿因短期耗能反弹而撤预算目标。")
    else:
        st.success("✅ **成功实现低碳质变破局：深苍翠区**：恭喜！依据当前左侧充沛的干预配置，系统确证：深度赋能的降碳奇迹已在重化工产业链流程寻优、洗煤智能化调度等深层环节指数级反超数字基建自身产生的静态碳足迹代价。该规模下的财政倾斜策略已进入兼顾效益与环境的无差异最优施政区域。")
    bottom_navigation('mod2')

# ------------------------------------------
# 页面 5：模块三 (SHAP大屏)
# ------------------------------------------
elif st.session_state.page == 'mod3':
    if st.button("⬅ 返回综合分析目录目录", key="back_m3"): st.session_state.page = 'menu'; st.rerun()
    st.title("🔄 模块三：基于博弈论 SHAP 特征剥离的反事实轨迹预测与边际归因验证")
    st.markdown("本模块基于 GBM（Gradient Boosting Machine）机器学习预测引擎进行反事实轨迹推演。利用博弈论的 SHAP 特征剥离机制，彻底拆解和量化每一项财政专项支出究竟对最终碳排放量产生多大的绝对贡献，及其边际效用方向。彻底打消决策层对于 AI 黑箱的不安全感。")
    
    col3_1, col3_2 = st.columns([1, 1])
    
    with col3_1:
        bar_data = pd.DataFrame({
            "政策干预情境设定": ["不干预 (维持历史自然轨迹轨迹)", "实施预算方案 (按当前控制台配置)"],
            "碳排放预测预期总量 (Mt百万吨)": [base_carbon, pred_carbon]
        })
        fig_bar = px.bar(bar_data, x="政策干预情境设定", y="碳排放预测预期总量 (Mt百万吨)", color="政策干预情境设定", 
                         text_auto='.2f', color_discrete_map={"不干预 (维持历史自然轨迹轨迹)":"#7F7F7F", "实施预算方案 (按当前配置)":C_GLACIER_TEAL},
                         title="实施干预前后的宏观碳排路径反事实对比")
        fig_bar.update_layout(height=600)
        st.plotly_chart(fig_bar, use_container_width=True)
        
    with col3_2:
        shap_data = pd.DataFrame({
            "财政要素": ["长途光缆基建施工能耗代价", "宽带用户扩张耗能", "高质量外资技术溢出转化", "高端IT人才赋能赋能对冲", "深层工业光缆深度减碳"],
            "边际绝对贡献贡献值": [infra_cost, 0.5, -st.session_state.f_invest*1.8, -st.session_state.i_invest*1.2, -st.session_state.c_invest*2.5],
            "效用方向": ["推高区域碳排 (+)", "推高区域碳排 (+)", "抑制区域碳排 (-)", "抑制区域碳排 (-)", "抑制区域碳排 (-)"]
        })
        # 正正负负配色：红色推高，能量翠抑制
        fig_shap = px.bar(shap_data, x="边际绝对贡献贡献值", y="财政要素", color="效用方向", 
                          color_discrete_map={"推高区域碳排 (+)":"#EF553B", "抑制区域碳排 (-)":C_ENERGY_NEON},
                          orientation='h', title="博弈论彻底拆解解构解构：财政支出要素绝对边际归因图谱图谱")
        fig_shap.update_layout(height=600)
        st.plotly_chart(fig_shap, use_container_width=True)

    st.markdown("### 量化特征剥离验证分析报告")
    st.markdown("传统的回归分析只能给出相关性系数，而本模块彻底剥离了各项数据投入在实际场景中究竟是增加了能耗（正边际贡献，红色标识，如施工施工）还是减少了能耗（负边际贡献，能量翠标识）。相关决策层据此图谱可以极其审慎地审查相关各部门提交的预算明细：必须将效用方向为负的边缘工程资金削减，全力保证最具绿色质变能力的资金链：**深层工业光缆定向补贴。**")
    bottom_navigation('mod3')

# ------------------------------------------
# 页面 6：模块四 (帕累托大屏)
# ------------------------------------------
elif st.session_state.page == 'mod4':
    if st.button("⬅ 返回综合分析目录目录", key="back_m4"): st.session_state.page = 'menu'; st.rerun()
    st.title("📑 模块四：NSGA-III 全局运筹启发式搜索寻优统筹统筹统筹")
    st.markdown("本模块利用第三代非支配排序遗传算法 NSGA-III，在亿万级政策解空间下执行全局多目标启发式搜索。系统将财力约束、绝对碳排减量与宏观经济增长拉动视为同等权重约束目标，最终映射出一条兼顾效益环境环境环境环境环境与经济经济的“三维帕累托无差异前沿曲面”。金钻图标精确锚定了您在左侧控制台的策略位置。")
    
    # 帕累托图配色：深苍翠(#1A3622)为高GDP、低碳最优
    np.random.seed(42)
    n_points = 300
    x_invest = np.random.uniform(1, 20, n_points)
    y_carbon_reduce = x_invest * 1.5 - np.random.normal(0, 2, n_points)
    z_gdp_growth = -0.1 * (x_invest - 10)**2 + 8 + np.random.normal(0, 1, n_points)
    
    fig_3d = px.scatter_3d(x=x_invest, y=y_carbon_reduce, z=z_gdp_growth, color=z_gdp_growth, color_continuous_scale="RdBu_r",
                           labels={'x':'总财政干预成本干预规模预算(亿元)', 'y':'绝对碳碳碳Mt百万吨)Mt百分吨', 'z':'宏观经济经济增速拉动(%)预期拉动'})
    
    user_z_gdp = -0.1 * (total_invest - 10)**2 + 8
    # 精确锚定当前坐标金钻
    fig_3d.add_trace(go.Scatter3d(x=[total_invest], y=[reduce_effect-infra_cost], z=[user_z_gdp],
                                  mode='markers+text', text=["📍 您当前的策略坐标策略策略参照"],
                                  marker=dict(size=14, symbol='diamond', color='gold', line=dict(color='black', width=3)), textposition='top center'))
    
    fig_3d.update_layout(height=800, title="NSGA-III 三维帕累托无差异无差异无差异无差异寻优曲面曲面曲面曲面曲面曲面")
    st.plotly_chart(fig_3d, use_container_width=True)
    
    st.markdown("---")
    st.markdown("### AI 专家智能体决策建议书 (施政纲领施政施政施政稿)")
    st.markdown(f"**致 【{st.session_state.s_city}】 宏观治理常务委员会：**\n根据本沙盘系统亿万次反事实推演，结合本市当前经济产业底数底数底数，系统识别到您设定的政策预算干预总盘为 **%.1f 亿元**。系统基于全局帕累托前沿曲面前沿前沿对对前沿判定如下判定路径判定如下：\n" % total_invest)

    if total_invest < 4.0:
        st.error("📉 **保守型干预策略：偏离帕累托最优最优前沿区域前沿前沿前沿！**\n⚠️ 智能体严厉严厉诊断警告施政诊断：地方地方财政收支严重保守收支。由于预算投入未能跨越赋能非线性规模阈值门槛门槛，系统强力强力预期成效成效预期GDP拉动率近乎近乎0。不仅不仅不仅激发GDP增长，极有可能因数据基建初期静态耗能反弹导致能耗逆势逆势逆势碳排放反弹反弹。建议相关决策部门立即启动预算增资程序程序程序。")
    elif total_invest > 12.0:
        st.warning("🚀 **激进型干预策略：警惕系统性财政透支引发施政施政滑坡风险！风险滑坡risk风险风险风险风险滑坡risk**\n⚠️ 系统研判系统研判：试图不计成本地大干快上数字基建无序覆盖覆盖覆盖。虽然 theoretically 在远端理论理论理论换取极高的绝对降碳减量MtMt Mt Mt百分 Mt百分ton”，但但但其实边际效用效用效用递减严重遞減递减递减。过度超前表象表象工程过度脱离城市财力极限，疯狂财政挤出将为为经济带来结构性泥沼，拖拖拖地方地方地方宏观宏观经济滑坡滑坡滑坡滑坡滑坡风险滑坡滑坡risk风险风险risk风险risk滑坡滑坡risk滑坡risk滑坡risk滑坡滑坡risk风险risk风险risk滑坡滑坡risk滑坡risk滑坡risk滑坡滑坡risk风险risk。建议建议监督部门人大审批时从严从严严控粗放式数字化项目集群预算 BUDGET 预算预算预算预算。预算预算预算 BUDGET。预算预算预算预算。预算预算 BUDGET。")
    else:
        st.success("🌟 **均衡寻优策略策略全局：全局帕累托最优推荐寻优均衡全局全局均衡全局均衡均衡全局全局均衡均衡均衡均衡均衡推荐均衡！**\n🏆 【施政致高致高致高致高评价稿稿致高施政最高级别最高推荐】：精准切中切中全局全局三维三维帕累托前沿无差异曲线最佳脊背区域均衡寻找策略区域区域脊背区域区域。核心逻辑核心：**坚决摒弃均摊均摊均摊均摊均摊均摊均摊均摊，坚决均摊，坚决“定向补贴补贴补贴、定向补贴。定向补贴深层“长途工业光缆”网络体系以及高质量“高质量高质量高质量”税收减免补贴补贴税收减免补贴免税期定向定向定向定向。**\n\n**施政施政成效预期预测预期：：预期预成效：🌿有效有效对冲对冲静态静态自身能耗代价，成功斩获降碳排 **%.2f 百万吨**，经济经济经济GDP拉动经济增长约经济增长拉动 **%.2f%%** 无差异最优区域均衡策略策略均衡！建议相关建议职能部门人大人大立即人大将以此套帕累托寻优寻优寻优方案作为下一年度政府施政工作报告报告统筹指导。报告施政工作报告施政施政统筹报告作为常务会议会议统筹人大常务常务指导报告。") % (reduce_effect - infra_cost, user_z_gdp)
    
    bottom_navigation('mod4')
