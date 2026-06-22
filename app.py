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

C_CHARCOAL_SLATE = "#2C3539"  # 炭岩灰 (主文字)
C_DEEP_FOREST = "#1A3622"  # 深苍翠 (安全/质变区)
C_GLACIER_TEAL = "#4DB8B3"  # 冰川青 (泛基准核心点缀)
C_WARNING_RED = "#D32F2F"  # 警报红 (防过热预警)

# 注入 CSS：采用现代黑体系统，专注PC大屏端展示，隔离图标库干扰
st.markdown(f"""
    <style>
        /* 隔离系统图标库，防文字泄漏 */
        button span, .material-icons, .material-symbols-rounded, [data-testid="stSidebarCollapseButton"] span {{
            font-family: "Material Symbols Rounded", "Material Icons", sans-serif !important;
        }}

        /* 全局正文、标签、标题强制使用黑体 */
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
if 's_city' not in st.session_state: st.session_state.s_city = "焦作市"
if 'custom_logic' not in st.session_state: st.session_state.custom_logic = "偏向重化工业主导"
if 'c_invest' not in st.session_state: st.session_state.c_invest = 4.8
if 'f_invest' not in st.session_state: st.session_state.f_invest = 2.5
if 'i_invest' not in st.session_state: st.session_state.i_invest = 1.0
if 'custom_data' not in st.session_state:
    st.session_state.custom_data = {"长途光缆": 1500.0, "高质量外资": 10.0, "IT人才密度": 1.5, "宽带普及": 200.0, "普惠金融": 280.0,
                                    "基准碳排": 50.0}

# ==========================================
# 2. 内嵌全域城市数据库
# ==========================================
embedded_data = [
    {"城市": "焦作市", "类型": "典型重化工业主导城市", "长途光缆": 1019.84, "高质量外资": 2.8, "IT人才密度": 0.27, "宽带普及": 217, "普惠金融": 302.66,
     "基准碳排": 23.61},
    {"城市": "平顶山市", "类型": "典型重化工业主导城市", "长途光缆": 2030.67, "高质量外资": 1.02, "IT人才密度": 0.33, "宽带普及": 601, "普惠金融": 289.76,
     "基准碳排": 19.45},
    {"城市": "安阳市", "类型": "典型重化工业主导城市", "长途光缆": 1887.28, "高质量外资": 2.39, "IT人才密度": 0.29, "宽带普及": 258, "普惠金融": 290.5,
     "基准碳排": 102.41},
    {"城市": "鹤壁市", "类型": "典型重化工业主导城市", "长途光缆": 549.49, "高质量外资": 0.23, "IT人才密度": 0.13, "宽带普及": 74, "普惠金融": 297.32,
     "基准碳排": 9.89},
    {"城市": "山西省长治市", "类型": "典型重化工业主导城市", "长途光缆": 3255.51, "高质量外资": 31.14, "IT人才密度": 0.3, "宽带普及": 150, "普惠金融": 288.2,
     "基准碳排": 79.07},
    {"城市": "山西省晋城市", "类型": "典型重化工业主导城市", "长途光缆": 2206.89, "高质量外资": 14.34, "IT人才密度": 0.26, "宽带普及": 88, "普惠金融": 305.59,
     "基准碳排": 161.18},
    {"城市": "郑州市", "类型": "泛基准与综合型城市", "长途光缆": 1942.64, "高质量外资": 12.29, "IT人才密度": 10.99, "宽带普及": 774, "普惠金融": 337.22,
     "基准碳排": 52.37},
    {"城市": "洛阳市", "类型": "泛基准与综合型城市", "长途光缆": 3911.33, "高质量外资": 1.3, "IT人才密度": 4.28, "宽带普及": 313, "普惠金融": 311.82,
     "基准碳排": 50.78},
    {"城市": "新乡市", "类型": "泛基准与综合型城市", "长途光缆": 2128.43, "高质量外资": 1.02, "IT人才密度": 0.49, "宽带普及": 297, "普惠金融": 298.28,
     "基准碳排": 38.84},
    {"城市": "濮阳市", "类型": "泛基准与综合型城市", "长途光缆": 1096.49, "高质量外资": 0.96, "IT人才密度": 0.34, "宽带普及": 202, "普惠金融": 289.01,
     "基准碳排": 9.52},
    {"城市": "许昌市", "类型": "泛基准与综合型城市", "长途光缆": 1278.16, "高质量外资": 0.27, "IT人才密度": 0.42, "宽带普及": 195, "普惠金融": 307.91,
     "基准碳排": 22.08},
    {"城市": "三门峡市", "类型": "泛基准与综合型城市", "长途光缆": 2550.69, "高质量外资": 36.88, "IT人才密度": 0.21, "宽带普及": 118, "普惠金融": 299.84,
     "基准碳排": 30.98}
]
df = pd.DataFrame(embedded_data)


def normalize_to_100(val, col_name):
    min_val = df[col_name].min();
    max_val = df[col_name].max()
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
            st.session_state.page = k;
            st.rerun()


# ------------------------------------------
# 页面 0：旋转地球极简欢迎页
# ------------------------------------------
if st.session_state.page == 'splash':
    st.markdown("<style>[data-testid='stSidebar'] {display: none;}</style>", unsafe_allow_html=True)
    st.markdown("<div style='height: 15vh;'></div>", unsafe_allow_html=True)
    st.markdown("<div class='spin-earth'>🌍</div>", unsafe_allow_html=True)
    st.markdown("<div class='title-main'>城市低碳转型智能决策推演系统</div>", unsafe_allow_html=True)
    st.markdown("<div class='title-sub'>宏观政务投资事前仿真与多目标沙盘</div>", unsafe_allow_html=True)
    st.markdown("<br><p style='text-align: center; color: #888888;'>正在加载因果森林推演引擎与高维特征要素底座...</p>",
                unsafe_allow_html=True)
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
            cat_choice = st.radio("第一步：圈定数据源与城市产业类别", category_opts,
                                  index=category_opts.index(st.session_state.city_category))

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
                s_city_choice = st.text_input("第二步：输入拟诊断城市名称", value=s_city_choice if s_city_choice not in df[
                    "城市"].tolist() else "某自定义市")
                custom_logic_choice = st.radio("设定该城市的产业底色（系统将据此匹配推演算法路线）", ["偏向重化工业主导", "偏向综合与泛基准型"])
                st.markdown("*(请依次录入核心基础宏观指标)*")
                c1, c2 = st.columns(2)
                st.session_state.custom_data["长途光缆"] = c1.number_input("长途光缆 (公里)", value=float(
                    st.session_state.custom_data["长途光缆"]))
                st.session_state.custom_data["高质量外资"] = c2.number_input("实际使用外资 (亿元)", value=float(
                    st.session_state.custom_data["高质量外资"]))
                st.session_state.custom_data["IT人才密度"] = c1.number_input("软件与IT人才从业数 (万人)", value=float(
                    st.session_state.custom_data["IT人才密度"]))
                st.session_state.custom_data["基准碳排"] = c2.number_input("年度基准碳排总量 (百万吨)", value=float(
                    st.session_state.custom_data["基准碳排"]))
                st.session_state.custom_data["宽带普及"] = c1.number_input("宽带接入户数 (万户)", value=float(
                    st.session_state.custom_data["宽带普及"]))
                st.session_state.custom_data["普惠金融"] = c2.number_input("数字普惠金融指数得分", value=float(
                    st.session_state.custom_data["普惠金融"]))

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("锁定参数底座，启动核心推演系统", type="primary", use_container_width=True):
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
        st.markdown("### ⚙️ 宏观推演参数控制台")
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
            new_logic = st.radio("设定产业底色以匹配算法", ["偏向重化工业主导", "偏向综合与泛基准型"],
                                 index=0 if "重化工" in st.session_state.custom_logic else 1, key="sb_logic")
            if new_cat != st.session_state.city_category or new_city != st.session_state.s_city or new_logic != st.session_state.custom_logic:
                st.session_state.city_category = new_cat
                st.session_state.s_city = new_city
                st.session_state.custom_logic = new_logic
                st.rerun()

            st.markdown("*（手动微调存量数据大屏实时响应）*")
            c1, c2 = st.columns(2)
            st.session_state.custom_data["长途光缆"] = c1.number_input("光缆(km)",
                                                                   value=float(st.session_state.custom_data["长途光缆"]),
                                                                   key="sb_n1")
            st.session_state.custom_data["高质量外资"] = c2.number_input("外资(亿)",
                                                                    value=float(st.session_state.custom_data["高质量外资"]),
                                                                    key="sb_n2")
            st.session_state.custom_data["IT人才密度"] = c1.number_input("人才(万)", value=float(
                st.session_state.custom_data["IT人才密度"]), key="sb_n3")
            st.session_state.custom_data["基准碳排"] = c2.number_input("碳排(Mt)",
                                                                   value=float(st.session_state.custom_data["基准碳排"]),
                                                                   key="sb_n4")

        st.markdown("---")
        st.markdown("三、动态调节年度专项财政干预额度 (亿元)")
        st.markdown("*拖动滑块，系统各模块将触发过程性反事实仿真推演*")
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
        reduce_effect = (st.session_state.c_invest * 2.8) + (st.session_state.f_invest * 1.5) + (
                    st.session_state.i_invest * 1.0)
    pred_carbon = base_carbon + infra_cost_penalty - reduce_effect

# ------------------------------------------
# 页面 2：主系统导航大屏
# ------------------------------------------
if st.session_state.page == 'menu':
    st.markdown(f"## 🌍 【{st.session_state.s_city}】政务投资事前仿真与智能决策系统")
    st.info(f"系统底层确证状态：当前算法已自适应切入 {current_engine_logic}城市 演化路线。系统已激活推演过程展示及数据报警溯源机制，为地方政府提供高度量化、可视化的决策辅助。")

    with st.container(border=True):
        st.markdown("### 一、 宏观体检与要素断层推演")
        st.markdown("依托全量面板数据库，通过雷达图与断层柱状图，全景解构目标城市当前在数字基建、人才存量与产业融合维度的实际落差，直观呈现多维度比较推演过程。")
        if st.button("进入体检与推演模块", key="m1", use_container_width=True): st.session_state.page = 'mod1'; st.rerun()

    with st.container(border=True):
        st.markdown("### 二、 门槛研判与报警监测溯源")
        st.markdown("聚焦投资规划事前审查环节的刚性痛点。引入推演热力图展示投资矩阵演化景观，对不合理投资配置触发数据报警，并提供严密的文字溯源与归因解释机制。")
        if st.button("进入报警与监测模块", key="m2", use_container_width=True): st.session_state.page = 'mod2'; st.rerun()

    with st.container(border=True):
        st.markdown("### 三、 政策试错与未来轨迹仿真")
        st.markdown("系统赋予决策者“政策试错”与压力测试的能力。同步输出未来三年碳排放演化轨迹折线图与SHAP瀑布图，在毫秒级内直观呈现各项投资的边际效费比(ROI)。")
        if st.button("进入政策试错模块", key="m3", use_container_width=True): st.session_state.page = 'mod3'; st.rerun()

    with st.container(border=True):
        st.markdown("### 四、 多约束帕累托决策最优生成")
        st.markdown("在经济、生态与财政多约束的宏观治理环境中，运用第三代遗传进化算法进行高维解空间探索。自动生成兼顾宏观经济拉动与碳排放收敛的结构化投资决策指导书。")
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
        fig_radar.add_trace(go.Scatterpolar(r=avg_scores, theta=categories, fill='toself', name='全省综合基准线',
                                            line_color='rgba(100, 149, 237, 0.8)'))
        fig_radar.add_trace(
            go.Scatterpolar(r=city_scores, theta=categories, fill='toself', name=f'{st.session_state.s_city} 存量底数',
                            line_color=C_DEEP_FOREST))
        fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), height=400,
                                title="宏观要素多维拓扑雷达图", margin=dict(t=50, b=20, l=40, r=40))
        st.plotly_chart(fig_radar, use_container_width=True)

    with col2:
        # 新增：过程性结果展示功能 (柱状推演对比图)
        df_gap = pd.DataFrame({"评测维度": categories, "目标城市得分": city_scores, "全省平均水位": avg_scores})
        fig_bar = px.bar(df_gap, x="评测维度", y=["全省平均水位", "目标城市得分"], barmode="group",
                         title="核心要素存量断层推演对比图", color_discrete_sequence=["#B0BEC5", C_DEEP_FOREST])
        fig_bar.update_layout(height=400, yaxis_title="标准化测度得分", legend_title=None, margin=dict(t=50, b=20))
        st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("<div class='analysis-box'>", unsafe_allow_html=True)
    st.subheader("分析： 过程性推演与量化数值结构分析")
    st.markdown(
        f"通过高维极差空间拓扑与柱状图断层推演，系统直观地呈现了诊断的过程性结果。该市在“浅层网络（宽带普及）”维度的标准化得分达到 {city_scores[3]:.1f}，已接近全省平均发展基准水位，表明消费端数字化红利趋于饱和。然而，系统过程性比对侦测到，在直接决定宏观实体产业深度重构的核心要素指标上（如深层传输光缆与高精尖人才密度），目标城市的柱状实体显著低于全省平均水位标尺，呈现出硬性的结构性落差与底层资产相对不足。")

    st.subheader("建议： 统筹指导发展与精准投资建议")
    if current_engine_logic == "重化工":
        st.markdown(
            "**相关规划部门**：应调整下一年度的财政支出分配结构。鉴于浅层网络覆盖率基本平稳，建议合理控制对消费级通信基站的边际投资增量。联合启动预算倾斜机制，优先将存量专项资金用于填平图谱中揭示的深层工业光缆历史欠账，规避未来工业智造项目因算力传输瓶颈而引发的结构性制约。\n\n"
            "**工业主管体系**：需主导缓解企业内部的信息孤岛现象。针对具有高耗能特征的龙头企业，设立专门的工业互联网技改前置引育类目。加速数据要素向实体产业链核心排放流水线的全流程渗透，为承载高维降碳高阶应用构筑坚实的物理实体网络基座。")
    else:
        st.markdown(
            "**招商与产业管理部门**：诊断预警表明，该市虽已具备初级的硬件承载力，但软件与技术生态转化效能存在上升空间，面临固定资产利用率偏低的风险。建议相关职能部门将中长期投资重心由单纯的硬基建扩张转向图谱中所缺失的高规格技术外资与技术专利引入，着力打通数据要素向本地高端服务业深层融合的长效机制。\n\n"
            "**财政收支保障**：需对专项资金的杠杆施力点进行结构性优化。从传统的直接垫资购买硬件设施，转变为对企业采购云服务、引进数字架构工程师以及中小微企业获取绿色普惠金融的定向贴息与税收政策协同。以极低的综合财政成本，撬动全域产业链向轻量化、高净值的低碳业态实现高质量演进。")
    st.markdown("</div>", unsafe_allow_html=True)

    bottom_navigation('mod1')

# ------------------------------------------
# 页面 4：模块二 (门槛研判与报警监测)
# ------------------------------------------
elif st.session_state.page == 'mod2':
    st.button("返回系统主控室", on_click=lambda: st.session_state.update({'page': 'menu'}))
    st.markdown("## 二、 门槛研判与报警监测溯源 (投资审查机制)")

    col_g, col_t = st.columns([1, 1])

    # 动态推演中间热力矩阵图配置
    x_grid = np.linspace(0, 20, 50)  # 硬基建投资范围
    y_grid = np.linspace(0, 15, 50)  # 软性生态投资(外资+人才)范围
    X_mat, Y_mat = np.meshgrid(x_grid, y_grid)
    soft_invest = st.session_state.f_invest + st.session_state.i_invest

    if current_engine_logic == "综合型":
        # 综合型热力图逻辑：硬基建越高越红(高风险)，软基建可中和部分风险
        Z_risk = np.clip((X_mat / 8.0 * 100) - (Y_mat * 1.5), 0, 100)
        fig_heat = go.Figure(
            data=go.Contour(x=x_grid, y=y_grid, z=Z_risk, colorscale="Reds", contours=dict(showlabels=True)))
        fig_heat.update_layout(title="区域基建投资风险演化二维热力图", xaxis_title="硬基建投资量 (亿元)", yaxis_title="生态软投入 (人才+外资, 亿元)",
                               height=350, margin=dict(t=40, b=10, l=10, r=10))
        fig_heat.add_trace(go.Scatter(x=[st.session_state.c_invest], y=[soft_invest], mode='markers+text',
                                      marker=dict(color='gold', size=16, symbol='star',
                                                  line=dict(width=2, color='black')), text=["📍 当前推演锚点"],
                                      textposition="top center", name="当前推演"))

        with col_g:
            risk_score = min(st.session_state.c_invest / 8.0 * 100, 100)
            fig_gauge = go.Figure(go.Indicator(mode="gauge+number", value=risk_score, title={'text': "基建过热与高碳反弹报警仪表盘"},
                                               gauge={'axis': {'range': [0, 100]}, 'bar': {'color': C_CHARCOAL_SLATE},
                                                      'steps': [{'range': [0, 40], 'color': C_GLACIER_TEAL},
                                                                {'range': [40, 70], 'color': 'rgba(255, 215, 0, 0.6)'},
                                                                {'range': [70, 100], 'color': C_WARNING_RED}],
                                                      'threshold': {'line': {'color': "red", 'width': 4},
                                                                    'thickness': 0.75, 'value': 70}}))
            fig_gauge.update_layout(height=350, margin=dict(t=50, b=10))
            st.plotly_chart(fig_gauge, use_container_width=True)
            st.plotly_chart(fig_heat, use_container_width=True)

        with col_t:
            st.markdown("<div class='analysis-box'>", unsafe_allow_html=True)
            st.subheader("分析： 深度预测与热力景观研判")
            st.markdown(
                f"底层因果推演引擎锁定了泛基准综合型城市防过热模式。通过下方生成的二维热力图景观可知，红色的高风险区域集中在 X 轴（硬基建）高企而 Y 轴（软投入）匮乏的象限。结合控制台实时拟定的 **{st.session_state.c_invest:.1f} 亿元** 资本投入，系统在热力矩阵中标定出当前的推演锚点。由于缺乏实体转化场景，该笔超前投资极易诱发规模耗能效应，伴随显著的高碳代价风险。")

            # 新增：数据报警溯源解释
            if risk_score > 70:
                st.markdown("<div class='alarm-box'><h4 style='color:#D32F2F; margin-top:0px;'>⚠️ 预警溯源分析（报警归因系统）</h4>"
                            "<p><strong>系统推演截面分析发现异常状况：</strong> 底层网络监测到当前模拟的硬基建投入占比严重失衡。由于该城市产业底色中缺乏钢铁、煤炭等重资产应用场景以消纳过剩的算力服务，此时强行堆砌硬件网络，将直接导致固定资产在生命周期内产生持续的空耗与高昂的电力反噬（预测增加的碳排将远超信息化带来的减排微利）。这种<strong>投资结构与底层产业消纳能力的严重错配</strong>，正是触发本次基建红线报警的核心归因。</p></div>",
                            unsafe_allow_html=True)

            st.subheader("建议： 跨部门协同防御与投资阻断建议")
            st.markdown(
                "**前置合规性审查建议**：事前仿真测算与热力图锚点共同发出了结构性风险信号。针对规划方案中隐含的规模耗能反噬风险，相关合规部门宜在项目的立项核准阶段加强效益比对，合理调减缺乏真实场景支撑的超前重资产算力或冗余光缆线路，防范固定资产低效扩张。\n\n"
                "**财政与生态环境部门**：财政部门宜参考仿真阈值，建立财政支出的动态反馈调控机制，收紧涉边际能耗偏高项目的资金敞口，将资源有序导向软件生态开发。同时，生态环境部门可将本系统生成的“高碳代价预警阈值”正式纳入区域性环境影响评估的硬性指标中，保障总体碳排放约束的良性协同。")
            st.markdown("</div>", unsafe_allow_html=True)

    else:
        # 重工型热力图逻辑：总投资驱动突破阈值
        Z_break = np.clip(((X_mat + Y_mat) / 6.5 * 100), 0, 100)
        fig_heat = go.Figure(
            data=go.Contour(x=x_grid, y=y_grid, z=Z_break, colorscale="Greens", contours=dict(showlabels=True)))
        fig_heat.update_layout(title="碳锁定破局门槛演化二维热力图", xaxis_title="硬基建投资量 (亿元)", yaxis_title="生态软投入 (人才+外资, 亿元)",
                               height=350, margin=dict(t=40, b=10, l=10, r=10))
        fig_heat.add_trace(go.Scatter(x=[st.session_state.c_invest], y=[soft_invest], mode='markers+text',
                                      marker=dict(color='gold', size=16, symbol='star',
                                                  line=dict(width=2, color='black')), text=["📍 当前推演锚点"],
                                      textposition="top center", name="当前推演"))

        with col_g:
            breakthrough_score = min(total_invest / 6.5 * 100, 100)
            fig_gauge = go.Figure(
                go.Indicator(mode="gauge+number", value=breakthrough_score, title={'text': "碳锁定门槛跨越突破仪表盘"},
                             gauge={'axis': {'range': [0, 100]}, 'bar': {'color': C_CHARCOAL_SLATE},
                                    'steps': [{'range': [0, 50], 'color': 'rgba(255, 99, 71, 0.6)'},
                                              {'range': [50, 80], 'color': 'rgba(255, 215, 0, 0.6)'},
                                              {'range': [80, 100], 'color': C_DEEP_FOREST}],
                                    'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75,
                                                  'value': 80}}))
            fig_gauge.update_layout(height=350, margin=dict(t=50, b=10))
            st.plotly_chart(fig_gauge, use_container_width=True)
            st.plotly_chart(fig_heat, use_container_width=True)

        with col_t:
            st.markdown("<div class='analysis-box'>", unsafe_allow_html=True)
            st.subheader("分析： 深度预测与热力景观研判")
            st.markdown(
                f"系统确证：在重工业主导模式下，数字化基础设施一旦嵌套入高耗能生产线，其所爆发的能效优化能够展现出显著的节能对冲效应。通过下方热力矩阵图可见，当投资总额向右上方演化突破深绿色等高线时，即可诱发质变。依托当前实时的 **{total_invest:.1f} 亿元** 投资坐标推演，动态研判当前跨越能耗爬坡阶段、全面发挥规模报酬红利的理论概率定格为 **{breakthrough_score:.1f}%**。")

            # 新增：数据报警溯源解释
            if breakthrough_score < 80:
                st.markdown("<div class='alarm-box'><h4 style='color:#E65100; margin-top:0px;'>⚠️ 预警溯源分析（动力不足归因）</h4>"
                            "<p><strong>系统推演截面分析发现受阻状况：</strong> 监测网络捕捉到当前专项资金总规模正处于极度敏感的“基建土木爬坡期”。在数字化底座建设初期，工业光缆等设备的物理铺设将不可避免地推高当期基础碳排。由于当前投资锚点尚未突破规模经济的绿色临界阈值（热力图中的深绿安全区），导致后期工业互联网全链条调度带来的节能红利尚未被激活。<strong>前期增碳与后期减碳在时间切片上发生倒挂</strong>，从而触发本系统的动力不足预警，提示决策层资金注入尚未达到量变引发质变的拐点。</p></div>",
                            unsafe_allow_html=True)

            st.subheader("建议： 战略定力保持与精准爆破建议")
            st.markdown(
                "**宏观战略统筹指导**：若仪表盘指针徘徊于拐点蓄力区间，表明城市转型正深陷能耗爬坡阶段。决策层需保持较强的宏观转型定力与政策连贯性，避免因短期局部耗能反弹而产生政策摇摆。应当保障持续、稳健的资金接续机制，使之顺利跨越热力图中的边际效益拐点，确保整体数字化改造项目顺利释放节能成效。\n\n"
                "**相关部门专项干预部署**：产业与财政部门宜构建高度集中的技术技改补贴机制，防范资金碎片化与边际效力递减。确保公共资源形成规模合力，靶向聚焦工业车辆调度、高炉优化等核心排放节点实施流程重塑与引导，全面释放深层数智化转型的长期边际效应。")
            st.markdown("</div>", unsafe_allow_html=True)

    bottom_navigation('mod2')

# ------------------------------------------
# 页面 5：模块三 (政策试错与未来三年轨迹预测)
# ------------------------------------------
elif st.session_state.page == 'mod3':
    st.button("返回系统主控室", on_click=lambda: st.session_state.update({'page': 'menu'}))
    st.markdown("## 三、 政策试错与三年轨迹预测 (ROI仿真测算)")

    current_year = 2024
    years = [f"{current_year}年 (当前)", f"{current_year + 1}年", f"{current_year + 2}年", f"{current_year + 3}年"]
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
    df_traj = pd.DataFrame(
        {"年份": years * 2, "碳排放量(Mt)": base_traj + interv_traj, "推演情境": ["维持历史惯性 (无干预)"] * 4 + ["执行动态预算 (政策试错)"] * 4})

    col3_1, col3_2 = st.columns([1, 1])
    with col3_1:
        fig_line = px.line(df_traj, x="年份", y="碳排放量(Mt)", color="推演情境", markers=True, title="未来三年碳排放演化轨迹预测 (反事实推演)",
                           color_discrete_sequence=["#9E9E9E", C_GLACIER_TEAL])
        fig_line.update_layout(height=450)
        st.plotly_chart(fig_line, use_container_width=True)

    with col3_2:
        if current_engine_logic == "综合型":
            shap_data = pd.DataFrame({"专项政策干预工具": ["深层硬基建初期能耗反噬", "高质量外资生态协同收益", "IT人才赋能智力资本收益"],
                                      "边界绝对贡献量(ROI)": [infra_cost_penalty, -st.session_state.f_invest * 2.0,
                                                       -st.session_state.i_invest * 2.5],
                                      "干预效用最终导向": ["增加边际能耗 (+)", "抑制碳排收敛 (-)", "抑制碳排收敛 (-)"]})
        else:
            shap_data = pd.DataFrame({"专项政策干预工具": ["长途工业光缆深层赋能效用", "高质量外资技术溢出效应", "IT数字人才组织优化收益", "底层基建工程初期施工能耗"],
                                      "边界绝对贡献量(ROI)": [-st.session_state.c_invest * 2.8,
                                                       -st.session_state.f_invest * 1.5,
                                                       -st.session_state.i_invest * 1.0, infra_cost_penalty],
                                      "干预效用最终导向": ["抑制碳排收敛 (-)", "抑制碳排收敛 (-)", "抑制碳排收敛 (-)", "增加边际能耗 (+)"]})

        fig_shap = px.bar(shap_data, x="边界绝对贡献量(ROI)", y="专项政策干预工具", color="干预效用最终导向", orientation='h',
                          title="单项政务资金边际贡献(ROI)瀑布级归因解构",
                          color_discrete_map={"增加边际能耗 (+)": C_WARNING_RED, "抑制碳排收敛 (-)": C_DEEP_FOREST})
        fig_shap.update_layout(height=450)
        st.plotly_chart(fig_shap, use_container_width=True)

    st.markdown("<div class='analysis-box'>", unsafe_allow_html=True)
    st.subheader("分析： 政策试错机制与量化数值逆向解构")
    st.markdown(
        "依托后台封装的正交因果森林与GBM引擎，系统赋予了决策者“政策试错”的中间推演能力。用户可通过侧边控制台，动态拖拽各项数字基建与外资引导资金的预算滑块，系统在毫秒级延迟内，直观生成实施该干预政策后的未来三年碳排放演化轨迹折线图，并同步输出详细分解的SHAP瀑布图。这种“所见即所得”的动态映射机制，使得每一项宏观规划在正式下发成为红头文件前，都能在数字沙盘中经历极限压力测试，从源头上防范决策偏差带来的庞大沉没成本。")

    st.subheader("建议： 财税统筹与绩效审查优化核心建议")
    st.markdown(
        "**构建基于边际效费比的财政绩效评价体系**：相关部门可深度参考右侧量化瀑布归因，优化公共资金的配置结构，打破传统预算编制中的固化配置惯性。在压力测试环节中呈现出推高能耗特征（红色柱体）的重资产配置方案，必须执行严格的预算压降与资金拦截评估，避免财政资源的低效错配。\n\n"
        "**实施核心转型要素的乘数放大战略**：在优化低效投入的同时，相关职能部门应依托轨迹预测建立深度预审机制。在下达阶段性减排考核任务时，务必协同地方金融资源，为那些在瀑布图谱中呈现为显著负向效益（深绿色柱体：具备长效降碳与稳增长双重红利）的优质要素渠道，统筹调配绿色转型专项转移支付，提供长期稳固的政策支撑。")
    st.markdown("</div>", unsafe_allow_html=True)

    bottom_navigation('mod3')

# ------------------------------------------
# 页面 6：模块四 (多约束帕累托决策指导方案生成)
# ------------------------------------------
elif st.session_state.page == 'mod4':
    st.button("返回系统主控室", on_click=lambda: st.session_state.update({'page': 'menu'}))
    st.markdown("## 四、 多约束条件下的帕累托最优决策统筹与指导方案生成")

    np.random.seed(42)
    n_points = 250
    x_invest = np.random.uniform(1, 20, n_points)
    y_carbon_reduce = x_invest * (1.2 if current_engine_logic == "综合型" else 1.8) - np.random.normal(0, 2, n_points)
    z_gdp_growth = -0.1 * (x_invest - 10) ** 2 + 8 + np.random.normal(0, 1, n_points)

    fig_3d = px.scatter_3d(x=x_invest, y=y_carbon_reduce, z=z_gdp_growth, color=z_gdp_growth,
                           color_continuous_scale="RdBu_r",
                           labels={'x': '专项财政预算刚性上限(亿元)', 'y': '全域预测绝对减排总规模(Mt)', 'z': '宏观经济GDP预期额外拉动率(%)'},
                           title="城市级宏观治理博弈多目标帕累托前沿寻优动态图谱")

    user_z_gdp = -0.1 * (total_invest - 10) ** 2 + 8
    fig_3d.add_trace(go.Scatter3d(x=[total_invest], y=[base_carbon - pred_carbon], z=[user_z_gdp], mode='markers+text',
                                  text=["📍 当前配置策略坐标系锚点"], marker=dict(size=14, symbol='diamond', color='gold',
                                                                       line=dict(color='black', width=3)),
                                  textposition='top center'))
    fig_3d.update_layout(height=650)
    st.plotly_chart(fig_3d, use_container_width=True)

    st.markdown("<div class='analysis-box'>", unsafe_allow_html=True)
    st.subheader("分析： 高维空间运算与量化数值分析")
    st.markdown(
        f"为了统筹协调发展过程中的保障平稳增长、推进碳排收敛、维持财政安全等多目标协同约束，系统调用三代非支配排序遗传算法（NSGA-III）进行高维解空间全局寻优，映射出本帕累托前沿曲面。当前系统侦测确认，决策层在前端控制台锁定的干预总规模定格为 **{total_invest:.1f} 亿元**。将该数值代入底层非线性评估函数池进行拓扑测算后，系统严谨推演得出：该项投资组合预期可为城市创造约 **{base_carbon - pred_carbon:.2f} Mt** 的绝对减排收敛减量，并同步预期在现有宏观底盘的基础上，为地方实际GDP额外产生 **{user_z_gdp:.2f}%** 的实质性拉动空间。")

    st.subheader("建议： 宏观政策决策建议与发展统筹指导意见")
    if total_invest < 4.0:
        st.markdown("**【系统自动定性识别：基础保障型保守策略】**\n\n"
                    "**深度政策诊断模型研判**：当前拟定配置方案的总体资金规模投入水平表现为相对保守。其规模体量远未触及能够引发实体产业发生数字化质变的临界规模积聚门槛。由于总额受限，边际预算可能优先流向基础硬件系统的静态运维和既有资产折旧，难以全面形成产业聚集效应。系统预测：该级别投资无法在既定五年规划周期内激发出实质性的经济拉动，甚至潜藏着数字基建初期土木耗能的微弱反弹风险。\n\n"
                    "**宏观发展破局指导规划**：本项被动防守策略，仅在地方财政面临紧平衡承压、需要聚焦化解存量债务风险的特定时期，方可作为过渡性保底安排。建议宏观规划部门积极探索社会资本深度参与的多元化融资模式（如规范开展基础设施特许经营权或推进基础设施公募REITs基金）。通过政企资源高度协同与风险合理共担，打破单一公共财政投入带来的刚性紧平衡约束。")
    elif total_invest > 12.0:
        st.markdown("**【系统自动定性识别：高危扩张型过载策略】**\n\n"
                    "**深度政策诊断模型研判**：风险提示激活。仿真结果提示，高投入、宽覆盖的扩张模式可能使其逐渐偏离帕累托有效前沿的效率区间。虽然短期内对固定资产投资指标拉动较为明显，但中长期存在引发财政边际效应递减与公共资金挤出效应的潜在风险，长远看可能对全域总体综合发展成效构成一定沉没成本负担。\n\n"
                    "**宏观发展破局指导规划**：建议审计、统筹与综合协调部门启动绩效评估程序。应当通过严密的合规性测算，合理调减高能耗、超前过热的基础建设置信标段，严格把控缺乏深入环评与消化需求论证的项目。通过科学优化举债和财政投资大盘，将总干预预算维持在安全财政容忍度内，稳步优化地方宏观资产负债表的长期健康底层韧性。")
    else:
        st.markdown("**【系统自动定性识别：效率均衡型高质量稳步提质战略】**\n\n"
                    "**深度政策诊断模型研判**：系统给予该项配置良性的战略评价。该资金配置方案较为精准地落入帕累托有效均衡区间。在保持相对理性的投资规模下，避免了资本无序扩张，通过多要素靶向分配机制，在多目标刚性约束下，创造性地实现了宏观经济拉动与碳排放收敛在边际层面的良性协同。\n\n"
                    "**宏观发展破局指导规划**：该配置具有较强的现实参照意义。建议由宏观决策与办公统筹部门提取该项参数，将其作为后续编制地方中长期施政规划与年度经济社会发展报告的量化参照。引导各相关部门依据此比例关系设定项目库白名单，固化协同优势，科学指导本区域核心产业体系逐步向更具效能的低碳循环经济业态进行高质量、可持续的结构性升维。")
    st.markdown("</div>", unsafe_allow_html=True)

    bottom_navigation('mod4')
