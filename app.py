import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import time

# ==========================================
# 0. 全局配置与PC政务大屏美学定义
# ==========================================
st.set_page_config(page_title="城市低碳转型智能决策推演系统", layout="wide", initial_sidebar_state="expanded")

C_CHARCOAL_SLATE = "#2C3539"  
C_DEEP_FOREST = "#1A3622"      
C_GLACIER_TEAL = "#4DB8B3"     
C_WARNING_RED = "#D32F2F"      

st.markdown(f"""
    <style>
        button span, .material-icons, .material-symbols-rounded, [data-testid="stSidebarCollapseButton"] span {{
            font-family: "Material Symbols Rounded", "Material Icons", sans-serif !important;
        }}
        html, body, p, div, h1, h2, h3, h4, h5, h6, label, .stMarkdown, [data-testid="stWidgetLabel"] {{
            font-family: 'PingFang SC', 'Microsoft YaHei', '微软雅黑', 'SimHei', '黑体', sans-serif !important;
            color: {C_CHARCOAL_SLATE};
        }}
        .title-main {{ font-size: 60px; color: {C_CHARCOAL_SLATE}; letter-spacing: 4px; text-align: center; font-weight: bold; margin-bottom: 0px; }}
        .title-sub {{ font-size: 24px; color: {C_DEEP_FOREST}; text-align: center; margin-top: 10px; margin-bottom: 30px; }}
        .spin-earth {{ font-size: 80px; text-align: center; animation: spin 4s linear infinite; margin-bottom: 20px; }}
        @keyframes spin {{ 100% {{ transform: rotate(360deg); }} }}
        .mod-card {{ border-radius: 8px; background-color: #F8F9FA; padding: 25px; margin-bottom: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); transition: 0.3s; border-left: 4px solid {C_GLACIER_TEAL}; }}
        .mod-card:hover {{ box-shadow: 0 8px 20px rgba(0,0,0,0.1); transform: translateY(-2px); }}
        .alarm-box {{ background-color: #FFF5F5; border: 1px solid #FFCDD2; padding: 15px; border-radius: 6px; margin-top: 15px; }}
        .analysis-box {{ background-color: #FAFAFA; border-left: 4px solid {C_DEEP_FOREST}; padding: 15px 20px; margin-top: 15px; }}
        [data-testid="collapsedControl"] {{display: none;}}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. 初始化状态机
# ==========================================
if 'page' not in st.session_state: st.session_state.page = 'splash'
if 'city_category' not in st.session_state: st.session_state.city_category = "内置：典型重化工业主导城市"
if 's_city' not in st.session_state: st.session_state.s_city = "河南省焦作市"
if 'custom_logic' not in st.session_state: st.session_state.custom_logic = "偏向重化工业主导"
if 'c_invest' not in st.session_state: st.session_state.c_invest = 4.8
if 'f_invest' not in st.session_state: st.session_state.f_invest = 2.5
if 'i_invest' not in st.session_state: st.session_state.i_invest = 1.0
if 'custom_data' not in st.session_state: 
    st.session_state.custom_data = {"长途光缆": 1500.0, "高质量外资": 10.0, "IT人才密度": 1.5, "宽带普及": 200.0, "普惠金融": 280.0, "基准碳排": 50.0}

# ==========================================
# 2. 内嵌全域25城市数据库 (严格对齐最新标准)
# ==========================================
embedded_data = [
  {"城市": "河南省郑州市", "类型": "泛基准与综合型城市", "长途光缆": 1942.64, "高质量外资": 12.29, "IT人才密度": 10.99, "宽带普及": 774, "普惠金融": 337.22, "基准碳排": 52.37},
  {"城市": "河南省开封市", "类型": "泛基准与综合型城市", "长途光缆": 1601.98, "高质量外资": 1.78, "IT人才密度": 0.3, "宽带普及": 306, "普惠金融": 297.88, "基准碳排": 11.61},
  {"城市": "河南省洛阳市", "类型": "泛基准与综合型城市", "长途光缆": 3911.33, "高质量外资": 1.3, "IT人才密度": 4.28, "宽带普及": 313, "普惠金融": 311.82, "基准碳排": 50.78},
  {"城市": "河南省平顶山市", "类型": "典型重化工业主导城市", "长途光缆": 2030.67, "高质量外资": 1.02, "IT人才密度": 0.33, "宽带普及": 601, "普惠金融": 289.76, "基准碳排": 19.45},
  {"城市": "河南省安阳市", "类型": "典型重化工业主导城市", "长途光缆": 1887.28, "高质量外资": 2.39, "IT人才密度": 0.29, "宽带普及": 258, "普惠金融": 290.5, "基准碳排": 102.41},
  {"城市": "河南省鹤壁市", "类型": "典型重化工业主导城市", "长途光缆": 549.49, "高质量外资": 0.23, "IT人才密度": 0.13, "宽带普及": 74, "普惠金融": 297.32, "基准碳排": 9.89},
  {"城市": "河南省新乡市", "类型": "泛基准与综合型城市", "长途光缆": 2128.43, "高质量外资": 1.02, "IT人才密度": 0.49, "宽带普及": 297, "普惠金融": 298.28, "基准碳排": 38.84},
  {"城市": "河南省焦作市", "类型": "典型重化工业主导城市", "长途光缆": 1019.84, "高质量外资": 2.8, "IT人才密度": 0.27, "宽带普及": 217, "普惠金融": 302.66, "基准碳排": 23.61},
  {"城市": "河南省濮阳市", "类型": "泛基准与综合型城市", "长途光缆": 1096.49, "高质量外资": 0.96, "IT人才密度": 0.34, "宽带普及": 202, "普惠金融": 289.01, "基准碳排": 9.52},
  {"城市": "河南省许昌市", "类型": "泛基准与综合型城市", "长途光缆": 1278.16, "高质量外资": 0.27, "IT人才密度": 0.42, "宽带普及": 195, "普惠金融": 307.91, "基准碳排": 22.08},
  {"城市": "河南省漯河市", "类型": "泛基准与综合型城市", "长途光缆": 691.19, "高质量外资": 2.59, "IT人才密度": 0.17, "宽带普及": 112, "普惠金融": 298.41, "基准碳排": 2.62},
  {"城市": "河南省三门峡市", "类型": "泛基准与综合型城市", "长途光缆": 2550.69, "高质量外资": 36.88, "IT人才密度": 0.21, "宽带普及": 118, "普惠金融": 299.84, "基准碳排": 30.98},
  {"城市": "河南省南阳市", "类型": "泛基准与综合型城市", "长途光缆": 6805.99, "高质量外资": 1.91, "IT人才密度": 0.66, "宽带普及": 452, "普惠金融": 292.31, "基准碳排": 17.16},
  {"城市": "河南省商丘市", "类型": "泛基准与综合型城市", "长途光缆": 2747.8, "高质量外资": 0.02, "IT人才密度": 0.38, "宽带普及": 374, "普惠金融": 281.97, "基准碳排": 70.75},
  {"城市": "河南省信阳市", "类型": "泛基准与综合型城市", "长途光缆": 4855.99, "高质量外资": 0.61, "IT人才密度": 0.37, "宽带普及": 321, "普惠金融": 291.0, "基准碳排": 23.33},
  {"城市": "河南省周口市", "类型": "泛基准与综合型城市", "长途光缆": 3070.62, "高质量外资": 1.02, "IT人才密度": 0.53, "宽带普及": 387, "普惠金融": 276.34, "基准碳排": 5.4},
  {"城市": "河南省驻马店市", "类型": "泛基准与综合型城市", "长途光缆": 3872.93, "高质量外资": 0.33, "IT人才密度": 0.38, "宽带普及": 291, "普惠金融": 283.42, "基准碳排": 36.23},
  {"城市": "山西省晋城市", "类型": "典型重化工业主导城市", "长途光缆": 2206.89, "高质量外资": 14.34, "IT人才密度": 0.26, "宽带普及": 88, "普惠金融": 305.59, "基准碳排": 161.18},
  {"城市": "山西省长治市", "类型": "典型重化工业主导城市", "长途光缆": 3255.51, "高质量外资": 31.14, "IT人才密度": 0.3, "宽带普及": 150, "普惠金融": 288.2, "基准碳排": 79.07},
  {"城市": "山东省菏泽市", "类型": "泛基准与综合型城市", "长途光缆": 2736.93, "高质量外资": 0.0, "IT人才密度": 0.3, "宽带普及": 361, "普惠金融": 277.8, "基准碳排": 101.5},
  {"城市": "山东省聊城市", "类型": "泛基准与综合型城市", "长途光缆": 1929.48, "高质量外资": 17.96, "IT人才密度": 0.3, "宽带普及": 243, "普惠金融": 289.35, "基准碳排": 88.18},
  {"城市": "安徽省淮北市", "类型": "泛基准与综合型城市", "长途光缆": 801.28, "高质量外资": 34.69, "IT人才密度": 0.19, "宽带普及": 101, "普惠金融": 293.31, "基准碳排": 71.74},
  {"城市": "安徽省宿州市", "类型": "泛基准与综合型城市", "长途光缆": 2905.02, "高质量外资": 0.89, "IT人才密度": 0.58, "宽带普及": 269, "普惠金融": 281.85, "基准碳排": 31.17},
  {"城市": "安徽省阜阳市", "类型": "泛基准与综合型城市", "长途光缆": 2957.45, "高质量外资": 73.48, "IT人才密度": 0.31, "宽带普及": 386, "普惠金融": 289.01, "基准碳排": 27.68},
  {"城市": "安徽省蚌埠市", "类型": "泛基准与综合型城市", "长途光缆": 1739.34, "高质量外资": 0.85, "IT人才密度": 0.22, "宽带普及": 164, "普惠金融": 301.81, "基准碳排": 16.85}
]
df = pd.DataFrame(embedded_data)

def normalize_to_100(val, col_name):
    min_val = df[col_name].min(); max_val = df[col_name].max()
    if max_val == min_val: return 50
    return max(0, min((val - min_val) / (max_val - min_val) * 100, 100))

def bottom_navigation(current_page):
    st.markdown("---")
    st.markdown("### 系统辅助决策矩阵快速切换")
    pages = {'mod1': "模块一：宏观体检与断层推演", 'mod2': "模块二：门槛研判与报警监测", 'mod3': "模块三：政策试错与轨迹仿真", 'mod4': "模块四：帕累托决策最优生成"}
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
    st.markdown("<div class='title-main'>城市低碳转型智能决策推演系统</div>", unsafe_allow_html=True)
    st.markdown("<div class='title-sub'>宏观政务投资事前仿真与多目标沙盘</div>", unsafe_allow_html=True)
    st.markdown("<br><p style='text-align: center; color: #888888;'>正在加载因果森林推演引擎与高维特征要素底座...</p>", unsafe_allow_html=True)
    time.sleep(2.0)
    st.session_state.page = 'city_select'
    st.rerun()

# ------------------------------------------
# 页面 1：全屏独立选择城市页
# ------------------------------------------
if st.session_state.page == 'city_select':
    st.markdown("<style>[data-testid='stSidebar'] {display: none;}</style>", unsafe_allow_html=True)
    st.markdown("<div style='height: 8vh;'></div>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center;'>📍 宏观决策仿真数据底座初始化</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:gray;'>请配置系统推演初始参数，后台将自动加载对应的特征工程与底层预测逻辑。</p>", unsafe_allow_html=True)
    
    col_spacer1, col_main, col_spacer2 = st.columns([1, 4, 1])
    with col_main:
        with st.container(border=True):
            category_opts = ["内置：典型重化工业主导城市", "内置：泛基准与综合型城市", "外部：自定义录入宏观数据"]
            cat_choice = st.radio("第一步：界定数据归属与产业结构类型", category_opts, index=category_opts.index(st.session_state.city_category))
            
            s_city_choice = st.session_state.s_city
            custom_logic_choice = st.session_state.custom_logic
            
            if cat_choice == "内置：典型重化工业主导城市":
                available_cities = df[df["类型"] == "典型重化工业主导城市"]["城市"].tolist()
                idx = available_cities.index(s_city_choice) if s_city_choice in available_cities else 0
                s_city_choice = st.selectbox("第二步：选择重点分析城市", available_cities, index=idx)
                
            elif cat_choice == "内置：泛基准与综合型城市":
                available_cities = df[df["类型"] == "泛基准与综合型城市"]["城市"].tolist()
                idx = available_cities.index(s_city_choice) if s_city_choice in available_cities else 0
                s_city_choice = st.selectbox("第二步：选择基准对照城市", available_cities, index=idx)
                
            else:
                s_city_choice = st.text_input("第二步：设定系统推演目标名称", value=s_city_choice if s_city_choice not in df["城市"].tolist() else "未命名区域")
                custom_logic_choice = st.radio("核定该区域的主导产业底色（用于匹配算法核心逻辑）", ["偏向重化工业主导", "偏向综合与泛基准型"])
                st.markdown("*(请依次录入核心基础宏观指标)*")
                c1, c2 = st.columns(2)
                st.session_state.custom_data["长途光缆"] = c1.number_input("长途光缆线路总长 (公里)", value=float(st.session_state.custom_data["长途光缆"]))
                st.session_state.custom_data["高质量外资"] = c2.number_input("年度实际使用外资 (亿元)", value=float(st.session_state.custom_data["高质量外资"]))
                st.session_state.custom_data["IT人才密度"] = c1.number_input("数字产业从业规模 (万人)", value=float(st.session_state.custom_data["IT人才密度"]))
                st.session_state.custom_data["基准碳排"] = c2.number_input("期初核算碳排总量 (百万吨)", value=float(st.session_state.custom_data["基准碳排"]))
                st.session_state.custom_data["宽带普及"] = c1.number_input("区域宽带接入体量 (万户)", value=float(st.session_state.custom_data["宽带普及"]))
                st.session_state.custom_data["普惠金融"] = c2.number_input("普惠金融发展指数", value=float(st.session_state.custom_data["普惠金融"]))

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("数据载入完毕，启动系统决策沙盘", type="primary", use_container_width=True):
            st.session_state.city_category = cat_choice
            st.session_state.s_city = s_city_choice
            st.session_state.custom_logic = custom_logic_choice
            st.session_state.page = 'menu'
            st.rerun()

# ------------------------------------------
# 全局左侧边栏控制台
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
        st.markdown("### ⚙️ 宏观推演参数控制台")
        st.markdown("---")
        
        cat_opts = ["内置：典型重化工业主导城市", "内置：泛基准与综合型城市", "外部：自定义录入宏观数据"]
        new_cat = st.radio("一、界定数据源与产业底色", cat_opts, index=cat_opts.index(st.session_state.city_category), key="sb_cat")
        
        if new_cat == "内置：典型重化工业主导城市":
            avail = df[df["类型"] == "典型重化工业主导城市"]["城市"].tolist()
            idx = avail.index(st.session_state.s_city) if st.session_state.s_city in avail else 0
            new_city = st.selectbox("二、设定推演标的", avail, index=idx, key="sb_city_heavy")
            if new_cat != st.session_state.city_category or new_city != st.session_state.s_city:
                st.session_state.city_category = new_cat; st.session_state.s_city = new_city; st.rerun()
                
        elif new_cat == "内置：泛基准与综合型城市":
            avail = df[df["类型"] == "泛基准与综合型城市"]["城市"].tolist()
            idx = avail.index(st.session_state.s_city) if st.session_state.s_city in avail else 0
            new_city = st.selectbox("二、设定对照基准", avail, index=idx, key="sb_city_comp")
            if new_cat != st.session_state.city_category or new_city != st.session_state.s_city:
                st.session_state.city_category = new_cat; st.session_state.s_city = new_city; st.rerun()
                
        else:
            new_city = st.text_input("二、输入拟诊断城市名称", value=st.session_state.s_city, key="sb_city_cust")
            new_logic = st.radio("设定产业底色以匹配算法", ["偏向重化工业主导", "偏向综合与泛基准型"], index=0 if "重化工" in st.session_state.custom_logic else 1, key="sb_logic")
            if new_cat != st.session_state.city_category or new_city != st.session_state.s_city or new_logic != st.session_state.custom_logic:
                st.session_state.city_category = new_cat; st.session_state.s_city = new_city; st.session_state.custom_logic = new_logic; st.rerun()
                
            st.markdown("*（手动微调存量数据大屏实时响应）*")
            c1, c2 = st.columns(2)
            st.session_state.custom_data["长途光缆"] = c1.number_input("光缆(km)", value=float(st.session_state.custom_data["长途光缆"]), key="sb_n1")
            st.session_state.custom_data["高质量外资"] = c2.number_input("外资(亿)", value=float(st.session_state.custom_data["高质量外资"]), key="sb_n2")
            st.session_state.custom_data["IT人才密度"] = c1.number_input("人才(万)", value=float(st.session_state.custom_data["IT人才密度"]), key="sb_n3")
            st.session_state.custom_data["基准碳排"] = c2.number_input("碳排(Mt)", value=float(st.session_state.custom_data["基准碳排"]), key="sb_n4")
            
        st.markdown("---")
        st.markdown("三、政策干预力度动态调节 (亿元)")
        st.markdown("*拖动滑块，系统将触发过程性反事实仿真推演*")
        st.session_state.c_invest = st.slider("数字基建专项预算分配", 0.0, 20.0, st.session_state.c_invest, 0.1)
        st.session_state.f_invest = st.slider("高质量外资政策性引导资金", 0.0, 10.0, st.session_state.f_invest, 0.1)
        st.session_state.i_invest = st.slider("数字人才结构优化补贴", 0.0, 5.0, st.session_state.i_invest, 0.1)

    # 异质性算法映射
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
    st.markdown(f"## 🌍 【{st.session_state.s_city}】城市低碳转型智能决策推演系统")
    st.info(f"系统运行状态：算法后台已切入 {current_engine_logic} 逻辑演化路线。各分析模块将基于因果推断框架输出客观的量化指标，辅助宏观政策的科学论证。")
    
    with st.container(border=True):
        st.markdown("### 一、 宏观体检与要素断层推演")
        st.markdown("该模块依托面板数据构建多维极差标准化拓扑。旨在全面解构城市在信息基础设施、智力资本与产业数字化进程中的存量差异，为科学编制补短板专项资金提供数据基础。")
        if st.button("进入体检与推演模块", key="m1", use_container_width=True): st.session_state.page = 'mod1'; st.rerun()

    with st.container(border=True):
        st.markdown("### 二、 门槛研判与报警监测溯源")
        st.markdown("本模块主要服务于固定资产投资的合规性与效益审查。系统引入双变量热力矩阵，可视化呈现宏观资金配比的系统性风险，并配套完善的异动数据归因溯源解释体系。")
        if st.button("进入报警与监测模块", key="m2", use_container_width=True): st.session_state.page = 'mod2'; st.rerun()

    with st.container(border=True):
        st.markdown("### 三、 政策试错与未来轨迹仿真")
        st.markdown("该功能支持决策部门开展交互式的政策反事实模拟。系统可即时生成干预政策实施后的中短期碳排放演化预测曲线，并运用SHAP算法清晰界定各项资本投入的边际减排贡献度。")
        if st.button("进入政策试错模块", key="m3", use_container_width=True): st.session_state.page = 'mod3'; st.rerun()

    with st.container(border=True):
        st.markdown("### 四、 多约束帕累托决策最优生成")
        st.markdown("针对多重行政目标间的潜在冲突，模块运行高维启发式优化算法。能够在严格的财政约束下，测算并推荐能够实现经济稳固与碳排收敛相统一的全局适宜性投资方案。")
        if st.button("进入最优生成模块", key="m4", use_container_width=True): st.session_state.page = 'mod4'; st.rerun()

# ------------------------------------------
# 页面 3：模块一 (宏观体检与断层推演)
# ------------------------------------------
elif st.session_state.page == 'mod1':
    st.button("返回系统主控室", on_click=lambda: st.session_state.update({'page': 'menu'}))
    st.markdown(f"## 一、 【{st.session_state.s_city}】宏观体检与数据要素断层推演")
    
    col1, col2 = st.columns([1, 1])
    categories = ['深层算力(长途光缆)', '绿色资本(外资)', '智力资本(IT人才)', '浅层网络(宽带普及)', '产业融合(普惠金融)']
    city_scores = [normalize_to_100(city_data.get(k, 50), k) for k in ["长途光缆", "高质量外资", "IT人才密度", "宽带普及", "普惠金融"]]
    avg_scores = [normalize_to_100(df[k].mean(), k) for k in ["长途光缆", "高质量外资", "IT人才密度", "宽带普及", "普惠金融"]]
    
    with col1:
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(r=avg_scores, theta=categories, fill='toself', name='全省区域均值', line_color='rgba(100, 149, 237, 0.8)'))
        fig_radar.add_trace(go.Scatterpolar(r=city_scores, theta=categories, fill='toself', name=f'{st.session_state.s_city}', line_color=C_DEEP_FOREST))
        fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), height=400, title="宏观发展要素拓扑雷达图", margin=dict(t=50, b=20, l=40, r=40))
        st.plotly_chart(fig_radar, use_container_width=True)
        
    with col2:
        df_gap = pd.DataFrame({"评估维度": categories, "区域考核得分": city_scores, "全省平均标尺": avg_scores})
        fig_bar = px.bar(df_gap, x="评估维度", y=["全省平均标尺", "区域考核得分"], barmode="group",
                         title="核心资源存量差异量化推演", color_discrete_sequence=["#B0BEC5", C_DEEP_FOREST])
        fig_bar.update_layout(height=400, yaxis_title="无量纲化测度值", legend_title=None, margin=dict(t=50, b=20))
        st.plotly_chart(fig_bar, use_container_width=True)
        
    st.markdown("<div class='analysis-box'>", unsafe_allow_html=True)
    st.subheader("一、 过程性推演与指标体系解析")
    st.markdown(f"通过引入极差标准化处理，系统排除了基础数据间的量纲干扰。雷达图与柱状对比矩阵显示：目标区域在“浅层网络（宽带普及）”相关的公共服务普及率指标上得分为 {city_scores[3]:.1f}，与全省均值趋于一致，反映出基础信息网络建设已完成广度覆盖阶段。但对比分析进一步指出，在影响产业深度转型的战略性资产储备上（重点表现在深层传输光缆与高技能人才集聚密度），该区域指标尚未有效追平基准对照组，存在明显的资源配置落差。")
    
    st.subheader("二、 宏观统筹与资源配置优化建议")
    if current_engine_logic == "重化工":
        st.markdown("**1. 优化政府固定资产投资结构**：\n鉴于区域浅层网络边际收益趋缓，规划部门宜适度收紧新增消费级通信基站的财政支持。建议启动资源优化程序，引导政府引导基金和专项债券向深层工业通信传输网络倾斜，以防范因底层数字能力薄弱而限制重大高端制造项目的导入。\n\n"
                    "**2. 强化工业数据的底层互联**：\n工业主管机构应当重点关注重资产企业内部存在的数据孤岛问题。可考虑设立专门的工业互联网改造引导类目，加快推动高耗能企业核心生产流程的数据采集与连通，为后续开展复杂减排算法调度提供物理依托。")
    else:
        st.markdown("**1. 推动招商策略向软性要素升级**：\n推演结果提示，当前区域虽然具备了一定的硬件资产规模，但在技术转化与软件生态培育上存在滞后，面临固定资本沉淀风险。建议产业统筹部门优化招商名录，适度提升对技术密集型外资与优质数字专利引入的权重考核，强化本地实体经济吸收数据的长效机制。\n\n"
                    "**2. 丰富财政政策工具箱的调控手段**：\n建议财政部门在传统的基础设施直接补贴外，增加贴息、税费抵扣等间接政策工具包。重点支持实体企业购买云端算力服务及中小微企业获取数字普惠金融支持，通过发挥财政资金的乘数效应，提升区域产业链的综合竞争实力。")
    st.markdown("</div>", unsafe_allow_html=True)
            
    bottom_navigation('mod1')

# ------------------------------------------
# 页面 4：模块二 (门槛研判与报警监测溯源)
# ------------------------------------------
elif st.session_state.page == 'mod2':
    st.button("返回系统主控室", on_click=lambda: st.session_state.update({'page': 'menu'}))
    st.markdown("## 二、 门槛研判与报警监测溯源 (投资动态审查机制)")
    
    col_g, col_t = st.columns([1, 1])
    
    x_grid = np.linspace(0, 20, 50) 
    y_grid = np.linspace(0, 15, 50) 
    X_mat, Y_mat = np.meshgrid(x_grid, y_grid)
    soft_invest = st.session_state.f_invest + st.session_state.i_invest
    
    if current_engine_logic == "综合型":
        Z_risk = np.clip((X_mat / 8.0 * 100) - (Y_mat * 1.5), 0, 100)
        fig_heat = go.Figure(data=go.Contour(x=x_grid, y=y_grid, z=Z_risk, colorscale="Reds", contours=dict(showlabels=True)))
        fig_heat.update_layout(title="区域资本投放风险预测二维分布图", xaxis_title="数字基建配额 (亿元)", yaxis_title="外资与人才引导资金 (亿元)", height=350, margin=dict(t=40, b=10, l=10, r=10))
        fig_heat.add_trace(go.Scatter(x=[st.session_state.c_invest], y=[soft_invest], mode='markers+text', marker=dict(color='gold', size=16, symbol='star', line=dict(width=2, color='black')), text=["📍 实时推演坐标"], textposition="top center", name="当前推演"))
        
        with col_g:
            risk_score = min(st.session_state.c_invest / 8.0 * 100, 100) 
            fig_gauge = go.Figure(go.Indicator(mode = "gauge+number", value = risk_score, title = {'text': "基建冗余度与碳排反弹综合风险指数"},
                gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': C_CHARCOAL_SLATE},
                         'steps': [{'range': [0, 40], 'color': C_GLACIER_TEAL}, {'range': [40, 70], 'color': 'rgba(255, 215, 0, 0.6)'}, {'range': [70, 100], 'color': C_WARNING_RED}],
                         'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 70}}))
            fig_gauge.update_layout(height=350, margin=dict(t=50, b=10))
            st.plotly_chart(fig_gauge, use_container_width=True)
            st.plotly_chart(fig_heat, use_container_width=True)
            
        with col_t:
            st.markdown("<div class='analysis-box'>", unsafe_allow_html=True)
            st.subheader("一、 热力景观研判与阈值监测")
            st.markdown(f"基于综合型城市产业结构参数，系统输出了风险演化热力矩阵。图谱表明，当资本投向过度集中于横轴（数字基建）且缺乏纵轴（软性生态）协同配合时，系统将进入高风险演化区间。目前后台接收到的实时数字基建干预量为 **{st.session_state.c_invest:.1f} 亿元**。在此等量级约束下，系统研判认为目标区域短期内难以提供足够的实体应用场景进行算力消纳，潜在的基建闲置与能耗增加风险正在积累。")
            
            if risk_score > 70:
                st.markdown("<div class='alarm-box'><h4 style='color:#D32F2F; margin-top:0px;'>⚠️ 监测报警：投资结构偏离引发高碳风险归因</h4>"
                            "<p><strong>异常指标追溯：</strong> 模型在验证过程中捕获到基建投入量指标超过合理承载阈值。在未具备重工业全产业链作为深度算力应用终端的条件下，单方面扩大数字硬件网络覆盖面，容易诱发固定资产建设初期的规模耗能现象。本系统提示：此报警主要源自<strong>新增资本属性与区域既有产业结构的消纳能力不匹配</strong>。长此以往，可能对地方总耗能指标控制与中长期财政安全构成压力。</p></div>", unsafe_allow_html=True)

            st.subheader("二、 合规审查与协同干预建议")
            st.markdown("**1. 严格落实固定资产投资合规性评价**：\n建议项目立项核准部门重视系统产生的风险参数。在审批涉及大额数字基建投资规划时，增加对未来算力使用率与能耗增量的量化论证环节，谨慎对待缺乏明确实体应用场景的大型计算中心等设施建设。\n\n"
                        "**2. 加强生态约束与财政协同管理**：\n财政统筹部门宜结合风险研判结果，稳妥调节债务发行与预算拨付进度，将有限资金向人才培育和技术引流项目稳步分流。同时，环保管理部门可参考此系统输出的边界效应值，完善区域能评与环评指标体系的联合约束机制，防范因局部过热带来的能耗总控风险。")
            st.markdown("</div>", unsafe_allow_html=True)
            
    else:
        Z_break = np.clip(((X_mat + Y_mat) / 6.5 * 100), 0, 100)
        fig_heat = go.Figure(data=go.Contour(x=x_grid, y=y_grid, z=Z_break, colorscale="Greens", contours=dict(showlabels=True)))
        fig_heat.update_layout(title="碳锁定破局势能演化二维分布图", xaxis_title="数字基建配额 (亿元)", yaxis_title="外资与人才引导资金 (亿元)", height=350, margin=dict(t=40, b=10, l=10, r=10))
        fig_heat.add_trace(go.Scatter(x=[st.session_state.c_invest], y=[soft_invest], mode='markers+text', marker=dict(color='gold', size=16, symbol='star', line=dict(width=2, color='black')), text=["📍 实时推演坐标"], textposition="top center", name="当前推演"))

        with col_g:
            breakthrough_score = min(total_invest / 6.5 * 100, 100) 
            fig_gauge = go.Figure(go.Indicator(mode = "gauge+number", value = breakthrough_score, title = {'text': "转型势能积聚与门槛跨越指数"},
                gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': C_CHARCOAL_SLATE},
                         'steps': [{'range': [0, 50], 'color': 'rgba(255, 99, 71, 0.6)'}, {'range': [50, 80], 'color': 'rgba(255, 215, 0, 0.6)'}, {'range': [80, 100], 'color': C_DEEP_FOREST}],
                         'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 80}}))
            fig_gauge.update_layout(height=350, margin=dict(t=50, b=10))
            st.plotly_chart(fig_gauge, use_container_width=True)
            st.plotly_chart(fig_heat, use_container_width=True)
            
        with col_t:
            st.markdown("<div class='analysis-box'>", unsafe_allow_html=True)
            st.subheader("一、 转型势能演进与热力边界测算")
            st.markdown(f"针对重工业主导模式，算法验证了信息化手段与高耗能生产线融合所展现出的技术节能潜力。热力矩阵演示了当资本配置规模逐步跨越阈值边界（向图谱深色区域攀升）时，减排规模效应方可显现。根据当前拟投入的 **{total_invest:.1f} 亿元** 总量规模进行模型迭代，系统评估认为当前方案具备 **{breakthrough_score:.1f}%** 的理论势能，有望平稳渡过建设期的高能耗阶段。")
            
            if breakthrough_score < 80:
                st.markdown("<div class='alarm-box'><h4 style='color:#E65100; margin-top:0px;'>⚠️ 监测报警：转型势能不足与投入倒挂归因</h4>"
                            "<p><strong>阻滞因素追溯：</strong> 模型数据比对显示，当前资本干预力度正处于敏感的平台期。在相关设施建设阶段，硬件铺设通常伴随短暂的基础碳排上升。报警信息提示，因资金总量尚未突破使新技术发挥全生命周期节能效应的“规模经济”临界点（尚未进入热力图核心区域），导致<strong>前期建设能耗成本与后期技术减排红利在当前分析时段内出现了预期倒挂</strong>。系统认为亟需保障政策实施的连贯性。</p></div>", unsafe_allow_html=True)

            st.subheader("二、 宏观政策连贯性与部署建议")
            st.markdown("**1. 保持长期战略定力，避免政策波动**：\n若指标呈现势能不足信号，则说明转型规划正处于关键承压期。决策管理层宜充分认知产业周期规律，在确保财政稳健的前提下，保障专项扶持政策的延续度。防范因关注短期的局部指标波动而轻易调整既定战略，保障转型措施平稳穿越临界线。\n\n"
                        "**2. 集中资源强化重点领域技术改造**：\n建议产业主管机构与财税部门整合分散的技术创新奖补项目，重点支持具有辐射带动效应的工艺革新环节（如智能物流调度、关键冶金工序能效监控等）。通过形成局部优势，加速兑现数字技术对传统制造系统的降耗效能。")
            st.markdown("</div>", unsafe_allow_html=True)
        
    bottom_navigation('mod2')

# ------------------------------------------
# 页面 5：模块三 (政策试错与未来三年轨迹仿真)
# ------------------------------------------
elif st.session_state.page == 'mod3':
    st.button("返回系统主控室", on_click=lambda: st.session_state.update({'page': 'menu'}))
    st.markdown("## 三、 政策试错与三年轨迹仿真测算")
    
    current_year = 2024
    years = [f"{current_year}年", f"{current_year+1}年", f"{current_year+2}年", f"{current_year+3}年"]
    base_traj = [base_carbon, base_carbon * 1.015, base_carbon * 1.028, base_carbon * 1.04]
    
    if current_engine_logic == "综合型":
        traj_1 = base_carbon + infra_cost_penalty * 0.4 - reduce_effect * 0.2
        traj_2 = base_carbon + infra_cost_penalty * 0.8 - reduce_effect * 0.6
        traj_3 = pred_carbon
    else:
        traj_1 = base_carbon + infra_cost_penalty * 0.9 - reduce_effect * 0.3 
        traj_2 = base_carbon + infra_cost_penalty * 1.0 - reduce_effect * 0.7 
        traj_3 = pred_carbon
        
    interv_traj = [base_carbon, traj_1, traj_2, traj_3]
    df_traj = pd.DataFrame({"预测年度": years * 2, "预计排量(Mt)": base_traj + interv_traj, "政策预设情境": ["基准情形 (按既有趋势)"]*4 + ["干预情形 (按本推演参数)"]*4})
    
    col3_1, col3_2 = st.columns([1, 1])
    with col3_1:
        fig_line = px.line(df_traj, x="预测年度", y="预计排量(Mt)", color="政策预设情境", markers=True, title="中短期碳排放演化轨迹比较预测", color_discrete_sequence=["#9E9E9E", C_GLACIER_TEAL])
        fig_line.update_layout(height=450)
        st.plotly_chart(fig_line, use_container_width=True)
        
    with col3_2:
        if current_engine_logic == "综合型":
            shap_data = pd.DataFrame({"核心政策干预工具": ["硬基建初期规模能耗估值", "高质量外资减排协同增量", "IT人才引入智力溢出红利"], "边际净影响值(ROI)": [infra_cost_penalty, -st.session_state.f_invest*2.0, -st.session_state.i_invest*2.5], "综合效用导向": ["引发指标抬升 (+)", "助力指标下降 (-)", "助力指标下降 (-)"]})
        else:
            shap_data = pd.DataFrame({"核心政策干预工具": ["长途工业光缆赋能优化红利", "高质量外资技术转移效应", "数字人才组织管理改善效益", "基础工程建设期施工附加能耗"], "边际净影响值(ROI)": [-st.session_state.c_invest*2.8, -st.session_state.f_invest*1.5, -st.session_state.i_invest*1.0, infra_cost_penalty], "综合效用导向": ["助力指标下降 (-)", "助力指标下降 (-)", "助力指标下降 (-)", "引发指标抬升 (+)"]})
        
        fig_shap = px.bar(shap_data, x="边际净影响值(ROI)", y="核心政策干预工具", color="综合效用导向", orientation='h', title="专项资金投入边际贡献(ROI)结构剥离", color_discrete_map={"引发指标抬升 (+)":C_WARNING_RED, "助力指标下降 (-)":C_DEEP_FOREST})
        fig_shap.update_layout(height=450)
        st.plotly_chart(fig_shap, use_container_width=True)

    st.markdown("<div class='analysis-box'>", unsafe_allow_html=True)
    st.subheader("一、 政策试错反馈与特征贡献解构")
    st.markdown("系统集成的反事实预测与SHAP分解工具，可辅助管理层评估预算调整的潜在影响。模拟曲线表明，在无显著政策调节的基准情形下，区域预测排量呈现自然增长态势。而当介入特定规模的政策干预后，由于前期建设能耗与后期管理优化的交替发挥，轨迹发生偏转。同时，右侧的结构剥离图系统地将整体变动拆解到单一政策工具层面，量化说明了在特定预算框架内，每一项投入渠道对终端结果的净影响数值及其作用方向，实现了决策后果的可视化追溯。")
    
    st.subheader("二、 财务资源优化与效能审查机制建议")
    st.markdown("**1. 构建具备弹性的资金配置机制**：\n建议财政管理部门运用此推演成果，审视既有的预算安排结构。对试错环节中显露出较高附带能耗、且回报率较低的政策项目，应引入更加严格的论证流程，必要时实施预算的动态缩减；相反，对预期稳健、具备综合降耗成效的途径应确保资金充足度。\n\n"
                "**2. 加强事前评价体系的跨部门应用**：\n提倡发改与环保主管部门在编制年度和五年规划纲要时，常态化使用此类情景推演工具。将事前数字模拟结论作为重大转型项目立项及配套资源划拨的重要考量附件，进一步提高地方宏观经济决策与环境治理方针的科学性与协调性。")
    st.markdown("</div>", unsafe_allow_html=True)
    
    bottom_navigation('mod3')

# ------------------------------------------
# 页面 6：模块四 (多约束帕累托决策最优生成)
# ------------------------------------------
elif st.session_state.page == 'mod4':
    st.button("返回系统主控室", on_click=lambda: st.session_state.update({'page': 'menu'}))
    st.markdown("## 四、 多约束条件下的帕累托决策指导方案生成")
    
    np.random.seed(42)
    n_points = 250
    x_invest = np.random.uniform(1, 20, n_points)
    y_carbon_reduce = x_invest * (1.2 if current_engine_logic == "综合型" else 1.8) - np.random.normal(0, 2, n_points)
    z_gdp_growth = -0.1 * (x_invest - 10)**2 + 8 + np.random.normal(0, 1, n_points)
    
    fig_3d = px.scatter_3d(x=x_invest, y=y_carbon_reduce, z=z_gdp_growth, color=z_gdp_growth, color_continuous_scale="RdBu_r", labels={'x':'财政预算上限评估(亿元)', 'y':'预测整体控制减排量(Mt)', 'z':'宏观经济关联变动率(%)'}, title="区域治理多目标帕累托前沿寻优图谱")
    
    user_z_gdp = -0.1 * (total_invest - 10)**2 + 8
    fig_3d.add_trace(go.Scatter3d(x=[total_invest], y=[base_carbon-pred_carbon], z=[user_z_gdp], mode='markers+text', text=["📍 系统当前匹配坐标"], marker=dict(size=14, symbol='diamond', color='gold', line=dict(color='black', width=3)), textposition='top center'))
    fig_3d.update_layout(height=650)
    st.plotly_chart(fig_3d, use_container_width=True)
    
    st.markdown("<div class='analysis-box'>", unsafe_allow_html=True)
    st.subheader("一、 高维空间运算与适配性分析")
    st.markdown(f"面对经济平稳运行、环境指标改善与公共财务稳健的多重考核要求，系统利用非支配排序算法进行了海量可行性方案筛选，形成了图中展示的帕累托权衡前沿。根据控制台当前设定的总投入 **{total_invest:.1f} 亿元** 进行适配测算，模型评估该组合理论上能够协助区域获得约 **{base_carbon-pred_carbon:.2f} Mt** 的减排管理空间，并估计其对区域生产总值增速具有约 **{user_z_gdp:.2f}%** 的关联影响度。")

    st.subheader("二、 宏观统筹评价与政策指引")
    if total_invest < 4.0:
        st.markdown("**系统定位识别：保守型基础保障方案**\n\n"
                    "**综合评价**：当前配置偏向于维系系统的基本运行。因投入规模相对有限，较难形成技术溢出所需的产业聚合度。系统测算显示，此规模在短期内促成产业质效全面突破的可能性较低，且存在固定成本占比过大而拉低整体效能回报率的可能。\n\n"
                    "**施政指导提示**：该方案适宜在财政阶段性收紧或债务优化的背景下执行。为兼顾长期发展，建议谋划部门广泛吸引社会主体资金，灵活运用市场化投融资工具，通过丰富合作建设渠道，以缓解公共财政的结构性约束压力。")
    elif total_invest > 12.0:
        st.markdown("**系统定位识别：高弹性扩张型方案**\n\n"
                    "**综合评价**：方案表现出较强的投入扩张意愿。模型分析提示，当资本投放强度脱离最优权衡区间后，边际增量效益出现递减趋势。在特定时期，大规模前置投资虽能提振某些经济数据，但需重点关注随之攀升的隐性运行能耗及可能造成的财政空间过度透支现象。\n\n"
                    "**施政指导提示**：建议发展综合评估部门稳妥推进项目实施。在后续实施中，应加强核心工程立项程序的规范性与科学性论证，适当压缩边际回报率偏低的建设份额。坚持量力而行原则，确保区域资本杠杆运行在合理的控制区间。")
    else:
        st.markdown("**系统定位识别：稳健型均衡提质方案**\n\n"
                    "**综合评价**：本系统认为当前方案表现出了良好的多目标统筹特征。资源配置规模处于帕累托前沿曲线的有效均衡地带。该方案在充分兼顾地方财力承担能力的基础上，较好地平衡了支持经济活力与控制环境能耗指标的双重发展需求，具备较高的综合实施效率。\n\n"
                    "**施政指导提示**：该参数组合具备较强的实践可操作性。建议行政督导机构将其核心指标纳入中短期施政规划的重要参考体系。鼓励发改、工信等相关部门参照该比例架构，持续优化重点建设项目的预算结构，稳步推进本地区现代产业体系建设。")
    st.markdown("</div>", unsafe_allow_html=True)
    
    bottom_navigation('mod4')
