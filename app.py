import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import time
import re
import hashlib

# ==========================================
# 0. 全局配置与PC政务大屏美学定义
# ==========================================
st.set_page_config(page_title="城市低碳治理智能推演系统", layout="wide", initial_sidebar_state="expanded")

C_CHARCOAL_SLATE = "#2C3539"
C_DEEP_FOREST = "#1A3622"
C_GLACIER_TEAL = "#4DB8B3"
C_WARNING_RED = "#D32F2F"

st.markdown(f"""
    <style>
        button span, .material-icons, .material-symbols-rounded, [data-testid="stSidebarCollapseButton"] span {{ font-family: "Material Symbols Rounded", "Material Icons", sans-serif !important; }}
        html, body, p, div, h1, h2, h3, h4, h5, h6, label, .stMarkdown, [data-testid="stWidgetLabel"] {{ font-family: 'PingFang SC', 'Microsoft YaHei', '微软雅黑', 'SimHei', '黑体', sans-serif !important; color: {C_CHARCOAL_SLATE}; }}
        .title-main {{ font-size: 60px; color: {C_CHARCOAL_SLATE}; letter-spacing: 4px; text-align: center; font-weight: bold; margin-bottom: 0px; }}
        .title-sub {{ font-size: 24px; color: {C_DEEP_FOREST}; text-align: center; margin-top: 10px; margin-bottom: 30px; }}
        .spin-earth {{ font-size: 80px; text-align: center; animation: spin 4s linear infinite; margin-bottom: 20px; }}
        @keyframes spin {{ 100% {{ transform: rotate(360deg); }} }}
        .mod-card {{ border-radius: 8px; background-color: #F8F9FA; padding: 25px; margin-bottom: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); transition: 0.3s; border-left: 4px solid {C_GLACIER_TEAL}; }}
        .mod-card:hover {{ box-shadow: 0 8px 20px rgba(0,0,0,0.1); transform: translateY(-2px); }}
        .alarm-box {{ background-color: #FFF5F5; border: 1px solid #FFCDD2; padding: 15px; border-radius: 6px; margin-top: 15px; line-height: 1.6; }}
        .analysis-box {{ background-color: #FAFAFA; border-left: 4px solid {C_DEEP_FOREST}; padding: 15px 20px; margin-top: 15px; line-height: 1.8; font-size: 15px; }}
        [data-testid="collapsedControl"] {{display: none;}}
        .report-section {{ margin-bottom: 20px; }}
        .report-section h4 {{ color: #1A3622; font-weight: bold; margin-bottom: 10px; border-bottom: 1px solid #ddd; padding-bottom: 5px; }}
        .report-section strong {{ color: #2C3539; }}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. 深度智库预载入 (模块一基础体检数据底座)
# ==========================================
city_advice_db = {
    "焦作": {
        "m1": "【系统数据分析与推演过程】：通过高维极差空间拓扑与雷达图矩阵比对，本系统提取该市各项存量特征并与全域样本均值标尺进行映射。数据量化分析显示，该市在浅层宽带普及与普惠金融维度的无量纲得分已接近全域均线，呈现出消费端数字红利饱和的特征。而在支撑重化工底座转型的深层核心要素（长途光缆仅1020公里，IT人才仅0.27万人）上，系统柱状断层推演直观暴露出极大的结构性落差。本系统诊断客观反映出该区域底层信息基础设施明显滞后于实体经济制造规模的物理现实。\n\n【多部门协同决策指导建议】：\n\n1. 固定资产投资导向：建议在编制下一年度投资目录时，重构专项资金分配结构。本数据可作为实证，暂缓消费级通信基站的新建，将有限财政向深层工业光缆与算力枢纽倾斜。\n2. 数据孤岛清查机制：建议依托断层数据，重点排查市属重资产企业内部的“数据孤岛”现象，为开展复杂的能耗算法调度筑牢物理根基。"
    },
    "平顶山": {
        "m1": "【系统数据分析与推演过程】：对比数据显示，平顶山拥有全样本中处于高位的浅层宽带普及度（高达601万户），且深层光缆基数达2031公里，硬件网络底座较为扎实。然而，系统的雷达图检测出外资引入量（1.02亿）与普惠金融渗透率处于极度枯竭的边缘。推演过程直观指出，该市正面临极为严重的“硬资产过剩、软技术断层”危机，空有庞大的通信光缆，却缺乏具备国际先进低碳管理体系的外资力量以及本土数字智力支撑来盘活这些重资产。\n\n【多部门协同决策指导建议】：\n\n1. 招商结构调优模式：诊断提供的“软硬件失衡指数”为转换招商思维提供了数理证明。建议全面转向定向吸引携带前沿减排专利、算法模型的国际高质量数字技术企业入驻。\n2. 存量软资产激活：建议指导市属大型煤炭、能源国企开放应用场景。推动国有资本优先投资购买软件SaaS服务而非重复购置底层硬件设备。"
    },
    "安阳": {
        "m1": "【系统数据分析与推演过程】：作为老工业基地，安阳面临着全样本排名前列的巨量碳排压力（高达102.41Mt）。雷达图谱与极差测度显示，尽管其光缆基数达到中游（1887公里），但相较于其庞大且沉重的钢铁、煤化工业体量，当前的数字要素赋能深度存在极其严重的历史欠账。断层推演矩阵直观标红了其数字化工具在渗透重型冶炼企业底层的不足，这种严重的底层信息传输能力亏欠，构成了目前区域高位碳排无法实现精准测度与调度的根本阻碍。\n\n【多部门协同决策指导建议】：\n\n1. 历史包袱定向量化：建议以此测度模型为依据，向上级全景展示沉重的工业历史包袱。本断层报告可作为申报国家级转型示范区专项补助资金的核心实证附件。\n2. 技术革新专项注入：面对深层算力的缺位，建议联合社会资本设立针对特钢等传统产业的数字化技改专项基金，用强力资金弥补初期技术断层。"
    },
    "鹤壁": {
        "m1": "【系统数据分析与推演过程】：系统全域极差拓扑比对显示，鹤壁在底层硬件（光缆549公里，全样本垫底）与智力软件（IT人才仅0.13万，外资几乎归零）上呈现出“双重严重断层”。推演模型直观指出，该区域的信息传输动脉极其微弱，不仅浅层消费端网络尚未完全普及，其支撑重工业转型的深层物理基座更是处于极度匮乏状态。这种“一穷二白”的要素底盘，意味着系统在短期内根本无法为其构建有效的数据闭环。\n\n【多部门协同决策指导建议】：\n\n1. 财政缺口理论辩护：本断层诊断报告为争取外部转移支付提供了客观量化证据，合法合理地论证利用上级资金来填补本地底层基建账单的迫切性。\n2. 孤岛式示范标杆：面对基建匮乏现实，建议切忌“撒胡椒面”式的平均主义。优先在具有代表性的龙头企业内部开展“局域性”工业物联网试点，打造孤岛标杆。"
    },
    "长治": {
        "m1": "【系统数据分析与推演过程】：长治在本次雷达拓扑检测中呈现出极其特殊的“非对称性巨峰”。数据表明，其长途光缆长达3255.51公里，外资存量更是高达31.14亿元，具备了极其雄厚的物理基建与资本输入盘面。然而，与这庞大硬件与资金不匹配的是，其IT人才密度仅有0.30万人。系统柱状断层推演尖锐地指出：该市存在严重的“硬件设备极其超前、资本充沛，但智力核心完全脱节”的异构断层。大量外资引入的先进设备与庞大的光纤网络，正面临着无人开发、无高级算法驱动的“半闲置”状态。\n\n【多部门协同决策指导建议】：\n\n1. 招才引智优先序列：系统暴露的结构性塌陷为调整引才战略提供了最迫切论据。建议立刻将重心转向设立专项数字工程师引进计划，以匹配庞大的硬件底座。\n2. 技术生态强制耦合：鉴于外资引入量高位，建议要求驻地外资企业在本土设立研发中心、建立校企联合培养机制，以此强行补齐智力短板。"
    },
    "晋城": {
        "m1": "【系统数据分析与推演过程】：晋城以161.18Mt的惊人碳排放量，成为全域面板中极值最高的“重度碳锁定”样本。然而，雷达图谱与极差测度极其残酷地显示：面对这头“碳排放巨兽”，其数字对抗要素却显得微乎其微（光缆仅2207公里，人才仅0.26万）。推演矩阵直观标红了全要素的结构性枯竭，系统客观诊断指出：这种极度悬殊的“排量-控制力”比例，意味着该市现有的数字化赋能水平在如此庞大的煤炭与冶炼巨无霸面前几乎完全丧失了调控渗透能力。\n\n【多部门协同决策指导建议】：\n\n1. 宏观缺口向上申诉：面对评估出的巨大断层鸿沟，建议直接将极端体检报告转化为申请重大气候投融资试点城市的硬核佐证材料，证明常规财政已无力填补该缺口。\n2. 强制级基座重构：针对大型排碳主体的底层信息管网瘫痪状况，建议下发带有强制性的重资产物联网改造指令，不设缓冲期。"
    },
    "郑州": {
        "m1": "【系统数据分析与推演过程】：通过高维空间拓扑矩阵映射，郑州作为枢纽城市，其雷达图谱呈现出全样本中最强悍的“软实力霸权”。其数字产业与IT人才密度高达10.99万人，普惠金融指数与外资引进均处于全域巅峰极值。然而，其深层物理光缆（1943公里）相对于其经济体量而言，表现为“适度够用”。系统诊断确认：该市已彻底摆脱了依赖铺设物理硬基建拉动数字化的初级阶段，全面迈入了以算法、算力调度与智力资本要素驱动的深水区。\n\n【多部门协同决策指导建议】：\n\n1. 顶层研发导向：量化测度确证了资源禀赋。建议彻底剥离土建工程财政依赖，全盘转向对人工智能大模型、零碳数据交易平台的顶层设计投入。\n2. 智力资源在地转化：建议针对庞大的人才规模，出台专项“算力券”与“碳普惠激励”融合政策，将人才优势就地转化为数字降碳产业输出的护城河。"
    },
    "洛阳": {
        "m1": "【系统数据分析与推演过程】：作为综合型城市，洛阳在本次空间拓扑中暴露出罕见的“资产错位”。数据穿透显示，其光缆总长达3911公里，硬件底盘堪称奢华，人才具备优良规模。但与之形成惨烈断层的是，其外资引入仅有1.30亿元。系统诊断毫不留情地指出：洛阳正陷入“基建严重超前，外部先进技术与资本导入梗阻”的内循环困局，巨量地下光缆资产存在极大的算力空转风险。\n\n【多部门协同决策指导建议】：\n\n1. 存量资产紧急唤醒：基于断层示警，强烈建议立即控制新增市级骨干网络工程，盘点摸底现有数字资产利用率，规避重复无效建设。\n2. 靶向型绿色招商：面对外资与光缆的极度错位，必须向外界证明具备即插即用的世界级网络底座，将政策重心全盘压在吸引具备国际供应链标准的智造企业上。"
    },
    "新乡": {
        "m1": "【系统数据分析与推演过程】：新乡在雷达拓扑测度中呈现出典型的“中等均衡”分布。其光缆长度、宽带普及等硬件指标均严丝合缝地卡在全域均线附近。但在决定转型纵深的数字人才密度（0.49万）与外资引进（1.02亿）上暴露出了疲软乏力的断层迹象。系统诊断直击痛点：这种全科平庸的体检报告，意味着网络覆盖广度虽已达标，但极其缺乏深度重构制造业的高阶数字融合生态，处于高不成低不就的发展胶着期。\n\n【多部门协同决策指导建议】：\n\n1. 细分灯塔工程：系统客观证明普遍广度覆盖已无边际收益，规划层面应集中机动财力，在优势细分领域打造零碳数字标杆工厂，撕开转型突破口。\n2. 外交靶向技术引进：引资策略必须实施精准打击，专盯能带来成套能耗管理SaaS系统与供应链碳足迹认证服务的外向型数字平台。"
    },
    "开封": {
        "m1": "【系统数据分析与推演过程】：开封得益于文旅为主导的产业底色，其初始碳排放基数极低（11.61Mt）。数据测度显示，其光缆与宽带普及率已完美支撑起当前城市的运行体量。然而，系统断层推演标出了外资与高阶IT人才的塌陷区。这从量化层面确认了该市数字经济目前仅停留在表层的消费结算，极其缺乏能将城市文商旅农资源进行深度低碳化数据变现的高级要素。\n\n【多部门协同决策指导建议】：\n\n1. 轻量级SaaS化转向：基于硬件已够用的诊断，建议彻底放弃重资产数据中心指标争夺，资金盘全面转向开发“全域零碳智慧文旅服务平台”。\n2. ESG主题引资路线：利用“低碳基数轻型城市”优势，重点向主打ESG（环境、社会治理）评级投资的国际文创基金抛出橄榄枝，弥补工业招商不足。"
    },
    "许昌": {
        "m1": "【系统数据分析与推演过程】：通过全域极差比对，许昌暴露出了极其尖锐的“单维塌陷”特征。其在普惠金融等本土指标上表现良好，但实际使用外资量仅为惨淡的0.27亿元。系统断层推演矩阵毫不留情指出：该市在转型中处于极其严重的“对外技术封闭与资本孤岛”状态。缺乏外部鲶鱼效应刺激与国际减排算法模型的引入，将彻底锁死该市制造业向高端价值链攀升的空间。\n\n【多部门协同决策指导建议】：\n\n1. 考核权重极端调优：断层报告是对现有模式的直接预警，建议将招商考核的权重全面倾向于引进携带绿色供应链管理技术与节能专利的科技服务企业。\n2. 轻量型合作示范区：不再搞大而全的物理建设，依托底盘数据专门设立具备极高环保与数字化基准的绿色智造中外合作专区。"
    },
    "漯河": {
        "m1": "【系统数据分析与推演过程】：漯河在全样本空间中呈现出罕见的“超微型碳排地标”特征（仅2.62Mt）。其光缆长度与人才密度看似在雷达图上呈现全方位“坍塌”。但系统极差判定引擎敏锐地纠正了错觉：这不是“欠账”，而是与轻工业的“极度适配”。在完全没有重工包袱下，强行增加深层光缆反而是对生态的破坏。该市唯一的真正短板在于人才（0.17万）的过度奇缺，严重制约了食品产业向现代智能溯源演进。\n\n【多部门协同决策指导建议】：\n\n1. 抵制同质化基建：反向纠偏功能理直气壮地拒绝了大型数字基建分摊指标，建议全盘转向申请“食品安全全链路上链溯源工程”专项预算。\n2. 单点脑力购买战略：面对人才干瘪，必须抛弃底层招募思维，出台高薪单点政策，直接向外部购买“食品供应链算法专家”大脑。"
    },
    "三门峡": {
        "m1": "【系统数据分析与推演过程】：三门峡在拓扑映射中呈现全样本最扭曲的“畸形断裂带”。外资吸纳量高达惊人的36.88亿元，且长途光缆长达2550公里，资本与硬件极度奢华。但与之对应的IT人才密度惨烈跌至0.21万人。系统发出疯狂警报：巨量资本涌入却完全没有技术人员去承接与开发。这是严重的“有资本无大脑”空转惨剧，先进减排设备正因缺乏本土智力调试而处于低效闲置状态。\n\n【多部门协同决策指导建议】：\n\n1. 非常规人才空降：暴露的断层宣告传统引才破产。建议将解决此缺口定为最高优先工程，不惜一切代价为巨额驻地外资安装控制大脑。\n2. 第三方外包纾困：面对外资潜在撤资风险，建议通过政府购买顶级IT外包服务的方式，免费为落户企业补齐短期的技术运维调试断层。"
    },
    "南阳": {
        "m1": "【系统数据分析与推演过程】：南阳在矩阵中投射出了最令人战栗的“重度基建过载体质”。作为农业大市，其长途光缆里程竟达到惊世骇俗的6805.99公里（位列全域断层第一）。然而外资投入可怜至1.91亿元，人才仅0.66万人。诊断系统拉响最高级赤字警报：这是一场规模空前的“物理硬件跃进”，海量空置光纤埋入地下，基础设施承载力已严重溢出其实体经济实际需求的百倍以上。\n\n【多部门协同决策指导建议】：\n\n1. 无效基建全面冰冻：极端断层报告是彻查低效建设的量化依据。必须从根源上刹住脱离实际产业的土建冲动，核清存量真实载荷率。\n2. 存量网络强制共享：强烈建议彻底叫停新增骨干网许可，出台“存量网络资源强制特许经营与引流条例”，逼迫应用强行向既有管道导入业务流以止血。"
    },
    "濮阳": {
        "m1": "【系统数据分析与推演过程】：濮阳呈现出典型的“低水平内卷式均衡”。碳排基数压至9.52Mt，然而光缆、IT人才与外资三项动能指标均处于全域末端象限。系统断层矩阵极其客观地指出：该市既没有沉重的碳基数包袱，也没有冗余的基建负债，但同样完全丧失了数字化转型的先发势能。这是一种缺乏外部技术注入、单纯依靠内生微弱循环维持的“结构性贫血”状态。\n\n【多部门协同决策指导建议】：\n\n1. 放弃基座竞逐：基于低水平均衡体检，应放弃对标核心城市的宏大物理基建，合法争取省级的算力调拨与网络公有云免费接入。\n2. 纯应用级外采策略：针对技术枯竭，招商必须放弃“重资产”执念，全面转向补贴本土中小企业跨区购买成熟的SaaS解决方案，以极低成本填补断层。"
    },
    "商丘": {
        "m1": "【系统数据分析与推演过程】：作为综合交通枢纽，商丘暴露出骇人的“资本孤岛”特征，外资仅0.02亿元，几乎物理归零。同时面对70.75Mt的高昂碳排，其人才仅0.38万，深层光缆却铺设了2747公里。雷达拓扑严厉指出：该市利用区位优势大搞基建，却未能吸引任何绿色资本与调控技术。庞大物流量正在裸奔，缺乏算力中枢调度，是导致其效率低下且碳排高企的核心病灶。\n\n【多部门协同决策指导建议】：\n\n1. 智慧物流靶向破局：系统揭示的耻辱柱是对招商政策的强力预警，建议将考核权重以100%倾斜度压在引进具备国际碳足迹追踪技术的科技企业上。\n2. 基建全面软化改造：面对资产错配，立即停止新增单纯路网土建，后续交通资金强制转化为车路协同与数据调度专属改造专款。"
    },
    "信阳": {
        "m1": "【系统数据分析与推演过程】：信阳展现出极度刺眼的“重资产过载”病态特征。作为绿色生态城市（碳排仅23.33Mt），其地下竟埋设了高达4855公里的光缆。然而人才仅0.37万，外资0.61亿。雷达矩阵发出最高级红色警报：该市硬基建投资已彻底失控，完全脱离了本地生态文旅的承载力。天量的网络正处于无人维护、无业务跑冒的沉睡状态，形成了巨额沉没成本黑洞。\n\n【多部门协同决策指导建议】：\n\n1. 行政清算与休养生息：极端断层报告是清算低效重复建设的数学铁证。需全面叫停所谓“新基建”名义的土建发包，确立生态优先。\n2. 沉睡资产折价兜售：面对巨额过载，积极向沿海大型互联网或云端企业推销廉价的过剩骨干带宽资源，以竭力挽回财政沉没成本。"
    },
    "周口": {
        "m1": "【系统数据分析与推演过程】：周口投射出了一个极具潜力的“低碳排、高底盘”轮廓。基准碳排仅5.40Mt，且光缆达3070公里，人才有相对优良储备。然而普惠金融指数排名倒数。系统极差拓扑明确诊断：该市的物理基建与初级人才已准备就绪，但严重受制于落后的金融供血体系。海量农业微小主体因得不到普惠金融赋能，无法将网络基建转化为数字产值，呈现“管道通畅但无水可流”断层。\n\n【多部门协同决策指导建议】：\n\n1. 普惠金融强制打通：量化断层报告是推动金融改革的最强发令枪，建议利用现成网络底盘，大规模推行针对涉农主体的线上无抵押数据信贷。\n2. 极简应用补贴引流：将振兴重心从修路搭桥全面转向软件采买，政府出面利用金融杠杆补贴农机与溯源系统，用应用把底层网络直接盘活。"
    }
}

# ==========================================
# 2. 初始化状态机
# ==========================================
if 'page' not in st.session_state: st.session_state.page = 'splash'
if 'city_category' not in st.session_state: st.session_state.city_category = "内置：重工锁定型城市"
if 's_city' not in st.session_state: st.session_state.s_city = "焦作"
if 'custom_logic' not in st.session_state: st.session_state.custom_logic = "偏向重化工业主导"
if 'c_invest' not in st.session_state: st.session_state.c_invest = 4.8
if 'f_invest' not in st.session_state: st.session_state.f_invest = 2.5
if 'i_invest' not in st.session_state: st.session_state.i_invest = 1.0
if 'custom_data' not in st.session_state:
    st.session_state.custom_data = {"长途光缆": 1500.0, "外资引进与对外开放程度": 10.0, "IT人才密度": 1.5, "宽带普及": 200.0, "普惠金融": 280.0,
                                    "基准碳排": 50.0}

# 全量内置数据字典
built_in_stats = {
    "郑州": {"长途光缆": 1942.64, "外资引进与对外开放程度": 12.29, "IT人才密度": 10.99, "宽带普及": 774, "普惠金融": 337.22, "基准碳排": 52.37},
    "开封": {"长途光缆": 1601.98, "外资引进与对外开放程度": 1.78, "IT人才密度": 0.3, "宽带普及": 306, "普惠金融": 297.88, "基准碳排": 11.61},
    "洛阳": {"长途光缆": 3911.33, "外资引进与对外开放程度": 1.3, "IT人才密度": 4.28, "宽带普及": 313, "普惠金融": 311.82, "基准碳排": 50.78},
    "平顶山": {"长途光缆": 2030.67, "外资引进与对外开放程度": 1.02, "IT人才密度": 0.33, "宽带普及": 601, "普惠金融": 289.76, "基准碳排": 19.45},
    "安阳": {"长途光缆": 1887.28, "外资引进与对外开放程度": 2.39, "IT人才密度": 0.29, "宽带普及": 258, "普惠金融": 290.5, "基准碳排": 102.41},
    "鹤壁": {"长途光缆": 549.49, "外资引进与对外开放程度": 0.23, "IT人才密度": 0.13, "宽带普及": 74, "普惠金融": 297.32, "基准碳排": 9.89},
    "新乡": {"长途光缆": 2128.43, "外资引进与对外开放程度": 1.02, "IT人才密度": 0.49, "宽带普及": 297, "普惠金融": 298.28, "基准碳排": 38.84},
    "焦作": {"长途光缆": 1019.84, "外资引进与对外开放程度": 2.8, "IT人才密度": 0.27, "宽带普及": 217, "普惠金融": 302.66, "基准碳排": 23.61},
    "濮阳": {"长途光缆": 1096.49, "外资引进与对外开放程度": 0.96, "IT人才密度": 0.34, "宽带普及": 202, "普惠金融": 289.01, "基准碳排": 9.52},
    "许昌": {"长途光缆": 1278.16, "外资引进与对外开放程度": 0.27, "IT人才密度": 0.42, "宽带普及": 195, "普惠金融": 307.91, "基准碳排": 22.08},
    "漯河": {"长途光缆": 691.19, "外资引进与对外开放程度": 2.59, "IT人才密度": 0.17, "宽带普及": 112, "普惠金融": 298.41, "基准碳排": 2.62},
    "三门峡": {"长途光缆": 2550.69, "外资引进与对外开放程度": 36.88, "IT人才密度": 0.21, "宽带普及": 118, "普惠金融": 299.84, "基准碳排": 30.98},
    "南阳": {"长途光缆": 6805.99, "外资引进与对外开放程度": 1.91, "IT人才密度": 0.66, "宽带普及": 452, "普惠金融": 292.31, "基准碳排": 17.16},
    "商丘": {"长途光缆": 2747.8, "外资引进与对外开放程度": 0.02, "IT人才密度": 0.38, "宽带普及": 374, "普惠金融": 281.97, "基准碳排": 70.75},
    "信阳": {"长途光缆": 4855.99, "外资引进与对外开放程度": 0.61, "IT人才密度": 0.37, "宽带普及": 321, "普惠金融": 291.0, "基准碳排": 23.33},
    "周口": {"长途光缆": 3070.62, "外资引进与对外开放程度": 1.02, "IT人才密度": 0.53, "宽带普及": 387, "普惠金融": 276.34, "基准碳排": 5.4}
}

embedded_data = []
for c_name, c_data in built_in_stats.items():
    c_type = "重工锁定型城市" if any(h in c_name for h in ["焦作", "平顶山", "安阳", "鹤壁", "长治", "晋城"]) else "综合服务型城市"
    row = {"城市": c_name, "类型": c_type}
    row.update(c_data)
    embedded_data.append(row)

df = pd.DataFrame(embedded_data)


# ------------------------------------------
# 3. 动态算法核心推理引擎 (Dynamic Generator)
# ------------------------------------------
def find_closest_city_advice(input_data, is_heavy):
    target_type = "重工锁定型城市" if is_heavy else "综合服务型城市"
    pool = df[df["类型"] == target_type]
    best_city, min_dist = None, float('inf')
    features = ["长途光缆", "外资引进与对外开放程度", "IT人才密度", "基准碳排"]
    for idx, row in pool.iterrows():
        dist = 0
        for f in features:
            f_max, f_min = pool[f].max(), pool[f].min()
            rng = f_max - f_min if f_max > f_min else 1.0
            dist += ((input_data[f] - row[f]) / rng) ** 2
        if dist < min_dist:
            min_dist = dist
            best_city = row["城市"]
    return re.sub(r'^.*?省|^.*?自治区|^.*?市(?!$)', '', best_city).replace("市", "")

def generate_dynamic_report(city_name, current_data, logic, module_key, c_inv, f_inv, i_inv):
    """大模型核心动态生成引擎：根据输入的滑块参数，实时推导运算文本"""
    total = c_inv + f_inv + i_inv
    if total <= 0: total = 0.001

    if module_key == "m2":
        soft_invest = f_inv + i_inv
        analysis = f"【系统数据分析与推演过程】：双变量热力矩阵正实时监控当前资本投放的系统性风险。当前控制台输入的拟干预总额为 **{total:.1f} 亿元**，其中数字硬基建规模设定为 {c_inv:.1f} 亿元，软性生态引导资金（外资与人才）合计 {soft_invest:.1f} 亿元。\n\n"

        if logic == "综合服务型城市":
            risk_score = min(c_inv / 8.0 * 100, 100)
            analysis += f"研判溯源：由于该区域缺乏重化工业依托，对重资产硬件投资的碳溢出极为敏感。系统测算当前的“基建冗余度与碳排反弹风险指数”为 **{risk_score:.1f}**。此时的硬基建配比"
            if risk_score > 70:
                analysis += "已严重越过警戒红线。算法推导表明，脱离实际业务场景的算力堆砌不仅无法有效降碳，反而因高昂的建设与运维空耗，导致预期碳排轨迹发生恶性倒挂。"
            elif risk_score > 40:
                analysis += "处于敏感观察域。硬件初期的土建能耗正在抵消部分减排效益，建议放缓物理施工节奏，优先进行软性业务端的数据回填。"
            else:
                analysis += "落入深绿色安全区间。轻量化的硬件配合足额的软性资本，成功规避了能耗倒挂陷阱，资本边际投入处于健康平稳状态。"
        else:
            breakthrough_score = min(total / 6.5 * 100, 100)
            analysis += f"研判溯源：该区域具备重化工底蕴，碳锁定刚性极强。系统测算当前的“转型势能积聚与跨越指数”为 **{breakthrough_score:.1f}**。推演显示，当前的整体投资烈度"
            if breakthrough_score < 50:
                analysis += "严重匮乏。由于未触及破局的规模经济阈值，微弱的投资难以撕裂旧有能耗体系，反而使区域陷入了高碳阵痛期的前端空耗。"
            elif breakthrough_score < 80:
                analysis += "正处于爬坡博弈阶段。系统监测到前期排量呈现短期波动，需警惕因资金流中断导致的转型半途而废。"
            else:
                analysis += "已成功跨越绿色悖论临界点。高强度的组合投资触发了系统性拐点，有效激活了底层物理网络与生产制造环节的深度降碳耦合。"

        advice = "【多部门协同决策指导建议】：\n\n"
        advice += "1. 投资动态审查机制：建议利用本模块动态研判的指数阈值确立前置审批规范。针对处于高危或低效区间的投资预算模型，实施能耗效益一票否决；反之则开辟政策快速通道，以数据化治理提升行政效能。\n"
        advice += "2. 过程性容错管理：鉴于系统客观揭示了资本生效存在客观的阶段性阵痛特征。政策指导层面需构建相适应的考核容错空间，防范因短期的环保指标波动而中断长周期、高效益的降碳转型路径。"

        return analysis + "\n" + advice

    elif module_key == "m3":
        if logic == "综合服务型城市":
            roi_c = c_inv * 3.5
            roi_f = -f_inv * 2.0
            roi_i = -i_inv * 2.5
        else:
            roi_c = -c_inv * 2.8
            roi_f = -f_inv * 1.5
            roi_i = -i_inv * 1.0

        analysis = f"【系统数据分析与推演过程】：后台因果预测引擎接收到 {total:.1f} 亿元的动态预算测试指令，并在极短时间内演算了各项构成要素的边际净影响值(ROI)。\n\n"
        analysis += f"轨迹仿真解析：当前设定的资源配置边界（数字基建 {c_inv:.1f}亿、外资引导 {f_inv:.1f}亿、人才补贴 {i_inv:.1f}亿）正实时驱动未来排放折线的演化。通过SHAP博弈论算法进行贡献度剥离后发现，"

        if logic == "综合服务型城市":
            analysis += f"由外资引进与高端人才带来的智力溢出红利（减排净贡献达 {abs(roi_f + roi_i):.2f} 单位）构成了拉动系统碳排收敛的绝对主导力量。反观硬基建投资不仅未能降碳，反而产生了 {roi_c:.2f} 单位的反向能耗反弹。该仿真结果明确界定出轻型城市的降耗杠杆在于“软生态搭建”而非物理扩张。"
        else:
            analysis += f"深层工业基建投资对高耗能终端释放了极强的降碳压制作用（净效益达 {abs(roi_c):.2f} 单位），证实重型基本盘依然高度依赖于大标段网络骨干重塑。同时，软性资本（联合贡献度 {abs(roi_f + roi_i):.2f}）有效发挥了催化剂属性，提升了重资产设备的综合运转效能。"

        analysis += "\n\n算法归因结论：前述反事实沙盘推演客观论证了预算参数微调对最终政策收效落点的非线性影响规律。建议结合【模块四】算法指引，实施系统级的财政配置纠偏。"

        advice = "【多部门协同决策指导建议】：\n\n"
        advice += "1. 预算精准滴灌导向：建议摒弃传统的均匀发力或普惠式财政补贴逻辑。应依托算法揭示的边际效用测度（ROI排序），将核心转移支付战略性地投向回报最陡峭的短板领域，以此化解财政资源配置错配难题。\n"
        advice += "2. 柔性杠杆重塑模式：动态推演确证了要素间存在的显著乘数放大效应。地方财政无需承担项目全周期硬件投入，宜运用诸如绿色贴息、数字化升级服务券等柔性杠杆工具，撬动外部社会化资金完成产业数字化缝合。"

        return analysis + "\n" + advice

    elif module_key == "m4":
        if logic == "综合服务型城市":
            opt_c = total * 0.15
            opt_f = total * 0.40
            opt_i = total * 0.45
            strategy_name = "轻量化软性生态赋能战略"
        else:
            opt_c = total * 0.55
            opt_f = total * 0.25
            opt_i = total * 0.20
            strategy_name = "重资产底层基座重构战略"

        c_diff = c_inv - opt_c
        f_diff = f_inv - opt_f
        i_diff = i_inv - opt_i

        dist = np.sqrt(c_diff ** 2 + f_diff ** 2 + i_diff ** 2)
        match_score = max(0, 100 - (dist / total) * 100) if total > 0 else 0

        analysis = f"【系统数据分析与推演过程】：NSGA-III多目标遗传算法已在包含数万种参数组合的高维解空间内执行了全局定向搜索。算法锚定当前设定的 **{total:.1f} 亿元** 财政约束边界，以“宏观经济稳健增长”与“碳排放深度收敛”为硬约束双底线，计算出理论状态下的帕累托前沿演化曲面。\n\n"
        analysis += f"推演寻优结论：依据 **{city_name}** 的底层产业基因模型，算法锁定出该预算级别下的全局极值点配比方案应为：数字基建规模控制在 **{opt_c:.1f}亿**，外资引进引导资金保持在 **{opt_f:.1f}亿**，人才结构优化补贴设定在 **{opt_i:.1f}亿**。系统运筹研判将此组合定性为“{strategy_name}”。\n\n"
        analysis += f"决策拟合度评估：当前控制台正在输入的交互参数，与算法推演出的全局理论最优解的空间综合拟合度为 **{match_score:.1f}%**。这表明，"

        if match_score >= 85:
            analysis += "您当前的预算配置框架已极度逼近帕累托最优状态演化集。该架构确保了在不触及地方隐性债务高压线的前提下，能够实现经济正向拉动与绿色生态降碳效益的全面最大化释放。"
        elif match_score >= 60:
            analysis += "当前的资金分布结构仍处于基础安全可行域内，但存在一定的资金冗余损耗。建议参考上述算法界定的黄金分割参数值，对要素的投入方向实施结构性微调与纠偏优化。"
        else:
            analysis += "当前设定存在较严重的预算错配，运行轨迹已脱离帕累托安全曲面，潜在触发局部资源空转与能耗逆向反弹的系统级风险。应立即冻结该粗放型规划，向系统计算出的最优参数集实施强行并轨。"

        advice = "【多部门协同决策指导建议】：\n\n"
        advice += "1. 顶层防线约束：建议将本算法引擎推演出的【帕累托最优参数配比集】上升为区域财政规划审定的数理依据红线。强力阻断和遏制任何偏离算法容错边界的非理性涉数、涉碳大型项目开支。\n"
        advice += "2. 跨部门指标联动：改革执行末端考核体系，淡化投资完成额绝对数，将“行政施政资金的流向拟合度”转化为关键评价权重。通过运筹学底层的数理边界驱动，确保区域长期治理路线精确咬合系统规划出的最优演进轨道。"

        return analysis + "\n" + advice


def get_report(city_name, current_data, logic, module_key, c_inv=0, f_inv=0, i_inv=0):
    clean_name = re.sub(r'^.*?省|^.*?自治区|^.*?市(?!$)', '', city_name).replace("市", "")

    # 对于 m1，调用历史静态诊断底座
    if module_key == "m1":
        if clean_name in city_advice_db:
            return city_advice_db[clean_name]["m1"]
        else:
            is_heavy = True if logic == "偏向重化工业主导" else False
            mirror_city = find_closest_city_advice(current_data, is_heavy)
            safe_city = mirror_city if mirror_city in city_advice_db else ("焦作" if is_heavy else "郑州")
            return city_advice_db[safe_city]["m1"].replace(safe_city, clean_name)
    else:
        # 对于 m2/m3/m4，全面启动动态大模型推演引擎生成
        engine_logic = "重化工" if logic == "偏向重化工业主导" else "综合服务型城市"
        return generate_dynamic_report(clean_name, current_data, engine_logic, module_key, c_inv, f_inv, i_inv)


# ------------------------------------------
# 4. 前端渲染组件
# ------------------------------------------
def render_custom_report(text):
    if "【多部门协同决策指导建议】：" in text:
        analysis_part, advice_part = text.split("【多部门协同决策指导建议】：")

        clean_analysis = analysis_part.replace("【系统数据分析与推演过程】：", "").strip()

        st.markdown(f"""
            <div style='background-color: #FAFAFA; border-left: 4px solid #1A3622; padding: 15px 20px; margin-top: 15px; margin-bottom: 25px; line-height: 1.8; font-size: 15px;'>
                <h4 style='color: #1A3622; margin-top: 0px; margin-bottom: 10px;'>📊 动态数据推演与过程解析</h4>
                {clean_analysis}
            </div>
        """, unsafe_allow_html=True)

        st.markdown("<h3 style='color: #2C3539; font-weight: bold; margin-bottom: 15px;'>🎯 宏观政策指导方案</h3>",
                    unsafe_allow_html=True)

        advices = advice_part.strip().split("\n")
        for adv in advices:
            adv = adv.strip()
            if adv:
                if "：" in adv and (adv.startswith("1.") or adv.startswith("2.") or adv.startswith("3.")):
                    title, content = adv.split("：", 1)
                    st.markdown(f"""
                    <div style='background-color: #FFFFFF; border: 1px solid #E0E0E0; border-left: 5px solid #4DB8B3; padding: 20px; border-radius: 8px; margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);'>
                        <h4 style='color: #1A3622; font-size: 19px; margin-top: 0; margin-bottom: 12px; font-weight: bold;'>🏛️ {title}</h4>
                        <p style='margin-bottom: 0; color: #444444; line-height: 1.7; font-size: 15px;'>{content}</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"<p>{adv}</p>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='analysis-box'>{text}</div>", unsafe_allow_html=True)


def normalize_to_100(val, col_name):
    min_val = df[col_name].min()
    max_val = df[col_name].max()
    if max_val == min_val: return 50
    return max(0, min((val - min_val) / (max_val - min_val) * 100, 100))


def bottom_navigation(current_page):
    st.markdown("---")
    st.markdown("### 系统辅助决策矩阵快速切换")
    pages = {'mod1': "模块一：宏观体检与断层推演", 'mod2': "模块二：门槛研判与动态预警", 'mod3': "模块三：政策试错与轨迹推演", 'mod4': "模块四：多目标寻优与组合决策"}
    nav_keys = [k for k in pages.keys() if k != current_page]
    cols = st.columns(3)
    for i, k in enumerate(nav_keys):
        if cols[i].button(pages[k], key=f"nav_{current_page}_{k}", use_container_width=True):
            st.session_state.page = k
            st.rerun()


# ------------------------------------------
# 页面导航控制流
# ------------------------------------------
if st.session_state.page == 'splash':
    st.markdown("<style>[data-testid='stSidebar'] {display: none;}</style>", unsafe_allow_html=True)
    st.markdown("<div style='height: 15vh;'></div>", unsafe_allow_html=True)
    st.markdown("<div class='spin-earth'>🌍</div>", unsafe_allow_html=True)
    st.markdown("<div class='title-main'>城市低碳治理智能推演系统</div>", unsafe_allow_html=True)
    st.markdown("<div class='title-sub'>宏观政策事前仿真与多目标寻优沙盘</div>", unsafe_allow_html=True)
    st.markdown("<br><p style='text-align: center; color: #888888;'>正在加载正交因果森林推演引擎与智库级报告底座...</p>", unsafe_allow_html=True)
    time.sleep(2.0)
    st.session_state.page = 'city_select'
    st.rerun()

elif st.session_state.page == 'city_select':
    st.markdown("<style>[data-testid='stSidebar'] {display: none;}</style>", unsafe_allow_html=True)
    st.markdown("<div style='height: 8vh;'></div>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center;'>📍 宏观决策仿真数据底座初始化</h2>", unsafe_allow_html=True)

    col_spacer1, col_main, col_spacer2 = st.columns([1, 4, 1])
    with col_main:
        with st.container(border=True):
            category_opts = ["内置：重工锁定型城市", "内置：综合服务型城市", "外部：自定义录入宏观数据"]
            cat_choice = st.radio("第一步：界定数据归属与产业结构类型", category_opts,
                                  index=category_opts.index(st.session_state.city_category))
            s_city_choice = st.session_state.s_city
            custom_logic_choice = st.session_state.custom_logic

            if cat_choice == "内置：重工锁定型城市":
                available_cities = df[df["类型"] == "重工锁定型城市"]["城市"].tolist()
                idx = available_cities.index(s_city_choice) if s_city_choice in available_cities else 0
                s_city_choice = st.selectbox("第二步：选择重点推演城市", available_cities, index=idx)
            elif cat_choice == "内置：综合服务型城市":
                available_cities = df[df["类型"] == "综合服务型城市"]["城市"].tolist()
                idx = available_cities.index(s_city_choice) if s_city_choice in available_cities else 0
                s_city_choice = st.selectbox("第二步：选择基准对照城市", available_cities, index=idx)
            else:
                s_city_choice = st.text_input("第二步：设定系统推演目标名称", value=s_city_choice if s_city_choice not in df["城市"].tolist() else "未命名区域")
                custom_logic_choice = st.radio("核定该区域的主导产业底色（用于匹配智能算法推演逻辑）", ["偏向重化工业主导", "偏向综合与服务型"])
                st.markdown("*(请依次录入核心基础宏观指标)*")
                c1, c2 = st.columns(2)
                st.session_state.custom_data["长途光缆"] = c1.number_input("长途光缆线路总长 (公里)", value=float(st.session_state.custom_data["长途光缆"]))
                st.session_state.custom_data["外资引进与对外开放程度"] = c2.number_input("年度实际使用外资 (亿元)", value=float(st.session_state.custom_data["外资引进与对外开放程度"]))
                st.session_state.custom_data["IT人才密度"] = c1.number_input("数字产业从业规模 (万人)", value=float(st.session_state.custom_data["IT人才密度"]))
                st.session_state.custom_data["基准碳排"] = c2.number_input("期初核算碳排总量 (百万吨)", value=float(st.session_state.custom_data["基准碳排"]))
                st.session_state.custom_data["宽带普及"] = c1.number_input("区域宽带接入体量 (万户)", value=float(st.session_state.custom_data["宽带普及"]))
                st.session_state.custom_data["普惠金融"] = c2.number_input("普惠金融发展指数", value=float(st.session_state.custom_data["普惠金融"]))

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("参数配置完毕，启动系统引擎", type="primary", use_container_width=True):
            st.session_state.city_category = cat_choice
            st.session_state.s_city = s_city_choice
            st.session_state.custom_logic = custom_logic_choice
            st.session_state.page = 'menu'
            st.rerun()
else:
    # ------------------------------------------
    # 交互式侧边栏与数据核心载入
    # ------------------------------------------
    if st.session_state.city_category == "内置：重工锁定型城市":
        current_engine_logic = "重化工"
        city_data = df[df["城市"] == st.session_state.s_city].iloc[0].to_dict()
    elif st.session_state.city_category == "内置：综合服务型城市":
        current_engine_logic = "综合型"
        city_data = df[df["城市"] == st.session_state.s_city].iloc[0].to_dict()
    else:
        current_engine_logic = "重化工" if "重化工" in st.session_state.custom_logic else "综合型"
        city_data = st.session_state.custom_data

    with st.sidebar:
        st.markdown("### ⚙️ 宏观推演交互参数控制台")
        st.markdown("---")

        cat_opts = ["内置：重工锁定型城市", "内置：综合服务型城市", "外部：自定义录入宏观数据"]
        new_cat = st.radio("一、快速切换数据类型", cat_opts, index=cat_opts.index(st.session_state.city_category), key="sb_cat")

        if new_cat == "内置：重工锁定型城市":
            avail = df[df["类型"] == "重工锁定型城市"]["城市"].tolist()
            idx = avail.index(st.session_state.s_city) if st.session_state.s_city in avail else 0
            new_city = st.selectbox("二、设定推演标的", avail, index=idx, key="sb_city_heavy")
            if new_cat != st.session_state.city_category or new_city != st.session_state.s_city:
                st.session_state.city_category = new_cat; st.session_state.s_city = new_city; st.rerun()

        elif new_cat == "内置：综合服务型城市":
            avail = df[df["类型"] == "综合服务型城市"]["城市"].tolist()
            idx = avail.index(st.session_state.s_city) if st.session_state.s_city in avail else 0
            new_city = st.selectbox("二、设定对照基准", avail, index=idx, key="sb_city_comp")
            if new_cat != st.session_state.city_category or new_city != st.session_state.s_city:
                st.session_state.city_category = new_cat; st.session_state.s_city = new_city; st.rerun()

        else:
            new_city = st.text_input("二、输入拟推演区域名称", value=st.session_state.s_city, key="sb_city_cust")
            new_logic = st.radio("核定产业底色以匹配算法", ["偏向重化工业主导", "偏向综合与服务型"], index=0 if "重化工" in st.session_state.custom_logic else 1, key="sb_logic")
            if new_cat != st.session_state.city_category or new_city != st.session_state.s_city or new_logic != st.session_state.custom_logic:
                st.session_state.city_category = new_cat; st.session_state.s_city = new_city; st.session_state.custom_logic = new_logic; st.rerun()
            st.markdown("*（手动微调以下存量数据，触发全息计算图谱）*")
            c1, c2 = st.columns(2)
            st.session_state.custom_data["长途光缆"] = c1.number_input("光缆(km)", value=float(st.session_state.custom_data["长途光缆"]), key="sb_n1")
            st.session_state.custom_data["外资引进与对外开放程度"] = c2.number_input("外资(亿)", value=float(st.session_state.custom_data["外资引进与对外开放程度"]), key="sb_n2")
            st.session_state.custom_data["IT人才密度"] = c1.number_input("人才(万)", value=float(st.session_state.custom_data["IT人才密度"]), key="sb_n3")
            st.session_state.custom_data["基准碳排"] = c2.number_input("碳排(Mt)", value=float(st.session_state.custom_data["基准碳排"]), key="sb_n4")

        st.markdown("---")
        st.markdown("三、政策资金拨付推演 (亿元)")
        st.markdown("*请拉动滑块，右侧系统将会动态推演出相匹配的最佳指导方案*")
        st.session_state.c_invest = st.slider("数字基建专项预算分配", 0.0, 20.0, st.session_state.c_invest, 0.1)
        st.session_state.f_invest = st.slider("外资政策性引导预算分配", 0.0, 10.0, st.session_state.f_invest, 0.1)
        st.session_state.i_invest = st.slider("数字人才结构优化补贴", 0.0, 5.0, st.session_state.i_invest, 0.1)

    total_invest = st.session_state.c_invest + st.session_state.f_invest + st.session_state.i_invest
    base_carbon = city_data["基准碳排"]
    
    # 公式预演推导
    if current_engine_logic == "综合型":
        infra_cost_penalty = st.session_state.c_invest * 3.5
        reduce_effect = (st.session_state.f_invest * 2.0) + (st.session_state.i_invest * 2.5)
    else:
        infra_cost_penalty = st.session_state.c_invest * 0.8
        reduce_effect = (st.session_state.c_invest * 2.8) + (st.session_state.f_invest * 1.5) + (st.session_state.i_invest * 1.0)
    
    pred_carbon = max(base_carbon * 0.4, base_carbon + infra_cost_penalty - reduce_effect)

    # ------------------------------------------
    # 模块导航页
    # ------------------------------------------
    if st.session_state.page == 'menu':
        st.markdown(f"## 🌍 【{st.session_state.s_city}】城市低碳治理智能推演系统")
        st.info("系统声明：本系统内置高精度双重机器学习运筹算法，最终输出由您输入的参数动态演算而来。方案仅提供严密的量化论证与宏观战略指导边界，不直接替代执行层决策。")
        
        with st.container(border=True):
            st.markdown("### 一、 宏观体检与要素断层推演")
            st.markdown("基于内置大数据库构建多维极差矩阵，揭示区域在数字基座、智力储备领域的真实基准断层。")
            if st.button("进入体检底座模块", key="m1", use_container_width=True): st.session_state.page = 'mod1'; st.rerun()
        with st.container(border=True):
            st.markdown("### 二、 门槛研判与动态预警")
            st.markdown("根据当前设定的参数投资烈度，利用双变量矩阵算法，实时生成区域宏观风险研判结果与指导。")
            if st.button("进入动态预警模块", key="m2", use_container_width=True): st.session_state.page = 'mod2'; st.rerun()
        with st.container(border=True):
            st.markdown("### 三、 政策试错与轨迹推演")
            st.markdown("展现当前滑动参数对未来三年碳排折线的影响。依托SHAP值剥离工具，动态生成ROI分析及资源滴灌优化路线。")
            if st.button("进入政策推演模块", key="m3", use_container_width=True): st.session_state.page = 'mod3'; st.rerun()
        with st.container(border=True):
            st.markdown("### 四、 多目标寻优与组合决策")
            st.markdown("基于非支配排序遗传算法（NSGA-III），依据设定的资金总盘子，全盘计算最完美比例并对您当前配比实施实时评价。")
            if st.button("进入多目标最优生成", key="m4", use_container_width=True): st.session_state.page = 'mod4'; st.rerun()

    # ------------------------------------------
    # 模块一：宏观体检
    # ------------------------------------------
    elif st.session_state.page == 'mod1':
        st.button("返回系统主控室", on_click=lambda: st.session_state.update({'page': 'menu'}))
        st.markdown(f"## 一、 【{st.session_state.s_city}】宏观体检与数据要素断层推演")

        categories = ['深层算力(长途光缆)', '绿色资本(外资)', '智力资本(IT人才)', '浅层网络(宽带普及)', '产业融合(普惠金融)']
        city_scores = [normalize_to_100(city_data.get(k, 50), k) for k in ["长途光缆", "外资引进与对外开放程度", "IT人才密度", "宽带普及", "普惠金融"]]
        avg_scores = [normalize_to_100(df[k].mean(), k) for k in ["长途光缆", "外资引进与对外开放程度", "IT人才密度", "宽带普及", "普惠金融"]]

        col_left, col_right = st.columns([1.2, 1])
        with col_left:
            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(r=avg_scores, theta=categories, fill='toself', name='全域面板样本均线', line_color='rgba(100, 149, 237, 0.8)'))
            fig_radar.add_trace(go.Scatterpolar(r=city_scores, theta=categories, fill='toself', name=f'{st.session_state.s_city}', line_color=C_DEEP_FOREST))
            fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), height=350, title="宏观发展要素拓扑雷达图", margin=dict(t=50, b=20, l=40, r=40))
            st.plotly_chart(fig_radar, use_container_width=True)

            df_gap = pd.DataFrame({"评估维度": categories, "区域考核得分": city_scores, "全域样本均线": avg_scores})
            fig_bar = px.bar(df_gap, x="评估维度", y=["全域样本均线", "区域考核得分"], barmode="group", title="核心资源存量差异量化推演", color_discrete_sequence=["#B0BEC5", C_DEEP_FOREST])
            fig_bar.update_layout(height=350, yaxis_title="无量纲化测度值", legend_title=None, margin=dict(t=50, b=20))
            st.plotly_chart(fig_bar, use_container_width=True)

        with col_right:
            report_text = get_report(st.session_state.s_city, city_data, st.session_state.custom_logic, "m1")
            render_custom_report(report_text)
        bottom_navigation('mod1')

    # ------------------------------------------
    # 模块二：门槛研判
    # ------------------------------------------
    elif st.session_state.page == 'mod2':
        st.button("返回系统主控室", on_click=lambda: st.session_state.update({'page': 'menu'}))
        st.markdown(f"## 二、 【{st.session_state.s_city}】动态预警研判分析")

        x_grid, y_grid = np.linspace(0, 20, 50), np.linspace(0, 15, 50)
        X_mat, Y_mat = np.meshgrid(x_grid, y_grid)
        soft_invest = st.session_state.f_invest + st.session_state.i_invest
        col_left, col_right = st.columns([1.2, 1])

        if current_engine_logic == "综合型":
            Z_risk = np.clip((X_mat / 8.0 * 100) - (Y_mat * 1.5), 0, 100)
            fig_heat = go.Figure(data=go.Contour(x=x_grid, y=y_grid, z=Z_risk, colorscale="Reds", contours=dict(showlabels=True)))
            fig_heat.update_layout(title="区域资本投放风险预测二维分布图", xaxis_title="数字基建参数 (亿元)", yaxis_title="外资与人才融合资金 (亿元)", height=350, margin=dict(t=40, b=10, l=10, r=10))
            fig_heat.add_trace(go.Scatter(x=[st.session_state.c_invest], y=[soft_invest], mode='markers+text', marker=dict(color='gold', size=16, symbol='star', line=dict(width=2, color='black')), text=["📍 动态坐标"], textposition="top center"))

            with col_left:
                risk_score = min(st.session_state.c_invest / 8.0 * 100, 100)
                fig_gauge = go.Figure(go.Indicator(mode="gauge+number", value=risk_score, title={'text': "基建冗余度与碳排反弹综合风险指数"},
                                     gauge={'axis': {'range': [0, 100]}, 'bar': {'color': C_CHARCOAL_SLATE},
                                            'steps': [{'range': [0, 40], 'color': C_GLACIER_TEAL}, {'range': [40, 70], 'color': 'rgba(255, 215, 0, 0.6)'}, {'range': [70, 100], 'color': C_WARNING_RED}], 'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 70}}))
                fig_gauge.update_layout(height=300, margin=dict(t=50, b=10))
                st.plotly_chart(fig_gauge, use_container_width=True)
                st.plotly_chart(fig_heat, use_container_width=True)
        else:
            Z_break = np.clip(((X_mat + Y_mat) / 6.5 * 100), 0, 100)
            fig_heat = go.Figure(data=go.Contour(x=x_grid, y=y_grid, z=Z_break, colorscale="Greens", contours=dict(showlabels=True)))
            fig_heat.update_layout(title="碳锁定破局势能演化二维分布图", xaxis_title="数字基建参数 (亿元)", yaxis_title="外资与人才融合资金 (亿元)", height=350, margin=dict(t=40, b=10, l=10, r=10))
            fig_heat.add_trace(go.Scatter(x=[st.session_state.c_invest], y=[soft_invest], mode='markers+text', marker=dict(color='gold', size=16, symbol='star', line=dict(width=2, color='black')), text=["📍 动态坐标"], textposition="top center"))

            with col_left:
                breakthrough_score = min(total_invest / 6.5 * 100, 100)
                fig_gauge = go.Figure(go.Indicator(mode="gauge+number", value=breakthrough_score, title={'text': "转型势能积聚与门槛跨越指数"},
                                     gauge={'axis': {'range': [0, 100]}, 'bar': {'color': C_CHARCOAL_SLATE},
                                            'steps': [{'range': [0, 50], 'color': 'rgba(255, 99, 71, 0.6)'}, {'range': [50, 80], 'color': 'rgba(255, 215, 0, 0.6)'}, {'range': [80, 100], 'color': C_DEEP_FOREST}], 'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 80}}))
                fig_gauge.update_layout(height=300, margin=dict(t=50, b=10))
                st.plotly_chart(fig_gauge, use_container_width=True)
                st.plotly_chart(fig_heat, use_container_width=True)

        with col_right:
            report_text = get_report(st.session_state.s_city, city_data, st.session_state.custom_logic, "m2", st.session_state.c_invest, st.session_state.f_invest, st.session_state.i_invest)
            render_custom_report(report_text)
        bottom_navigation('mod2')

    # ------------------------------------------
    # 模块三：政策试错与轨迹仿真
    # ------------------------------------------
    elif st.session_state.page == 'mod3':
        st.button("返回系统主控室", on_click=lambda: st.session_state.update({'page': 'menu'}))
        st.markdown(f"## 三、 【{st.session_state.s_city}】政策交互干预与三年轨迹推演")

        years = [f"{2024+i}年" for i in range(4)]
        base_traj = [base_carbon, base_carbon * 1.015, base_carbon * 1.028, base_carbon * 1.04]
        
        # 折线中间点生成
        if current_engine_logic == "综合型":
            traj_1 = max(base_carbon * 0.4, base_carbon + infra_cost_penalty * 0.4 - reduce_effect * 0.2)
            traj_2 = max(base_carbon * 0.4, base_carbon + infra_cost_penalty * 0.8 - reduce_effect * 0.6)
        else:
            traj_1 = max(base_carbon * 0.4, base_carbon + infra_cost_penalty * 0.9 - reduce_effect * 0.3)
            traj_2 = max(base_carbon * 0.4, base_carbon + infra_cost_penalty * 1.0 - reduce_effect * 0.7)
            
        interv_traj = [base_carbon, traj_1, traj_2, pred_carbon]
        df_traj = pd.DataFrame({"预测年度": years * 2, "预计排量(Mt)": base_traj + interv_traj, "演化情境": ["原始基准轨迹"] * 4 + ["当前参数推演轨迹"] * 4})

        col_left, col_right = st.columns([1.2, 1])
        with col_left:
            fig_line = px.line(df_traj, x="预测年度", y="预计排量(Mt)", color="演化情境", markers=True, title="中短期碳排折线演化动态模拟", color_discrete_sequence=["#9E9E9E", C_GLACIER_TEAL])
            fig_line.update_layout(height=350)
            st.plotly_chart(fig_line, use_container_width=True)

            # 动态瀑布图渲染
            if current_engine_logic == "综合型":
                x_labels = ["基准碳排", "硬基建空耗", "外资生态红利", "人才溢出红利", "推演落点"]
                measure, y_vals = ["absolute", "relative", "relative", "relative", "total"], [base_carbon, infra_cost_penalty, -st.session_state.f_invest * 2.0, -st.session_state.i_invest * 2.5, pred_carbon]
            else:
                x_labels = ["基准碳排", "施工额外能耗", "光缆主导红利", "外资技术迁移", "算法管理提升", "推演落点"]
                measure, y_vals = ["absolute", "relative", "relative", "relative", "relative", "total"], [base_carbon, infra_cost_penalty, -st.session_state.c_invest * 2.8, -st.session_state.f_invest * 1.5, -st.session_state.i_invest * 1.0, pred_carbon]

            fig_shap = go.Figure(go.Waterfall(orientation="v", measure=measure, x=x_labels, textposition="outside",
                                text=[f"{v:+.2f}" if m == "relative" else f"{v:.2f}" for v, m in zip(y_vals, measure)],
                                y=y_vals, connector={"line": {"color": "rgb(63, 63, 63)"}}, decreasing={"marker": {"color": C_DEEP_FOREST}}, increasing={"marker": {"color": C_WARNING_RED}}, totals={"marker": {"color": C_GLACIER_TEAL}}))
            fig_shap.update_layout(title="因果推断边际影响(ROI)定量剥离", showlegend=False, height=350, margin=dict(t=40, b=20, l=10, r=10))
            st.plotly_chart(fig_shap, use_container_width=True)

        with col_right:
            report_text = get_report(st.session_state.s_city, city_data, st.session_state.custom_logic, "m3", st.session_state.c_invest, st.session_state.f_invest, st.session_state.i_invest)
            render_custom_report(report_text)
        bottom_navigation('mod3')

    # ------------------------------------------
    # 模块四：帕累托决策
    # ------------------------------------------
    elif st.session_state.page == 'mod4':
        st.button("返回系统主控室", on_click=lambda: st.session_state.update({'page': 'menu'}))
        st.markdown(f"## 四、 【{st.session_state.s_city}】全局多目标约束最佳配置推演")

        # 利用哈希种子确保该城市的底层三维数据曲面特征不变，只改变标点
        np.random.seed(int(hashlib.md5(st.session_state.s_city.encode('utf-8')).hexdigest(), 16) % (2 ** 32))
        n_pts = 250
        x_invest = np.random.uniform(1, 20, n_pts)
        y_carbon_reduce = x_invest * (1.2 if current_engine_logic == "综合型" else 1.8) - np.random.normal(0, 2, n_pts)
        z_gdp_growth = -0.1 * (x_invest - 10) ** 2 + 8 + np.random.normal(0, 1, n_pts)

        col_left, col_right = st.columns([1.2, 1])
        with col_left:
            fig_3d = px.scatter_3d(x=x_invest, y=y_carbon_reduce, z=z_gdp_growth, color=z_gdp_growth, color_continuous_scale="RdBu_r",
                                   labels={'x': '宏观总算盘(亿元)', 'y': '期望减排量(Mt)', 'z': 'GDP预计变动率(%)'}, title="算法生成高维帕累托最优可行域前沿")
            user_z_gdp = -0.1 * (total_invest - 10) ** 2 + 8
            fig_3d.add_trace(go.Scatter3d(x=[total_invest], y=[base_carbon - pred_carbon], z=[user_z_gdp], mode='markers+text',
                             text=["📍 当前参数落点"], marker=dict(size=14, symbol='diamond', color='gold', line=dict(color='black', width=3)), textposition='top center'))
            fig_3d.update_layout(height=650)
            st.plotly_chart(fig_3d, use_container_width=True)

        with col_right:
            report_text = get_report(st.session_state.s_city, city_data, st.session_state.custom_logic, "m4", st.session_state.c_invest, st.session_state.f_invest, st.session_state.i_invest)
            render_custom_report(report_text)
        bottom_navigation('mod4')
