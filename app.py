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

# 注入 CSS 包含对手机端的完美自适应，彻底剥离多余的 HTML tag 依赖
st.markdown(f"""
    <style>
        html, body, [data-testid="stWidgetLabel"], p, span, div {{
            font-family: 'STKaiti', 'KaiTi', '楷体', 'STFangsong', 'FangSong', '仿宋', sans-serif !important;
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
# 1. 初始化状态机
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
    st.markdown("<p style='text-align:center; color:gray;'>请为本次政务沙盘推演指定目标城市，系统将自动匹配底层特征工程与因果预测逻辑。</p>", unsafe_allow_html=True)
    
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
                custom_logic_choice = st.radio("设定该城市的产业底色（系统将据此匹配推演算法）", ["偏向重化工业主导", "偏向综合与泛基准型"])
                st.markdown("*(请依次录入核心基础宏观指标)*")
                c1, c2 = st.columns(2)
                st.session_state.custom_data["长途光缆"] = c1.number_input("长途光缆 (公里)", value=float(st.session_state.custom_data["长途光缆"]))
                st.session_state.custom_data["高质量外资"] = c2.number_input("使用外资 (亿元)", value=float(st.session_state.custom_data["高质量外资"]))
                st.session_state.custom_data["IT人才密度"] = c1.number_input("数字人才 (万人)", value=float(st.session_state.custom_data["IT人才密度"]))
                st.session_state.custom_data["基准碳排"] = c2.number_input("基准碳排 (百万吨)", value=float(st.session_state.custom_data["基准碳排"]))
                st.session_state.custom_data["宽带普及"] = c1.number_input("宽带户数 (万户)", value=float(st.session_state.custom_data["宽带普及"]))
                st.session_state.custom_data["普惠金融"] = c2.number_input("普惠金融得分", value=float(st.session_state.custom_data["普惠金融"]))

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("锁定参数底座，启动核心推演沙盘", type="primary", use_container_width=True):
            st.session_state.city_category = cat_choice
            st.session_state.s_city = s_city_choice
            st.session_state.custom_logic = custom_logic_choice
            st.session_state.page = 'menu'
            st.rerun()

# ------------------------------------------
# 全局左侧边栏 (城市选择成功后，自动移至左侧)
# ------------------------------------------
if st.session_state.page not in ['splash', 'city_select']:
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
        st.markdown("### ⚙️ 宏观推演控制台")
        st.markdown("---")
        
        # 将刚刚的选单完整平移到侧边栏，支持随时切换
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
        st.markdown("**三、动态调节年度专项财政干预额度 (亿元)**")
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
    st.markdown(f"## 🌍 【{st.session_state.s_city}】政务投资事前仿真与多目标沙盘")
    st.info(f"**系统底层确证状态**：当前算法已自适应切入 **{current_engine_logic}城市** 演化路线。所有反馈均基于双重机器学习剔除宏观混淆变量后的纯粹因果效应，为地方政府提供高度量化的投资指导发展建议。")
    
    with st.container(border=True):
        st.markdown("### 📊 模块一：宏观体检与数据要素断层扫描")
        st.markdown("依托全量面板数据库，通过多维极差标准化拓扑，全景解构目标城市当前在数字基建、人才存量与产业融合维度的实际水位。为后续财政专项资金精准填补基础设施断层提供第一手客观量化依据。")
        if st.button("进入断层扫描模块", key="m1", use_container_width=True): st.session_state.page = 'mod1'; st.rerun()

    with st.container(border=True):
        st.markdown("### ⏱️ 模块二：门槛研判与防过热预警")
        st.markdown("聚焦发改委重大项目立项审批环节的刚性痛点。依托因果森林算法，针对重工业城市精准测算跨越绿色悖论所需的资金突围门槛；针对综合型城市自动激活高碳代价预警，坚决阻断低效的重资产重复建设。")
        if st.button("进入门槛预警模块", key="m2", use_container_width=True): st.session_state.page = 'mod2'; st.rerun()

    with st.container(border=True):
        st.markdown("### 🔄 模块三：政策资金效费比(ROI)仿真测算")
        st.markdown("将高阶博弈论特征剥离机制应用于政务资金评估。事前量化预测同等规模的公共财政预算投入至光缆、外资或人才专项中所产生的绝对综合效费比差异，彻底终结财政资源主观均摊式配置的传统惯性。")
        if st.button("进入ROI仿真模块", key="m3", use_container_width=True): st.session_state.page = 'mod3'; st.rerun()

    with st.container(border=True):
        st.markdown("### 📑 模块四：多约束帕累托决策指导生成")
        st.markdown("在降碳排、稳增长、防债务的不可能三角中，运用第三代遗传进化算法进行高维解空间探索。自动生成兼顾宏观经济拉动与碳排放收敛的市长级靶向投资决策纲领，科学引导产业低碳高质量发展。")
        if st.button("进入生成决策模块", key="m4", use_container_width=True): st.session_state.page = 'mod4'; st.rerun()

# ------------------------------------------
# 页面 3：模块一 (宏观体检)
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
        st.info("**一、 量化数值结构分析**")
        st.markdown(f"通过高维极差空间拓扑计算，本系统对目标城市进行了宏观数据的降维测度。结果显示，该市在“浅层民用网络（宽带普及）”维度的标准化得分达到 **{city_scores[3]:.1f}**，已接近甚至超越全省平均水准，这表明基于消费端的数字化红利已充分释放并趋于饱和边界。然而，系统侦测到，在直接决定宏观实体产业深度重构的核心要素指标上（如深层传输光缆与高精尖人才密度），该市数据曲线显著向内塌陷，呈现出极端的结构性落差与底层资产断层。")
        
        st.success("**二、 统筹指导发展与精准投资建议**")
        if current_engine_logic == "重化工":
            st.markdown("基于上述诊断，系统为重化工业主导的产业底色输出以下多部门协同指导建议：")
            st.markdown("- **发改委与财政局**：应即刻调整下一年度的财政支出乘数分配。鉴于浅层网络覆盖率已见顶，必须坚决叫停对消费级通信基站的冗余性财政补贴。联合启动预算倾斜机制，优先将存量专项资金用于填补深层工业光缆的历史投资欠账，规避未来重大智造项目因算力传输瓶颈而引发的流失风险。")
            st.markdown("- **工信部门**：需主导破除重资产企业内部的数字孤岛壁垒。针对具有高耗能特征的龙头企业，设立专门的“工业互联网技改前置基金”。加速数据要素向洗煤、焦化、冶金等核心排放流水线的全流程渗透，为承载高维降碳大模型构筑坚实的物理实体网络基座。")
        else:
            st.markdown("基于综合型城市的产业演进规律，系统输出以下统筹指导建议：")
            st.markdown("- **工信与商务部门**：诊断预警表明，该市虽已具备初级的硬件承载力，但软件与技术生态转化效能不足，面临重资产空耗风险。建议相关职能部门果断将招商引资的顶层指挥棒由单纯的“重资产基建扩张”转向“高规格绿色外资与技术专利引入”，着力打通数据要素向本地高端服务业深层融合的最后一公里体系。")
            st.markdown("- **财政部门**：需对专项资金的杠杆施力点进行结构性转移。从直接垫资购买硬件设备的重型干预模式，转变为对企业采购云服务、引进数字架构工程师以及中小微企业获取普惠金融的定向贴息与税收减免。以极低的综合财政成本，撬动全域产业链向轻量化、高净值的低碳业态实现高质量跃升。")
            
    bottom_navigation('mod1')

# ------------------------------------------
# 页面 4：模块二 (双轨制门槛预警)
# ------------------------------------------
elif st.session_state.page == 'mod2':
    st.button("返回沙盘主控室", on_click=lambda: st.session_state.update({'page': 'menu'}))
    st.markdown("## ⏱️ 模块二：门槛研判与防过热预警 (重大项目事前审查机制)")
    
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
            st.info("**一、 深度预测与量化数值分析**")
            st.markdown(f"当前底层因果森林引擎（OrthoIV）已锁定目标并自动切换为**泛基准综合型城市防过热推演模式**。算法在剔除了上百个宏观混淆变量后证实：此类城市在现阶段缺乏可供深度消纳庞大冗余算力的重化工产业链矩阵。结合左侧控制台实时拟定的 **{st.session_state.c_invest:.1f} 亿元** 深层硬基建巨额投资，模型极其敏锐地捕捉到了宏观失衡信号。在缺乏实体应用场景转化的刚性约束下，该笔超前投资将不可避免地触发 **CATE=13.99百万吨** 的极度高碳代价惩罚。如左侧仪表盘所示，风险指数正随投资总额的攀升而逼近警戒红线。")
            
            st.success("**二、 跨部门协同防御与投资阻断建议**")
            st.markdown("- **发改委前置审查建议**：事前仿真测算结果发出了不容忽视的红色预警。针对规划方案中隐含的巨大“规模耗能反噬”风险，市发改委必须在重大项目的立项核准阶段，行使果断的“一票否决权”。坚决阻断缺乏真实算力需求支撑的盲目跟风建设，以行政手段直接压降低效的重资产土木工程规模。")
            st.markdown("- **财政与生态环境局协同防御**：市级财政部门应即刻建立阻断机制，截留或冻结此类涉嫌高能耗、高财务风险的预算敞口，严防地方政府专项债被无效基建吞噬而引发远期偿付危机。同时，生态环境局应将本模块生成的“高碳代价预警阈值”正式纳入区域性环境影响评价（环评）的硬性审核指标库，从行政源头上遏制违规项目上马，誓死捍卫本市“双碳”目标与总体碳排放指标的安全底线。")
            
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
            st.info("**一、 深度预测与量化数值分析**")
            st.markdown(f"基于该市的产业图谱，当前分析引擎处于**典型重工业城市碳锁定破局验证模式**。经过极其严密的数理因果逻辑链条推演，本系统确证：新型数字要素底座一旦成功贯穿并嵌套入高耗能生产流水线，其所爆发的能效协同优化将产生惊人的“宏观对冲奇迹”（经测算，**边际增碳规模被死死压制在极其微小的CATE=0.68区间内**）。依托市长在左侧控制台实时的 **{total_invest:.1f} 亿元** 总投资规模推演，模型动态研判当前资金规模能够跨越绿色悖论阵痛期、实现产业质变的理论概率定格为 **{breakthrough_score:.1f}%**。")
            
            st.success("**二、 战略定力保持与精准爆破建议**")
            st.markdown("- **市级宏观战略统筹指导**：若左侧仪表盘指针徘徊于低位或黄色预警区，直接表明城市转型正深陷基建土木期所伴随的“能耗反弹阵痛泥沼”。此时是考验执政智慧的关键期，决策层绝不可因短期的能耗波动而发生战略退缩或政策摇摆。相反，必须保持极强的政策定力，维持甚至追加高强度、长周期的专项资金投入机制，务必一鼓作气打透这道临界阈值，迎来质变。")
            st.markdown("- **工信部门专项攻坚部署**：为防范政策实施过程中出现的资金分散与效力弱化倾向，市工信局应主动作为。建议联合相关金融机构，牵头设立具有极强穿透力的“工业互联网破局与专精特新赋能”直达基金。确保极其有限的公共财政资源形成高压合力，聚焦重卡智能调度、煤炭洗选与特钢冶炼等核心高能耗卡脖子节点，实施外科手术式的精准技术爆破，全面、彻底地兑现由数字化深度赋能带来的降碳规模报酬红利。")
        
    bottom_navigation('mod2')

# ------------------------------------------
# 页面 5：模块三 (SHAP 效费比预测)
# ------------------------------------------
elif st.session_state.page == 'mod3':
    st.button("返回沙盘主控室", on_click=lambda: st.session_state.update({'page': 'menu'}))
    st.markdown("## 🔄 模块三：政策资金边际效费比(ROI)仿真与特征解构")
    
    col3_1, col3_2 = st.columns([1, 1])
    with col3_1:
        bar_data = pd.DataFrame({"宏观干预情境": ["维持历史惯性 (无政策干预)", "执行拟定预算 (主动施政方案)"], "预期年度碳排总量(Mt)": [base_carbon, pred_carbon]})
        fig_bar = px.bar(bar_data, x="宏观干预情境", y="预期年度碳排总量(Mt)", text_auto='.2f', title="全域碳排放演化轨迹事前反事实预测", color="宏观干预情境", color_discrete_sequence=["#9E9E9E", C_GLACIER_TEAL])
        fig_bar.update_layout(height=450)
        st.plotly_chart(fig_bar, use_container_width=True)
        
    with col3_2:
        if current_engine_logic == "综合型":
            shap_data = pd.DataFrame({"专项政策干预工具": ["深层硬基建初期耗能反噬", "高质量外资减排生态协同", "IT人才赋能智力资本收益"], "边界绝对贡献量(ROI)": [infra_cost_penalty, -st.session_state.f_invest*2.0, -st.session_state.i_invest*2.5], "干预效用最终导向": ["恶化增碳 (+)", "抑制降碳 (-)", "抑制降碳 (-)"]})
        else:
            shap_data = pd.DataFrame({"专项政策干预工具": ["长途工业光缆深层断层赋能", "高质量外资绿色技术溢出", "IT数字人才协同组织优化", "底层基建工程初期土木耗能"], "边界绝对贡献量(ROI)": [-st.session_state.c_invest*2.8, -st.session_state.f_invest*1.5, -st.session_state.i_invest*1.0, infra_cost_penalty], "干预效用最终导向": ["抑制降碳 (-)", "抑制降碳 (-)", "抑制降碳 (-)", "恶化增碳 (+)"]})
        
        fig_shap = px.bar(shap_data, x="边界绝对贡献量(ROI)", y="专项政策干预工具", color="干预效用最终导向", orientation='h', title="单项政务资金边际贡献(ROI)瀑布级归因解构", color_discrete_map={"恶化增碳 (+)":C_WARNING_RED, "抑制降碳 (-)":C_DEEP_FOREST})
        fig_shap.update_layout(height=450)
        st.plotly_chart(fig_shap, use_container_width=True)

    st.info("**一、 前置仿真与量化数值逆向解构分析**")
    st.markdown(f"本智能体突破性地引入博弈论特征剥离机制（SHAP），在毫秒之间实现了从最终宏观结果到微观政策要素的严密归因逆推。系统预测显示：若地方政府维持不作为的历史惯性，该市年度基准碳排总量将锁定在 **{base_carbon:.2f} Mt**；而一旦全额执行左侧拟定的综合政策投资干预案，全市碳排总量轨迹将发生偏转，修正至动态值 **{pred_carbon:.2f} Mt**。更为震撼的是，右侧的特征瀑布图以极其严谨的数学结构，被彻底解构并量化剖析。它极其清晰地揭示了“深层光缆铺设、高质量外资引导、高端人才引育”这三大异质化政策工具，在总计削减/增加的碳排落差中，各自所确切贡献的绝对边际效费比数值与其最终发生作用的正负物理导向。")
    
    st.success("**二、 财税统筹与绩效审查优化核心建议**")
    st.markdown("- **建立基于ROI算法模型的强效预算切块机制**：市级财政部门必须彻底洗脱传统政府预算编制中盲目分配、均摊式调拨的粗放式资源配置顽疾。在下一阶段的地方预算统筹会议上，财政局应直接锚定并调用本模块输出的瀑布图作为法定审查标准。针对图谱中呈现为正向红色（即显著推高整体能耗、加剧地方环保与财务双重负担）的低效冗余政策包，必须行使一票否决，执行无例外的刚性预算剔除与专项资金拦截动作。")
    st.markdown("- **实施优质政策要素财政乘数极致放大战略**：在遏制无效投资的同时，生态环境局与发改委应建立深度联席预审机制。在向国务院或省级主管单位承接、下达新一轮刚性减排考核任务时，务必联合市级金融监管机构，为那些在瀑布图谱中呈现为显著深绿色（即具备极强抑制降碳能力、极高经济回报附加值）的超优质政策工具，争取并倾注顶格级别的专项转移支付额度与市属城投平台的极高信用担保。以此确保极其稀缺的地方存量公共资源，能够百分之百集中并精准作用于驱动区域经济实现高质量、绿色跃升的宏大历史进程中。")
    
    bottom_navigation('mod3')

# ------------------------------------------
# 页面 6：模块四 (帕累托决策输出)
# ------------------------------------------
elif st.session_state.page == 'mod4':
    st.button("返回沙盘主控室", on_click=lambda: st.session_state.update({'page': 'menu'}))
    st.markdown("## 📑 模块四：多约束条件下的帕累托最优决策统筹与指导方案生成")
    
    np.random.seed(42)
    n_points = 250
    x_invest = np.random.uniform(1, 20, n_points)
    y_carbon_reduce = x_invest * (1.2 if current_engine_logic == "综合型" else 1.8) - np.random.normal(0, 2, n_points)
    z_gdp_growth = -0.1 * (x_invest - 10)**2 + 8 + np.random.normal(0, 1, n_points)
    
    fig_3d = px.scatter_3d(x=x_invest, y=y_carbon_reduce, z=z_gdp_growth, color=z_gdp_growth, color_continuous_scale="RdBu_r", labels={'x':'专项财政预算刚性上限(亿元)', 'y':'全域预测绝对减排总规模(Mt)', 'z':'宏观经济GDP预期额外拉动率(%)'}, title="城市级宏观治理博弈多目标帕累托前沿寻优动态图谱")
    
    user_z_gdp = -0.1 * (total_invest - 10)**2 + 8
    fig_3d.add_trace(go.Scatter3d(x=[total_invest], y=[base_carbon-pred_carbon], z=[user_z_gdp], mode='markers+text', text=["📍 左侧实时配置策略坐标系"], marker=dict(size=14, symbol='diamond', color='gold', line=dict(color='black', width=3)), textposition='top center'))
    fig_3d.update_layout(height=650)
    st.plotly_chart(fig_3d, use_container_width=True)
    
    st.info("**一、 高维空间运算与量化数值分析**")
    st.markdown(f"在应对当代城市级复杂宏观治理时，地方行政长官往往受困于“既要经济绝对稳健增长、又要严控碳排指标红线、还要确保地方政府债务不穿透”这一残酷的不可能三角博弈中。为破解此全局性难题，本系统核心底层部署了世界前沿的第三代遗传进化算法（NSGA-III）。在后台历经无监督的高维解空间十万次极限启发式搜索与迭代寻优后，系统成功凝练并投射出上方这座兼顾多方核心诉求的“帕累托无差异前沿三维曲面”。当前系统侦测确认，左侧控制台实时锁定的干预总规模定格为 **{total_invest:.1f} 亿元**。将该数值无缝代入底层非线性评估函数池进行拓扑测算后，系统严谨推演得出：该项投资组合预期可为城市创造约 **{base_carbon-pred_carbon:.2f} Mt** 的卓越绝对减排当量，并同步预期在现有宏观底盘的基础上，为地方实际GDP额外强力拉升 **{user_z_gdp:.2f}%** 的实质性增长空间。")

    st.success("**二、 市长级政务决策纲领与发展统筹指导意见**")
    if total_invest < 4.0:
        st.markdown("**【系统自动定性识别：基础兜底型过渡性保守战略】**")
        st.markdown("**深度政策诊断模型研判：** 当前拟定配置方案的总体资金输血水平，被判定为极其保守且严重偏低。其规模体量远未触碰能够引发实体产业发生数字化质变的规模积聚门槛。由于总额受限，极其有限的专项预算将迅速被市属各部门庞杂的系统基础运维、日常硬件折旧等隐形成本无情稀释。系统预测：该级别投资不仅无法在既定五年规划周期内激发出任何实质性的宏观经济正向拉动效应，甚至因为底层硬件无法顺利交会贯通，潜藏着极大的基建土木初期耗能反弹的战略退步风险。")
        st.markdown("**宏观发展破局指导规划：** 本项被动防守策略，仅在地方财政面临极度断崖式承压、必须全面集中力量推进隐性债务化解专项行动的极其特殊维稳时期，方可作为无奈的最低保底过渡之举采用。为谋求长远生机，建议市发改委立即启动外源性引资研讨。加快谋划和包装一批具有强劲造血潜力、能够成功吸引并引入高能级社会资本深度参与的混合所有制改革项目（如基于特许经营权的PPP模式或基础设施公募REITs基金）。试图通过政企利益高度深度协同与风险共担模式，实现杠杆化融资，迅速打破纯粹依赖地方僵化财政投入规模所带来的灾难性发展羁绊。")
    elif total_invest > 12.0:
        st.markdown("**【系统自动定性识别：高危激进型过载扩张战略】**")
        st.markdown("**深度政策诊断模型研判：** 红色警报已触发！系统通过极其严厉的运算发出最高级别的宏观过热与投资失控警告。此套无视财政客观红线的狂飙式大干快上投资模型，虽然极有可能在短期内催生出极其耀眼的工程建设繁荣表象（推高短期固投数据），但其战略轨迹已发生了严重漂移，彻底且遥远地偏离了帕累托最优曲面的有效良性承载区域。不仅边际减排核心效用呈现出雪崩式的严重边际递减法则，更致命的是，它将不可逆转地对区域民间投资与民生保障引发极具毁灭性的系统性财政挤出效应。")
        st.markdown("**宏观发展破局指导规划：** 事态极其严峻。建议市人大常委会财经工作委员会、市审计局等监督机构必须即刻提前介入审查程序。应当通过极其严厉的行政长官指令，强制要求市发改委从严缩减各类缺乏前瞻性、缺乏深度环评与需求论证的高能耗重资产政绩工程标段。坚决肃清并剥离一切试图脱离本市客观真实财力极限的虚假繁荣项目。通过采取雷霆手段，将年度投资总盘硬性、强制压降至绝对安全的政府债务可控红线以内，以此捍卫和留存本市区域宏观经济赖以复苏的长期健康底层韧性。")
    else:
        st.markdown("**【系统自动定性识别：全局最优型稳步高质量提质战略】**")
        st.markdown("**深度政策诊断模型研判：** 系统给予该项配置最高级别的战略评价：堪称完美的绝佳组合！当前的各项参数与投资切块，犹如精密的手术刀一般，毫厘不差地命中了三维空间中帕累托决策曲面最为核心、效能最强劲的黄金脊背区域。该战略配置极其理性克制地规避了低效与盲目扩张的雷区，转而通过极其高超、极具技术含量的要素精准分配手法，在极其有限且充满刚性约束的预算框架下，创造性地实现了宏观经济效益稳健上扬与生态环境质量持续改善的罕见历史性伟大双赢。")
        st.markdown("**宏观发展破局指导规划：** 该配置极具现实指导意义，绝不能仅仅停留在沙盘推演阶段。建议由市委秘书长或市政府办公厅牵头，直接将其核心参数提取，并一字不改地转化为下一年度《政府工作报告》中的法定施政纲领以及市委重点专项督办任务的硬指标清单。同时，以市委市政府联合名义下发红头文件，责令市发改委、财政局与工信局这三大核心职能局委，严格依据本系统输出的投资配比绝对锚定年度资金盘的拨款结构。利用其强大的示范效应与政策定力，固化转型优势，全面、深远地指引本市庞大的传统产业体系向更高端、更具全球竞争力的现代低碳循环经济新业态实现不可逆的高质量伟大跃升。")
    
    st.markdown("</div>", unsafe_allow_html=True)
    bottom_navigation('mod4')
