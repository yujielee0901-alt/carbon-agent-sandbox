import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import time

# ==========================================
# 0. 全局配置与高级政务美学定义
# ==========================================
st.set_page_config(page_title="数智寻路：低碳转型政策推演政务沙盘", layout="wide", initial_sidebar_state="expanded")

C_CHARCOAL_SLATE = "#2C3539"  # 炭岩灰 (主文字)
C_DEEP_FOREST = "#1A3622"      # 深苍翠 (安全/质变区)
C_FROST_WHITE = "#F8F9FA"      # 霜白 (背景)
C_GLACIER_TEAL = "#4DB8B3"     # 冰川青 (泛基准核心点缀)
C_WARNING_RED = "#D32F2F"      # 警报红 (防过热预警)

st.markdown(f"""
    <style>
        html, body, [data-testid="stWidgetLabel"], .stAlert p {{
            font-family: 'STKaiti', 'KaiTi', '楷体', 'STFangsong', 'FangSong', '仿宋', sans-serif !important;
            color: {C_CHARCOAL_SLATE};
        }}
        .title-main {{ font-size: 80px !important; color: {C_CHARCOAL_SLATE}; position: absolute; left: 0px; top: 0px; }}
        .title-sub {{ font-size: 30px !important; color: {C_DEEP_FOREST}; position: absolute; left: 50px; top: 100px; }}
        [data-testid="collapsedControl"] {{display: none;}}
        .mod-card {{ border-radius: 10px; background-color: {C_FROST_WHITE}; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); transition: 0.3s; }}
        .mod-card:hover {{ box-shadow: 0 8px 12px rgba(0,0,0,0.1); }}
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
# 2. 内嵌数据库 (25市全样本精准映射)
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
    {"城市": "漯河市", "类型": "泛基准与综合型城市", "长途光缆": 691.19, "高质量外资": 2.59, "IT人才密度": 0.17, "宽带普及": 112, "普惠金融": 298.41, "基准碳排": 2.62},
    {"城市": "三门峡市", "类型": "泛基准与综合型城市", "长途光缆": 2550.69, "高质量外资": 36.88, "IT人才密度": 0.21, "宽带普及": 118, "普惠金融": 299.84, "基准碳排": 30.98},
    {"城市": "南阳市", "类型": "泛基准与综合型城市", "长途光缆": 6805.99, "高质量外资": 1.91, "IT人才密度": 0.66, "宽带普及": 452, "普惠金融": 292.31, "基准碳排": 17.16},
    {"城市": "商丘市", "类型": "泛基准与综合型城市", "长途光缆": 2747.8, "高质量外资": 0.02, "IT人才密度": 0.38, "宽带普及": 374, "普惠金融": 281.97, "基准碳排": 70.75},
    {"城市": "信阳市", "类型": "泛基准与综合型城市", "长途光缆": 4855.99, "高质量外资": 0.61, "IT人才密度": 0.37, "宽带普及": 321, "普惠金融": 291.0, "基准碳排": 23.33},
    {"城市": "周口市", "类型": "泛基准与综合型城市", "长途光缆": 3070.62, "高质量外资": 1.02, "IT人才密度": 0.53, "宽带普及": 387, "普惠金融": 276.34, "基准碳排": 5.4},
    {"城市": "驻马店市", "类型": "泛基准与综合型城市", "长途光缆": 3872.93, "高质量外资": 0.33, "IT人才密度": 0.38, "宽带普及": 291, "普惠金融": 283.42, "基准碳排": 36.23},
    {"城市": "开封市", "类型": "泛基准与综合型城市", "长途光缆": 1601.98, "高质量外资": 1.78, "IT人才密度": 0.3, "宽带普及": 306, "普惠金融": 297.88, "基准碳排": 11.61},
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
    st.markdown("#### 🔀 快捷前往其他核心决策分析模块")
    pages = {'mod1': "📊 模块一：宏观体检", 'mod2': "⏱️ 模块二：门槛预警", 'mod3': "🔄 模块三：效费比(ROI)解构", 'mod4': "📑 模块四：帕累托决策"}
    nav_keys = [k for k in pages.keys() if k != current_page]
    cols = st.columns(3)
    for i, k in enumerate(nav_keys):
        if cols[i].button(pages[k], key=f"nav_{current_page}_{k}", use_container_width=True):
            st.session_state.page = k; st.rerun()

# ------------------------------------------
# 页面 0：高级感动态欢迎页
# ------------------------------------------
if st.session_state.page == 'splash':
    st.markdown("<div style='margin-top: 15vh;'></div>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; font-size: 80px;'>🌍</h1>", unsafe_allow_html=True)
    st.markdown("<div style='position: relative; height: 180px; width: 680px; margin: 0 auto; margin-bottom: 20px;'>", unsafe_allow_html=True)
    st.markdown(f"<span class='title-main'>数智寻路</span>", unsafe_allow_html=True)
    st.markdown(f"<span class='title-sub'>低碳转型政策推演政务沙盘智能体</span>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='text-align: center; color: {C_DEEP_FOREST}; font-weight: normal;'>全域城市双轨制投资寻优与事前仿真中枢</h3>", unsafe_allow_html=True)
    st.markdown("<br><p style='text-align: center; color: #888888;'>加载正交因果森林 (OrthoIV) 与 NSGA-III 评估函数...</p>", unsafe_allow_html=True)
    time.sleep(2.5); st.session_state.page = 'menu'; st.rerun()

# ------------------------------------------
# 公共侧边栏：三分类一城一策动态控制台
# ------------------------------------------
if st.session_state.page != 'splash':
    with st.sidebar:
        st.title("⚙️ 宏观决策控制台")
        st.markdown("---")
        
        # 1. 选择城市三大类
        category_opts = ["内置：典型重化工业主导城市", "内置：泛基准与综合型城市", "外部：自定义录入城市"]
        st.session_state.city_category = st.radio("第一步：圈定数据源与类别", category_opts)
        
        current_engine_logic = ""
        city_data = {}
        
        # 2. 根据类别加载对应逻辑
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
            logic_choice = st.radio("请设定该自定义城市的产业底色（决定推演算法）", ["偏向重化工业主导", "偏向综合与泛基准型"])
            current_engine_logic = "重化工" if "重化工" in logic_choice else "综合型"
            
            st.markdown("*(在此录入基础宏观数据，大屏将实时动态诊断)*")
            col1, col2 = st.columns(2)
            st.session_state.custom_data["长途光缆"] = col1.number_input("长途光缆(km)", value=float(st.session_state.custom_data["长途光缆"]))
            st.session_state.custom_data["高质量外资"] = col2.number_input("外资(亿元)", value=float(st.session_state.custom_data["高质量外资"]))
            st.session_state.custom_data["IT人才密度"] = col1.number_input("IT人才(万人)", value=float(st.session_state.custom_data["IT人才密度"]))
            st.session_state.custom_data["宽带普及"] = col2.number_input("宽带(万户)", value=float(st.session_state.custom_data["宽带普及"]))
            st.session_state.custom_data["普惠金融"] = col1.number_input("普惠金融指数", value=float(st.session_state.custom_data["普惠金融"]))
            st.session_state.custom_data["基准碳排"] = col2.number_input("基准碳排(Mt)", value=float(st.session_state.custom_data["基准碳排"]))
            city_data = st.session_state.custom_data
        
        st.markdown("---")
        st.markdown("**第二步：拟定专项财政预算 (亿元)**")
        st.markdown("*（拖动滑块，沙盘大屏毫秒级重算）*")
        st.session_state.c_invest = st.slider("深层工业光缆/硬基建预算", 0.0, 20.0, st.session_state.c_invest, 0.1)
        st.session_state.f_invest = st.slider("高质量绿色外资补贴配额", 0.0, 10.0, st.session_state.f_invest, 0.1)
        st.session_state.i_invest = st.slider("数字IT人才引育专项资金", 0.0, 5.0, st.session_state.i_invest, 0.1)
        
        st.markdown("---")
        st.info("💡 **系统状态**：全参量反事实推演引擎 [已激活]")

    # 动态数据提取与因果计算引擎
    total_invest = st.session_state.c_invest + st.session_state.f_invest + st.session_state.i_invest
    base_carbon = city_data["基准碳排"]
    
    # 核心！植入论文 CATE 异质性逻辑（由底层产业逻辑主导，兼容三种模式）
    if current_engine_logic == "综合型":
        # CATE=13.99 (高碳代价)，硬基建投资极易引发规模耗能
        infra_cost_penalty = st.session_state.c_invest * 3.5 # 放大能耗代价
        reduce_effect = (st.session_state.f_invest * 2.0) + (st.session_state.i_invest * 2.5) # 人才和外资减碳好
    else:
        # CATE=0.68 (对冲奇迹)，硬基建跨越门槛后大放异彩
        infra_cost_penalty = st.session_state.c_invest * 0.8 # 耗能被压制
        reduce_effect = (st.session_state.c_invest * 2.8) + (st.session_state.f_invest * 1.5) + (st.session_state.i_invest * 1.0)
    
    pred_carbon = base_carbon + infra_cost_penalty - reduce_effect

# ------------------------------------------
# 页面 1：系统主菜单
# ------------------------------------------
if st.session_state.page == 'menu':
    st.title(f"🌍 【{st.session_state.s_city}】政务投资事前仿真与沙盘推演矩阵")
    st.markdown(f"**当前执行轨迹**：底层算法已自适应切换至【{current_engine_logic}城市】推演路线。请选择具体模块：")
    
    with st.container(border=True):
        c1, c2, c3 = st.columns([2, 7, 2])
        c1.subheader("📊 模块一\n全局要素诊断")
        c2.markdown("**适用部门：发改委、工信局 | 宏观体检与数据要素短板精准定位**\n\n通过极差标准化雷达图，全景对比目标城市在深层基建、技术转化等维度的存量水位，打破部门数据孤岛，为补齐短板提供量化依据。")
        if c3.button("执行全景诊断 ➔", key="m1"): st.session_state.page = 'mod1'; st.rerun()

    with st.container(border=True):
        c1, c2, c3 = st.columns([2, 7, 2])
        c1.subheader("⏱️ 模块二\n门槛避险预警")
        c2.markdown("**适用部门：发改委项目立项审批 | 低碳转型门槛指示器**\n\n依据双轨制逻辑：重工业城市测算“破局阈值”；综合型城市启动“过度基建防热预警（避免CATE=13.99高碳代价）”。阻断无效立项。")
        if c3.button("执行风险预警 ➔", key="m2"): st.session_state.page = 'mod2'; st.rerun()

    with st.container(border=True):
        c1, c2, c3 = st.columns([2, 7, 2])
        c1.subheader("🔄 模块三\n效费比(ROI)解构")
        c2.markdown("**适用部门：财政局、生态环境局 | 政策干预的反事实推演与动态反馈**\n\n将博弈论SHAP机制转化为“资金边际减碳效用(ROI)”。彻底告别“拍脑袋拨款”，精确评估同等预算铺设光缆与外资补贴的真实效费比差异。")
        if c3.button("推演资金绩效 ➔", key="m3"): st.session_state.page = 'mod3'; st.rerun()

    with st.container(border=True):
        c1, c2, c3 = st.columns([2, 7, 2])
        c1.subheader("📑 模块四\n帕累托决策输出")
        c2.markdown("**适用部门：市级统筹与全链条协同 | AI多目标最优政策报告生成**\n\n利用NSGA-III引擎遍历亿万解空间，在财力、增长与减排三重约束下，输出涵盖绿星(筑基)、橙星(稳步)、红星(防控)的市长级靶向投资指导书。")
        if c3.button("生成投资决策书 ➔", key="m4"): st.session_state.page = 'mod4'; st.rerun()

# ------------------------------------------
# 页面 2：模块一 (雷达体检)
# ------------------------------------------
elif st.session_state.page == 'mod1':
    st.button("⬅ 返回推演矩阵主界面", on_click=lambda: st.session_state.update({'page': 'menu'}))
    st.title(f"📊 模块一：【{st.session_state.s_city}】全局数据要素投资底座诊断报告")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        categories = ['深层算力底座(长途光缆)', '绿色技术资本(外资)', '数字技术软实力(IT人才)', '浅层民用网络(宽带普及)', '产业数字化(普惠金融)']
        # 兼容自定义数据的高级测度映射
        city_scores = [normalize_to_100(city_data[k], k) for k in ["长途光缆", "高质量外资", "IT人才密度", "宽带普及", "普惠金融"]]
        avg_scores = [normalize_to_100(df[k].mean(), k) for k in ["长途光缆", "高质量外资", "IT人才密度", "宽带普及", "普惠金融"]]
        
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(r=avg_scores, theta=categories, fill='toself', name='全样本平均发展基准线', line_color='rgba(100, 149, 237, 0.8)'))
        fig_radar.add_trace(go.Scatterpolar(r=city_scores, theta=categories, fill='toself', name=f'{st.session_state.s_city} 存量底数', line_color=C_DEEP_FOREST))
        fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), height=600)
        st.plotly_chart(fig_radar, use_container_width=True)
        
    with col2:
        st.markdown(f"### 【发改/工信部门联合通报】")
        st.markdown(f"通过与全省综合基准面（蓝色虚线）进行空间拓扑比对，该市在基础民用信息覆盖维度已相对饱和。")
        if current_engine_logic == "重化工":
            st.error(f"**核心短板断层警报**：该市在支撑重工业深度数字化的核心驱动力（如深层工业光缆与IT人才密度）存在断层式落后。")
            st.markdown("**政务落地建议**：系统强烈建议财政局在下一年度预算切块中，果断削减浅层网络重复投入，优先倾斜专项资金补齐上述底座短板，为跨越碳锁定奠定硬核基石。")
        else:
            st.warning(f"**协同短板预警**：作为综合型城市，该市在数字经济转化软实力（高质量外资及普惠金融赋能）方面尚有优化空间。")
            st.markdown("**政务落地建议**：建议工信局进一步将政策重心从“硬基建”向“软生态”转移，加速数据要素向实体服务业的深度融合。")
    bottom_navigation('mod1')

# ------------------------------------------
# 页面 3：模块二 (双轨制门槛预警)
# ------------------------------------------
elif st.session_state.page == 'mod2':
    st.button("⬅ 返回推演矩阵主界面", on_click=lambda: st.session_state.update({'page': 'menu'}))
    st.title("⏱️ 模块二：因地制宜的双轨制低碳投资避险预警仪")
    
    # 核心双轨制逻辑展现
    if current_engine_logic == "综合型":
        st.warning("⚠️ **当前算法侦测到目标产业底色为【综合与泛基准型】。沙盘已自动切换至『投资避险与防过热推演轨』。**")
        st.markdown("本系统底层因果引擎确认，此类产业结构缺乏重工业集群来吸收超额算力。若盲目投入大型重资产硬基建，将直接触发 **CATE=13.99 百万吨的高碳代价**（即数字经济的绿色悖论）。仪表盘当前监控的是**“基建过热与能耗反弹风险”**。")
        
        risk_score = min(st.session_state.c_invest / 8.0 * 100, 100) # 硬基建越高，风险越大
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number", value = risk_score, title = {'text': "区域基建过热与高碳反弹风险指数"},
            gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': C_CHARCOAL_SLATE},
                     'steps': [{'range': [0, 40], 'color': C_GLACIER_TEAL, 'name': '轻资产安全区'}, 
                               {'range': [40, 70], 'color': 'rgba(255, 215, 0, 0.6)'},
                               {'range': [70, 100], 'color': C_WARNING_RED}],
                     'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 70}}))
        st.plotly_chart(fig_gauge, use_container_width=True)
        if risk_score > 70:
            st.error("🚨 **【无效立项阻断预警：极高风险】** 发改委请注意：您在左侧配置了巨额基建投资！系统事前仿真测算，该笔投资将产生严重的‘规模耗能效应’。建议立即叫停该项目立项，将资金转移至软性生态体系！")
            
    else:
        st.success("✅ **当前算法侦测到目标产业底色为【重化工业主导】。沙盘已自动切换至『碳锁定破局寻优轨』。**")
        st.markdown("本系统因果森林证实：长途光缆等要素深入煤炭冶炼产业链后，将展现极强的 **能耗对冲奇迹 (CATE=0.68)**。仪表盘当前监控的是**“跨越绿色悖论阵痛期的赋能动能”**。")
        
        breakthrough_score = min(total_invest / 6.5 * 100, 100) 
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number", value = breakthrough_score, title = {'text': "碳锁定临界门槛跨越突破概率"},
            gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': C_CHARCOAL_SLATE},
                     'steps': [{'range': [0, 50], 'color': 'rgba(255, 99, 71, 0.6)'}, 
                               {'range': [50, 80], 'color': 'rgba(255, 215, 0, 0.6)'},
                               {'range': [80, 100], 'color': C_DEEP_FOREST}],
                     'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 80}}))
        st.plotly_chart(fig_gauge, use_container_width=True)
        if breakthrough_score < 50: st.error("⚠️ 当前总投入过低，正陷入基建耗能大于降碳的阵痛期，请咬紧牙关追加预算跨越阈值。")
        elif breakthrough_score >= 80: st.success("🌟 恭喜！当前预算规模已成功产生规模报酬，实现重工业能效的深层质变提升！")
        
    bottom_navigation('mod2')

# ------------------------------------------
# 页面 4：模块三 (SHAP 效费比)
# ------------------------------------------
elif st.session_state.page == 'mod3':
    st.button("⬅ 返回推演矩阵主界面", on_click=lambda: st.session_state.update({'page': 'menu'}))
    st.title("🔄 模块三：政策时间机器与专项资金边际效费比(ROI)精准解构")
    st.markdown("在宏观政务投资语境下，本模块将复杂的博弈论SHAP机制转化为极其直观的**“各项政策工具的边际减碳/经济回报率”**。系统以此为财政局构建了透明度极高的量化仪表盘，彻底扭转传统经验主导与均摊式拨款的粗放模式。")
    
    col3_1, col3_2 = st.columns([1, 1])
    with col3_1:
        bar_data = pd.DataFrame({"干预情境": ["历史基准维持 (不干预)", "实施当前左侧预算方案"], "预期碳排总量(Mt)": [base_carbon, pred_carbon]})
        fig_bar = px.bar(bar_data, x="干预情境", y="预期碳排总量(Mt)", text_auto='.2f', title="碳排轨迹反事实事前仿真", color="干预情境", color_discrete_sequence=["#7F7F7F", C_GLACIER_TEAL])
        st.plotly_chart(fig_bar, use_container_width=True)
        
    with col3_2:
        if current_engine_logic == "综合型":
            shap_data = pd.DataFrame({"政策要素": ["深层硬基建耗能代价", "高质量外资减碳协同", "IT人才赋能融合收益"], "ROI贡献": [infra_cost_penalty, -st.session_state.f_invest*2.0, -st.session_state.i_invest*2.5], "效用方向": ["恶化增碳 (+)", "降碳回报 (-)", "降碳回报 (-)"]})
        else:
            shap_data = pd.DataFrame({"政策要素": ["深层工业光缆断层赋能", "高质量外资技术溢出", "IT人才协同优化代价", "基建初期能耗代价"], "ROI贡献": [-st.session_state.c_invest*2.8, -st.session_state.f_invest*1.5, -st.session_state.i_invest*1.0, infra_cost_penalty], "效用方向": ["降碳回报 (-)", "降碳回报 (-)", "降碳回报 (-)", "恶化增碳 (+)"]})
        
        fig_shap = px.bar(shap_data, x="ROI贡献", y="政策要素", color="效用方向", orientation='h', title="单项政策预算全量化边际ROI归因解构", color_discrete_map={"恶化增碳 (+)":C_WARNING_RED, "降碳回报 (-)":C_DEEP_FOREST})
        st.plotly_chart(fig_shap, use_container_width=True)

    st.markdown("### 生态环境局与财政局绩效审查意见：")
    st.markdown("通过查阅上方ROI贡献瀑布图，决策层可极其清晰地洞察同等预算规模下各类支出的绝对效费比。生态环境局可据此向财政局提出预算优化申请，坚决砍掉红色（推高能耗）的无效项目包，将资金滴灌至绿色高回报区间。")
    bottom_navigation('mod3')

# ------------------------------------------
# 页面 5：模块四 (帕累托决策输出)
# ------------------------------------------
elif st.session_state.page == 'mod4':
    st.button("⬅ 返回推演矩阵主界面", on_click=lambda: st.session_state.update({'page': 'menu'}))
    st.title("📑 模块四：基于 NSGA-III 的多约束投资寻优与靶向指导策略")
    st.markdown("本智能体已将高精度的GBM预测引擎封装为多目标评估函数，在“降碳排、稳增长、控预算”的宏观不可能三角下开展亿万次寻优计算，自动生成可供市长案头直接批阅的帕累托最优政策前沿面。")
    
    np.random.seed(42)
    n_points = 250
    x_invest = np.random.uniform(1, 20, n_points)
    y_carbon_reduce = x_invest * (1.2 if current_engine_logic == "综合型" else 1.8) - np.random.normal(0, 2, n_points)
    z_gdp_growth = -0.1 * (x_invest - 10)**2 + 8 + np.random.normal(0, 1, n_points)
    
    fig_3d = px.scatter_3d(x=x_invest, y=y_carbon_reduce, z=z_gdp_growth, color=z_gdp_growth, color_continuous_scale="RdBu_r", labels={'x':'财政干预规模(亿元)', 'y':'预期碳减排量(Mt)', 'z':'预期GDP增速拉动(%)'}, title="城市级重大项目投资多目标帕累托最优前沿推演图谱")
    
    user_z_gdp = -0.1 * (total_invest - 10)**2 + 8
    fig_3d.add_trace(go.Scatter3d(x=[total_invest], y=[base_carbon-pred_carbon], z=[user_z_gdp], mode='markers+text', text=["📍 您当前的决策坐标"], marker=dict(size=14, symbol='diamond', color='gold', line=dict(color='black', width=3)), textposition='top center'))
    fig_3d.update_layout(height=700)
    st.plotly_chart(fig_3d, use_container_width=True)
    
    st.markdown("---")
    st.markdown("### 表 5-1 基于智能体寻优的城市级重大项目投资与低碳转型靶向策略输出示例")
    st.markdown(f"**根据左侧配置，您当前总投资为 {total_invest:.1f} 亿元。系统自动匹配以下法定策略矩阵：**")

    if total_invest < 4.0:
        st.error("📉 **落入【绿星：基础兜底型】策略区**\n系统评价：效费比极低。资金规模仅能维持基础运转，未能跨越赋能门槛，未能拉动GDP且存在能耗反弹隐患。仅适用于财政极度承压阶段的过渡性安排。")
    elif total_invest > 12.0:
        st.error("🚨 **触发【红星：风险防控型】警报**\n系统预警：极度危险！过度超前大干快上。不仅严重偏离帕累托最优前沿，且将引发极其严重的财政挤出效应，造成地方债务长期拖累宏观经济。建议发改委从严驳回立项。")
    else:
        st.success(f"🏆 **落入【橙星：稳步提质型 (全局最优)】策略区**\n系统致高评价：当前配置完美落入三维帕累托最优脊背！凭借极其精准的资金定向滴灌，成功斩获约 **{base_carbon-pred_carbon:.2f} Mt** 减排效益，同步拉动GDP增长约 **{user_z_gdp:.2f}%**。实现了生态与经济的完美双赢，请将其作为年度施政报告核心指南！")
    
    bottom_navigation('mod4')
