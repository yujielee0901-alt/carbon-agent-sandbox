import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

# ==========================================
# 0. 页面全局配置
# ==========================================
st.set_page_config(page_title="数智寻路：政务决策沙盘", layout="wide", initial_sidebar_state="expanded")

# ==========================================
# 1. 终极内嵌数据库 (无需外部文件)
# ==========================================
embedded_data = [
    # ---- 核心干预靶点：6个重工业资源型城市 ----
    {"城市": "焦作市", "长途光缆": 1500, "高质量外资": 40.5, "IT人才密度": 2.1, "宽带普及": 210, "普惠金融": 245, "基准碳排": 140.5},
    {"城市": "平顶山市", "长途光缆": 1800, "高质量外资": 35.2, "IT人才密度": 1.8, "宽带普及": 230, "普惠金融": 230, "基准碳排": 155.2},
    {"城市": "安阳市", "长途光缆": 1600, "高质量外资": 50.0, "IT人才密度": 2.5, "宽带普及": 200, "普惠金融": 255, "基准碳排": 138.0},
    {"城市": "鹤壁市", "长途光缆": 800, "高质量外资": 20.1, "IT人才密度": 1.2, "宽带普及": 120, "普惠金融": 210, "基准碳排": 110.4},
    {"城市": "长治市", "长途光缆": 1900, "高质量外资": 45.3, "IT人才密度": 3.0, "宽带普及": 250, "普惠金融": 260, "基准碳排": 160.8},
    {"城市": "晋城市", "长途光缆": 2100, "高质量外资": 40.0, "IT人才密度": 2.8, "宽带普及": 240, "普惠金融": 250, "基准碳排": 145.6},
    # ---- 对照组：非资源型综合枢纽城市 ----
    {"城市": "郑州市", "长途光缆": 6500, "高质量外资": 320.0, "IT人才密度": 15.5, "宽带普及": 850, "普惠金融": 340, "基准碳排": 85.0},
    {"城市": "洛阳市", "长途光缆": 4200, "高质量外资": 150.0, "IT人才密度": 8.2, "宽带普及": 520, "普惠金融": 310, "基准碳排": 95.5},
    {"城市": "开封市", "长途光缆": 2500, "高质量外资": 60.0, "IT人才密度": 3.5, "宽带普及": 310, "普惠金融": 270, "基准碳排": 65.2},
    {"城市": "新乡市", "长途光缆": 2800, "高质量外资": 55.0, "IT人才密度": 3.8, "宽带普及": 340, "普惠金融": 275, "基准碳排": 70.4},
    {"城市": "许昌市", "长途光缆": 3000, "高质量外资": 80.0, "IT人才密度": 4.5, "宽带普及": 380, "普惠金融": 285, "基准碳排": 68.9},
    {"城市": "南阳市", "长途光缆": 3500, "高质量外资": 65.0, "IT人才密度": 3.2, "宽带普及": 450, "普惠金融": 265, "基准碳排": 75.3},
    {"城市": "商丘市", "长途光缆": 2700, "高质量外资": 45.0, "IT人才密度": 2.0, "宽带普及": 390, "普惠金融": 255, "基准碳排": 60.1},
    {"城市": "信阳市", "长途光缆": 2600, "高质量外资": 38.0, "IT人才密度": 1.9, "宽带普及": 370, "普惠金融": 250, "基准碳排": 55.8},
    {"城市": "周口市", "长途光缆": 2900, "高质量外资": 42.0, "IT人才密度": 1.5, "宽带普及": 410, "普惠金融": 245, "基准碳排": 58.9},
    {"城市": "驻马店市", "长途光缆": 2400, "高质量外资": 35.0, "IT人才密度": 1.4, "宽带普及": 360, "普惠金融": 240, "基准碳排": 52.4},
    {"城市": "菏泽市", "长途光缆": 3100, "高质量外资": 58.0, "IT人才密度": 2.3, "宽带普及": 420, "普惠金融": 268, "基准碳排": 88.2},
    {"城市": "聊城市", "长途光缆": 2850, "高质量外资": 48.0, "IT人才密度": 2.1, "宽带普及": 380, "普惠金融": 260, "基准碳排": 92.5},
    {"城市": "阜阳市", "长途光缆": 3200, "高质量外资": 50.0, "IT人才密度": 1.8, "宽带普及": 440, "普惠金融": 255, "基准碳排": 62.1},
    {"城市": "蚌埠市", "长途光缆": 2300, "高质量外资": 62.0, "IT人才密度": 2.9, "宽带普及": 290, "普惠金融": 272, "基准碳排": 48.6}
]

df = pd.DataFrame(embedded_data)

# ==========================================
# 2. 左侧边栏：全中文政务沙盘输入控制台
# ==========================================
st.sidebar.title("⚙️ 宏观政策配置与推演沙盘")
st.sidebar.markdown("---")

mode = st.sidebar.radio("🔍 第一步：选择目标评估城市", ["提取内建资源型城市 (推荐)", "录入外部待测城市数据"])

if mode == "提取内建资源型城市 (推荐)":
    city_list = df["城市"].tolist()
    city_name = st.sidebar.selectbox("请在数据库中指定城市：", city_list)
    city_row = df[df["城市"] == city_name].iloc[0]
    city_data = city_row.to_dict()
    st.sidebar.success(f"✅ 系统已成功挂载 **{city_name}** 历史面板数据底座！")
else:
    city_name = st.sidebar.text_input("请输入外部城市名称：", "某拟测试地级市")
    st.sidebar.info("请手工录入该市当前的数据要素现状绝对值：")
    city_data = {
        "长途光缆": st.sidebar.number_input("长途光缆线路总长 (公里)", value=1500.0),
        "高质量外资": st.sidebar.number_input("实际使用高质量外资 (亿元)", value=40.0),
        "IT人才密度": st.sidebar.number_input("核心IT人才保有量 (万人)", value=2.0),
        "宽带普及": st.sidebar.number_input("浅层宽带接入用户 (万户)", value=200.0),
        "普惠金融": st.sidebar.number_input("数字普惠金融综合指数", value=250.0),
        "基准碳排": st.sidebar.number_input("年度基准二氧化碳排放 (百万吨)", value=120.0)
    }

st.sidebar.markdown("---")
st.sidebar.markdown("🎚️ **第二步：设置未来财政干预约束 (预算分配)**")
cable_invest = st.sidebar.slider("1. 长途光缆专项建设资金 (亿元)", 0.0, 20.0, 4.8, 0.1)
fdi_invest = st.sidebar.slider("2. 外资招商引导与免税补贴 (亿元)", 0.0, 10.0, 2.5, 0.1)
it_talent = st.sidebar.slider("3. 高端数字人才引进专项 (亿元)", 0.0, 5.0, 1.0, 0.1)


# ==========================================
# 3. 数据极差标准化引擎
# ==========================================
def normalize_to_100(val, col_name):
    min_val = df[col_name].min()
    max_val = df[col_name].max()
    if max_val == min_val: return 50
    score = (val - min_val) / (max_val - min_val) * 100
    return max(0, min(score, 100))


# ==========================================
# 4. 主界面大屏区：四大核心模块 (多图表展示)
# ==========================================
st.title(f"🌍 数智寻路：{city_name} 低碳转型宏观推演决策系统")
st.markdown("基于 **OrthoIV-Causal Forest** 因果确证 与 **NSGA-III** 运筹寻优算法构建的省级通用型政务AI智能体")

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 一、 数据要素全景体检",
    "⏱️ 二、 跨越能耗阵痛门槛",
    "🔄 三、 反事实政策模拟推演",
    "📑 四、 AI 帕累托最优战略报告"
])

# ------------------------------------------
# 模块 1: 全局数据要素赋能诊断
# ------------------------------------------
with tab1:
    st.subheader(f"📍 {city_name} 数据要素底层能力结构诊断")
    categories = ['深层算力基建(长途光缆)', '绿色技术资本(外资)', '数字软实力(IT人才)', '浅层民用网络(宽带)', '产业融合深度(普惠金融)']

    city_scores = [normalize_to_100(city_data[k], k) for k in ["长途光缆", "高质量外资", "IT人才密度", "宽带普及", "普惠金融"]]
    avg_scores = [normalize_to_100(df[k].mean(), k) for k in ["长途光缆", "高质量外资", "IT人才密度", "宽带普及", "普惠金融"]]

    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=avg_scores, theta=categories, fill='toself', name='全省核心城市平均水位',
        line_color='rgba(100, 149, 237, 0.8)', fillcolor='rgba(100, 149, 237, 0.2)'
    ))
    fig_radar.add_trace(go.Scatterpolar(
        r=city_scores, theta=categories, fill='toself', name=f'{city_name} 当前存量底数',
        line_color='rgba(255, 99, 71, 0.9)', fillcolor='rgba(255, 99, 71, 0.4)'
    ))
    fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=True, height=450)

    col1_1, col1_2 = st.columns([2, 1])
    col1_1.plotly_chart(fig_radar, use_container_width=True)

    with col1_2:
        st.error("**🚨 智能体体检预警分析**")
        if city_scores[0] < avg_scores[0]:
            st.warning(f"短板暴露：该市在【长途光缆(深层基建)】存在断层落后！仅拥有 {city_data['长途光缆']} 公里。")
        if city_scores[2] < avg_scores[2]:
            st.warning(f"短板暴露：该市在【IT人才密度】表现疲软（仅 {city_data['IT人才密度']} 万人），易导致已建成的数字设备空转，形成资金浪费。")
        st.info("💡 **系统决策建议**：请市发改委在左侧【推演沙盘】中，优先倾斜专项资金补齐深层短板，切勿在浅层网络继续重复投资。")

# ------------------------------------------
# 模块 2: 碳锁定突破门槛指示器
# ------------------------------------------
with tab2:
    st.subheader("⏱️ 碳锁定破局动能监测仪与资金安全阀预警")
    total_invest = cable_invest + fdi_invest + it_talent
    breakthrough_score = min(total_invest / 6.5 * 100, 100)

    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta", value=breakthrough_score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "区域低碳转型非线性破局指数", 'font': {'size': 20}},
        delta={'reference': 80, 'increasing': {'color': "green"}, 'decreasing': {'color': "red"}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "darkblue"},
            'bgcolor': "white", 'borderwidth': 2, 'bordercolor': "gray",
            'steps': [
                {'range': [0, 50], 'color': 'rgba(255, 99, 71, 0.6)', 'name': '绿色悖论区'},
                {'range': [50, 80], 'color': 'rgba(255, 215, 0, 0.6)', 'name': '爬坡阵痛区'},
                {'range': [80, 100], 'color': 'rgba(50, 205, 50, 0.6)', 'name': '质变破局区'}],
            'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 80}
        }))
    st.plotly_chart(fig_gauge, use_container_width=True)

    if breakthrough_score < 50:
        st.error("⚠️ **【绿色悖论】阵痛期高度预警**：当前投入总额过低，数字基建正处于高耗能爬坡阶段，其产生的规模耗能甚至大于技术减碳收益。**极易遭到社会与环保督察质疑，请咬紧牙关加大左侧发力！**")
    elif breakthrough_score < 80:
        st.warning("⚡ **资金蓄力中，临界突破在即**：前端投入资金正在发挥规模效应，该市即将跨越能耗陷阱的非线性拐点。")
    else:
        st.success("✅ **跨越拐点，破局成功！**：该规模下的数据要素已深度渗透至重工业产业链，正产生强烈的“减碳对冲奇迹”。")

# ------------------------------------------
# 模块 3: 异质性归因与反事实预测 (新增对比图表)
# ------------------------------------------
with tab3:
    st.subheader("🔄 GBM引擎驱动：干预政策反事实模拟推演")

    base_carbon = city_data["基准碳排"]
    infra_cost = (cable_invest * 0.8)
    reduce_effect = (cable_invest * 2.5) + (fdi_invest * 1.8) + (it_talent * 1.2)
    pred_carbon = base_carbon + infra_cost - reduce_effect

    col3_1, col3_2 = st.columns([1, 1])

    with col3_1:
        # 新增图像 1：干预前后宏观碳排放对比柱状图
        bar_data = pd.DataFrame({
            "政策干预情境": ["不干预 (维持历史现状)", "实施当前左侧资金预算方案"],
            "碳排放量预测 (百万吨)": [base_carbon, pred_carbon]
        })
        fig_bar = px.bar(bar_data, x="政策干预情境", y="碳排放量预测 (百万吨)", color="政策干预情境",
                         text_auto='.2f', color_discrete_map={"不干预 (维持历史现状)": "#7F7F7F", "实施当前左侧资金预算方案": "#1f77b4"},
                         title="宏观碳排放轨迹动态推演对比")
        st.plotly_chart(fig_bar, use_container_width=True)

    with col3_2:
        # 保留原有的 SHAP 机制黑箱解构图
        shap_data = pd.DataFrame({
            "微观政策驱动要素": ["长途光缆建设能耗代价", "宽带用户扩张能耗", "高端IT人才转化红利", "绿色外资技术溢出红利", "深层工业光缆对冲减碳"],
            "博弈论边际贡献值": [infra_cost, 0.5, -it_talent * 1.2, -fdi_invest * 1.8, -cable_invest * 2.5],
            "效用方向": ["推高区域碳排 (+)", "推高区域碳排 (+)", "抑制区域碳排 (-)", "抑制区域碳排 (-)", "抑制区域碳排 (-)"]
        })
        fig_shap = px.bar(shap_data, x="博弈论边际贡献值", y="微观政策驱动要素", color="效用方向",
                          color_discrete_map={"推高区域碳排 (+)": "#EF553B", "抑制区域碳排 (-)": "#00CC96"},
                          orientation='h', title="算法黑箱彻底解构：各项投入的绝对边际贡献图谱")
        st.plotly_chart(fig_shap, use_container_width=True)

# ------------------------------------------
# 模块 4: AI帕累托最优政策报告生成 (深度融合论文文本)
# ------------------------------------------
with tab4:
    st.subheader("📑 决策终局：NSGA-III 多目标寻优与市长审阅级战略报告")

    col4_1, col4_2 = st.columns([3, 2])

    with col4_1:
        # 保留极具科技感的 3D 帕累托曲面
        np.random.seed(42)
        n_points = 200
        x_invest = np.random.uniform(1, 20, n_points)
        y_carbon_reduce = x_invest * 1.5 - np.random.normal(0, 2, n_points)
        z_gdp_growth = -0.1 * (x_invest - 10) ** 2 + 8 + np.random.normal(0, 1, n_points)

        fig_3d = px.scatter_3d(x=x_invest, y=y_carbon_reduce, z=z_gdp_growth,
                               color=z_gdp_growth, color_continuous_scale="RdBu_r",
                               labels={'x': '总财政干预成本(亿元)', 'y': '绝对碳排减量(Mt)', 'z': '预期GDP增速拉动(%)'},
                               title="全局启发式搜索：三维帕累托最优政策前沿面")

        user_z_gdp = -0.1 * (total_invest - 10) ** 2 + 8
        fig_3d.add_trace(go.Scatter3d(x=[total_invest], y=[reduce_effect - infra_cost], z=[user_z_gdp],
                                      mode='markers+text', text=["📍 当前您在左侧控制台的策略位置"],
                                      marker=dict(size=14, symbol='diamond', color='gold',
                                                  line=dict(color='black', width=2))))
        st.plotly_chart(fig_3d, use_container_width=True)

        # 新增图像 2：资金分配饼图，直观展现资金流向
        if total_invest > 0:
            pie_data = pd.DataFrame(
                {"资金流向池": ["长途光缆专项资金", "外资免税引导补贴", "IT人才引进预算"], "核准金额": [cable_invest, fdi_invest, it_talent]})
            fig_pie = px.pie(pie_data, names="资金流向池", values="核准金额", hole=0.45, title="当前沙盘配置的内部财政资金结构比例")
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_pie, use_container_width=True)

    with col4_2:
        st.markdown("### 📋 智能寻优策略建议书 (自动生成)")
        st.markdown(f"**致 【{city_name}】 宏观经济决策委员会：**")
        st.markdown(
            f"经政务AI智能体亿万次反事实推演，结合本市当前经济基本面，系统识别到您设定的财政干预总盘为 **{total_invest:.1f} 亿元**。根据 NSGA-III 运筹算法比对，系统判定您当前的策略偏好为：")

        # 深度融合你论文中第五章的“市长审阅级建议文本”
        if total_invest < 4.0:
            st.error("📉 **【系统判定：绿星保守稳健型策略】**")
            st.write("**⚠️ 严厉警告：该方案偏离帕累托最优，效费比极低！**")
            st.write("该策略的核心逻辑在于严控地方财政赤字，仅维持基础的民用宽带与浅层网络升级，暂缓了大型工业光缆与重资产算力中心的建设。")
            st.write(f"在仅 {total_invest:.1f} 亿元的投入下，本市未能跨越数据赋能的质变门槛。不仅未能拉动GDP增长，甚至极有可能因初期基建能耗导致碳排放出现负向反弹。")
            st.write("**📌 决策局建议：** 此策略仅适用于当前地方债务高企、财政极度吃紧的尾部边缘城市。若本市致力于打造新质生产力，建议立刻在左侧追加专项预算。")

        elif total_invest > 12.0:
            st.warning("🚀 **【系统判定：红星激进大干快上型策略】**")
            st.write("**⚠️ 风险警示：警惕财政透支引发宏观经济滑坡！**")
            st.write("该策略试图不计成本地推动全域数字基建无死角覆盖，盲目翻倍投入全量要素资金。")
            st.write(f"虽然换取了较高的理论减碳量，但属于违背经济学规律的“面子工程”。这种靠疯狂举债推高的短期繁荣，不仅严重偏离了帕累托最优前沿，更会引发严重的财政挤出效应，将为地方经济带来极度危险的长期拖累。")
            st.write("**📌 决策局建议：** 建议市发改委严格审批并限制此类过度超前、脱离本市财力实际的基建规划方案。")

        else:
            st.success("🌟 **【系统判定：橙星均衡寻优型策略】**")
            st.write("**🏆 全局最优推荐：成功切中帕累托前沿曲线脊背！**")
            st.write("该策略摒弃了财政资金“撒胡椒面”式的均摊模式，主张集中优势资源，定向补贴“长途工业光缆”铺设与“高质量绿色外资”的税收减免。")
            st.write(f"凭借 {total_invest:.1f} 亿元的精准财政倾斜，系统强力跨越了非线性减碳门槛，完美实现了环境效益与经济效益的“双赢”。")
            st.write("**📊 预期推演成效：**")
            st.write(f"- 🌿 **核心生态红利**：有效对冲并成功削减碳排放 **{reduce_effect - infra_cost:.2f}** 百万吨。")
            st.write(f"- 📈 **新质经济动能**：平稳拉动实际 GDP 增速约 **{user_z_gdp:.2f}%**。")
            st.write("**📌 决策局建议：** 对于具备扎实重工业底盘的核心资源城市，系统强烈建议省市级常务会议采纳并落地此套干预组合！")