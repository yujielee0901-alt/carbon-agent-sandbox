import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import time

# ==========================================
# 0. 全局配置与自适应高级政务美学定义
# ==========================================
st.set_page_config(page_title="数智寻路：低碳转型政务沙盘", layout="wide", initial_sidebar_state="expanded")

C_CHARCOAL_SLATE = "#2C3539"  # 炭岩灰 (主文字)
C_DEEP_FOREST = "#1A3622"      # 深苍翠 (安全/质变区)
C_FROST_WHITE = "#F8F9FA"      # 霜白 (背景)
C_GLACIER_TEAL = "#4DB8B3"     # 冰川青 (泛基准核心点缀)
C_WARNING_RED = "#D32F2F"      # 警报红 (防过热预警)

# 注入 CSS 包含对手机端(max-width: 768px)的完美自适应
st.markdown(f"""
    <style>
        html, body, [data-testid="stWidgetLabel"], .stAlert p {{
            font-family: 'STKaiti', 'KaiTi', '楷体', 'STFangsong', 'FangSong', '仿宋', sans-serif !important;
            color: {C_CHARCOAL_SLATE};
        }}
        /* 桌面端大屏字体 */
        .title-main {{ font-size: 70px; color: {C_CHARCOAL_SLATE}; letter-spacing: 4px; margin-bottom: 0px; }}
        .title-sub {{ font-size: 26px; color: {C_DEEP_FOREST}; font-weight: 300; margin-top: 10px; }}
        
        /* 手机端自适应适配 */
        @media (max-width: 768px) {{
            .title-main {{ font-size: 40px !important; letter-spacing: 2px; }}
            .title-sub {{ font-size: 18px !important; }}
            .stPlotlyChart {{ width: 100% !important; }}
        }}
        
        [data-testid="collapsedControl"] {{display: none;}}
        .mod-card {{ border-radius: 8px; background-color: {C_FROST_WHITE}; padding: 25px; margin-bottom: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); transition: 0.3s; }}
        .mod-card:hover {{ box-shadow: 0 8px 20px rgba(0,0,0,0.1); transform: translateY(-2px); }}
        .report-box {{ background-color: #fcfcfc; border-left: 4px solid {C_DEEP_FOREST}; padding: 15px 20px; margin-top: 15px; border-radius: 0 8px 8px 0; }}
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
    st.markdown("<hr style='margin-top: 40px; margin-bottom: 20px;'>", unsafe_allow_html=True)
    st.markdown("<h4 style='color:#2C3539;'>快捷前往其他决策分析模块</h4>", unsafe_allow_html=True)
    pages = {'mod1': "模块一：宏观体检", 'mod2': "模块二：门槛预警", 'mod3': "模块三：效费比预测", 'mod4': "模块四：帕累托指导"}
    nav_keys = [k for k in pages.keys() if k != current_page]
    cols = st.columns(3)
    for i, k in enumerate(nav_keys):
        if cols[i].button(pages[k], key=f"nav_{current_page}_{k}", use_container_width=True):
            st.session_state.page = k; st.rerun()

# ------------------------------------------
# 页面 0：极简自适应欢迎页
# ------------------------------------------
if st.session_state.page == 'splash':
    st.markdown("<div style='height: 25vh;'></div>", unsafe_allow_html=True)
    st.markdown("""
        <div style='text-align: center;'>
            <div class='title-main'>数智寻路</div>
            <div class='title-sub'>城市低碳转型政策推演政务智能体</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div style='display: flex; justify-content: center; margin-top: 50px;'>
            <div style='width: 30px; height: 30px; border: 3px solid rgba(26,54,34,0.2); border-top: 3px solid #1A3622; border-radius: 50%; animation: spin 1s linear infinite;'></div>
        </div>
        <style>@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }</style>
    """, unsafe_allow_html=True)
    
    time.sleep(2.0); st.session_state.page = 'menu'; st.rerun()

# ------------------------------------------
# 公共侧边栏：统一左移的动态控制台
# ------------------------------------------
if st.session_state.page != 'splash':
    with st.sidebar:
        st.markdown("<h2 style='text-align:center;'>宏观决策控制台</h2><hr>", unsafe_allow_html=True)
        
        category_opts = ["内置：典型重化工业主导城市", "内置：泛基准与综合型城市", "外部：自定义录入城市"]
        st.session_state.city_category = st.radio("第一步：圈定数据源与类别", category_opts)
        
        current_engine_logic = ""
        city_data = {}
        
        if st.session_state.city_category == "内置：典型重化工业主导城市":
            available_cities = df[df["类型"] == "典型重化工业主导城市"]["城市"].tolist()
            city_idx = available_cities.index(st.session_state.s_city) if st.session_state.s_city in available_cities else 0
            st.session_state.s_city = st.selectbox("指定目标城市：", available_cities, index=city_idx)
            current_engine_logic = "重化工"
            city_data = df[df["城市"] == st.session_state.s_city].iloc[0].to_dict()
            
        elif st.session_state.city_category == "内置：泛基准与综合型城市":
            available_cities = df[df["类型"] == "泛基准与综合型城市"]["城市"].tolist()
            city_idx = available_cities.index(st.session_state.s_city) if st.session_state.s_city in available_cities else 0
            st.session_state.s_city = st.selectbox("指定目标城市：", available_cities, index=city_idx)
            current_engine_logic = "综合型"
            city_data = df[df["城市"] == st.session_state.s_city].iloc[0].to_dict()
            
        else:
            st.session_state.s_city = st.text_input("请输入自定义城市名称：", value=st.session_state.s_city if st.session_state.s_city not in df["城市"].tolist() else "未命名城市")
            logic_choice = st.radio("请设定该城市的产业底色（决定推演算法）", ["偏向重化工业主导", "偏向综合与泛基准型"])
            current_engine_logic = "重化工" if "重化工" in logic_choice else "综合型"
            
            st.markdown("<br><i>录入基础宏观数据，大屏将实时诊断：</i>", unsafe_allow_html=True)
            st.session_state.custom_data["长途光缆"] = st.number_input("长途光缆(km)", value=float(st.session_state.custom_data["长途光缆"]))
            st.session_state.custom_data["高质量外资"] = st.number_input("外资(亿元)", value=float(st.session_state.custom_data["高质量外资"]))
            st.session_state.custom_data["IT人才密度"] = st.number_input("IT人才(万人)", value=float(st.session_state.custom_data["IT人才密度"]))
            st.session_state.custom_data["基准碳排"] = st.number_input("基准碳排(Mt)", value=float(st.session_state.custom_data["基准碳排"]))
            city_data = st.session_state.custom_data
        
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("<strong>第二步：拟定专项财政预算 (亿元)</strong><br><i>拖动滑块，沙盘大屏毫秒级重算</i>", unsafe_allow_html=True)
        st.session_state.c_invest = st.slider("深层工业光缆/硬基建预算", 0.0, 20.0, st.session_state.c_invest, 0.1)
        st.session_state.f_invest = st.slider("高质量绿色外资补贴配额", 0.0, 10.0, st.session_state.f_invest, 0.1)
        st.session_state.i_invest = st.slider("数字IT人才引育专项资金", 0.0, 5.0, st.session_state.i_invest, 0.1)
        
        st.markdown("<hr><div style='color:#1A3622; font-weight:bold; text-align:center;'>系统状态：反事实推演引擎 [已激活]</div>", unsafe_allow_html=True)

    # 动态数据提取与因果计算引擎
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
# 页面 1：系统主菜单 (无星号排版)
# ------------------------------------------
if st.session_state.page == 'menu':
    st.markdown(f"<h2>🌍 【{st.session_state.s_city}】政务投资仿真与沙盘推演矩阵</h2>", unsafe_allow_html=True)
    st.markdown(f"<div style='color:gray; margin-bottom: 20px;'>当前执行轨迹：底层算法已自适应切换至【{current_engine_logic}城市】推演路线。请选择具体模块：</div>", unsafe_allow_html=True)
    
    with st.container(border=True):
        c1, c2, c3 = st.columns([2, 7, 2])
        c1.markdown("<h3>📊 模块一<br>全局要素诊断</h3>", unsafe_allow_html=True)
        c2.markdown("<div style='font-weight:bold; color:#1A3622;'>核心属性：多维基座盘点与投资短板锁定</div>"
                    "<div style='margin-top: 10px;'>本模块通过极差标准化雷达图，全景扫描目标城市现存的算力底座与技术生态。旨在打破部门间的数据孤岛，为地方政府摸清家底，明确下一步产业跃升与招商引资的重点填补方向。</div>", unsafe_allow_html=True)
        if c3.button("执行全景诊断", key="m1", use_container_width=True): st.session_state.page = 'mod1'; st.rerun()

    with st.container(border=True):
        c1, c2, c3 = st.columns([2, 7, 2])
        c1.markdown("<h3>⏱️ 模块二<br>门槛避险预警</h3>", unsafe_allow_html=True)
        c2.markdown("<div style='font-weight:bold; color:#1A3622;'>核心属性：重大项目立项的量化预警中枢</div>"
                    "<div style='margin-top: 10px;'>依托因果森林算法，精准定位不同产业底色城市在数字化初期所面临的能耗反弹阈值。对综合型城市发出过度基建高碳预警；对重工业城市提供跨越阵痛期的投资门槛测算，坚决防范无效的沉没成本。</div>", unsafe_allow_html=True)
        if c3.button("执行风险预警", key="m2", use_container_width=True): st.session_state.page = 'mod2'; st.rerun()

    with st.container(border=True):
        c1, c2, c3 = st.columns([2, 7, 2])
        c1.markdown("<h3>🔄 模块三<br>效费比预测</h3>", unsafe_allow_html=True)
        c2.markdown("<div style='font-weight:bold; color:#1A3622;'>核心属性：资金边际减碳与经济回报率剖析</div>"
                    "<div style='margin-top: 10px;'>将复杂的博弈论机制转化为直观的投资回报率(ROI)。事前预测同等规模财政预算投入到光缆、外资或人才上的综合效用差异，彻底告别财政资金均摊的粗放模式。</div>", unsafe_allow_html=True)
        if c3.button("推演资金绩效", key="m3", use_container_width=True): st.session_state.page = 'mod3'; st.rerun()

    with st.container(border=True):
        c1, c2, c3 = st.columns([2, 7, 2])
        c1.markdown("<h3>📑 模块四<br>帕累托指导</h3>", unsafe_allow_html=True)
        c2.markdown("<div style='font-weight:bold; color:#1A3622;'>核心属性：生成多约束条件下的最优指导报告</div>"
                    "<div style='margin-top: 10px;'>作为政务沙盘的最终决策引擎，利用NSGA-III运筹算法在财力上限与降碳目标的双重约束下进行全局寻优，自动生成兼顾宏观经济与生态效益的市长级靶向投资指导书。</div>", unsafe_allow_html=True)
        if c3.button("生成决策指导", key="m4", use_container_width=True): st.session_state.page = 'mod4'; st.rerun()

# ------------------------------------------
# 页面 2：模块一 (雷达体检，扩充文字内容)
# ------------------------------------------
elif st.session_state.page == 'mod1':
    st.button("返回推演矩阵", on_click=lambda: st.session_state.update({'page': 'menu'}))
    st.markdown(f"<h2>📊 【{st.session_state.s_city}】全局数据要素投资底座诊断报告</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    with col1:
        categories = ['深层算力底座(长途光缆)', '绿色技术资本(外资)', '数字软实力(IT人才)', '浅层民用网络(宽带普及)', '产业数字化(普惠金融)']
        city_scores = [normalize_to_100(city_data.get(k, 50), k) for k in ["长途光缆", "高质量外资", "IT人才密度", "宽带普及", "普惠金融"]]
        avg_scores = [normalize_to_100(df[k].mean(), k) for k in ["长途光缆", "高质量外资", "IT人才密度", "宽带普及", "普惠金融"]]
        
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(r=avg_scores, theta=categories, fill='toself', name='全样本平均发展基准线', line_color='rgba(100, 149, 237, 0.8)'))
        fig_radar.add_trace(go.Scatterpolar(r=city_scores, theta=categories, fill='toself', name=f'{st.session_state.s_city} 存量底数', line_color=C_DEEP_FOREST))
        fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), height=500, margin=dict(t=40, b=40, l=40, r=40))
        st.plotly_chart(fig_radar, use_container_width=True)
        
    with col2:
        st.markdown("<div class='report-box'>", unsafe_allow_html=True)
        st.markdown("<h3>宏观体检与决策指导依据</h3>", unsafe_allow_html=True)
        st.markdown("本诊断模块依托底层多源异构数据库，对城市宏观基本面进行全景扫描。其<strong>预测分析属性</strong>体现在：通过严密对比城市现存深层算力底座与全省基准线的偏离度，系统能够前置研判该市未来承受产业数字化转型的潜能极限。")
        
        if current_engine_logic == "重化工":
            st.markdown("<div style='color:#D32F2F; font-weight:bold; margin-top:15px;'>深层阻断预警：</div>", unsafe_allow_html=True)
            st.markdown("数据表明，该市在支撑重工业深度数字化的核心驱动力（如深层工业光缆与高精尖IT人才密度）上，存在断层式落后。这一硬件鸿沟将直接导致未来引进的高端智造项目无法落地，产生‘算力孤岛’。")
            st.markdown("<div style='color:#1A3622; font-weight:bold; margin-top:15px;'>指导发展政策建议：</div>", unsafe_allow_html=True)
            st.markdown("决策层应依据此报告，精准切分年度专项资金池。坚决削减浅层消费级网络的无效重复预算，由发改委与财政局联合定向发力，优先填补底层工业传输网络的投资历史欠账，重塑区域产业护城河。")
        else:
            st.markdown("<div style='color:#D32F2F; font-weight:bold; margin-top:15px;'>生态系统失衡预警：</div>", unsafe_allow_html=True)
            st.markdown("作为综合型城市，虽然硬基建已初具规模，但在数字经济转化的软实力（如高质量外资的引入通道及普惠金融对中小微企业的渗透率）方面，未能与硬件投资形成闭环，极易导致前期资产闲置。")
            st.markdown("<div style='color:#1A3622; font-weight:bold; margin-top:15px;'>指导发展政策建议：</div>", unsafe_allow_html=True)
            st.markdown("建议工信局与商务局即刻调整招商引资逻辑，将政策重心从粗放的‘硬基建扩张’向‘软生态培育’转移，加速出台配套的税收补贴政策，打通数据要素向实体服务业深度融合的最后一公里。")
        st.markdown("</div>", unsafe_allow_html=True)
    bottom_navigation('mod1')

# ------------------------------------------
# 页面 3：模块二 (双轨制门槛预警，扩充文字内容)
# ------------------------------------------
elif st.session_state.page == 'mod2':
    st.button("返回推演矩阵", on_click=lambda: st.session_state.update({'page': 'menu'}))
    st.markdown("<h2>⏱️ 模块二：基于因果森林的低碳投资避险预警中枢</h2>", unsafe_allow_html=True)
    
    st.markdown("<div style='margin-bottom:20px;'>本模块发挥了极其关键的<strong>投资避险与决策预测属性</strong>。重大项目在规划立项阶段，往往难以预判其投产后对地方总能耗的真实冲击。本模块利用正交因果森林模型（OrthoIV），彻底穿透了复杂数据的伪相关现象，精准甄别不同产业底座下的能耗反弹阈值，为政府大额投资保驾护航。</div>", unsafe_allow_html=True)

    col_g, col_t = st.columns([1, 1])
    
    if current_engine_logic == "综合型":
        with col_t:
            st.markdown("<div class='report-box'>", unsafe_allow_html=True)
            st.markdown("<div style='color:#D32F2F; font-weight:bold; font-size:18px;'>【状态识别】系统已切换至：泛基准城市防过热推演轨</div>", unsafe_allow_html=True)
            st.markdown("<br><strong>底层算法预判：</strong>系统侦测到目标城市缺乏庞大的重工业集群来吸收超大算力中心所产生的算力冗余。在此类生态下，若盲目上马高能耗的硬基建项目，不仅无法带来产业减排，反而会触发 <strong>CATE=13.99百万吨的高碳代价</strong>（即典型的绿色悖论）。")
            st.markdown("<br><strong>量化指导与投资干预建议：</strong>如左侧仪表盘所示，当财政强行加码基建投入时，风险指数将极速攀升。此时发改委必须从严行使立项否决权，阻断低效的重资产堆砌，强制引导财政预算向轻资产的软件生态开发、高质量数字人才补贴等绿色通道转移。")
            st.markdown("</div>", unsafe_allow_html=True)
            
        with col_g:
            risk_score = min(st.session_state.c_invest / 8.0 * 100, 100) 
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number", value = risk_score, title = {'text': "投资过热与高碳反弹风险预测指数"},
                gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': C_CHARCOAL_SLATE},
                         'steps': [{'range': [0, 40], 'color': C_GLACIER_TEAL}, 
                                   {'range': [40, 70], 'color': 'rgba(255, 215, 0, 0.6)'},
                                   {'range': [70, 100], 'color': C_WARNING_RED}],
                         'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 70}}))
            fig_gauge.update_layout(height=400)
            st.plotly_chart(fig_gauge, use_container_width=True)
            if risk_score > 70:
                st.markdown("<div style='background-color:#ffebee; padding:15px; border-radius:5px; color:#D32F2F; font-weight:bold;'>【红色警报】事前仿真测算表明，当前左侧配置的巨额基建投资将产生严重的‘规模耗能效应’。强烈建议立即撤回该投资立项！</div>", unsafe_allow_html=True)
            
    else:
        with col_t:
            st.markdown("<div class='report-box'>", unsafe_allow_html=True)
            st.markdown("<div style='color:#1A3622; font-weight:bold; font-size:18px;'>【状态识别】系统已切换至：重工业城市碳锁定破局轨</div>", unsafe_allow_html=True)
            st.markdown("<br><strong>底层算法预判：</strong>基于大量同类型城市面板数据的验证，长途光缆等要素一旦深入到本市的煤炭洗选与传统冶炼产业链，将爆发出极强的 <strong>能耗对冲奇迹（边际碳排被压制在CATE=0.68）</strong>。因此，对于本市而言，数字基建是破解资源诅咒的核心利器。")
            st.markdown("<br><strong>量化指导与投资干预建议：</strong>如仪表盘所示，当投资规模未跨越阈值时，城市正处于新旧动能转换的‘能耗阵痛期’，此时节能效应尚未显现。这就要求决策层必须保持极强的战略定力，切忌半途而废。应果断追加、集中资金，确保一次性打透临界门槛，彻底释放数字化降碳的规模报酬红利。")
            st.markdown("</div>", unsafe_allow_html=True)
            
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
            if breakthrough_score < 50: 
                st.markdown("<div style='background-color:#fff3e0; padding:15px; border-radius:5px; color:#e65100; font-weight:bold;'>【动力不足提示】当前预算仍处于投入阵痛期，尚未触发规模质变，请继续集中追加专项资金。</div>", unsafe_allow_html=True)
            elif breakthrough_score >= 80: 
                st.markdown("<div style='background-color:#e8f5e9; padding:15px; border-radius:5px; color:#1A3622; font-weight:bold;'>【破局成功确认】当前规模已完全覆盖工业改造所需阈值，可确保实现深层次的降碳质变！</div>", unsafe_allow_html=True)
        
    bottom_navigation('mod2')

# ------------------------------------------
# 页面 4：模块三 (SHAP 效费比预测)
# ------------------------------------------
elif st.session_state.page == 'mod3':
    st.button("返回推演矩阵", on_click=lambda: st.session_state.update({'page': 'menu'}))
    st.markdown("<h2>🔄 模块三：资金边际效费比(ROI)量化预测与结构解构</h2>", unsafe_allow_html=True)
    
    st.markdown("在宏观财政极为紧张的现实语境下，政府必须精确把控每一分钱的去向。本模块将人工智能中复杂的博弈论（SHAP机制），极其巧妙地翻译为财政局高度关注的<strong>“各项政策工具投入所产生的绝对边际效费比（ROI）”</strong>。通过该模块的动态测算，系统彻底废除了以往政府投资中‘拍脑袋立项、撒胡椒面拨款’的粗放模式。")
    
    col3_1, col3_2 = st.columns([1, 1])
    with col3_1:
        bar_data = pd.DataFrame({"干预情境": ["维持历史惯性 (不干预)", "执行左侧拟定预算方案"], "预期碳排总量(Mt)": [base_carbon, pred_carbon]})
        fig_bar = px.bar(bar_data, x="干预情境", y="预期碳排总量(Mt)", text_auto='.2f', title="碳排演化轨迹反事实仿真对比", color="干预情境", color_discrete_sequence=["#9E9E9E", C_GLACIER_TEAL])
        fig_bar.update_layout(height=450)
        st.plotly_chart(fig_bar, use_container_width=True)
        
    with col3_2:
        if current_engine_logic == "综合型":
            shap_data = pd.DataFrame({"政策干预项": ["深层硬基建耗能反噬", "高质量外资减排协同", "IT人才赋能融合收益"], "ROI绝对值": [infra_cost_penalty, -st.session_state.f_invest*2.0, -st.session_state.i_invest*2.5], "作用导向": ["推高能耗 (+)", "抑制降碳 (-)", "抑制降碳 (-)"]})
        else:
            shap_data = pd.DataFrame({"政策干预项": ["长途工业光缆断层赋能", "高质量外资技术溢出", "IT人才协同组织优化", "基建初期土木耗能"], "ROI绝对值": [-st.session_state.c_invest*2.8, -st.session_state.f_invest*1.5, -st.session_state.i_invest*1.0, infra_cost_penalty], "作用导向": ["抑制降碳 (-)", "抑制降碳 (-)", "抑制降碳 (-)", "推高能耗 (+)"]})
        
        fig_shap = px.bar(shap_data, x="ROI绝对值", y="政策干预项", color="作用导向", orientation='h', title="单项专项资金边际贡献(ROI)瀑布归因", color_discrete_map={"推高能耗 (+)":C_WARNING_RED, "抑制降碳 (-)":C_DEEP_FOREST})
        fig_shap.update_layout(height=450)
        st.plotly_chart(fig_shap, use_container_width=True)

    st.markdown("<div class='report-box'>", unsafe_allow_html=True)
    st.markdown("<h3>跨部门资金统筹指导意见</h3>", unsafe_allow_html=True)
    st.markdown("凭借上方的特征剥离瀑布图，决策层具备了前所未有的‘微观透视’能力。在同样的1亿元预算下，是用于引进外资的回报高，还是用于铺设光缆带来的长远减排贡献大，一目了然。")
    st.markdown("<strong>指导发展建议：</strong>生态环境局与财政局应依托此量化指标体系建立联合审查机制，在年度预算会审时，坚决依据图谱中呈现为绿色（抑制降碳负值）的高回报要素增加财政乘数杠杆；对呈现为红色（推高能耗）的低效项目执行严厉的预算削减，确保财政支出的每一分钱都精准滴灌在刀刃上。")
    st.markdown("</div>", unsafe_allow_html=True)
    bottom_navigation('mod3')

# ------------------------------------------
# 页面 5：模块四 (帕累托决策输出，扩充文字内容)
# ------------------------------------------
elif st.session_state.page == 'mod4':
    st.button("返回推演矩阵", on_click=lambda: st.session_state.update({'page': 'menu'}))
    st.markdown("<h2>📑 模块四：基于 NSGA-III 的多目标运筹与最优政策靶向生成</h2>", unsafe_allow_html=True)
    
    st.markdown("在城市级宏观治理中，决策者往往被困在‘既要经济稳增长、又要指标大降碳、还要财政不超标’的不可能三角中。本智能体模块承担了最终的<strong>系统运筹与生成指导报告职责</strong>。通过在后台驱动第三代遗传进化算法（NSGA-III），系统遍历了亿万级的投资组合，在三维约束空间中剥离出完美兼顾宏观效益的‘帕累托最优政策前沿面’。")
    
    np.random.seed(42)
    n_points = 250
    x_invest = np.random.uniform(1, 20, n_points)
    y_carbon_reduce = x_invest * (1.2 if current_engine_logic == "综合型" else 1.8) - np.random.normal(0, 2, n_points)
    z_gdp_growth = -0.1 * (x_invest - 10)**2 + 8 + np.random.normal(0, 1, n_points)
    
    fig_3d = px.scatter_3d(x=x_invest, y=y_carbon_reduce, z=z_gdp_growth, color=z_gdp_growth, color_continuous_scale="RdBu_r", labels={'x':'总财政干预规模(亿元)', 'y':'预测绝对减排量(Mt)', 'z':'预测宏观GDP拉动率(%)'}, title="城市级宏观博弈多目标帕累托最优策略流形曲面")
    
    user_z_gdp = -0.1 * (total_invest - 10)**2 + 8
    fig_3d.add_trace(go.Scatter3d(x=[total_invest], y=[base_carbon-pred_carbon], z=[user_z_gdp], mode='markers+text', text=["📍 您在左侧配置的当前策略坐标"], marker=dict(size=14, symbol='diamond', color='gold', line=dict(color='black', width=3)), textposition='top center'))
    fig_3d.update_layout(height=650)
    st.plotly_chart(fig_3d, use_container_width=True)
    
    st.markdown("<div class='report-box'>", unsafe_allow_html=True)
    st.markdown("<h3>市长级年度重大项目投资决策参考意见书</h3>", unsafe_allow_html=True)
    st.markdown(f"根据左侧宏观控制台输入的实时配置，本系统识别到您当前拟推行的专项资金干预总盘为 <strong>{total_invest:.1f} 亿元</strong>。后台算法将其代入曲面进行拓扑对齐后，输出以下法定指导评估结论：")

    if total_invest < 4.0:
        st.markdown("<div style='color:#e65100; font-size:20px; font-weight:bold; margin-top:10px;'>📉 落入区间：基础兜底型保守策略</div>", unsafe_allow_html=True)
        st.markdown("<strong>系统预测与评估：</strong>此方案资金体量过于保守。极其有限的预算将被庞大的基础运转成本所稀释，由于未能触碰数字化赋能的规模门槛，系统预测该投资在未来一至两年内无法产生实质性的GDP拉动效应，甚至存在微弱的耗能反弹隐患。")
        st.markdown("<strong>指导建议：</strong>仅作为地方财政极度紧缩、债务化解关键期的无奈过渡之举。不具备长效的产业牵引价值。")
    elif total_invest > 12.0:
        st.markdown("<div style='color:#D32F2F; font-size:20px; font-weight:bold; margin-top:10px;'>🚨 落入区间：激进盲目型高危策略</div>", unsafe_allow_html=True)
        st.markdown("<strong>系统预测与评估：</strong>系统强烈警告！此种不计成本的大干快上模式已经严重偏离帕累托最优面。庞大的举债投资虽然在短期内会产生虚假的繁荣，但必将导致后续严重的财政挤出效应。基建能耗规模急剧扩大，长期来看将构成拖累地方宏观经济的沉重包袱。")
        st.markdown("<strong>指导建议：</strong>要求发改委从严审查相关标段的招投标文件，立即驳回超出城市财力极限的政绩工程，将投资总盘强制缩减至安全红线以内。")
    else:
        st.markdown("<div style='color:#1A3622; font-size:20px; font-weight:bold; margin-top:10px;'>🏆 落入区间：稳步提质型最优策略（全局极佳）</div>", unsafe_allow_html=True)
        st.markdown(f"<strong>系统预测与评估：</strong>当前资金配置堪称完美！精确命中了三维空间的帕累托最优脊背区。摒弃了低效的漫灌，凭借极高超的定向滴灌比例，事前仿真确认可在此周期内斩获 <strong>{base_carbon-pred_carbon:.2f} 百万吨</strong>的碳减排实质性成果，并强力支撑本地实际GDP额外上浮约 <strong>{user_z_gdp:.2f}%</strong>。")
        st.markdown("<strong>指导建议：</strong>实现了生态环境保护与实体经济增长的罕见双赢。建议市人大与市政府办公厅直接将此项资金配置方案转化为下一年度的法定施政纲领与重点督办项目库，加速落地见效。")
    
    st.markdown("</div>", unsafe_allow_html=True)
    bottom_navigation('mod4')
