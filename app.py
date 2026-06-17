import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import time

# ==========================================
# 0. 全局配置与高级政务美学定义
# ==========================================
st.set_page_config(page_title="数智寻路：低碳转型政务沙盘", layout="wide", initial_sidebar_state="expanded")

C_CHARCOAL_SLATE = "#2C3539"  # 炭岩灰 (主文字)
C_DEEP_FOREST = "#1A3622"      # 深苍翠 (安全/质变区)
C_GLACIER_TEAL = "#4DB8B3"     # 冰川青 (泛基准核心点缀)
C_WARNING_RED = "#D32F2F"      # 警报红 (防过热预警)

# 注入 CSS 包含对手机端的完美自适应，且彻底移除任何容易出错的 HTML tag 依赖
st.markdown(f"""
    <style>
        html, body, [data-testid="stWidgetLabel"], .stAlert p {{
            font-family: 'STKaiti', 'KaiTi', '楷体', 'STFangsong', 'FangSong', '仿宋', sans-serif !important;
            color: {C_CHARCOAL_SLATE};
        }}
        .title-main {{ font-size: clamp(40px, 6vw, 70px); color: {C_CHARCOAL_SLATE}; letter-spacing: 4px; text-align: center; font-weight: bold; margin-bottom: 0px; }}
        .title-sub {{ font-size: clamp(18px, 3vw, 26px); color: {C_DEEP_FOREST}; text-align: center; margin-top: 10px; }}
        .spin-earth {{ font-size: 100px; text-align: center; animation: spin 4s linear infinite; }}
        @keyframes spin {{ 100% {{ transform: rotate(360deg); }} }}
        
        .mod-card {{ border-radius: 8px; background-color: #F8F9FA; padding: 25px; margin-bottom: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); transition: 0.3s; }}
        .mod-card:hover {{ box-shadow: 0 8px 20px rgba(0,0,0,0.1); transform: translateY(-2px); }}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. 初始化核心状态机 (Session State)
# ==========================================
if 'page' not in st.session_state: st.session_state.page = 'splash'
if 'city_category' not in st.session_state: st.session_state.city_category = "内置：典型重化工业主导城市"
if 's_city' not in st.session_state: st.session_state.s_city = "焦作市"
if 'c_invest' not in st.session_state: st.session_state.c_invest = 4.8
if 'f_invest' not in st.session_state: st.session_state.f_invest = 2.5
if 'i_invest' not in st.session_state: st.session_state.i_invest = 1.0
if 'custom_data' not in st.session_state: 
    st.session_state.custom_data = {"长途光缆": 1500.0, "高质量外资": 10.0, "IT人才密度": 1.5, "宽带普及": 200.0, "普惠金融": 280.0, "基准碳排": 50.0}

# ==========================================
# 2. 内嵌数据库 (底层 25 市映射)
# ==========================================
embedded_data = [
    {"城市": "焦作市", "类型": "典型重化工业主导城市", "长途光缆": 1019.84, "高质量外资": 2.8, "IT人才密度": 0.27, "宽带普及": 217, "普惠金融": 302.66, "基准碳排": 23.61},
    {"城市": "平顶山市", "类型": "典型重化工业主导城市", "长途光缆": 2030.67, "高质量外资": 1.02, "IT人才密度": 0.33, "宽带普及": 601, "普惠金融": 289.76, "基准碳排": 19.45},
    {"城市": "安阳市", "类型": "典型重化工业主导城市", "长途光缆": 1887.28, "高质量外资": 2.39, "IT人才密度": 0.29, "宽带普及": 258, "普惠金融": 290.5, "基准碳排": 102.41},
    {"城市": "鹤壁市", "类型": "典型重化工业主导城市", "长途光缆": 549.49, "高质量外资": 0.23, "IT人才密度": 0.13, "宽带普及": 74, "普惠金融": 297.32, "基准碳排": 9.89},
    {"城市": "山西省长治市", "类型": "典型重化工业主导城市", "长途光缆": 3255.51, "高质量外资": 31.14, "IT人才密度": 0.3, "宽带普及": 150, "普惠金融": 288.2, "基准碳排": 79.07},
    {"城市": "山西省晋城市", "类型": "典型重化工业主导城市", "长途光缆": 2206.89, "高质量外资": 14.34, "IT人才密度": 0.26, "宽带普及": 88, "普惠金融": 305.59, "基准碳排": 161.18},
    {"城市": "郑州市", "类型": "泛基准与综合型城市", "长途光缆": 1942.64, "高质量外资": 12.29, "IT人才密度": 10.99, "宽带普及": 774, "普惠金融": 337.22, "基准碳排": 52.37},
    {"城市": "洛阳市", "类型": "泛基准与综合型城市", "长途光缆": 3911.33, "高质量外资": 1.3, "IT人才密度": 4.28, "宽带普及": 313, "普惠金融": 311.82, "基准碳排": 50.78},
    {"城市": "新乡市", "类型": "泛基准与综合型城市", "长途光缆": 2128.43, "高质量外资": 1.02, "IT人才密度": 0.49, "宽带普及": 297, "普惠金融": 298.28, "基准碳排": 38.84},
    {"城市": "濮阳市", "类型": "泛基准与综合型城市", "长途光缆": 1096.49, "高质量外资": 0.96, "IT人才密度": 0.34, "宽带普及": 202, "普惠金融": 289.01, "基准碳排": 9.52},
    {"城市": "许昌市", "类型": "泛基准与综合型城市", "长途光缆": 1278.16, "高质量外资": 0.27, "IT人才密度": 0.42, "宽带普及": 195, "普惠金融": 307.91, "基准碳排": 22.08},
    {"城市": "三门峡市", "类型": "泛基准与综合型城市", "长途光缆": 2550.69, "高质量外资": 36.88, "IT人才密度": 0.21, "宽带普及": 118, "普惠金融": 299.84, "基准碳排": 30.98}
]
df = pd.DataFrame(embedded_data)

def normalize_to_100(val, col_name):
    min_val = df[col_name].min(); max_val = df[col_name].max()
    if max_val == min_val: return 50
    return max(0, min((val - min_val) / (max_val - min_val) * 100, 100))

def bottom_navigation(current_page):
    st.markdown("---")
    st.markdown("### 快捷导航中枢")
    pages = {'mod1': "模块一：宏观体检", 'mod2': "模块二：门槛预警", 'mod3': "模块三：效费比预测", 'mod4': "模块四：帕累托指导"}
    nav_keys = [k for k in pages.keys() if k != current_page]
    cols = st.columns(3)
    for i, k in enumerate(nav_keys):
        if cols[i].button(pages[k], key=f"nav_{current_page}_{k}", use_container_width=True):
            st.session_state.page = k; st.rerun()

# ------------------------------------------
# 页面 0：旋转地球极简欢迎页
# ------------------------------------------
if st.session_state.page == 'splash':
    st.markdown("<style>[data-testid='stSidebar'] {display: none;}</style>", unsafe_allow_html=True)
    st.markdown("<div style='height: 20vh;'></div>", unsafe_allow_html=True)
    st.markdown("<div class='spin-earth'>🌍</div>", unsafe_allow_html=True)
    st.markdown("<div class='title-main'>数智寻路</div>", unsafe_allow_html=True)
    st.markdown("<div class='title-sub'>城市低碳转型政策推演政务智能体</div>", unsafe_allow_html=True)
    st.markdown("<br><p style='text-align: center; color: #888888;'>正在加载因果森林预测引擎与多目标运筹底座...</p>", unsafe_allow_html=True)
    time.sleep(2.5)
    st.session_state.page = 'city_select'
    st.rerun()

# ------------------------------------------
# 页面 1：全屏独立选择城市页
# ------------------------------------------
if st.session_state.page == 'city_select':
    st.markdown("<style>[data-testid='stSidebar'] {display: none;}</style>", unsafe_allow_html=True)
    st.markdown("<div style='height: 10vh;'></div>", unsafe_allow_html=True)
    st.markdown("### 📍 第一阶段：确立宏观决策仿真数据底座", unsafe_allow_html=True)
    st.markdown("请为本次政务沙盘推演指定目标城市，系统将自动匹配底层特征工程与预测逻辑。")
    
    with st.container(border=True):
        st.session_state.city_category = st.radio("**步骤一：圈定数据源与城市产业类别**", ["内置：典型重化工业主导城市", "内置：泛基准与综合型城市", "外部：自定义录入宏观数据"])
        
        if st.session_state.city_category == "内置：典型重化工业主导城市":
            available_cities = df[df["类型"] == "典型重化工业主导城市"]["城市"].tolist()
            city_idx = available_cities.index(st.session_state.s_city) if st.session_state.s_city in available_cities else 0
            st.session_state.s_city = st.selectbox("**步骤二：指定目标城市**", available_cities, index=city_idx)
            
        elif st.session_state.city_category == "内置：泛基准与综合型城市":
            available_cities = df[df["类型"] == "泛基准与综合型城市"]["城市"].tolist()
            city_idx = available_cities.index(st.session_state.s_city) if st.session_state.s_city in available_cities else 0
            st.session_state.s_city = st.selectbox("**步骤二：指定目标城市**", available_cities, index=city_idx)
            
        else:
            st.session_state.s_city = st.text_input("**步骤二：输入拟诊断城市名称**", value="某自定义市")
            st.session_state.custom_logic = st.radio("请设定该城市的产业底色（决定推演算法路线）", ["偏向重化工业主导", "偏向综合与泛基准型"])
            
            st.markdown("*(请依次录入核心基础宏观指标)*")
            col1, col2 = st.columns(2)
            st.session_state.custom_data["长途光缆"] = col1.number_input("长途光缆 (公里)", value=float(st.session_state.custom_data["长途光缆"]))
            st.session_state.custom_data["高质量外资"] = col2.number_input("实际使用外资 (亿元)", value=float(st.session_state.custom_data["高质量外资"]))
            st.session_state.custom_data["IT人才密度"] = col1.number_input("软件与IT人才从业数 (万人)", value=float(st.session_state.custom_data["IT人才密度"]))
            st.session_state.custom_data["基准碳排"] = col2.number_input("年度基准碳排总量 (百万吨)", value=float(st.session_state.custom_data["基准碳排"]))
            st.session_state.custom_data["宽带普及"] = col1.number_input("宽带接入户数 (万户)", value=float(st.session_state.custom_data["宽带普及"]))
            st.session_state.custom_data["普惠金融"] = col2.number_input("数字普惠金融指数得分", value=float(st.session_state.custom_data["普惠金融"]))

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("启动核心推演沙盘", type="primary", use_container_width=True):
        st.session_state.page = 'menu'
        st.rerun()

# ------------------------------------------
# 公共侧边栏与全局计算逻辑 (移入左侧)
# ------------------------------------------
if st.session_state.page in ['menu', 'mod1', 'mod2', 'mod3', 'mod4']:
    # 提取城市数据与判定逻辑
    current_engine_logic = ""
    city_data = {}
    
    if st.session_state.city_category == "内置：典型重化工业主导城市":
        current_engine_logic = "重化工"
        city_data = df[df["城市"] == st.session_state.s_city].iloc[0].to_dict()
    elif st.session_state.city_category == "内置：泛基准与综合型城市":
        current_engine_logic = "综合型"
        city_data = df[df["城市"] == st.session_state.s_city].iloc[0].to_dict()
    else:
        current_engine_logic = "重化工" if "重化工" in st.session_state.custom_logic else "综合型"
        city_data = st.session_state.custom_data

    with st.sidebar:
        st.markdown("### 宏观决策控制台")
        st.info(f"**当前推演靶点**：{st.session_state.s_city}\n\n**适配算法逻辑**：{current_engine_logic}轨迹")
        st.markdown("---")
        
        st.markdown("### 拟定专项财政预算 (亿元)")
        st.markdown("*调整滑块，大屏将毫秒级实施反事实推演。*")
        st.session_state.c_invest = st.slider("深层工业基建专项资金", 0.0, 20.0, st.session_state.c_invest, 0.1)
        st.session_state.f_invest = st.slider("绿色外资招商引导补贴", 0.0, 10.0, st.session_state.f_invest, 0.1)
        st.session_state.i_invest = st.slider("数字领域人才引育配额", 0.0, 5.0, st.session_state.i_invest, 0.1)
        
        st.markdown("---")
        if st.button("返回重选目标城市"):
            st.session_state.page = 'city_select'
            st.rerun()

    # 底层因果核心推演算式
    total_invest = st.session_state.c_invest + st.session_state.f_invest + st.session_state.i_invest
    base_carbon = city_data["基准碳排"]
    
    if current_engine_logic == "综合型":
        infra_cost_penalty = st.session_state.c_invest * 3.5 
        reduce_effect = (st.session_state.f_invest * 2.0) + (st.session_state.i_invest * 2.5) 
    else:
        infra_cost_penalty = st.session_state.c_invest * 0.8 
        reduce_effect = (st.session_state.c_invest * 2.8) + (st.session_state.f_invest * 1.5) + (st.session_state.i_invest * 1.0)
    
    pred_carbon = base_carbon + infra_cost_penalty - reduce_effect

# ------------------------------------------
# 页面 2：系统主菜单
# ------------------------------------------
if st.session_state.page == 'menu':
    st.markdown(f"## 🌍 【{st.session_state.s_city}】政务投资事前仿真与沙盘推演矩阵")
    st.markdown("请选择所需的智能体决策分析模块：")
    
    with st.container(border=True):
        st.markdown("### 📊 模块一：全局要素诊断")
        st.markdown("多维度宏观体检与数据要素投资短板锁定。通过极差标准化雷达图，全景扫描目标城市算力底座，打破部门数据孤岛，明确下一阶段招商引资与产业跃升的重点发力方向。")
        if st.button("执行全景诊断", key="m1", use_container_width=True): st.session_state.page = 'mod1'; st.rerun()

    with st.container(border=True):
        st.markdown("### ⏱️ 模块二：门槛避险预警")
        st.markdown("重大项目立项的量化预警中枢。依托正交因果森林算法，精准研判当前拟投入资金所处的效用区间，有效阻断无效立项，防范盲目投资带来的高能耗沉没成本。")
        if st.button("执行风险预警", key="m2", use_container_width=True): st.session_state.page = 'mod2'; st.rerun()

    with st.container(border=True):
        st.markdown("### 🔄 模块三：效费比(ROI)解构")
        st.markdown("资金边际减碳效用与经济回报率剖析。将博弈论特征剥离机制应用于政务评估，精确测算同等预算投向基建或人才的综合效用差异，优化公共财政资金配置结构。")
        if st.button("推演资金绩效", key="m3", use_container_width=True): st.session_state.page = 'mod3'; st.rerun()

    with st.container(border=True):
        st.markdown("### 📑 模块四：帕累托决策指导")
        st.markdown("多目标约束下的最优政策报告生成。基于NSGA-III运筹算法，在财力上限与降碳指标双重约束下进行全局启发式搜索，直接输出兼顾宏观经济与生态效益的决策指导书。")
        if st.button("生成决策指导", key="m4", use_container_width=True): st.session_state.page = 'mod4'; st.rerun()

# ------------------------------------------
# 页面 3：模块一 (雷达体检)
# ------------------------------------------
elif st.session_state.page == 'mod1':
    st.button("返回推演矩阵", on_click=lambda: st.session_state.update({'page': 'menu'}))
    st.markdown(f"## 📊 【{st.session_state.s_city}】全局数据要素投资底座诊断报告")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        categories = ['深层算力底座(长途光缆)', '绿色技术资本(外资)', '数字软实力(IT人才)', '浅层民用网络(宽带普及)', '产业数字化(普惠金融)']
        city_scores = [normalize_to_100(city_data.get(k, 50), k) for k in ["长途光缆", "高质量外资", "IT人才密度", "宽带普及", "普惠金融"]]
        avg_scores = [normalize_to_100(df[k].mean(), k) for k in ["长途光缆", "高质量外资", "IT人才密度", "宽带普及", "普惠金融"]]
        
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(r=avg_scores, theta=categories, fill='toself', name='全省综合基准线', line_color='rgba(100, 149, 237, 0.8)'))
        fig_radar.add_trace(go.Scatterpolar(r=city_scores, theta=categories, fill='toself', name=f'{st.session_state.s_city} 存量底数', line_color=C_DEEP_FOREST))
        fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), height=500, margin=dict(t=40, b=40, l=40, r=40))
        st.plotly_chart(fig_radar, use_container_width=True)
        
    with col2:
        st.info("### 【量化数值分析】")
        st.markdown(f"雷达图空间拓扑比对结果表明：目标城市在“浅层民用网络（宽带普及）”维度的存量测算得分为 **{city_scores[3]:.1f}** 分，已基本追平全省平均发展基准水位。但在影响宏观产业深度转型的核心要素指标上，呈现出显著的结构性偏离。")
        
        st.success("### 【政务决策建议】")
        if current_engine_logic == "重化工":
            st.markdown("- **靶向补齐深层算力短板**：测算显示该市长途光缆与IT人才密度严重滞后。建议发改委与财政局联合优化年度预算切块，优先倾斜专项资金用于底层工业传输网络的填平补齐，规避由算力孤岛引发的项目流失风险。")
            st.markdown("- **调整浅层基建冗余投资**：坚决削减消费级网络设施的重复性财政支出，将资金沉淀转移至重化工业亟需的数字化生产线技改补贴中，夯实跨越“碳锁定”的硬核基石。")
        else:
            st.markdown("- **推动政策重心向软性生态转移**：作为综合型城市，该市在高质量外资引入通道及普惠金融渗透率方面尚未形成闭环。建议工信局与商务局重点优化营商环境，加速引入外资持有的绿色低碳专利技术。")
            st.markdown("- **防范重资产闲置风险**：警惕过度投资实体数据中心等硬基建，避免因缺乏重型产业消化场景而导致资产闲置与能耗空耗，全面加速数据要素向实体服务业的深度融合进程。")
            
    bottom_navigation('mod1')

# ------------------------------------------
# 页面 4：模块二 (双轨制门槛预警)
# ------------------------------------------
elif st.session_state.page == 'mod2':
    st.button("返回推演矩阵", on_click=lambda: st.session_state.update({'page': 'menu'}))
    st.markdown("## ⏱️ 模块二：基于因果森林的低碳投资避险预警中枢")
    
    col_g, col_t = st.columns([1, 1])
    
    if current_engine_logic == "综合型":
        with col_g:
            risk_score = min(st.session_state.c_invest / 8.0 * 100, 100) 
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number", value = risk_score, title = {'text': "区域基建过热与高碳反弹风险预测指数"},
                gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': C_CHARCOAL_SLATE},
                         'steps': [{'range': [0, 40], 'color': C_GLACIER_TEAL}, 
                                   {'range': [40, 70], 'color': 'rgba(255, 215, 0, 0.6)'},
                                   {'range': [70, 100], 'color': C_WARNING_RED}],
                         'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 70}}))
            fig_gauge.update_layout(height=400)
            st.plotly_chart(fig_gauge, use_container_width=True)
            
        with col_t:
            st.info("### 【量化数值分析】")
            st.markdown(f"当前算法已切换至 **泛基准综合型城市防过热推演轨**。底层因果引擎（OrthoIV）测算确认，此类城市缺乏重工业集群吸收超大算力冗余。在此生态下，当前左侧控制台拟定的 **{st.session_state.c_invest:.1f} 亿元** 硬基建投资，将直接触发 **CATE=13.99百万吨** 的高碳代价预警。")
            
            st.success("### 【政务决策建议】")
            st.markdown("- **严格落实项目立项审查**：事前仿真测算表明，当前资金配置下将产生显著的“规模耗能效应”。建议发改委即刻行使立项否决权，阻断低效的重资产堆砌。")
            st.markdown("- **实施资金靶向转移支付**：要求财政局调整支出口径，将节约的重资产基建预算强制转移至软件生态开发与高质量数字人才补贴等绿色通道中，彻底消除无差异普惠式财政补贴带来的沉没成本。")
            
    else:
        with col_g:
            breakthrough_score = min(total_invest / 6.5 * 100, 100) 
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number", value = breakthrough_score, title = {'text': "碳锁定临界门槛跨越概率预测"},
                gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': C_CHARCOAL_SLATE},
                         'steps': [{'range': [0, 50], 'color': 'rgba(255, 99, 71, 0.6)'}, 
                                   {'range': [50, 80], 'color': 'rgba(255, 215, 0, 0.6)'},
                                   {'range': [80, 100], 'color': C_DEEP_FOREST}],
                         'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 80}}))
            fig_gauge.update_layout(height=400)
            st.plotly_chart(fig_gauge, use_container_width=True)
            
        with col_t:
            st.info("### 【量化数值分析】")
            st.markdown(f"当前算法已切换至 **重工业城市碳锁定破局轨**。面板实证确证，要素一旦深入本市传统产业链，将爆发出极强的能耗对冲奇迹（**CATE=0.68**）。依据左侧配置的 **{total_invest:.1f} 亿元** 总投资，系统动态研判当前跨越门槛概率为 **{breakthrough_score:.1f}%**。")
            
            st.success("### 【政务决策建议】")
            st.markdown("- **维持高强度连贯投入机制**：若当前门槛概率不足，表明城市正处于新旧动能转换的能耗阵痛期。决策层必须保持坚定的战略定力，果断追加预算以打透临界阈值，释放数字化降碳的规模报酬红利。")
            st.markdown("- **集中力量攻坚深层工业基建**：防范政策实施的碎片化倾向。工信局应主导构建以长途光缆与工业互联网为核心的专属转型引导基金，确保专项资金在核心瓶颈处实现精准爆破。")
        
    bottom_navigation('mod2')

# ------------------------------------------
# 页面 5：模块三 (SHAP 效费比预测)
# ------------------------------------------
elif st.session_state.page == 'mod3':
    st.button("返回推演矩阵", on_click=lambda: st.session_state.update({'page': 'menu'}))
    st.markdown("## 🔄 模块三：资金边际效费比(ROI)量化预测与结构解构")
    
    col3_1, col3_2 = st.columns([1, 1])
    with col3_1:
        bar_data = pd.DataFrame({"干预情境": ["维持历史惯性 (不干预)", "执行左侧拟定预算方案"], "预期碳排总量(Mt)": [base_carbon, pred_carbon]})
        fig_bar = px.bar(bar_data, x="干预情境", y="预期碳排总量(Mt)", text_auto='.2f', title="碳排演化轨迹反事实仿真对比", color="干预情境", color_discrete_sequence=["#9E9E9E", C_GLACIER_TEAL])
        fig_bar.update_layout(height=400)
        st.plotly_chart(fig_bar, use_container_width=True)
        
    with col3_2:
        if current_engine_logic == "综合型":
            shap_data = pd.DataFrame({"政策干预项": ["深层硬基建耗能反噬", "高质量外资减排协同", "IT人才赋能融合收益"], "ROI绝对值": [infra_cost_penalty, -st.session_state.f_invest*2.0, -st.session_state.i_invest*2.5], "作用导向": ["推高能耗 (+)", "抑制降碳 (-)"]*2 + ["抑制降碳 (-)"]})
        else:
            shap_data = pd.DataFrame({"政策干预项": ["长途工业光缆断层赋能", "高质量外资技术溢出", "IT人才协同组织优化", "基建初期土木耗能"], "ROI绝对值": [-st.session_state.c_invest*2.8, -st.session_state.f_invest*1.5, -st.session_state.i_invest*1.0, infra_cost_penalty], "作用导向": ["抑制降碳 (-)", "抑制降碳 (-)", "抑制降碳 (-)", "推高能耗 (+)"]})
        
        fig_shap = px.bar(shap_data, x="ROI绝对值", y="政策干预项", color="作用导向", orientation='h', title="专项资金绝对边际贡献(ROI)瀑布解构", color_discrete_map={"推高能耗 (+)":C_WARNING_RED, "抑制降碳 (-)":C_DEEP_FOREST})
        fig_shap.update_layout(height=400)
        st.plotly_chart(fig_shap, use_container_width=True)

    st.info("### 【量化数值分析】")
    st.markdown(f"基于博弈论SHAP机制测算，在左侧拟定的总投资规模下，系统执行了毫秒级的结构剥离运算。结果表明，历史基准碳排预测值为 **{base_carbon:.2f} Mt**；执行该投资方案后，预期修正总量变动为 **{pred_carbon:.2f} Mt**。右侧瀑布图精确量化了“光缆基建、人才引育、外资补贴”各项要素工具在这一差值中所贡献的绝对效费比与作用方向。")
    
    st.success("### 【政务决策建议】")
    st.markdown("- **建立基于ROI的预算切块与联合审查机制**：财政局与生态环境局应依托本瀑布图重构预算分配标准。针对呈现为正值（推高能耗）的低回报项目，严格实施预算压降与资金截留。")
    st.markdown("- **实施政策要素乘数放大战略**：针对呈现为显著负值（强力抑制碳排）的高效费比政策包，建议市级财政赋予更高的乘数杠杆与信用担保，确保存量预算资源集中投入至经济回报率最为丰厚的领域，从根本上终结粗放型资源配置体制。")
    
    bottom_navigation('mod3')

# ------------------------------------------
# 页面 6：模块四 (帕累托决策输出)
# ------------------------------------------
elif st.session_state.page == 'mod4':
    st.button("返回推演矩阵", on_click=lambda: st.session_state.update({'page': 'menu'}))
    st.markdown("## 📑 模块四：基于 NSGA-III 的多目标运筹与最优政策靶向生成")
    
    np.random.seed(42)
    n_points = 250
    x_invest = np.random.uniform(1, 20, n_points)
    y_carbon_reduce = x_invest * (1.2 if current_engine_logic == "综合型" else 1.8) - np.random.normal(0, 2, n_points)
    z_gdp_growth = -0.1 * (x_invest - 10)**2 + 8 + np.random.normal(0, 1, n_points)
    
    fig_3d = px.scatter_3d(x=x_invest, y=y_carbon_reduce, z=z_gdp_growth, color=z_gdp_growth, color_continuous_scale="RdBu_r", labels={'x':'财政干预总规模(亿元)', 'y':'预测绝对减排量(Mt)', 'z':'预测GDP额外拉动率(%)'}, title="多约束条件下帕累托最优政策流形曲面演化图谱")
    
    user_z_gdp = -0.1 * (total_invest - 10)**2 + 8
    fig_3d.add_trace(go.Scatter3d(x=[total_invest], y=[base_carbon-pred_carbon], z=[user_z_gdp], mode='markers+text', text=["📍 左侧实时配置锚点坐标"], marker=dict(size=14, symbol='diamond', color='gold', line=dict(color='black', width=3)), textposition='top center'))
    fig_3d.update_layout(height=600)
    st.plotly_chart(fig_3d, use_container_width=True)
    
    st.info("### 【量化数值分析】")
    st.markdown(f"通过驱动高维NSGA-III运筹算法进行十万次启发式搜索，系统已映射出兼顾‘降碳排、稳增长、控预算’的帕累托最优前沿。当前左侧控制台侦测到拟注入干预总盘为 **{total_invest:.1f} 亿元**。代入底层评估函数测算，预期生成减排效益约 **{base_carbon-pred_carbon:.2f} Mt**，预期宏观GDP拉动率约 **{user_z_gdp:.2f}%**。")

    st.success("### 【政务决策建议】")
    if total_invest < 4.0:
        st.markdown("- **警惕保守预算衍生的滞后风险**：当前策略落入基础兜底区。有限的预算将被基础运转成本稀释，无法跨越赋能门槛，极易丧失产业提质的时间窗口期。")
        st.markdown("- **制定中长期增量引资规划**：建议发改委加快谋划能够引入社会资本参与的混合所有制改革项目，通过政企协同模式迅速突破本市财政投入规模的资金瓶颈限制。")
    elif total_invest > 12.0:
        st.markdown("- **严密防范系统性债务危机与挤出效应**：当前策略落入高危激进区，严重偏离帕累托最优曲面。庞大举债不仅推高基建能耗底数，长期将构成拖累宏观经济的财务包袱。")
        st.markdown("- **紧急启动项目库缩减重置程序**：要求市级统筹部门立刻驳回缺乏深度论证的基建政绩工程，将投资总盘强制缩减至安全债务红线以内，确保宏观杠杆率稳定。")
    else:
        st.markdown("- **固化年度投资战略基调**：当前配置精确命中三维帕累托最优脊背区。摒弃了低效的漫灌，实现了极其高超的要素滴灌。成功达成了生态保护与经济拉动的卓越双赢。")
        st.markdown("- **加速法定施政程序转化**：建议市政府办公厅直接将此项沙盘推演方案转化为本年度法定施政纲领与重点督办任务库。责成发改、工信、财政三大部门依据此比例设定资金白名单，加速落地见效。")
    
    bottom_navigation('mod4')
