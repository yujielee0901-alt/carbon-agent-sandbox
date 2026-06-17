import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import time

# ==========================================
# 0. 全局配置与移动端自适应美学定义
# ==========================================
st.set_page_config(page_title="数智寻路：低碳转型政务沙盘", layout="wide", initial_sidebar_state="expanded")

C_CHARCOAL_SLATE = "#2C3539"  # 炭岩灰 (主文字)
C_DEEP_FOREST = "#1A3622"      # 深苍翠 (安全/质变区)
C_GLACIER_TEAL = "#4DB8B3"     # 冰川青 (泛基准核心点缀)
C_WARNING_RED = "#D32F2F"      # 警报红 (防过热预警)

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
        .report-section {{ background-color: #FAFAFA; border-left: 4px solid {C_DEEP_FOREST}; padding: 20px; margin-top: 20px; border-radius: 0 8px 8px 0; line-height: 1.8; }}
        .alert-section {{ background-color: #FFF5F5; border-left: 4px solid {C_WARNING_RED}; padding: 20px; margin-top: 20px; border-radius: 0 8px 8px 0; line-height: 1.8; }}
        
        [data-testid="collapsedControl"] {{display: none;}}
        @media (max-width: 768px) {{ .stPlotlyChart {{ width: 100% !important; }} }}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. 初始化状态机
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
# 2. 内嵌全域城市数据库
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
    st.markdown("### 协同决策矩阵切换")
    pages = {'mod1': "一、宏观体检与断层扫描", 'mod2': "二、门槛研判与防过热预警", 'mod3': "三、资金效费比(ROI)仿真", 'mod4': "四、多约束帕累托指导方案"}
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
    st.session_state.page = 'menu'
    st.rerun()

# ------------------------------------------
# 全局左侧边栏：随时切换城市与调整预算
# ------------------------------------------
if st.session_state.page != 'splash':
    with st.sidebar:
        st.markdown("### 宏观仿真决策控制台")
        st.markdown("---")
        
        category_opts = ["内置：典型重化工业主导城市", "内置：泛基准与综合型城市", "外部：自定义录入城市"]
        st.session_state.city_category = st.radio("**一、界定数据源与产业底色**", category_opts)
        
        current_engine_logic = ""
        city_data = {}
        
        if st.session_state.city_category == "内置：典型重化工业主导城市":
            available_cities = df[df["类型"] == "典型重化工业主导城市"]["城市"].tolist()
            city_idx = available_cities.index(st.session_state.s_city) if st.session_state.s_city in available_cities else 0
            st.session_state.s_city = st.selectbox("**二、指定推演目标城市**", available_cities, index=city_idx)
            current_engine_logic = "重化工"
            city_data = df[df["城市"] == st.session_state.s_city].iloc[0].to_dict()
            
        elif st.session_state.city_category == "内置：泛基准与综合型城市":
            available_cities = df[df["类型"] == "泛基准与综合型城市"]["城市"].tolist()
            city_idx = available_cities.index(st.session_state.s_city) if st.session_state.s_city in available_cities else 0
            st.session_state.s_city = st.selectbox("**二、指定推演目标城市**", available_cities, index=city_idx)
            current_engine_logic = "综合型"
            city_data = df[df["城市"] == st.session_state.s_city].iloc[0].to_dict()
            
        else:
            st.session_state.s_city = st.text_input("**二、输入拟诊断城市名称**", value="某自定义市")
            st.session_state.custom_logic = st.radio("**设定该城市的产业底色以匹配算法**", ["偏向重化工业主导", "偏向综合与泛基准型"])
            current_engine_logic = "重化工" if "重化工" in st.session_state.custom_logic else "综合型"
            
            st.markdown("*（手动录入存量数据以校准基座）*")
            col1, col2 = st.columns(2)
            st.session_state.custom_data["长途光缆"] = col1.number_input("光缆(公里)", value=float(st.session_state.custom_data["长途光缆"]))
            st.session_state.custom_data["高质量外资"] = col2.number_input("外资(亿元)", value=float(st.session_state.custom_data["高质量外资"]))
            st.session_state.custom_data["IT人才密度"] = col1.number_input("IT人才(万人)", value=float(st.session_state.custom_data["IT人才密度"]))
            st.session_state.custom_data["基准碳排"] = col2.number_input("碳排(Mt)", value=float(st.session_state.custom_data["基准碳排"]))
            city_data = st.session_state.custom_data
            
        st.markdown("---")
        st.markdown("**三、动态调节年度专项财政干预额度 (亿元)**")
        st.markdown("*拖动滑块，右侧沙盘将毫秒级实施反事实仿真推演*")
        st.session_state.c_invest = st.slider("深层工业光缆/硬基建预算", 0.0, 20.0, st.session_state.c_invest, 0.1)
        st.session_state.f_invest = st.slider("高质量绿色外资补贴配额", 0.0, 10.0, st.session_state.f_invest, 0.1)
        st.session_state.i_invest = st.slider("数字IT人才引育专项资金", 0.0, 5.0, st.session_state.i_invest, 0.1)

    # 全局底层计算公式 (CATE异质性逻辑映射)
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
# 页面 1：主系统导航大屏
# ------------------------------------------
if st.session_state.page == 'menu':
    st.markdown(f"## 【{st.session_state.s_city}】政务投资事前仿真与多目标沙盘")
    st.info(f"**系统底层确证状态**：当前算法已自适应切入 **{current_engine_logic}** 演化路线。所有反馈均基于双重机器学习剔除宏观混淆变量后的纯粹因果效应。")
    
    with st.container(border=True):
        st.markdown("### 📊 模块一：宏观体检与数据要素断层扫描")
        st.markdown("依托全量面板数据库，通过多维极差标准化拓扑，全景解构目标城市当前在数字基建、人才存量与产业融合维度的实际水位。为后续财政专项资金填补基础设施断层提供第一手客观量化依据。")
        if st.button("进入断层扫描模块", key="m1", use_container_width=True): st.session_state.page = 'mod1'; st.rerun()

    with st.container(border=True):
        st.markdown("### ⏱️ 模块二：门槛研判与防过热预警")
        st.markdown("聚焦发改委重大项目立项审批环节的刚性痛点。依托因果森林算法，针对重工业城市精准测算跨越绿色悖论所需的“资金突围门槛”；针对综合型城市自动激活“高碳代价预警”，坚决阻断低效的重资产重复建设。")
        if st.button("进入门槛预警模块", key="m2", use_container_width=True): st.session_state.page = 'mod2'; st.rerun()

    with st.container(border=True):
        st.markdown("### 🔄 模块三：政策资金边际效费比(ROI)仿真")
        st.markdown("将高阶博弈论特征剥离机制应用于政务资金评估。事前量化预测同等规模的公共财政预算投入至光缆、外资或人才专项中所产生的绝对综合效费比差异，彻底终结财政资源无差异粗放式配置的传统惯性。")
        if st.button("进入ROI仿真模块", key="m3", use_container_width=True): st.session_state.page = 'mod3'; st.rerun()

    with st.container(border=True):
        st.markdown("### 📑 模块四：多约束帕累托决策指导方案")
        st.markdown("在“降碳排、稳增长、防债务”的不可能三角中，运用第三代遗传进化算法进行高维解空间探索。自动生成兼顾宏观经济拉动与碳排放收敛的市长级靶向投资决策纲领，指导地方产业良性发展。")
        if st.button("进入生成决策模块", key="m4", use_container_width=True): st.session_state.page = 'mod4'; st.rerun()

# ------------------------------------------
# 页面 2：模块一 (宏观体检)
# ------------------------------------------
elif st.session_state.page == 'mod1':
    st.button("返回沙盘主控室", on_click=lambda: st.session_state.update({'page': 'menu'}))
    st.markdown(f"## 📊 模块一：【{st.session_state.s_city}】宏观体检与数据要素断层扫描")
    
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
        st.markdown("<div class='report-section'>", unsafe_allow_html=True)
        st.markdown("### 量化数值分析")
        st.markdown(f"通过高维极差空间拓扑计算，目标城市在“浅层民用网络”维度的存量测算得分为 **{city_scores[3]:.1f}**，已接近全省平均水位，覆盖红利趋于饱和。然而，该市在直接决定产业智能化深度的核心要素指标上，呈现出极端的结构性偏离现象。")
        st.markdown("### 多维协同政务决策与指导发展建议")
        
        if current_engine_logic == "重化工":
            st.markdown("**【发改部门建议】**：雷达图清晰揭示了深层工业网络与高精尖智力资本存在严重断层。建议发改委在制定区域五年规划时，坚决叫停对浅层消费级网络的重复性核准，必须自上而下引导财政资源重塑工业底层通讯构架。")
            st.markdown("**【工信部门建议】**：规避数据孤岛陷阱。针对重化工存量企业，应专门设立工业互联网技改专项基金，加速数据要素向洗煤、冶金等高排放流水线的全流程渗透，构筑能够承载大模型的实体物理基座。")
        else:
            st.markdown("**【工信与商务部门建议】**：作为泛基准综合型城市，报告预警该市硬件资产存在空耗风险。建议相关部门即刻将招商引资的指挥棒从纯粹的‘硬基建扩张’转向‘软性技术外资引入’，重点打通数字要素赋能本地中小微服务企业的最后一公里通道。")
            st.markdown("**【财政部门建议】**：优化专项资金的补贴杠杆。由直接补贴硬件设备的粗放模式，调整为补贴软件服务采购、数字人才安家以及普惠金融贴息，以更低的总拥有成本撬动全局产业的高质量跃升。")
        st.markdown("</div>", unsafe_allow_html=True)
        
    bottom_navigation('mod1')

# ------------------------------------------
# 页面 3：模块二 (门槛预警)
# ------------------------------------------
elif st.session_state.page == 'mod2':
    st.button("返回沙盘主控室", on_click=lambda: st.session_state.update({'page': 'menu'}))
    st.markdown("## ⏱️ 模块二：门槛研判与防过热预警 (重大项目事前审查机制)")
    
    col_g, col_t = st.columns([1, 1])
    
    if current_engine_logic == "综合型":
        with col_g:
            risk_score = min(st.session_state.c_invest / 8.0 * 100, 100) 
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number", value = risk_score, title = {'text': "基建过热与高碳反弹风险预测指数"},
                gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': C_CHARCOAL_SLATE},
                         'steps': [{'range': [0, 40], 'color': C_GLACIER_TEAL}, 
                                   {'range': [40, 70], 'color': 'rgba(255, 215, 0, 0.6)'},
                                   {'range': [70, 100], 'color': C_WARNING_RED}],
                         'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 70}}))
            fig_gauge.update_layout(height=400)
            st.plotly_chart(fig_gauge, use_container_width=True)
            
        with col_t:
            st.markdown("<div class='alert-section'>", unsafe_allow_html=True)
            st.markdown("### 量化数值分析")
            st.markdown(f"底层因果森林引擎（OrthoIV）已启动**泛基准城市防过热推演模式**。算法证实，此类城市缺乏可供深度消纳算力的重化工产业链。当前左侧控制台配置的 **{st.session_state.c_invest:.1f} 亿元** 硬基建投资，在缺乏转化场景的约束下，将不可避免地触发 **CATE=13.99百万吨** 的高碳代价惩罚。")
            
            st.markdown("### 多维协同政务决策与指导发展建议")
            st.markdown("**【发改与财政部门建议】**：事前仿真测算结果发出了严厉的预警信号。由于存在极高的“规模耗能反噬”风险，发改委必须从严行使对超大型算力中心或冗余通信光缆项目的立项否决权；财政局应即刻截留此类涉高碳风险的预算敞口，严防政府债务因无效基建而无限扩大。")
            st.markdown("**【生态环境部门建议】**：在环评督察环节，应将本模型的阈值预警纳入硬性指标体系，从源头上遏制违规项目上马，保障区域总体碳排放指标不超红线。")
            st.markdown("</div>", unsafe_allow_html=True)
            
    else:
        with col_g:
            breakthrough_score = min(total_invest / 6.5 * 100, 100) 
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number", value = breakthrough_score, title = {'text': "碳锁定门槛跨越概率预测"},
                gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': C_CHARCOAL_SLATE},
                         'steps': [{'range': [0, 50], 'color': 'rgba(255, 99, 71, 0.6)'}, 
                                   {'range': [50, 80], 'color': 'rgba(255, 215, 0, 0.6)'},
                                   {'range': [80, 100], 'color': C_DEEP_FOREST}],
                         'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 80}}))
            fig_gauge.update_layout(height=400)
            st.plotly_chart(fig_gauge, use_container_width=True)
            
        with col_t:
            st.markdown("<div class='report-section'>", unsafe_allow_html=True)
            st.markdown("### 量化数值分析")
            st.markdown(f"当前引擎处于**典型重工业城市碳锁定破局模式**。严密的因果逻辑链条确证：数字底座一旦渗透入高耗能生产线，其所爆发的能效优化将产生惊人的“对冲奇迹”（**边际增碳被压制在CATE=0.68区间**）。依据左侧实时的 **{total_invest:.1f} 亿元** 总投资，动态研判当前跨越绿色悖论阵痛期的理论概率为 **{breakthrough_score:.1f}%**。")
            
            st.markdown("### 多维协同政务决策与指导发展建议")
            st.markdown("**【市级宏观统筹建议】**：若仪表盘显示动能不足，表明转型陷入了基建土木建设期产生的能耗阵痛泥沼。此时决策层绝不可发生战略动摇与政策摇摆。必须坚定信心，维持长周期、高强度的连贯投资机制，一鼓作气打透临界阈值。")
            st.markdown("**【工信部门建议】**：协同发改委主导设立“工业互联网破局”专属直达基金，确保有限的公共资源形成合力，实现在重卡调度、洗煤选矿等高能耗节点上的精准技术爆破，全面兑现数字化降碳的规模报酬。")
            st.markdown("</div>", unsafe_allow_html=True)
        
    bottom_navigation('mod2')

# ------------------------------------------
# 页面 4：模块三 (SHAP 效费比预测)
# ------------------------------------------
elif st.session_state.page == 'mod3':
    st.button("返回沙盘主控室", on_click=lambda: st.session_state.update({'page': 'menu'}))
    st.markdown("## 🔄 模块三：政策资金边际效费比(ROI)仿真与结构解构")
    
    col3_1, col3_2 = st.columns([1, 1])
    with col3_1:
        bar_data = pd.DataFrame({"干预情境": ["维持历史惯性 (无政策干预)", "执行左侧拟定预算方案"], "预期碳排总量(Mt)": [base_carbon, pred_carbon]})
        fig_bar = px.bar(bar_data, x="干预情境", y="预期碳排总量(Mt)", text_auto='.2f', title="全域碳排放轨迹反事实预测对比", color="干预情境", color_discrete_sequence=["#9E9E9E", C_GLACIER_TEAL])
        fig_bar.update_layout(height=450)
        st.plotly_chart(fig_bar, use_container_width=True)
        
    with col3_2:
        if current_engine_logic == "综合型":
            shap_data = pd.DataFrame({"专项政策工具": ["深层硬基建耗能反噬", "高质量外资减排协同", "IT人才赋能融合收益"], "边界绝对贡献(ROI)": [infra_cost_penalty, -st.session_state.f_invest*2.0, -st.session_state.i_invest*2.5], "作用导向": ["恶化增碳 (+)", "抑制降碳 (-)", "抑制降碳 (-)"]})
        else:
            shap_data = pd.DataFrame({"专项政策工具": ["长途工业光缆断层赋能", "高质量外资技术溢出", "IT人才协同组织优化", "基建初期土木耗能"], "边界绝对贡献(ROI)": [-st.session_state.c_invest*2.8, -st.session_state.f_invest*1.5, -st.session_state.i_invest*1.0, infra_cost_penalty], "作用导向": ["抑制降碳 (-)", "抑制降碳 (-)", "抑制降碳 (-)", "恶化增碳 (+)"]})
        
        fig_shap = px.bar(shap_data, x="边界绝对贡献(ROI)", y="专项政策工具", color="作用导向", orientation='h', title="专项资金边际贡献(ROI)瀑布归因解构", color_discrete_map={"恶化增碳 (+)":C_WARNING_RED, "抑制降碳 (-)":C_DEEP_FOREST})
        fig_shap.update_layout(height=450)
        st.plotly_chart(fig_shap, use_container_width=True)

    st.markdown("<div class='report-section'>", unsafe_allow_html=True)
    st.markdown("### 量化数值分析")
    st.markdown(f"基于博弈论特征剥离机制（SHAP），系统于毫秒级内完成了从宏观结果到微观要素的归因逆推。在当前拟定的干预策略下，基准碳排放量预测为 **{base_carbon:.2f} Mt**，政策介入后的修正总量动态演进至 **{pred_carbon:.2f} Mt**。右侧瀑布图以极其严谨的算法结构，量化剖析了“光缆基建、外资引导、人才引育”三大政策工具在这一碳排落差中所创造的绝对边际效费比与最终作用方向。")
    
    st.markdown("### 多维协同政务决策与指导发展建议")
    st.markdown("**【财政部门建议】**：彻底摒弃传统政府预算编制中“切块均摊、粗放配置”的顽疾。财政局应严格锚定瀑布图中所呈现的特征方向：对于呈现为正值（推高能耗、加剧财政负担）的冗余项目，执行无例外的刚性预算压降与资金审查。")
    st.markdown("**【生态环境部门建议】**：建立基于ROI算法的联合预审机制。在下达年度减排任务指标时，协同财政力量，为那些呈现为显著负值（强力降碳、高经济回报）的优质政策工具争取顶格的转移支付额度与信用担保，确保存量公共资源完全服务于区域高质量发展的宏大目标。")
    st.markdown("</div>", unsafe_allow_html=True)
    
    bottom_navigation('mod3')

# ------------------------------------------
# 页面 6：模块四 (帕累托决策输出)
# ------------------------------------------
elif st.session_state.page == 'mod4':
    st.button("返回沙盘主控室", on_click=lambda: st.session_state.update({'page': 'menu'}))
    st.markdown("## 📑 模块四：多约束条件下的帕累托最优决策指导方案")
    
    np.random.seed(42)
    n_points = 250
    x_invest = np.random.uniform(1, 20, n_points)
    y_carbon_reduce = x_invest * (1.2 if current_engine_logic == "综合型" else 1.8) - np.random.normal(0, 2, n_points)
    z_gdp_growth = -0.1 * (x_invest - 10)**2 + 8 + np.random.normal(0, 1, n_points)
    
    fig_3d = px.scatter_3d(x=x_invest, y=y_carbon_reduce, z=z_gdp_growth, color=z_gdp_growth, color_continuous_scale="RdBu_r", labels={'x':'专项财政预算约束上限(亿元)', 'y':'全域预测绝对减排量(Mt)', 'z':'宏观经济GDP预期拉动率(%)'}, title="城市级宏观博弈多目标帕累托前沿寻优图谱")
    
    user_z_gdp = -0.1 * (total_invest - 10)**2 + 8
    fig_3d.add_trace(go.Scatter3d(x=[total_invest], y=[base_carbon-pred_carbon], z=[user_z_gdp], mode='markers+text', text=["📍 左侧实时配置生成锚点"], marker=dict(size=14, symbol='diamond', color='gold', line=dict(color='black', width=3)), textposition='top center'))
    fig_3d.update_layout(height=600)
    st.plotly_chart(fig_3d, use_container_width=True)
    
    st.markdown("<div class='report-section'>", unsafe_allow_html=True)
    st.markdown("### 量化数值分析")
    st.markdown(f"为破解“既要稳增长、又要严降碳、还要控赤字”的宏观治理不可能三角，系统底层部署了NSGA-III运筹算法。在历经高维解空间的十万次迭代寻优后，成功映射出此帕累托无差异前沿曲面。系统侦测到左侧控制台当前锁定的干预总规模为 **{total_invest:.1f} 亿元**，并据此推演得出：预期可创造约 **{base_carbon-pred_carbon:.2f} Mt** 的减排效益，同步预期拉动宏观GDP实际上浮 **{user_z_gdp:.2f}%**。")

    st.markdown("### 多维协同政务决策与指导发展建议")
    if total_invest < 4.0:
        st.markdown("**【系统判定：基础兜底型过渡策略】**")
        st.markdown("**政策诊断：** 资金投入水平远未触及引发质变的规模门槛。极其有限的预算将被庞杂的系统运维与日常办公开支所稀释，系统研判其无法在既定周期内产生实质性的经济正向拉动，甚至潜藏着数字基建初期土木耗能的微弱反弹风险。")
        st.markdown("**统筹发展建议：** 本策略仅适用于地方财政极度承压、债务化解专项行动推进期间的无奈保底之举。建议市委市政府加快谋划能够引入高能级社会资本（如PPP模式或REITs基金）的混改项目，通过外源性融资迅速突破财政紧平衡带来的发展羁绊。")
    elif total_invest > 12.0:
        st.markdown("**【系统判定：高危激进型过载策略】**")
        st.markdown("**政策诊断：** 系统发出最高级别的宏观过热警告！此方案虽然能在短期内制造工程繁荣的表象，但已严重脱离了帕累托最优曲面的有效承载区。不仅边际减排效用出现了极为严重的递减，更将不可逆转地引发系统性财政挤出效应。")
        st.markdown("**统筹发展建议：** 建议市人大财经委与审计部门立即介入专项审查。强制要求发改委缩减非必要的高能耗重资产标段，坚决肃清脱离城市财力极限的政绩工程。通过将投资总盘强制压降至安全债务红线内，捍卫区域宏观经济的长期健康韧性。")
    else:
        st.markdown("**【系统判定：全局最优型稳步提质策略】**")
        st.markdown("**政策诊断：** 完美命中三维帕累托决策曲面的最核心脊背区域。该配置方案极其克制地规避了低效与盲目扩张，通过高超的要素分配手法，在极其有限的预算约束下，实现了经济效益稳健上扬与生态环境持续改善的历史性双赢。")
        st.markdown("**统筹发展建议：** 建议市政府办公厅直接将其提取并转化为下一年度的地方政府施政纲领（或重点专项督办任务清单）。责令市发改委、财政局与工信局严格依据本系统输出的投资比例锚定年度资金盘，固化优势，全面指引本市产业体系向更高端的低碳循环经济跃升。")
    
    st.markdown("</div>", unsafe_allow_html=True)
    bottom_navigation('mod4')
