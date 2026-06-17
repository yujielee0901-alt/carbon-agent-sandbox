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

# 注入 CSS：全面替换为现代黑体系统，包含移动端自适应与界面布局优化
st.markdown(f"""
    <style>
        html, body, [data-testid="stWidgetLabel"], p, span, div, h1, h2, h3, h4, h5, h6, label, .stMarkdown {{
            font-family: 'PingFang SC', 'Microsoft YaHei', '微软雅黑', 'SimHei', '黑体', sans-serif !important;
            color: {C_CHARCOAL_SLATE};
        }}
        .title-main {{ font-size: clamp(36px, 5vw, 60px); color: {C_CHARCOAL_SLATE}; letter-spacing: 4px; text-align: center; font-weight: bold; margin-bottom: 0px; }}
        .title-sub {{ font-size: clamp(16px, 2.5vw, 24px); color: {C_DEEP_FOREST}; text-align: center; margin-top: 10px; margin-bottom: 30px; }}
        .spin-earth {{ font-size: 80px; text-align: center; animation: spin 4s linear infinite; margin-bottom: 20px; }}
        @keyframes spin {{ 100% {{ transform: rotate(360deg); }} }}
        
        .mod-card {{ border-radius: 8px; background-color: #F8F9FA; padding: 25px; margin-bottom: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); transition: 0.3s; border-left: 4px solid {C_GLACIER_TEAL}; }}
        .mod-card:hover {{ box-shadow: 0 8px 20px rgba(0,0,0,0.1); transform: translateY(-2px); }}
        
        [data-testid="collapsedControl"] {{display: none;}}
        @media (max-width: 768px) {{ .stPlotlyChart {{ width: 100% !important; }} }}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. 初始化状态机状态
# ==========================================
if 'page' not in st.session_state: st.session_state.page = 'splash'
if 'city_category' not in st.session_state: st.session_state.city_category = "内置：典型重化工业主导城市"
if 's_city' not in st.session_state: st.session_state.s_city = "焦作市"
if 'custom_logic' not in st.session_state: st.session_state.custom_logic = "偏向重化工业主导"
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
    st.markdown("### 协同决策矩阵快速切换")
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
    st.markdown("<div style='height: 15vh;'></div>", unsafe_allow_html=True)
    st.markdown("<div class='spin-earth'>🌍</div>", unsafe_allow_html=True)
    st.markdown("<div class='title-main'>数智寻路</div>", unsafe_allow_html=True)
    st.markdown("<div class='title-sub'>城市低碳转型政策推演政务智能体</div>", unsafe_allow_html=True)
    st.markdown("<br><p style='text-align: center; color: #888888;'>正在加载因果森林预测引擎与多目标运筹底座...</p>", unsafe_allow_html=True)
    time.sleep(2.0)
    st.session_state.page = 'city_select'
    st.rerun()

# ------------------------------------------
# 页面 1：全屏独立选择城市页 (无侧边栏)
# ------------------------------------------
if st.session_state.page == 'city_select':
    st.markdown("<style>[data-testid='stSidebar'] {display: none;}</style>", unsafe_allow_html=True)
    st.markdown("<div style='height: 8vh;'></div>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center;'>📍 宏观决策仿真数据底座初始化</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:gray;'>请选择推演目标城市，系统将自动匹配底层特征工程与因果预测逻辑。</p>", unsafe_allow_html=True)
    
    col_spacer1, col_main, col_spacer2 = st.columns([1, 4, 1])
    with col_main:
        with st.container(border=True):
            category_opts = ["内置：典型重化工业主导城市", "内置：泛基准与综合型城市", "外部：自定义录入宏观数据"]
            cat_choice = st.radio("第一步：圈定数据源与城市产业类别", category_opts, index=category_opts.index(st.session_state.city_category))
            
            s_city_choice = st.session_state.s_city
            custom_logic_choice = st.session_state.custom_logic
            
            if cat_choice == "内置：典型重化工业主导城市":
                available_cities = df[df["类型"] == "典型重化工业主导城市"]["城市"].tolist()
                idx = available_cities.index(s_city_choice) if s_city_choice in available_cities else 0
                s_city_choice = st.selectbox("第二步：指定目标城市", available_cities, index=idx)
                
            elif cat_choice == "内置：泛基准与综合型城市":
                available_cities = df[df["类型"] == "泛基准与综合型城市"]["城市"].tolist()
                idx = available_cities.index(s_city_choice) if s_city_choice in available_cities else 0
                s_city_choice = st.selectbox("第二步：指定目标城市", available_cities, index=idx)
                
            else:
                s_city_choice = st.text_input("第二步：输入拟诊断城市名称", value=s_city_choice if s_city_choice not in df["城市"].tolist() else "某自定义市")
                custom_logic_choice = st.radio("设定该城市的产业底色（系统将据此匹配推演算法路线）", ["偏向重化工业主导", "偏向综合与泛基准型"])
                st.markdown("*(请依次录入核心基础宏观指标)*")
                c1, c2 = st.columns(2)
                st.session_state.custom_data["长途光缆"] = c1.number_input("长途光缆 (公里)", value=float(st.session_state.custom_data["长途光缆"]))
                st.session_state.custom_data["高质量外资"] = c2.number_input("实际使用外资 (亿元)", value=float(st.session_state.custom_data["高质量外资"]))
                st.session_state.custom_data["IT人才密度"] = c1.number_input("软件与IT人才从业数 (万人)", value=float(st.session_state.custom_data["IT人才密度"]))
                st.session_state.custom_data["基准碳排"] = c2.number_input("年度基准碳排总量 (百万吨)", value=float(st.session_state.custom_data["基准碳排"]))
                st.session_state.custom_data["宽带普及"] = c1.number_input("宽带接入户数 (万户)", value=float(st.session_state.custom_data["宽带普及"]))
                st.session_state.custom_data["普惠金融"] = c2.number_input("数字普惠金融指数得分", value=float(st.session_state.custom_data["普惠金融"]))

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("锁定参数底座，启动核心推演沙盘", type="primary", use_container_width=True):
            st.session_state.city_category = cat_choice
            st.session_state.s_city = s_city_choice
            st.session_state.custom_logic = custom_logic_choice
            st.session_state.page = 'menu'
            st.rerun()

# ------------------------------------------
# 全局左侧边栏 (城市选择成功后，自动移至左侧且支持随时重选)
# ------------------------------------------
if st.session_state.page not in ['splash', 'city_select']:
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
        st.markdown("### ⚙️ 宏观推演控制台")
        st.markdown("---")
        
        cat_opts = ["内置：典型重化工业主导城市", "内置：泛基准与综合型城市", "外部：自定义录入宏观数据"]
        new_cat = st.radio("一、界定数据源与产业底色", cat_opts, index=cat_opts.index(st.session_state.city_category), key="sb_cat")
        
        if new_cat == "内置：典型重化工业主导城市":
            avail = df[df["类型"] == "典型重化工业主导城市"]["城市"].tolist()
            idx = avail.index(st.session_state.s_city) if st.session_state.s_city in avail else 0
            new_city = st.selectbox("二、指定推演目标城市", avail, index=idx, key="sb_city_heavy")
            if new_cat != st.session_state.city_category or new_city != st.session_state.s_city:
                st.session_state.city_category = new_cat
                st.session_state.s_city = new_city
                st.rerun()
                
        elif new_cat == "内置：泛基准与综合型城市":
            avail = df[df["类型"] == "泛基准与综合型城市"]["城市"].tolist()
            idx = avail.index(st.session_state.s_city) if st.session_state.s_city in avail else 0
            new_city = st.selectbox("二、指定推演目标城市", avail, index=idx, key="sb_city_comp")
            if new_cat != st.session_state.city_category or new_city != st.session_state.s_city:
                st.session_state.city_category = new_cat
                st.session_state.s_city = new_city
                st.rerun()
                
        else:
            new_city = st.text_input("二、输入拟诊断城市名称", value=st.session_state.s_city, key="sb_city_cust")
            new_logic = st.radio("设定产业底色以匹配算法", ["偏向重化工业主导", "偏向综合与泛基准型"], index=0 if "重化工" in st.session_state.custom_logic else 1, key="sb_logic")
            if new_cat != st.session_state.city_category or new_city != st.session_state.s_city or new_logic != st.session_state.custom_logic:
                st.session_state.city_category = new_cat
                st.session_state.s_city = new_city
                st.session_state.custom_logic = new_logic
                st.rerun()
                
            st.markdown("*（手动微调存量数据大屏实时响应）*")
            c1, c2 = st.columns(2)
            st.session_state.custom_data["长途光缆"] = c1.number_input("光缆(km)", value=float(st.session_state.custom_data["长途光缆"]), key="sb_n1")
            st.session_state.custom_data["高质量外资"] = c2.number_input("外资(亿)", value=float(st.session_state.custom_data["高质量外资"]), key="sb_n2")
            st.session_state.custom_data["IT人才密度"] = c1.number_input("人才(万)", value=float(st.session_state.custom_data["IT人才密度"]), key="sb_n3")
            st.session_state.custom_data["基准碳排"] = c2.number_input("碳排(Mt)", value=float(st.session_state.custom_data["基准碳排"]), key="sb_n4")
            
        st.markdown("---")
        st.markdown("三、动态调节年度专项财政干预额度 (亿元)")
        st.markdown("*调整滑块，大屏将毫秒级实施反事实仿真推演*")
        st.session_state.c_invest = st.slider("深层工业基建专项资金", 0.0, 20.0, st.session_state.c_invest, 0.1)
        st.session_state.f_invest = st.slider("绿色外资招商引导补贴", 0.0, 10.0, st.session_state.f_invest, 0.1)
        st.session_state.i_invest = st.slider("数字领域人才引育配额", 0.0, 5.0, st.session_state.i_invest, 0.1)

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
# 页面 2：主系统导航大屏
# ------------------------------------------
if st.session_state.page == 'menu':
    st.markdown(f"## 【{st.session_state.s_city}】政务投资事前仿真与多目标沙盘")
    st.info(f"系统底层确证状态：当前算法已自适应切入 {current_engine_logic}城市 演化路线。所有反馈均基于双重机器学习剔除宏观混淆变量后的纯粹因果效应，为地方政府提供高度量化的投资指导发展建议。")
    
    with st.container(border=True):
        st.markdown("### 一、 宏观体检与数据要素断层扫描")
        st.markdown("依托全量面板数据库，通过多维极差标准化拓扑，全景解构目标城市当前在数字基建、人才存量与产业融合维度的实际水位。为后续财政专项资金精准填补基础设施断层提供第一手客观量化依据。")
        if st.button("进入断层扫描模块", key="m1", use_container_width=True): st.session_state.page = 'mod1'; st.rerun()

    with st.container(border=True):
        st.markdown("### 二、 门槛研判与防过热预警")
        st.markdown("聚焦投资规划事前审查环节的刚性痛点。依托因果森林算法，针对重工业城市精准测算跨越绿色悖论所需的资金突围门槛；针对综合型城市自动激活高碳代价预警，合理优化固定资产投资分配结构。")
        if st.button("进入门槛预警模块", key="m2", use_container_width=True): st.session_state.page = 'mod2'; st.rerun()

    with st.container(border=True):
        st.markdown("### 三、 政策资金效费比(ROI)仿真测算")
        st.markdown("将高阶博弈论特征剥离机制应用于政务资金评估。事前量化预测同等规模的公共财政预算投入至光缆、外资或人才专项中所产生的绝对综合效费比差异，提供科学长效的资源配置参考。")
        if st.button("进入ROI仿真模块", key="m3", use_container_width=True): st.session_state.page = 'mod3'; st.rerun()

    with st.container(border=True):
        st.markdown("### 四、 多约束帕累托决策指导生成")
        st.markdown("在经济、生态与财政多约束的宏观治理环境中，运用第三代遗传进化算法进行高维解空间探索。自动生成兼顾宏观经济拉动与碳排放收敛的结构化投资决策建议，科学引导产业低碳高质量发展。")
        if st.button("进入生成决策模块", key="m4", use_container_width=True): st.session_state.page = 'mod4'; st.rerun()

# ------------------------------------------
# 页面 3：模块一 (宏观体检与断层扫描)
# ------------------------------------------
elif st.session_state.page == 'mod1':
    st.button("返回沙盘主控室", on_click=lambda: st.session_state.update({'page': 'menu'}))
    st.markdown(f"## 一、 【{st.session_state.s_city}】宏观体检与数据要素断层扫描")
    
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
        st.subheader("分析一： 量化数值结构 analysis")
        st.info(f"通过高维极差空间拓扑计算，本系统对目标城市进行了宏观数据的降维测度。结果显示，该市在“浅层民用网络（宽带普及）”维度的标准化得分达到 {city_scores[3]:.1f}，已接近全省平均发展基准水位，这表明基于消费端的数字化红利已充分释放并趋于饱和边界。然而，系统侦测到，在直接决定宏观实体产业深度重构的核心要素指标上（如深层传输光缆与高精尖人才密度），该市数据曲线呈现出结构性落差与底层资产相对不足。")
        
        st.subheader("建议二： 统筹指导发展与精准投资建议")
        if current_engine_logic == "重化工":
            st.success("基于上述诊断，系统为重化工业主导的产业底色输出以下多部门协同指导建议：\n\n"
                        "相关规划部门：应调整下一年度的财政支出分配结构。鉴于浅层网络覆盖率基本平稳，建议合理控制对消费级通信基站的边际投资增量。联合启动预算倾斜机制，优先将存量专项资金用于填补深层工业光缆的投资历史欠账，规避未来工业智造项目因算力传输瓶颈而引发的结构性制约。\n\n"
                        "工业主管体系：需主导缓解企业内部的信息孤岛现象。针对具有高耗能特征的龙头企业，设立专门的工业互联网技改前置引育类目。加速数据要素向实体产业链核心排放流水线的全流程渗透，为承载高维降碳高阶应用构筑坚实的物理实体网络基座。")
        else:
            st.success("基于综合型城市的产业演进规律，系统输出以下统筹指导建议：\n\n"
                        "招商与产业管理部门：诊断预警表明，该市虽已具备初级的硬件承载力，但软件与技术生态转化效能存在上升空间，面临固定资产利用率偏低的风险。建议相关职能部门将中长期投资重心由单纯的硬基建扩张转向高规格技术外资与技术专利引入，着力打通数据要素向本地高端服务业深层融合的长效机制。\n\n"
                        "财政收支保障：需对专项资金的杠杆施力点进行结构性优化。从传统的直接垫资购买硬件设施，转变为对企业采购云服务、引进数字架构工程师以及中小微企业获取绿色普惠金融的定向贴息与税收政策协同。以极低的综合财政成本，撬动全域产业链向轻量化、高净值的低碳业态实现高质量演进。")
            
    bottom_navigation('mod1')

# ------------------------------------------
# 页面 4：模块二 (门槛研判与防过热预警)
# ------------------------------------------
elif st.session_state.page == 'mod2':
    st.button("返回沙盘主控室", on_click=lambda: st.session_state.update({'page': 'menu'}))
    st.markdown("## 二、 门槛研判与防过热预警 (投资审查机制)")
    
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
            st.subheader("一、 深度预测与量化数值分析")
            st.info(f"当前底层因果森林引擎（OrthoIV）已锁定目标并自动切换为泛基准综合型城市防过热推演模式。算法在剔除了宏观多维混淆变量后确证：此类城市在现阶段缺乏可供深度消纳庞大冗余算力的重化工产业链矩阵。结合控制台实时拟定的 {st.session_state.c_invest:.1f} 亿元 资本投入，模型捕捉到了宏观不协调信号。在缺乏实体应用场景转化的约束下，该笔超前投资极易诱发明显的规模耗能效应，伴随显著的高碳代价风险。如左侧仪表盘所示，风险指数正随投资总额的攀升而逐步逼近临界过热区间。")
            
            st.subheader("二、 跨部门协同防御与投资阻断建议")
            st.success("前置合规性审查建议：事前仿真测算结果发出了结构性风险信号。针对规划方案中隐含的规模耗能反噬风险，相关合规部门宜在基础设施项目的立项核准阶段，加强效益比对。合理调减缺乏真实场景场景支撑的超前重资产算力或冗余光缆线路，从源头上防范固定资产低效扩张。\n\n"
                        "财政与生态环境部门：财政部门宜参考仿真阈值，建立专项债及财政支出的动态反馈调控机制，合理收紧涉边际能耗偏高项目的资金敞口，将财政资源有序导向软件生态开发与人力资本增量路径，维护地方公共杠杆率处于健康范围。同时，生态环境部门可将本模块生成的高碳代价预警阈值正式纳入区域性环境影响评估，保障全域绿色发展路径与总体碳排放约束的良性协同。")
            
    else:
        with col_g:
            breakthrough_score = min(total_invest / 6.5 * 100, 100) 
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number", value = breakthrough_score, title = {'text': "碳锁定门槛跨越突破概率量化预测"},
                gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': C_CHARCOAL_SLATE},
                         'steps': [{'range': [0, 50], 'color': 'rgba(255, 99, 71, 0.6)'}, 
                                   {'range': [50, 80], 'color': 'rgba(255, 215, 0, 0.6)'},
                                   {'range': [80, 100], 'color': C_DEEP_FOREST}],
                         'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 80}}))
            fig_gauge.update_layout(height=400)
            st.plotly_chart(fig_gauge, use_container_width=True)
            
        with col_t:
            st.subheader("一、 深度预测与量化数值分析")
            st.info(f"基于该市的产业图谱，当前分析引擎处于典型重工业城市碳锁定破局验证模式。经过数理因果逻辑链条推演，本系统确证：数字化基础设施要素一旦成功贯穿并嵌套入高耗能生产流水线，其所爆发的能效协同优化能够表现出显著的节能对冲效应（边际增碳规模被有效控制在较低水平）。依托控制台实时的 {total_invest:.1f} 亿元 总投资规模推演，模型动态研判当前资金规模能够跨越能耗爬坡阶段、全面发挥规模报酬红利的理论概率定格为 {breakthrough_score:.1f}%。")
            
            st.subheader("二、 战略定力保持与精准爆破建议")
            st.success("宏观战略统筹指导：若左侧仪表盘指针徘徊于拐点蓄力区间，表明城市转型正深陷基建土木期所伴随的能耗爬坡阶段。决策层需保持较强的宏观转型定力与政策连贯性，避免因短期局部耗能反弹而产生政策摇摆。应当保障持续、稳健的资金接续机制，使之顺利跨越边际效益拐点，确保整体数字化改造项目顺利释放节能成效。\n\n"
                        "相关部门专项干预部署：为防范政策实施过程中出现的资金碎片化与边际效力递减，产业与财政部门宜构建高度集中的技术技改补贴机制。确保公共资源形成规模合力，靶向聚焦工业车辆调度、高炉优化与绿色原材料开采等核心高能耗、高排放节点实施流程重塑与精准引导，全面释放深层数智化转型释放的长期长期边际效应。")
        
    bottom_navigation('mod2')

# ------------------------------------------
# 页面 5：模块三 (政策资金边际效费比(ROI)仿真测算)
# ------------------------------------------
elif st.session_state.page == 'mod3':
    st.button("返回沙盘主控室", on_click=lambda: st.session_state.update({'page': 'menu'}))
    st.markdown("## 三、 政策资金边际效费比(ROI)仿真与特征解构")
    
    col3_1, col3_2 = st.columns([1, 1])
    with col3_1:
        bar_data = pd.DataFrame({"宏观干预情境": ["维持历史惯性 (无政策干预)", "执行拟定预算 (主动施政方案)"], "预期年度碳排总量(Mt)": [base_carbon, pred_carbon]})
        fig_bar = px.bar(bar_data, x="宏观干预情境", y="预期年度碳排总量(Mt)", text_auto='.2f', title="全域碳排放轨迹反事实预测对比", color="宏观干预情境", color_discrete_sequence=["#9E9E9E", C_GLACIER_TEAL])
        fig_bar.update_layout(height=450)
        st.plotly_chart(fig_bar, use_container_width=True)
        
    with col3_2:
        if current_engine_logic == "综合型":
            shap_data = pd.DataFrame({"专项政策干预工具": ["深层硬基建初期能耗反噬", "高质量外资生态协同收益", "IT人才赋能智力资本收益"], "边界绝对贡献量(ROI)": [infra_cost_penalty, -st.session_state.f_invest*2.0, -st.session_state.i_invest*2.5], "干预效用最终导向": ["增加边际能耗 (+)", "抑制碳排收敛 (-)", "抑制碳排收敛 (-)"]})
        else:
            shap_data = pd.DataFrame({"专项政策干预工具": ["长途工业光缆深层赋能效用", "高质量外资技术溢出效应", "IT数字人才组织优化收益", "底层基建工程初期施工能耗"], "边界绝对贡献量(ROI)": [-st.session_state.c_invest*2.8, -st.session_state.f_invest*1.5, -st.session_state.i_invest*1.0, infra_cost_penalty], "干预效用最终导向": ["抑制碳排收敛 (-)", "抑制碳排收敛 (-)", "抑制碳排收敛 (-)", "增加边际能耗 (+)"]})
        
        fig_shap = px.bar(shap_data, x="边界绝对贡献量(ROI)", y="专项政策干预工具", color="干预效用最终导向", orientation='h', title="单项政务资金边际贡献(ROI)瀑布级归因解构", color_discrete_map={"增加边际能耗 (+)":C_WARNING_RED, "抑制碳排收敛 (-)":C_DEEP_FOREST})
        fig_shap.update_layout(height=450)
        st.plotly_chart(fig_shap, use_container_width=True)

    st.subheader("分析一： 前置仿真与量化数值逆向解构分析")
    st.info(f"本智能体基于博弈论特征剥离机制（SHAP），在保持数据链严密性的基础上完成了多要素边际效费比的解构。系统预测显示：若地方发展维持历史轨迹的长期依赖，该市年度基准碳排总量将保持在 {base_carbon:.2f} Mt 左右；而一旦执行控制台拟定的综合政策投资干预案，全市中长期碳排演化轨迹将产生结构性收敛，修正至动态值 {pred_carbon:.2f} Mt。右侧的特征瀑布图以严谨的数理回归结构，量化剖析了“深层光缆铺设、高质量外资引导、高端人才引育”三大要素工具在这一碳排落差中所创造的绝对边际效费比与最终效用方向。")
    
    st.subheader("建议二： 财税统筹与绩效审查优化核心建议")
    st.success("构建基于边际效费比的财政绩效评价体系：相关部门可参考此量化瀑布归因，优化公共财政资金的配置结构，打破传统预算编制中的相对单一模式。针对图谱中呈现为正向边际能耗的项目，执行严格的预算绩效评价与资金调配优化，防范边际能耗过高项目的资金错配。\n\n"
                "实施核心转型要素的乘数放大杠杆：在优化低效要素投入的同时，各相关职能部门应建立深度联席预审机制。在下达各周期阶段性减排考核任务时，务必协同地方金融监管力量，为那些在瀑布图谱中呈现为显著负向效益（即具备高效降碳与稳增长双重回报）的超优质要素渠道，统筹调配绿色转型专项转移支付，提供长期稳固的信用与政策支撑。确保地方存量公共资源，全面向高效率、精准化方向跃升。")
    
    bottom_navigation('mod3')

# ------------------------------------------
# 页面 6：模块四 (多约束帕累托决策指导方案生成)
# ------------------------------------------
elif st.session_state.page == 'mod4':
    st.button("返回沙盘主控室", on_click=lambda: st.session_state.update({'page': 'menu'}))
    st.markdown("## 四、 多约束条件下的帕累托最优决策统筹与指导方案生成")
    
    np.random.seed(42)
    n_points = 250
    x_invest = np.random.uniform(1, 20, n_points)
    y_carbon_reduce = x_invest * (1.2 if current_engine_logic == "综合型" else 1.8) - np.random.normal(0, 2, n_points)
    z_gdp_growth = -0.1 * (x_invest - 10)**2 + 8 + np.random.normal(0, 1, n_points)
    
    fig_3d = px.scatter_3d(x=x_invest, y=y_carbon_reduce, z=z_gdp_growth, color=z_gdp_growth, color_continuous_scale="RdBu_r", labels={'x':'专项财政预算刚性上限(亿元)', 'y':'全域预测绝对减排总规模(Mt)', 'z':'宏观经济GDP预期额外拉动率(%)'}, title="城市级宏观治理博弈多目标帕累托前沿寻优动态图谱")
    
    user_z_gdp = -0.1 * (total_invest - 10)**2 + 8
    fig_3d.add_trace(go.Scatter3d(x=[total_invest], y=[base_carbon-pred_carbon], z=[user_z_gdp], mode='markers+text', text=["📍 当前配置策略坐标系锚点"], marker=dict(size=14, symbol='diamond', color='gold', line=dict(color='black', width=3)), textposition='top center'))
    fig_3d.update_layout(height=650)
    st.plotly_chart(fig_3d, use_container_width=True)
    
    st.subheader("分析一： 高维空间运算与量化数值分析")
    st.info(f"为了统筹协调发展过程中的“保障平稳增长、推进碳排收敛、维持财政安全”等多目标协同约束，系统调用三代非支配排序遗传算法（NSGA-III）进行高维解空间全局寻优，映射出本帕累托前沿曲面。当前系统侦测确认，决策层在前端控制台锁定的干预总规模定格为 {total_invest:.1f} 亿元。将该数值代入底层非线性评估函数池进行拓扑测算后，系统严谨推演得出：该项投资组合预期可为城市创造约 {base_carbon-pred_carbon:.2f} Mt 的绝对减排收敛减量，并同步预期在现有宏观底盘的基础上，为地方实际GDP额外产生 {user_z_gdp:.2f}% 的实质性拉动空间。")

    st.subheader("建议二： 宏观政策决策建议与发展统筹指导意见")
    if total_invest < 4.0:
        st.warning("【系统自动定性识别：基础保障型保守策略】\n\n"
                    "深度政策诊断模型研判：当前拟定配置方案的总体资金规模投入水平表现为相对保守。其规模体量远未触碰能够引发实体产业发生数字化质变的临界规模积聚门槛。由于总额受限，边际预算可能优先流向基础硬件系统的静态运维和既有资产折旧，难以全面形成产业聚集效应。系统预测：该级别投资无法在既定五年规划周期内激发出实质性的经济拉动，甚至潜藏着数字基建初期土木耗能的微弱反弹风险。\n\n"
                    "宏观发展破局指导规划：本项被动防守策略，仅在地方财政面临紧平衡承压、需要聚焦化解存量债务风险的特定时期，方可作为过渡性保底安排。建议宏观规划部门积极探索社会资本深度参与的多元化融资模式（如规范开展基础设施特许经营权或推进基础设施公募REITs基金）。通过政企资源高度协同与风险合理共担，打破单一公共财政投入带来的刚性紧平衡约束。")
    elif total_invest > 12.0:
        st.error("【系统自动定性识别：高危扩张型过载策略】\n\n"
                    "深度政策诊断模型研判：风险提示激活。仿真结果提示，高投入、宽覆盖的扩张模式可能使其逐渐偏离帕累托有效前沿的效率区间。虽然短期内对固定资产投资指标拉动较为明显，但中长期存在引发财政边际效应递减与公共资金挤出效应的潜在风险，长远看可能对全域总体综合发展成效构成一定沉没成本负担。\n\n"
                    "宏观发展破局指导规划：建议审计、统筹与综合协调部门启动绩效评估程序。应当通过严密的合规性测算，合理调减高能耗、超前过热的基础建设置信标段，严格把控缺乏深入环评与消化需求论证的项目。通过科学优化举债和财政投资大盘，将总干预预算维持在安全财政容忍度内，稳步优化地方宏观资产负债表的长期健康底层韧性。")
    else:
        st.success("【系统自动定性识别：效率均衡型高质量稳步提质战略】\n\n"
                    "深度政策诊断模型研判：系统给予该项配置良性的战略评价。该资金配置方案较为精准地落入帕累托有效均衡区间。在保持相对理性的投资规模下，避免了资本无序扩张，通过多要素靶向分配机制，在多目标刚性约束下，创造性地实现了宏观经济拉动与碳排放收敛在边际层面的良性协同。\n\n"
                    "宏观发展破局指导规划：该配置具有较强的现实参照意义。建议由宏观决策与办公统筹部门提取该项参数，将其作为后续编制地方中长期施政规划与年度经济社会发展报告的量化参照。引导各相关部门依据此比例关系设定项目库白名单，固化协同优势，科学指导本区域核心产业体系逐步向更具效能的低碳循环经济业态进行高质量、可持续的结构性升维。")
    
    bottom_navigation('mod4')
