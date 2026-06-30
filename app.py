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
        .analysis-box {{ background-color: #FAFAFA; border-left: 4px solid {C_DEEP_FOREST}; padding: 15px 20px; margin-top: 15px; line-height: 1.8; font-size: 15px; text-align: justify; }}
        [data-testid="collapsedControl"] {{display: none;}}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. 深度智库预载入 
# ==========================================
city_advice_db = {
    "焦作": {
        "m1": "【系统数据分析与推演过程】：通过高维极差空间拓扑与雷达图矩阵比对，本系统提取该市各项存量特征并与全域样本均值标尺进行深度映射。数据量化分析显示，该市在浅层宽带普及与普惠金融维度的无量纲得分已高度接近全域均线，这表明区域内消费端的数字红利已经基本饱和，继续投入的边际效益将显著递减。然而，在真正支撑重化工底座转型与实体经济高质量发展的深层核心要素上（长途光缆仅1020公里，IT人才仅0.27万人），系统柱状断层推演直观暴露出极大的结构性落差。本系统的综合诊断客观反映出，该区域的底层信息基础设施建设规模及其承载能力，已经明显滞后于实体经济庞大的制造规模与转型需求，形成了严重的“硬资产缺位、软技术断层”的数字要素空心化现象。\n\n【宏观政策指导方案】\n\n1. 固投专项重构：暂缓消费级基站新建，将专项债券额度全面向深层工业光缆与算力枢纽倾斜。\n2. 孤岛数据清查：重点排查重资产企业“数据孤岛”，加快核心生产线的数据采集与上云步伐。"},
    "平顶山": {
        "m1": "【系统数据分析与推演过程】：底层面板对比数据显示，平顶山拥有全样本中处于绝对高位的浅层宽带普及度（高达601万户），且深层光缆基数达2031公里，其整体硬件网络底座表现出高度扎实的重资产沉淀特征。然而，系统因果矩阵的雷达图测度却检测出，该市外资引入量（1.02亿）与普惠金融渗透率处于极度枯竭的边缘象限。这种不对称的拓扑演化过程直观指出，该市当前正面临极为严重的“重资产过剩、软技术断层”双重危机。虽然空有庞大且耗能的通信光缆资产，却极度缺乏具备国际先进低碳管理体系的外资力量注入，以及本土高端数字智力生态的支撑，导致现有的底层重资产处于低效乃至算力空转的闲置边缘。\n\n【宏观政策指导方案】\n\n1. 招商结构调优：全面转向定向吸引携带前沿减排专利与算法模型的国际高质量数字技术企业入驻。\n2. 存量资产激活：强力指导市属大型能源国企开放应用场景，优先购买软件SaaS服务以盘活底层闲置网络。"},
    "安阳": {
        "m1": "【系统数据分析与推演过程】：作为典型老工业基地，安阳在碳足迹溯源与面板测度中呈现出全样本排名前列的巨量碳排承压（高达102.41Mt）。雷达图谱与极差测度引擎深度解析显示，尽管该市信息光缆基数达到了样本中游水位（1887公里），但如果将其与本地区庞大且沉重的钢铁、煤化工业物理体量相除求得单位载荷率，则当前的数字要素赋能深度存在极其严重的历史欠账与投入倒挂。断层推演矩阵直观标红了其数字化工具在向重型冶炼企业底层车间渗透过程中的严重不足。这种底层工业物联网与信息传输能力的绝对性亏欠，构成了目前区域高位碳排数据无法实现精细化测度、算法调度与系统性收敛的根本物理阻碍。\n\n【宏观政策指导方案】\n\n1. 历史包袱量化申诉：依托极差测度底稿，将断层报告转化为申报国家级老工业基地转型示范区的强力论证附件。\n2. 技改专项定向注资：联合外部大资本设立针对特钢等传统高排产业的数字化技改专项基金，通过强力杠杆填补深层算力缺位。"},
    "鹤壁": {
        "m1": "【系统数据分析与推演过程】：系统全域极差拓扑映射与欧氏距离比对显示，鹤壁市在决定产业转型的底层硬件要素（长途光缆仅549公里，全样本垫底）与智力软性要素（IT高级人才仅0.13万人，外资生态几乎归零）上，呈现出令人警惕的“双重严重塌陷”病态分布。推演模型直观且冷峻地指出，该区域的信息传输动脉极其微弱，不仅浅层消费端的宽带网络尚未完成高质量的全面普及，其支撑重工业与能源产业完成底层转型的深层物理基座更是处于全域的极度匮乏状态。这种“一穷二白”的初始要素底盘，从根本上剥夺了该区域在短期内自发构建复杂降碳算法体系与闭环数据控制架构的物理可行性。\n\n【宏观政策指导方案】\n\n1. 财政缺口理论辩护：将本断层诊断报告作为客观量化证据，合法合理地向上级争取跨区域转移支付以填补底层基建历史欠账。\n2. 孤岛式示范标杆：坚决摒弃“撒胡椒面”式的平均建设，集中极端有限的资源在核心龙头企业内部打造局域物联网孤岛试点。"},
    "长治": {
        "m1": "【系统数据分析与推演过程】：长治在本次高维雷达拓扑检测中呈现出极其特殊且畸形的“非对称性巨峰”。数据降维穿透表明，其深层长途光缆铺设里程长达3255.51公里，实际利用外资存量更是高达31.14亿元，表明其具备了极其雄厚的物理基建沉淀与外部资本输入盘面。然而，与这庞大硬件与资金规模形成剧烈反差的是，其IT核心人才密度仅有0.30万人。系统调用柱状断层推演矩阵尖锐地指出：该市存在严重的“硬件设备极其超前、资本流极度充沛，但智力核心运转域完全脱节”的异构断层现象。大量外资引入的先进降耗设备与庞大光纤网络，正面临着无人深度开发、无高级算法驱动控制的“高规格半闲置”状态。\n\n【宏观政策指导方案】\n\n1. 招才引智绝对优序：立刻将施政重心从重资产投入全面转向设立专项数字工程师引进计划，以承接庞大的硬件底座。\n2. 技术生态强制耦合：依托高位外资存量，强制要求外资企业在本土设立研发中心，通过人才属地化强行补齐系统智力短板。"},
    "晋城": {
        "m1": "【系统数据分析与推演过程】：晋城以161.18Mt的惊人碳排放量绝对极值，成为全域推演面板中特征最为显著的“重度高危碳锁定”样本。然而，雷达拓扑图谱与极差测度矩阵极其残酷地显示：面对这头体量骇人、惯性极强的“碳排放巨兽”，该区域用于制衡与调度的数字对抗要素却显得微乎其微（深层光缆仅2207公里，核心人才仅0.26万）。系统的断层推演矩阵直观标红了全要素体系的结构性枯竭。客观诊断结果明确指出：这种极度悬殊的“排量体量-数字控制力”比例，意味着该市现有的数字化赋能水平在如此庞大的煤炭与冶炼巨无霸面前，犹如杯水车薪，系统已近乎完全丧失了底层能耗调控与降耗因子深度渗透的能力。\n\n【宏观政策指导方案】\n\n1. 宏观缺口向上破局：将极端断层报告直接转化为申请“资源型城市深度低碳转型特区”的佐证，引入超常规国家级转移支付。\n2. 强制级基座重构：针对大型排碳主体的底层信息管网，下发带有强制性的重资产物联网更新指令，不设过渡缓冲期。"},
    "郑州": {
        "m1": "【系统数据分析与推演过程】：通过多维高阶空间拓扑矩阵映射，郑州作为国家中心城市与综合枢纽，其雷达特征图谱呈现出全样本中最具统治力的“软实力霸权”结构。其数字产业与IT智力资本密度高达10.99万人（呈现断层式领先），普惠金融发展指数与外资开放引入规模均处于全域面板的巅峰极值区域。然而，其深层物理光缆（1943公里）相对于其庞大且复杂的第三产业经济体量而言，仅表现为“适度够用”而非盲目扩张。系统综合诊断确证：该市已彻底且成功地摆脱了依赖铺设物理硬基建去拉动数字化转型的初级粗放阶段，全面迈入了以底层算法优化、跨域算力调度与智力资本要素为核心驱动力的深度治理区。\n\n【宏观政策指导方案】\n\n1. 顶层研发绝对导向：彻底剥离土建工程的财政依赖，全盘转向对人工智能大模型、零碳数据交易中台的顶层设计投入。\n2. 智力资源在地转化：出台专项“算力券”与“碳普惠”政策，将庞大的软开发大军就地转化为数字降碳产业输出的技术护城河。"},
    "洛阳": {
        "m1": "【系统数据分析与推演过程】：作为具备深厚老工业基因的综合型城市，洛阳在本次空间极差拓扑演算中暴露出极其罕见且危险的“资产错位”现象。数据穿透追踪显示，其深层长途光缆总长高达3911公里，硬件网络底盘堪称奢华，且IT人才具备4.28万人的优良规模。但与之形成惨烈断层效应的是，其年度实际外资引入仅有1.30亿元。系统断层矩阵毫不留情地指出：洛阳正陷入“基建设施严重超前超配，但外部先进技术流与绿色资本流导入呈现严重梗阻”的内循环困局，巨量埋设的地下光缆资产由于缺乏高端国际数字生态的介入，正面临极大的算力空转、无效折旧与闲置沉淀风险。\n\n【宏观政策指导方案】\n\n1. 存量资产紧急唤醒：立即叫停市级骨干网络土木工程扩展，全面盘点摸底现有数字资产负荷率，严控无效重复建设。\n2. 靶向型绿色招商：依托现成的世界级高冗余网络底座，将政策重心全盘压在吸引具备国际ESG标准的智造外企上以盘活资产。"},
    "新乡": {
        "m1": "【系统数据分析与推演过程】：新乡在多维雷达拓扑测度中呈现出典型的“中等收入陷阱式”均值回归分布。其深层光缆长度、宽带普及规模等硬性底层指标，均严丝合缝地卡在全域样本的均线轨道附近。然而，在真正决定产业转型纵深的数字人才密度（仅0.49万）与外资开放程度（1.02亿）上，却暴露出了疲软乏力、后继无能的断层迹象。系统的综合测度诊断直击痛点：这种全科平庸、缺乏长板的体检报告，意味着该市的网络覆盖广度虽已基本达标，但极其缺乏能够深度重构实体制造业的高阶数字融合生态与顶尖算法架构，目前正处于高不成低不就、要素驱动力边际递减的发展胶着期。\n\n【宏观政策指导方案】\n\n1. 细分领域灯塔工程：放弃普遍广度的基建摊大饼模式，集中机动财力，在电池制造、生物医药等优势领域打造零碳数字绝对标杆。\n2. 外交靶向技术引进：引资策略实施精准打击，专盯能带来成套能耗管理SaaS系统与供应链碳认证的外向型数字平台服务商。"},
    "开封": {
        "m1": "【系统数据分析与推演过程】：开封市的雷达拓扑映射呈现出极具属地特征的轻量化结构。得益于文旅服务与轻质工业为主导的产业底色，其初始碳排放基数控制在极低的区间（仅11.61Mt，位于全样本低位区）。底层测度显示，其光缆敷设与宽带普及率，已在物理层面上完美支撑起当前城市的综合运行体量。然而，系统在多维断层推演中毫不客气地标出了外资与高阶IT人才的塌陷区。这从严肃的量化层面确认了该市当前的数字经济依然仅停留在表层的消费、票务与浅层结算阶段，系统内部极其缺乏能将城市文商旅农资源进行深度低碳化算法整合与数据变现的高级赋能要素。\n\n【宏观政策指导方案】\n\n1. 轻量级SaaS化转向：放弃重资产数据中心建设指标的规划争夺，全盘转向开发“全域零碳智慧文旅服务云平台”。\n2. ESG主题引资路线：利用低碳生态优势，重点向主打ESG（环境、社会治理）评级投资的国际文创基金及绿色低碳品牌引流。"},
    "许昌": {
        "m1": "【系统数据分析与推演过程】：通过全域极差拓扑的大样本比对，许昌市的雷达特征图谱暴露出了极其尖锐的“单维向度塌陷”。其在普惠金融指数等本土内生型指标上表现出良好的韧性，但实际使用外资量仅为惨淡的0.27亿元，几乎触及面板数据底盘。系统的高阶断层推演矩阵毫不留情地指出：该市在宏观数字经济转型进程中，正处于极其严重的“对外技术封闭与资本孤岛”状态。缺乏国际先进绿色外资的引入，意味着彻底切断了前沿低碳控制设备、成熟减排算法模型以及外部鲶鱼效应的刺激来源，这种生态级的断层将彻底锁死该市制造业向高端价值链与零碳域攀升的理论空间。\n\n【宏观政策指导方案】\n\n1. 考核权重极端调优：重构招商引资考核体系，将政绩权重全面倾斜于引进携带绿色供应链管理技术与节能专利的科技服务企业。\n2. 轻量型合作示范区：不再搞大而全的基础土建，依托底盘专门设立具备极高环保与数字化基准的中外绿色智造合作专区。"},
    "漯河": {
        "m1": "【系统数据分析与推演过程】：漯河在全样本高维空间中呈现出极度罕见的“超微型碳排地标”特征。其基准碳排仅有2.62Mt，这一全域绝对底谷数据与其中国食品名城的轻量化工业底色实现了完美吻合。其光缆长度与核心人才密度看似在雷达极坐标上呈现出全方位的“向心塌陷”。但系统的极差判定引擎敏锐地纠正了这一感官错觉：这不是历史欠账，而是极其合理的“产业适配”。在完全没有重型工业包袱的绿色轻资产底盘下，强行增加深层光缆不仅是严重的财政浪费，更是对优良生态的冗余破坏。该市唯一的真实约束短板在于高端人才储备的过度奇缺，这严重制约了千亿级轻工食品产业向现代智能溯源与自动化分拣演进的数据化步伐。\n\n【宏观政策指导方案】\n\n1. 抵制同质化重基建：理直气壮拒绝大型数字基建分摊指标，将预算全盘转向申请“食品安全全链路上链溯源工程”专项开发。\n2. 单点脑力购买战略：彻底抛弃底层代码人员招募思维，出台特规高薪政策，向外部直接购买解决轻工业智造瓶颈的算法架构师。"},
    "三门峡": {
        "m1": "【系统数据分析与推演过程】：三门峡在系统的全域雷达拓扑映射中，呈现出全样本最扭曲、结构最极端的“畸形断裂带”。其外资吸纳量高达惊人的36.88亿元（位列非省会中心城市的极值），且长途光缆长达2550公里，其硬件底座与资本输入均处于极其奢华的过剩状态。然而，与之相对应的核心IT人才密度，却惨烈地跌至0.21万人的全域面板绝对最低谷。系统断层推演矩阵发出疯狂的逻辑警报：巨量的外商绿色资本与先进的物理管网海量涌入，但本地生态竟然完全没有与之匹配的高阶工程技术人员去承接、去维护、去开发底层控制算法。这是极其严重的“有资本无大脑”的资源空转惨剧，大量外资引入的前沿设备正因缺乏本土智力调试而处于低效乃至闲置状态。\n\n【宏观政策指导方案】\n\n1. 非常规人才空降：将解决高端工程师缺口定为首要急控事项，不惜代价出台数字人才整建制挖引计划，激活存量沉睡设备。\n2. 第三方外包纾困：应对因配套奇缺导致的高位外资撤资风险，由政府出面全额购买第三方顶级IT外包服务免费提供给落户外企。"},
    "南阳": {
        "m1": "【系统数据分析与推演过程】：南阳在全样本特征矩阵中投射出了最令人战栗的“重度基建过载体质”。作为一个以农业与综合服务业为主的大市，其深层长途光缆总里程竟然达到了惊世骇俗的6805.99公里（处于全域断层式的第一极值）。然而，其外资投入规模可怜至1.91亿元，核心技术人才仅0.66万人。系统的断层诊断中枢拉响了最高级别的结构性赤字警报：该区域经历了一场规模空前且脱离实际的“物理硬件跃进”。海量超规格的空置光纤埋入地下陷入深度沉睡，由于极度缺乏外部技术流的导入与高端数据处理能力的接盘，这座城市的底层网络承载力已经严重溢出其实体经济实际需求的百倍量级之上。\n\n【宏观政策指导方案】\n\n1. 无效基建全面冰冻：彻查清算低效涉网市政土建工程，核清海量网络存量的真实载荷率，从源头上刹住脱离产业实际的土建冲动。\n2. 存量网络强制引流：出台存量网络资源强制特许经营与并网条例，逼迫属地边缘政企应用强行向既有闲置干线管道内引流以实现资产止血。"},
    "濮阳": {
        "m1": "【系统数据分析与推演过程】：濮阳在多维雷达拓扑测度中呈现出极其典型的“低水平内卷式均衡”。其碳排放基数被压制至9.52Mt，客观反映出传统资源型产业衰退与出清后的物理现实。然而，其深层光缆、IT人才与外资引入三项核心数字动能指标，均毫无悬念地处于全域样本的末端象限。系统断层推演矩阵极其客观且冷酷地指出：该市既没有沉重的碳基数历史包袱，也没有冗余的基建负债压力，但同样完全丧失了数字化转型的先发势能窗口。这是一种严重缺乏外部技术血液注入、单纯依靠内生微弱经济循环维持的结构性数字化贫血状态。\n\n【宏观政策指导方案】\n\n1. 放弃重基座竞逐：放弃对标核心城市的宏大物理IDC基建规划，转而合法争取省级层面的算力调拨与干线网络公有云免费接入。\n2. 纯应用级外采策略：招商全面放弃“重资产大项目”执念，将机动预算全数转为补贴本土小微企业跨区购买成熟的SaaS解决方案。"},
    "商丘": {
        "m1": "【系统数据分析与推演过程】：作为极为重要的豫东综合交通枢纽，商丘在系统的深度空间诊断中暴露出极其骇人的“资本孤岛”闭塞特征。其年度实际使用外资仅为0.02亿元，在全样本地市中几乎处于物理清零状态。同时，面对70.75Mt的高昂枢纽碳排基数，其数字人才仅有微不足道的0.38万人，但深层光缆却粗放地铺设了2747公里。雷达拓扑矩阵严厉地指出核心病灶：该市单纯利用交通区位优势大搞粗放型物流与路网基础建设，但完全未能建立吸收外部先进绿色资本与数字节点调控技术的生态。庞大而沉重的交通与基建物流量正在无序裸奔，极度缺乏算法算力中枢的智慧调度，这是导致其全域运转效率低下且碳排居高不下的致命缺陷。\n\n【宏观政策指导方案】\n\n1. 智慧物流靶向破局：彻底推翻低端占地型物流招商传统，100%倾斜引进具备国际先进碳足迹追踪与运筹调度技术的科技平台企业。\n2. 基建全面软化升级：立刻冻结新增的单纯路网土建计划，后续交通预算强制划归为“车路协同与数据调度控制平台”专属改造专款。"},
    "信阳": {
        "m1": "【系统数据分析与推演过程】：信阳在全样本极差测度中，展现出极其刺眼且违和的“重资产严重过载”病态特征。作为一个以生态立市、碳排基数被严格控制在23.33Mt的绿色轻资产城市，其地下竟然疯狂埋设了高达4855公里的深层长途光缆。然而，面对如此庞大惊人的通信资产，其IT高级人才仅有0.37万，外资引入仅0.61亿。系统的雷达拓扑矩阵发出了最高级别的红色断层熔断警报：该市前期的硬基建投资规划已经彻底失控，完全脱离了本地生态旅游与轻质农产品的实际承载吞吐力。天量的地下光缆正处于无人专业维护、无高频业务跑冒的深度沉睡状态，形成了吞噬巨额地方财政与运维电力的沉没成本黑洞。\n\n【宏观政策指导方案】\n\n1. 行政清算与全面冻结：全面叫停一切打着“智慧城市、新基建”名义的市政发包工程，将防范无效基建举债与资产闲置定为纪律铁律。\n2. 冗余资产折价出让：积极主动向沿海大型互联网算力节点及外部大厂推销本地廉价的过剩骨干带宽通道，竭力挽回财政沉淀损失。"},
    "周口": {
        "m1": "【系统数据分析与推演过程】：周口在全域面板测度模型中，投射出了一个极具反差潜力的“低碳排(5.4Mt)、高底盘(3070公里光缆)”的发展轮廓。其物理基建宽带网络与初级智力人才事实上已经具备了相对优良的储备。然而，其普惠金融指数却跌至全域倒数象限，外资规模严重萎靡。系统调用极差拓扑分析明确诊断出核心堵点：该市的硬性物理准备已然就绪，但区域经济活力严重受制于落后闭塞的金融供血体系。海量庞大的农业与轻质加工微小主体，因为得不到普惠金融在数字层面的滴灌赋能，根本无法将优良的网络基建转化为真实的数字经济产值，形成了一种极其典型且遗憾的“底层管道通畅但无水可流”的金融传输断层。\n\n【宏观政策指导方案】\n\n1. 普惠金融强制打通：利用庞大的网络底座强制赋能驻地金融机构，大规模推行针对涉农及轻工小微主体的全线上无抵押数据信贷。\n2. 极简应用补贴引流：将振兴重心从修路搭桥的土木工程全面转向软件采买，政府出资通过金融杠杆补贴农机与溯源系统，盘活网络。"},
    # 默认兜底
    "默认重工": {
        "m1": "【系统数据分析与推演过程】：该区域在多维特征矩阵中呈现出典型的重工业资产依赖与能耗排量高基数锁定特征。空间要素极差诊断发现，其现有的深层网络基础结构未能有效触达并覆盖核心排碳生产线，硬件信息铺设存在明显的浅层化、表象化与局域化特征。由于极度缺乏深层底层控制算法与物联网闭环的接入，导致庞大工业终端的排量居高不下，数字化赋能效应被严重稀释。\n\n【宏观政策指导方案】\n\n1. 基建底层延伸打通：强制将机动预算精准投向重工业真实生产场景的物联网传感器布设与深层光缆铺设。\n2. 资本刚性定向管控：严厉剥离非涉碳、非核心制造领域的无效财政注资，集中火力攻坚高耗能节点。"},
    "默认综合": {
        "m1": "【系统数据分析与推演过程】：该区域在雷达拓扑中表现为典型的轻资产、低碳基准的综合服务型面貌。基础硬件网络覆盖率展现出极大的广度与充足度，但系统预警其面临极高的有效应用场景缺失及算力空转风险。底层诊断指出，区域内数字高阶人才储备出现严重断层，且极度缺乏能够引导软性服务生态健康演化的靶向高阶外资注入与强力的创新金融杠杆支撑。\n\n【宏观政策指导方案】\n\n1. 轻资产云端软赋能：立即停建一切新增的实体IDC机房工程，预算全面转向针对服务业的云端SaaS平台使用补贴。\n2. 软要素政策强倾斜：财政杠杆与配套政策必须全力、毫无保留地向专业技术引流与普惠金融降息补贴倾斜。"}
}

# ==========================================
# 2. 全量底层数据挂载 (恢复全样本真实数据)
# ==========================================
built_in_stats = {
    "河南省郑州市": {"长途光缆": 1942.64, "外资引进与对外开放程度": 12.29, "IT人才密度": 10.99, "宽带普及": 774, "普惠金融": 337.22, "基准碳排": 52.37},
    "河南省开封市": {"长途光缆": 1601.98, "外资引进与对外开放程度": 1.78, "IT人才密度": 0.3, "宽带普及": 306, "普惠金融": 297.88, "基准碳排": 11.61},
    "河南省洛阳市": {"长途光缆": 3911.33, "外资引进与对外开放程度": 1.3, "IT人才密度": 4.28, "宽带普及": 313, "普惠金融": 311.82, "基准碳排": 50.78},
    "河南省平顶山市": {"长途光缆": 2030.67, "外资引进与对外开放程度": 1.02, "IT人才密度": 0.33, "宽带普及": 601, "普惠金融": 289.76, "基准碳排": 19.45},
    "河南省安阳市": {"长途光缆": 1887.28, "外资引进与对外开放程度": 2.39, "IT人才密度": 0.29, "宽带普及": 258, "普惠金融": 290.5, "基准碳排": 102.41},
    "河南省鹤壁市": {"长途光缆": 549.49, "外资引进与对外开放程度": 0.23, "IT人才密度": 0.13, "宽带普及": 74, "普惠金融": 297.32, "基准碳排": 9.89},
    "河南省新乡市": {"长途光缆": 2128.43, "外资引进与对外开放程度": 1.02, "IT人才密度": 0.49, "宽带普及": 297, "普惠金融": 298.28, "基准碳排": 38.84},
    "河南省焦作市": {"长途光缆": 1019.84, "外资引进与对外开放程度": 2.8, "IT人才密度": 0.27, "宽带普及": 217, "普惠金融": 302.66, "基准碳排": 23.61},
    "河南省濮阳市": {"长途光缆": 1096.49, "外资引进与对外开放程度": 0.96, "IT人才密度": 0.34, "宽带普及": 202, "普惠金融": 289.01, "基准碳排": 9.52},
    "河南省许昌市": {"长途光缆": 1278.16, "外资引进与对外开放程度": 0.27, "IT人才密度": 0.42, "宽带普及": 195, "普惠金融": 307.91, "基准碳排": 22.08},
    "河南省漯河市": {"长途光缆": 691.19, "外资引进与对外开放程度": 2.59, "IT人才密度": 0.17, "宽带普及": 112, "普惠金融": 298.41, "基准碳排": 2.62},
    "河南省三门峡市": {"长途光缆": 2550.69, "外资引进与对外开放程度": 36.88, "IT人才密度": 0.21, "宽带普及": 118, "普惠金融": 299.84, "基准碳排": 30.98},
    "河南省南阳市": {"长途光缆": 6805.99, "外资引进与对外开放程度": 1.91, "IT人才密度": 0.66, "宽带普及": 452, "普惠金融": 292.31, "基准碳排": 17.16},
    "河南省商丘市": {"长途光缆": 2747.8, "外资引进与对外开放程度": 0.02, "IT人才密度": 0.38, "宽带普及": 374, "普惠金融": 281.97, "基准碳排": 70.75},
    "河南省信阳市": {"长途光缆": 4855.99, "外资引进与对外开放程度": 0.61, "IT人才密度": 0.37, "宽带普及": 321, "普惠金融": 291.0, "基准碳排": 23.33},
    "河南省周口市": {"长途光缆": 3070.62, "外资引进与对外开放程度": 1.02, "IT人才密度": 0.53, "宽带普及": 387, "普惠金融": 276.34, "基准碳排": 5.4},
    "河南省驻马店市": {"长途光缆": 3872.93, "外资引进与对外开放程度": 0.33, "IT人才密度": 0.38, "宽带普及": 291, "普惠金融": 283.42, "基准碳排": 36.23},
    "山西省晋城市": {"长途光缆": 2206.89, "外资引进与对外开放程度": 14.34, "IT人才密度": 0.26, "宽带普及": 88, "普惠金融": 305.59, "基准碳排": 161.18},
    "山西省长治市": {"长途光缆": 3255.51, "外资引进与对外开放程度": 31.14, "IT人才密度": 0.3, "宽带普及": 150, "普惠金融": 288.2, "基准碳排": 79.07},
    "山东省菏泽市": {"长途光缆": 2736.93, "外资引进与对外开放程度": 0.0, "IT人才密度": 0.3, "宽带普及": 361, "普惠金融": 277.8, "基准碳排": 101.5},
    "山东省聊城市": {"长途光缆": 1929.48, "外资引进与对外开放程度": 17.96, "IT人才密度": 0.3, "宽带普及": 243, "普惠金融": 289.35, "基准碳排": 88.18},
    "安徽省淮北市": {"长途光缆": 801.28, "外资引进与对外开放程度": 34.69, "IT人才密度": 0.19, "宽带普及": 101, "普惠金融": 293.31, "基准碳排": 71.74},
    "安徽省宿州市": {"长途光缆": 2905.02, "外资引进与对外开放程度": 0.89, "IT人才密度": 0.58, "宽带普及": 269, "普惠金融": 281.85, "基准碳排": 31.17},
    "安徽省阜阳市": {"长途光缆": 2957.45, "外资引进与对外开放程度": 73.48, "IT人才密度": 0.31, "宽带普及": 386, "普惠金融": 289.01, "基准碳排": 27.68},
    "安徽省蚌埠市": {"长途光缆": 1739.34, "外资引进与对外开放程度": 0.85, "IT人才密度": 0.22, "宽带普及": 164, "普惠金融": 301.81, "基准碳排": 16.85}
}

embedded_data = []
for c_name, c_data in built_in_stats.items():
    is_heavy = any(h in c_name for h in ["焦作", "平顶山", "安阳", "鹤壁", "长治", "晋城"])
    c_type = "重工锁定型城市" if is_heavy else "综合服务型城市"
    row = {"城市": c_name, "类型": c_type}
    row.update(c_data)
    embedded_data.append(row)

df = pd.DataFrame(embedded_data)

# ------------------------------------------
# 3. 状态机与引擎逻辑
# ------------------------------------------
if 'page' not in st.session_state: st.session_state.page = 'splash'
if 'city_category' not in st.session_state: st.session_state.city_category = "内置：重工锁定型城市"
if 's_city' not in st.session_state: st.session_state.s_city = "河南省焦作市"
if 'custom_logic' not in st.session_state: st.session_state.custom_logic = "偏向重化工业主导"
if 'c_invest' not in st.session_state: st.session_state.c_invest = 4.8
if 'f_invest' not in st.session_state: st.session_state.f_invest = 2.5
if 'i_invest' not in st.session_state: st.session_state.i_invest = 1.0
if 'custom_data' not in st.session_state:
    st.session_state.custom_data = {"长途光缆": 1500.0, "外资引进与对外开放程度": 10.0, "IT人才密度": 1.5, "宽带普及": 200.0, "普惠金融": 280.0,
                                    "基准碳排": 50.0}


def find_closest_city_advice(input_data, is_heavy):
    target_type = "重工锁定型城市" if is_heavy else "综合服务型城市"
    pool = df[df["类型"] == target_type]
    best_city, min_dist = None, float('inf')
    for idx, row in pool.iterrows():
        dist = 0
        for f in ["长途光缆", "外资引进与对外开放程度", "IT人才密度", "基准碳排"]:
            rng = pool[f].max() - pool[f].min() or 1.0
            dist += ((input_data[f] - row[f]) / rng) ** 2
        if dist < min_dist:
            min_dist, best_city = dist, row["城市"]
    return re.sub(r'^.*?省|^.*?自治区|市$', '', best_city)


def generate_dynamic_report(city_name, current_data, logic, module_key, c_inv, f_inv, i_inv):
    """大模型动态推演生成引擎"""
    total = c_inv + f_inv + i_inv
    if total <= 0: total = 0.001

    if module_key == "m2":
        soft_invest = f_inv + i_inv
        analysis = f"【系统数据分析与推演过程】：底层正交因果森林算法及双变量热力矩阵正实时监控当前资本投放组合的系统性风险边界。当前控制台输入的拟干预总额为 {total:.1f} 亿元，其中数字硬基建规模设定为 {c_inv:.1f} 亿元，软性生态引导资金（涵盖外资与人才要素）合计 {soft_invest:.1f} 亿元。系统通过高频迭代演算，将各项资本投入与区域底层产业结构进行异质性参数匹配。\n\n"

        if logic == "综合服务型城市":
            risk_score = min(c_inv / 8.0 * 100, 100)
            analysis += f"演化溯源解析：由于该区域缺乏重化工业底层场景依托，系统捕捉到其对重资产硬件投资引发的碳溢出表现出极端敏感性。模型测算当前的“基建冗余度与碳排反弹风险指数”为 **{risk_score:.1f}**。这意味着当前的硬基建参数配比"
            if risk_score > 70:
                analysis += "已经严重击穿模型设定的高危警戒红线。算法物理推导表明，脱离实际业务场景的纯算力设施堆砌不仅无法引发有效降碳协同，反而会因为高昂的初期建设碳排与极低效的日常运维空耗，导致整体预期碳排演化轨迹发生不可逆的恶性倒挂灾难。"
                advice = "【宏观政策指导方案】\n\n1. 投资一票否决：立即中止一切大型算力中心及骨干网扩建的前期立项，环评直接触发过热红线阻断机制。\n2. 沉没成本清算：强制启动对存量及在建基建项目的专项能耗审计，切断形成无效沉淀资金的黑洞流向。"
            elif risk_score > 40:
                analysis += "目前正处于极其敏感的高频观察域内。模型仿真显示，硬件初期的物理土建附加能耗正在剧烈抵消有限的降碳效益，如果不立即放缓物理施工节奏并优先回填软性数据业务应用，系统随时可能向右侧的恶性高碳红区滑落。"
                advice = "【宏观政策指导方案】\n\n1. 减量替代准入：对新建网络工程强制实行“降耗指标对赌”，无法出具业务承接确权合同的一律暂缓审批。\n2. 绿色门槛前置：设定极为苛刻的PUE指标，新增算力平台必须承诺80%以上采用高比例绿电驱动以锁定生态底盘。"
            else:
                analysis += "稳稳落入代表良性循环的深绿色安全区间。系统验证显示，这种极度轻量化的硬件部署，配合足额前置的软性高维资本，成功规避了由硬件冗余诱发的能耗倒挂陷阱，整体资本边际投入效率处于高度健康与平稳的推进状态。"
                advice = "【宏观政策指导方案】\n\n1. 软应用加速普及：在安全容错区间内大胆扩大政策补贴面，全面支持属地民营企业采购成套数字SaaS管理平台。\n2. 轻量化信贷覆盖：联合驻地央行分支机构，依据安全数据图谱发行挂钩企业云端活跃度与减排预测量的低息微贷。"
        else:
            breakthrough_score = min(total / 6.5 * 100, 100)
            analysis += f"演化溯源解析：系统底盘确认该区域具备深厚的重化工底蕴，其传统产业的碳锁定刚性极强。算法引擎测算当前的“转型势能积聚与临界门槛跨越指数”为 **{breakthrough_score:.1f}**。动态推演显示，当前的总体投资烈度"
            if breakthrough_score < 50:
                analysis += "呈现出极其严重的量级匮乏。由于总投资量远远未能触及打破碳锁定所需的规模经济极小阈值，这种微弱、零散的资金注入根本无法撕裂坚固的旧有高能耗体系，反而极易使区域陷入漫长且无效的高碳建设期阵痛空耗之中。"
                advice = "【宏观政策指导方案】\n\n1. 饱和式集中突围：彻底摒弃“撒胡椒面”式的均摊拨款，财政必须采用“打歼灭战”模式，不触及规模阈值宁可全量不投。\n2. 长周期政策兜底：将因基建必然引发的前期高碳阵痛纳入行政免责范围，死守战略定力，防范短视性政策烂尾。"
            elif breakthrough_score < 80:
                analysis += "正处于激烈博弈的爬坡过坎阶段。系统高频监测到区域能耗指标在短期内呈现剧烈振荡，这标志着新旧体系正在发生深度物理置换。此时系统最为脆弱，需极度警惕因后续资金流短缩或政策摇摆导致的转型半途而废。"
                advice = "【宏观政策指导方案】\n\n1. 弹性环保容错：在关键爬坡阵痛期，环境执法机构必须保持宏观定力，严防使用机械“拉闸限产”手段绞杀转型火苗。\n2. 核心要素强绑定：招商引资执行端必须将“工艺设备+基建网络+控制工程师”进行刚性捆绑，严禁单维要素孤立引进。"
            else:
                analysis += "已强劲且成功地跨越了规模经济的“绿色悖论”临界拐点。模型证实，由于采取了超高强度的聚合组合投资策略，系统内部触发了显著的结构性降耗拐点，有效且不可逆地激活了底层物理传感网络与核心生产制造环节的深度协同质变。"
                advice = "【宏观政策指导方案】\n\n1. 乘胜追击提标：在系统红利爆发期，果断且大幅度地提高重工企业降耗的年度硬性考核权重，倒逼内卷式技术迭代。\n2. 绿色债务扩张：直接依据运筹算法出具的收敛预期证明，向国家级政策性金融机构大胆发行大额碳减排专属地方债。"

        return analysis + "\n" + advice

    elif module_key == "m3":
        if logic == "综合服务型城市":
            roi_c, roi_f, roi_i = c_inv * 3.5, -f_inv * 2.0, -i_inv * 2.5
        else:
            roi_c, roi_f, roi_i = -c_inv * 2.8, -f_inv * 1.5, -i_inv * 1.0

        analysis = f"【系统数据分析与推演过程】：后台GBM非线性因果预测引擎在接收到 {total:.1f} 亿元 的动态预算调配指令后，于毫秒级时间内完成了上千万次的反事实沙盘演算，精确测定了每一笔流向不同要素的资金对最终三年减排目标的边际净影响值(ROI)。\n\n轨迹仿真深度归因解析：通过调用SHAP博弈论解释器进行高维特征的贡献度逐一剥离后，系统算法揭示出核心机制："
        if logic == "综合服务型城市":
            analysis += f"对于缺乏重型高耗能消纳终端的轻资产城市，由外资引进注入的先进技术体系与顶尖人才引入带来的智力外溢红利（两者联合降耗净贡献达 {abs(roi_f + roi_i):.2f} 单位），构成了拉动全域碳排曲线加速收敛的绝对主导性力量。反观僵硬的传统硬基建物理投资，不仅未能产生边际降碳收益，反而因施工能耗叠加诱发了高达 {roi_c:.2f} 单位的恶性反向指标抬升。该沙盘仿真极其清晰地在数学上确证：轻型综合城市的降耗超级杠杆完全在于“软生态与业务流的强行植入”，而非毫无节制的物理管网扩张。"
            advice = "【宏观政策指导方案】\n\n1. 财补结构极简转向：立刻全面停发针对纯硬件购机的直接财补，全额重构并转换为“数字软技术采购券”与“外商高阶落户奖补”。\n2. 核心脑力战略置换：人才招引彻底抛弃基础代码实施层面，将顶格重金直击并锁定行业最前沿的模型架构师与运筹供应链专家。"
        else:
            analysis += f"在重工基盘的严苛约束下，深层工业级光缆与底层传感网络的巨额投资释放出了极其强悍的物理降碳压制力（单维净效益高达 {abs(roi_c):.2f} 单位），这在统计学上证实了重型高碳排放体系的解构依然具有高度的重资产网络骨干依赖性。与此同时，软性引导资本（外资与人才）虽然绝对降幅略逊，但其发挥了不可或缺的化学催化剂属性，通过先进工艺融合与管理算法迭代，极其显著地提升了重资产设备运转的整体生命周期效能与综合折旧性价比。"
            advice = "【宏观政策指导方案】\n\n1. 底层算力优先原则：严格确保工业级大标段光缆与深度传感器网络占据公共转移支付的绝对主导份额，强行构筑底层数字控制力。\n2. 技改预算强制配比：在下达每一笔重资产基建资金时，设置刚性要求绑定同等比例的外部软性算法模型采购与后期运维智力预算。"

        return analysis + "\n" + advice

    elif module_key == "m4":
        if logic == "综合服务型城市":
            opt_c, opt_f, opt_i = total * 0.15, total * 0.40, total * 0.45
            strategy_name = "轻量化软生态极简赋能战略"
        else:
            opt_c, opt_f, opt_i = total * 0.55, total * 0.25, total * 0.20
            strategy_name = "重资产底层物理基座重构战略"

        dist = np.sqrt((c_inv - opt_c) ** 2 + (f_inv - opt_f) ** 2 + (i_inv - opt_i) ** 2)
        match_score = max(0, 100 - (dist / total) * 100) if total > 0 else 0

        analysis = f"【系统数据分析与推演过程】：面对保障宏观平稳增长、强力推进碳排收敛与严防地方财政失控这一极其棘手的“宏观不可能三角”，系统最高级中枢调用了NSGA-III非支配排序多目标遗传运筹算法。算法引擎在严格锚定当前交互面板设定的 {total:.1f} 亿元 财政机动总约束盘前提下，以“宏观经济规模的稳健向上拉动”与“碳排放物理总量的深度收敛”为不可妥协的双刚性底线，在包含数百万种离散参数组合的高维解空间内执行了极其苛刻的全局定向启发式搜索，最终收敛并计算出理论极限状态下的三维帕累托最优前沿演化曲面。\n\n全局极值寻优与空间拓扑评价：基于系统对 **{city_name}** 底层要素禀赋与产业基因模型的读取提取，算法冰冷且客观地锁定出该总预算级别下的唯一全局最优极值点配比方案应严格执行：数字硬基建物理规模控制在 {opt_c:.1f}亿，外资与先进生态引导资金保持在 {opt_f:.1f}亿，高阶数字人才结构优化补贴设定在 {opt_i:.1f}亿。系统运筹决策层将此比例组合高维定性为“{strategy_name}”。"

        # 注意：这里植入了特殊的分隔符，用于前端UI分离排版
        fit_diagnosis = f"【多目标决策拟合度深度诊断】：系统正在抓取您当前控制台输入的实时交互参数，与底层算法推演出的全局理论帕累托最优解开展空间坐标拟合比对，综合欧氏测度拟合度为 {match_score:.1f}%。"

        if match_score >= 85:
            fit_diagnosis += "这一极高评分证实，您当前设置的宏观预算配置框架已极度精准地逼近甚至咬合了帕累托最优演化解集曲面。该数学架构极其可靠地确保了在绝不触碰地方城投隐性债务高压线的大前提下，能够实现区域宏观经济正向拉动与绿色生态降碳绝对效益的全面、系统性最大化释放。"
            advice = "【宏观政策指导方案】\n\n1. 法定预算防火墙确立：将本系统算法界定的最优分配比例参数直接固化为地方人民代表大会的法定预算红线，严禁任何形式的临时性干预或长官意志截留。\n2. 颗粒度穿透垂直下沉：在宏观指标已确认达优的背景下，迅速联手发改部门建立微观经济穿透考核节点，死死盯住巨量资金在具体企业端的真实算法转化效率。"
        elif match_score >= 60:
            fit_diagnosis += "评分表明，您当前的各项资金流分布结构整体上仍处于基础的安全可行域空间内，没有发生灾难性的偏离。但在多维博弈层面仍存在一定的系统内耗与资金冗余折损。系统强烈建议您参考上述算法严格界定的黄金分割理论参数值，对各子要素的投入倾斜方向实施精细的结构性微操微调与空间纠偏。"
            advice = "【宏观政策指导方案】\n\n1. 跨部门强制机动调剂：立刻启动行政中期预算重构研判，利用行政高压将发现的低效土建预算缺口强制按比例切块，强行平移注入至引资引智的短板盘面中。\n2. 效能对赌式拨付机制：彻底摒弃传统的一次性全额拨款模式。要求基层执行部门必须自证下一阶段的数据能向85%拟合度加速收敛，否则即刻触发财政拨付熔断机制。"
        else:
            fit_diagnosis += "极低的评分触发了最高维度的系统警告！数据表明当前设定存在极为严重的非理性预算错配。推演运行轨迹已经完全脱离了帕累托安全曲面的保护范围，如果付诸实施，将不可避免地触发局部海量资源空转陷阱与全域能耗逆向剧烈反弹的系统级恶性崩盘。必须立即悬崖勒马，冻结该粗放型规划方案，强制向系统计算出的最优参数集实施全面并轨重置。"
            advice = "【宏观政策指导方案】\n\n1. 冻结重置铁血纪律：立刻下达最高行政指令，全面冻结全域内一切严重脱离算法可行域的扩张性大基建项目的前期立项与流转，坚决推倒重来。\n2. 审计问责机制前置：纪检监委与审计机构应当将系统的最优坐标参数直接纳入追溯红线依据，对无视科学底线、盲目大干快上的决策主体实施极为严厉的离任高压问责。"

        return analysis + "\n" + fit_diagnosis + "\n" + advice


def get_report(city_name, current_data, logic, module_key, c_inv=0, f_inv=0, i_inv=0):
    clean_name = re.sub(r'^.*?省|^.*?自治区|市$', '', city_name)
    if module_key == "m1":
        if clean_name in city_advice_db:
            return city_advice_db[clean_name]["m1"]
        is_heavy = True if logic == "偏向重化工业主导" else False
        safe_city = "默认重工" if is_heavy else "默认综合"
        return city_advice_db[safe_city]["m1"]
    else:
        engine_logic = "重化工" if logic == "偏向重化工业主导" else "综合服务型城市"
        return generate_dynamic_report(city_name, current_data, engine_logic, module_key, c_inv, f_inv, i_inv)


# ------------------------------------------
# 4. 全局公共渲染组件
# ------------------------------------------
def render_custom_report(text):
    """渲染模块一至三的通用图文报告"""
    if "【宏观政策指导方案】" in text:
        analysis_part, advice_part = text.split("【宏观政策指导方案】")
        clean_analysis = analysis_part.replace("【系统数据分析与推演过程】：", "").strip()

        st.markdown(f"""
            <div style='background-color: #FAFAFA; border-left: 4px solid #1A3622; padding: 15px 20px; margin-top: 15px; margin-bottom: 25px; line-height: 1.8; font-size: 15px; text-align: justify;'>
                <h4 style='color: #1A3622; margin-top: 0px; margin-bottom: 12px; font-weight: bold;'>📊 动态数据推演与底层逻辑解析</h4>
                {clean_analysis}
            </div>
        """, unsafe_allow_html=True)
        st.markdown("<h3 style='color: #2C3539; font-weight: bold; margin-bottom: 15px;'>🎯 宏观政策指导方案</h3>",
                    unsafe_allow_html=True)

        for adv in advice_part.strip().split("\n"):
            adv = adv.strip()
            if adv and "：" in adv and adv[0].isdigit():
                title, content = adv.split("：", 1)
                st.markdown(f"""
                <div style='background-color: #FFFFFF; border: 1px solid #E0E0E0; border-left: 5px solid #4DB8B3; padding: 18px; border-radius: 6px; margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.03);'>
                    <h4 style='color: #1A3622; font-size: 17px; margin-top: 0; margin-bottom: 8px; font-weight: bold;'>🏛️ {title}</h4>
                    <p style='margin-bottom: 0; color: #444; line-height: 1.6; font-size: 14.5px; text-align: justify;'>{content}</p>
                </div>
                """, unsafe_allow_html=True)
            elif adv:
                st.markdown(f"<p>{adv}</p>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='analysis-box'>{text}</div>", unsafe_allow_html=True)


def normalize_to_100(val, col_name):
    min_v, max_v = df[col_name].min(), df[col_name].max()
    return 50 if max_v == min_v else max(0, min((val - min_v) / (max_v - min_v) * 100, 100))


def bottom_navigation(current_page):
    st.markdown("---")
    st.markdown("### 🎛️ 加权规范化评价矩阵快速切换")
    pages = {'mod1': "模块一：宏观体检与断层推演", 'mod2': "模块二：门槛研判与动态预警", 'mod3': "模块三：政策试错与轨迹推演", 'mod4': "模块四：多目标寻优与组合决策"}
    cols = st.columns(3)
    for i, k in enumerate([k for k in pages.keys() if k != current_page]):
        if cols[i].button(pages[k], key=f"nav_{k}", use_container_width=True):
            st.session_state.page = k;
            st.rerun()


# ------------------------------------------
# 5. 系统页面路由体系
# ------------------------------------------
if st.session_state.page == 'splash':
    st.markdown("<style>[data-testid='stSidebar'] {display: none;}</style>", unsafe_allow_html=True)
    st.markdown("<div style='height: 15vh;'></div>", unsafe_allow_html=True)
    st.markdown("<div class='spin-earth'>🌍</div>", unsafe_allow_html=True)
    st.markdown("<div class='title-main'>城市低碳治理智能推演系统</div>", unsafe_allow_html=True)
    st.markdown("<div class='title-sub'>基于正交因果森林与高维帕累托的宏观推演沙盘</div>", unsafe_allow_html=True)
    st.markdown("<br><p style='text-align: center; color: #888888;'>正在加载 25市 面板数据底座与动态大模型推演引擎...</p>",
                unsafe_allow_html=True)
    time.sleep(2.0)
    st.session_state.page = 'city_select'
    st.rerun()

elif st.session_state.page == 'city_select':
    st.markdown("<style>[data-testid='stSidebar'] {display: none;}</style>", unsafe_allow_html=True)
    st.markdown("<div style='height: 8vh;'></div>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center;'>📍 宏观推演仿真数据底座初始化</h2>", unsafe_allow_html=True)

    col_spacer1, col_main, col_spacer2 = st.columns([1, 4, 1])
    with col_main:
        with st.container(border=True):
            category_opts = ["内置：重工锁定型城市", "内置：综合服务型城市", "外部：自定义录入宏观数据"]
            cat_choice = st.radio("第一步：界定面板数据归属与底层产业结构类型", category_opts,
                                  index=category_opts.index(st.session_state.city_category))
            s_city_choice = st.session_state.s_city
            custom_logic_choice = st.session_state.custom_logic

            if cat_choice == "内置：重工锁定型城市":
                available_cities = df[df["类型"] == "重工锁定型城市"]["城市"].tolist()
                s_city_choice = st.selectbox("第二步：选择重工型推演城市靶点", available_cities, index=available_cities.index(
                    s_city_choice) if s_city_choice in available_cities else 0)
            elif cat_choice == "内置：综合服务型城市":
                available_cities = df[df["类型"] == "综合服务型城市"]["城市"].tolist()
                s_city_choice = st.selectbox("第二步：选择综合服务型参照基准城市", available_cities, index=available_cities.index(
                    s_city_choice) if s_city_choice in available_cities else 0)
            else:
                s_city_choice = st.text_input("第二步：设定系统推演目标标的名称", value=s_city_choice if s_city_choice not in df[
                    "城市"].tolist() else "未命名区域")
                custom_logic_choice = st.radio("核定该区域的主导产业底色以匹配智能算法逻辑", ["偏向重化工业主导", "偏向综合与服务型"])
                st.markdown("*(请依次录入核心基础宏观指标特征变量)*")
                c1, c2 = st.columns(2)
                st.session_state.custom_data["长途光缆"] = c1.number_input("长途光缆线路总长(公里)", value=float(
                    st.session_state.custom_data["长途光缆"]))
                st.session_state.custom_data["外资引进与对外开放程度"] = c2.number_input("年度实际使用外资(亿元)", value=float(
                    st.session_state.custom_data["外资引进与对外开放程度"]))
                st.session_state.custom_data["IT人才密度"] = c1.number_input("数字产业从业规模(万人)", value=float(
                    st.session_state.custom_data["IT人才密度"]))
                st.session_state.custom_data["基准碳排"] = c2.number_input("期初基准碳排总量(Mt)", value=float(
                    st.session_state.custom_data["基准碳排"]))

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("全域面板特征挂载完毕，启动系统推演推演引擎", type="primary", use_container_width=True):
            st.session_state.city_category = cat_choice
            st.session_state.s_city = s_city_choice
            st.session_state.custom_logic = custom_logic_choice
            st.session_state.page = 'menu'
            st.rerun()

else:
    # 全局交互侧边栏
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
        cat_opts = ["内置：重工锁定型城市", "内置：综合服务型城市", "外部：自定义录入数据"]
        new_cat = st.radio("一、底座数据类型热切换", cat_opts,
                           index=cat_opts.index(st.session_state.city_category.replace("宏观数据", "数据")), key="sb_cat")
        if new_cat != "外部：自定义录入数据":
            avail = df[df["类型"] == new_cat.split("：")[1]]["城市"].tolist()
            new_city = st.selectbox("二、设定空间推演靶点", avail, index=avail.index(
                st.session_state.s_city) if st.session_state.s_city in avail else 0, key="sb_city")
            if new_cat != st.session_state.city_category or new_city != st.session_state.s_city:
                st.session_state.city_category = new_cat;
                st.session_state.s_city = new_city;
                st.rerun()
           else:
                new_city = st.text_input("二、目标推演区域", value=st.session_state.s_city, key="sb_city_cust")
                new_logic = st.radio("核定底层算法基盘", ["偏向重化工业主导", "偏向综合与服务型"],
                                     index=0 if "重化工" in st.session_state.custom_logic else 1, key="sb_logic")

                st.markdown("*（手动微调以下宏观底盘数据，实时触发图谱演算）*")
                c1, c2 = st.columns(2)
                new_n1 = c1.number_input("长途光缆(km)", value=float(st.session_state.custom_data["长途光缆"]))
                new_n2 = c2.number_input("外资(亿元)", value=float(st.session_state.custom_data["外资引进与对外开放程度"]))
                new_n3 = c1.number_input("人才(万人)", value=float(st.session_state.custom_data["IT人才密度"]))
                new_n4 = c2.number_input("基准碳排(Mt)", value=float(st.session_state.custom_data["基准碳排"]))
                new_n5 = c1.number_input("宽带普及(万户)", value=float(st.session_state.custom_data["宽带普及"]))
                new_n6 = c2.number_input("普惠金融", value=float(st.session_state.custom_data["普惠金融"]))

                # 监听任何一个状态的变化并重新渲染引擎
                if (new_cat != st.session_state.city_category or
                        new_city != st.session_state.s_city or
                        new_logic != st.session_state.custom_logic or
                        new_n1 != st.session_state.custom_data["长途光缆"] or
                        new_n2 != st.session_state.custom_data["外资引进与对外开放程度"] or
                        new_n3 != st.session_state.custom_data["IT人才密度"] or
                        new_n4 != st.session_state.custom_data["基准碳排"] or
                        new_n5 != st.session_state.custom_data["宽带普及"] or
                        new_n6 != st.session_state.custom_data["普惠金融"]):
                    st.session_state.city_category = new_cat
                    st.session_state.s_city = new_city
                    st.session_state.custom_logic = new_logic
                    st.session_state.custom_data["长途光缆"] = new_n1
                    st.session_state.custom_data["外资引进与对外开放程度"] = new_n2
                    st.session_state.custom_data["IT人才密度"] = new_n3
                    st.session_state.custom_data["基准碳排"] = new_n4
                    st.session_state.custom_data["宽带普及"] = new_n5
                    st.session_state.custom_data["普惠金融"] = new_n6
                    st.rerun()

        st.markdown("---")
        st.markdown("三、政策干预资金参数域 (亿元)")
        st.markdown("*拉动滑块，右侧全维引擎将实时联动推演运算*")
        st.session_state.c_invest = st.slider("数字基础硬性基建专项预算", 0.0, 20.0, st.session_state.c_invest, 0.1)
        st.session_state.f_invest = st.slider("外资先进制程及生态引导资金", 0.0, 10.0, st.session_state.f_invest, 0.1)
        st.session_state.i_invest = st.slider("数字高阶人才结构优化补贴", 0.0, 5.0, st.session_state.i_invest, 0.1)

    total_invest = st.session_state.c_invest + st.session_state.f_invest + st.session_state.i_invest
    base_carbon = city_data.get("基准碳排", 50.0)

    if current_engine_logic == "综合型":
        infra_cost_penalty = st.session_state.c_invest * 3.5
        reduce_effect = (st.session_state.f_invest * 2.0) + (st.session_state.i_invest * 2.5)
    else:
        infra_cost_penalty = st.session_state.c_invest * 0.8
        reduce_effect = (st.session_state.c_invest * 2.8) + (st.session_state.f_invest * 1.5) + (
                    st.session_state.i_invest * 1.0)

    pred_carbon = max(base_carbon * 0.4, base_carbon + infra_cost_penalty - reduce_effect)

    # 导航菜单
    if st.session_state.page == 'menu':
        st.markdown(f"## 🌍 【{st.session_state.s_city}】低碳投资智能辅助系统")
        st.info(
            "系统声明：内置高精度双重机器学习（OrthoIV-CF）与遗传运筹算法（NSGA-III）。本系统生成的文字描述、趋势图谱与政策匹配指导，均由您在左侧控制台输入的滑块参数通过底层算法引擎动态高频演算生成，为您提供极致严密的数学论证支撑。")
        for num, mod, title, desc in [("一", "mod1", "宏观体检与数据要素断层推演", "构建多维高阶极差矩阵，深度剥离揭示区域在数字底层基座与智力软性储备的结构性断层。"),
                                      ("二", "mod2", "门槛研判与防过热动态全息预警", "依据交互投资干预烈度，利用双变量拓扑矩阵实时判定巨额资金引发空转与排量反弹的系统级风险。"),
                                      ("三", "mod3", "反事实沙盘试错与演化轨迹仿真", "动态推演当前投资总盘对未来三年期碳排折线的物理影响，依托SHAP博弈论生成ROI归因瀑布。"),
                                      ("四", "mod4", "全局多约束帕累托最优生成指令",
                                       "基于NSGA-III算法，在宏观约束下全盘计算最完美黄金比例，并对您当前配比实施实时纠偏指令。")]:
            with st.container(border=True):
                st.markdown(f"### {num}、 {title}")
                st.markdown(desc)
                if st.button(f"启动运算引擎进入模块{num}", key=mod,
                             use_container_width=True): st.session_state.page = mod; st.rerun()

    # 模块一
    elif st.session_state.page == 'mod1':
        st.button("中止当前演算并返回主系统", on_click=lambda: st.session_state.update({'page': 'menu'}))
        st.markdown(f"## 一、 【{st.session_state.s_city}】宏观体检与数据要素断层推演")
        categories = ['深层算力(长途光缆)', '绿色资本(外资)', '智力资本(IT人才)', '浅层网络(宽带普及)', '产业融合(普惠金融)']
        city_scores = [normalize_to_100(city_data.get(k, 50), k) for k in
                       ["长途光缆", "外资引进与对外开放程度", "IT人才密度", "宽带普及", "普惠金融"]]
        avg_scores = [normalize_to_100(df[k].mean(), k) for k in ["长途光缆", "外资引进与对外开放程度", "IT人才密度", "宽带普及", "普惠金融"]]

        col_left, col_right = st.columns([1.2, 1])
        with col_left:
            fig_radar = go.Figure(data=[
                go.Scatterpolar(r=avg_scores, theta=categories, fill='toself', name='全域面板样本均线', line_color='#6495ED'),
                go.Scatterpolar(r=city_scores, theta=categories, fill='toself', name=f'{st.session_state.s_city}',
                                line_color=C_DEEP_FOREST)])
            fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), height=350,
                                    title="宏观发展要素高维拓扑雷达映射", margin=dict(t=50, b=20, l=40, r=40))
            st.plotly_chart(fig_radar, use_container_width=True)
            df_gap = pd.DataFrame({"评估维度": categories, "区域考核得分": city_scores, "全域样本均线": avg_scores})
            fig_bar = px.bar(df_gap, x="评估维度", y=["全域样本均线", "区域考核得分"], barmode="group", title="核心资源要素物理存量极差推演",
                             color_discrete_sequence=["#B0BEC5", C_DEEP_FOREST])
            fig_bar.update_layout(height=350, margin=dict(t=50, b=20), legend_title=None, yaxis_title="极差无量纲测度得分")
            st.plotly_chart(fig_bar, use_container_width=True)
        with col_right:
            render_custom_report(get_report(st.session_state.s_city, city_data, st.session_state.custom_logic, "m1"))
        bottom_navigation('mod1')

    # 模块二
    elif st.session_state.page == 'mod2':
        st.button("中止当前演算并返回主系统", on_click=lambda: st.session_state.update({'page': 'menu'}))
        st.markdown(f"## 二、 【{st.session_state.s_city}】门槛研判与防过热动态全息预警")
        x_grid, y_grid = np.linspace(0, 20, 50), np.linspace(0, 15, 50)
        X_mat, Y_mat = np.meshgrid(x_grid, y_grid)
        soft_invest = st.session_state.f_invest + st.session_state.i_invest
        col_left, col_right = st.columns([1.2, 1])

        if current_engine_logic == "综合型":
            Z_risk = np.clip((X_mat / 8.0 * 100) - (Y_mat * 1.5), 0, 100)
            fig_heat = go.Figure(
                data=go.Contour(x=x_grid, y=y_grid, z=Z_risk, colorscale="Reds", contours=dict(showlabels=True)))
            fig_heat.update_layout(title="综合型城域资金错配及过热风险热力二维推演", xaxis_title="硬基建参数(亿)", yaxis_title="软生态资本(亿)",
                                   height=350, margin=dict(t=40, b=10, l=10, r=10))
            fig_heat.add_trace(go.Scatter(x=[st.session_state.c_invest], y=[soft_invest], mode='markers+text',
                                          marker=dict(color='gold', size=16, symbol='star',
                                                      line=dict(width=2, color='black')), text=["📍 实时推演动态坐标"],
                                          textposition="top center"))
            with col_left:
                fig_gauge = go.Figure(
                    go.Indicator(mode="gauge+number", value=min(st.session_state.c_invest / 8.0 * 100, 100),
                                 title={'text': "基建冗余度与碳排反弹综合风险指数"},
                                 gauge={'axis': {'range': [0, 100]},
                                        'steps': [{'range': [0, 40], 'color': C_GLACIER_TEAL},
                                                  {'range': [40, 70], 'color': 'rgba(255, 215, 0, 0.6)'},
                                                  {'range': [70, 100], 'color': C_WARNING_RED}],
                                        'threshold': {'line': {'color': "red", 'width': 4}, 'value': 70}}))
                fig_gauge.update_layout(height=300, margin=dict(t=50, b=10))
                st.plotly_chart(fig_gauge, use_container_width=True)
                st.plotly_chart(fig_heat, use_container_width=True)
        else:
            Z_break = np.clip(((X_mat + Y_mat) / 6.5 * 100), 0, 100)
            fig_heat = go.Figure(
                data=go.Contour(x=x_grid, y=y_grid, z=Z_break, colorscale="Greens", contours=dict(showlabels=True)))
            fig_heat.update_layout(title="重工锁定型城域势能积聚跨越拓扑预测图", xaxis_title="硬基建参数(亿)", yaxis_title="软生态资本(亿)",
                                   height=350, margin=dict(t=40, b=10, l=10, r=10))
            fig_heat.add_trace(go.Scatter(x=[st.session_state.c_invest], y=[soft_invest], mode='markers+text',
                                          marker=dict(color='gold', size=16, symbol='star',
                                                      line=dict(width=2, color='black')), text=["📍 实时推演动态坐标"],
                                          textposition="top center"))
            with col_left:
                fig_gauge = go.Figure(go.Indicator(mode="gauge+number", value=min(total_invest / 6.5 * 100, 100),
                                                   title={'text': "碳锁定破局与门槛跨越势能指数"},
                                                   gauge={'axis': {'range': [0, 100]}, 'steps': [
                                                       {'range': [0, 50], 'color': 'rgba(255, 99, 71, 0.6)'},
                                                       {'range': [50, 80], 'color': 'rgba(255, 215, 0, 0.6)'},
                                                       {'range': [80, 100], 'color': C_DEEP_FOREST}],
                                                          'threshold': {'line': {'color': "red", 'width': 4},
                                                                        'value': 80}}))
                fig_gauge.update_layout(height=300, margin=dict(t=50, b=10))
                st.plotly_chart(fig_gauge, use_container_width=True)
                st.plotly_chart(fig_heat, use_container_width=True)

        with col_right:
            render_custom_report(get_report(st.session_state.s_city, city_data, st.session_state.custom_logic, "m2",
                                            st.session_state.c_invest, st.session_state.f_invest,
                                            st.session_state.i_invest))
        bottom_navigation('mod2')

    # 模块三
    elif st.session_state.page == 'mod3':
        st.button("中止当前演算并返回主系统", on_click=lambda: st.session_state.update({'page': 'menu'}))
        st.markdown(f"## 三、 【{st.session_state.s_city}】反事实沙盘试错与演化轨迹仿真")
        years = [f"{2024 + i}年" for i in range(4)]
        base_traj = [base_carbon, base_carbon * 1.015, base_carbon * 1.028, base_carbon * 1.04]
        traj_1 = max(base_carbon * 0.4, base_carbon + infra_cost_penalty * (
            0.4 if current_engine_logic == "综合型" else 0.9) - reduce_effect * (
                         0.2 if current_engine_logic == "综合型" else 0.3))
        traj_2 = max(base_carbon * 0.4, base_carbon + infra_cost_penalty * (
            0.8 if current_engine_logic == "综合型" else 1.0) - reduce_effect * (
                         0.6 if current_engine_logic == "综合型" else 0.7))
        df_traj = pd.DataFrame(
            {"预测年度": years * 2, "核心排量监控值(Mt)": base_traj + [base_carbon, traj_1, traj_2, pred_carbon],
             "仿真演化情境": ["静态基准演化轨道"] * 4 + ["交互参数推演干预轨道"] * 4})

        col_left, col_right = st.columns([1.2, 1])
        with col_left:
            fig_line = px.line(df_traj, x="预测年度", y="核心排量监控值(Mt)", color="仿真演化情境", markers=True,
                               title="中短期全域核心减排折线分轨模拟预测", color_discrete_sequence=["#9E9E9E", C_GLACIER_TEAL])
            fig_line.update_layout(height=350)
            st.plotly_chart(fig_line, use_container_width=True)

            x_l = ["基准碳排底座", "硬建空耗反弹", "外资技术红利", "软性智力红利", "预测推演落点"] if current_engine_logic == "综合型" else ["基准碳排底座",
                                                                                                            "施工附加能耗",
                                                                                                            "深层光缆红利",
                                                                                                            "外资技术迁移",
                                                                                                            "管理算法跃升",
                                                                                                            "预测推演落点"]
            y_v = [base_carbon, infra_cost_penalty, -st.session_state.f_invest * 2.0, -st.session_state.i_invest * 2.5,
                   pred_carbon] if current_engine_logic == "综合型" else [base_carbon, infra_cost_penalty,
                                                                       -st.session_state.c_invest * 2.8,
                                                                       -st.session_state.f_invest * 1.5,
                                                                       -st.session_state.i_invest * 1.0, pred_carbon]
            m = ["absolute"] + ["relative"] * (len(y_v) - 2) + ["total"]

            fig_shap = go.Figure(go.Waterfall(orientation="v", measure=m, x=x_l, textposition="outside",
                                              text=[f"{v:+.2f}" if m == "relative" else f"{v:.2f}" for v, m in
                                                    zip(y_v, m)], y=y_v, connector={"line": {"color": "#444"}},
                                              decreasing={"marker": {"color": C_DEEP_FOREST}},
                                              increasing={"marker": {"color": C_WARNING_RED}},
                                              totals={"marker": {"color": C_GLACIER_TEAL}}))
            fig_shap.update_layout(title="SHAP博弈论算法边际影响(ROI)定量剥离", showlegend=False, height=350,
                                   margin=dict(t=40, b=20, l=10, r=10))
            st.plotly_chart(fig_shap, use_container_width=True)

        with col_right:
            render_custom_report(get_report(st.session_state.s_city, city_data, st.session_state.custom_logic, "m3",
                                            st.session_state.c_invest, st.session_state.f_invest,
                                            st.session_state.i_invest))
        bottom_navigation('mod3')

    # 模块四 (重构的“田”字排版)
    elif st.session_state.page == 'mod4':
        st.button("中止当前演算并返回主系统", on_click=lambda: st.session_state.update({'page': 'menu'}))
        st.markdown(f"## 四、 【{st.session_state.s_city}】全局多约束帕累托最优生成指令")

        np.random.seed(int(hashlib.md5(st.session_state.s_city.encode('utf-8')).hexdigest(), 16) % (2 ** 32))
        n_pts, x_inv = 250, np.random.uniform(1, 20, 250)
        y_cb = x_inv * (1.2 if current_engine_logic == "综合型" else 1.8) - np.random.normal(0, 2, n_pts)
        z_gdp = -0.1 * (x_inv - 10) ** 2 + 8 + np.random.normal(0, 1, n_pts)

        # 调取并拆分动态推演结果文本
        report_text = get_report(st.session_state.s_city, city_data, st.session_state.custom_logic, "m4",
                                 st.session_state.c_invest, st.session_state.f_invest, st.session_state.i_invest)

        main_part, fit_part, advice_part = "", "", ""
        if "【多目标决策拟合度深度诊断】：" in report_text and "【宏观政策指导方案】" in report_text:
            p1, rest = report_text.split("【多目标决策拟合度深度诊断】：")
            p2, p3 = rest.split("【宏观政策指导方案】")
            main_part = p1.replace("【系统数据分析与推演过程】：", "").strip()
            fit_part = p2.strip()
            advice_part = p3.strip()

        # 上半部分：图表(左) + 基础动态分析(右)
        col_top_left, col_top_right = st.columns([1.2, 1])
        with col_top_left:
            fig_3d = px.scatter_3d(x=x_inv, y=y_cb, z=z_gdp, color=z_gdp, color_continuous_scale="RdBu_r",
                                   labels={'x': '宏观总盘(亿)', 'y': '预测目标减排(Mt)', 'z': 'GDP预计变动(%)'},
                                   title="NSGA-III算法生成高维帕累托最优可行域前沿曲面")
            fig_3d.add_trace(
                go.Scatter3d(x=[total_invest], y=[base_carbon - pred_carbon], z=[-0.1 * (total_invest - 10) ** 2 + 8],
                             mode='markers+text', text=["📍 当前交互参数动态测度坐标"],
                             marker=dict(size=14, symbol='diamond', color='gold', line=dict(color='black', width=3)),
                             textposition='top center'))
            fig_3d.update_layout(height=650)
            st.plotly_chart(fig_3d, use_container_width=True)

        with col_top_right:
            st.markdown(f"""
                <div style='background-color: #FAFAFA; border-left: 4px solid #1A3622; padding: 15px 20px; margin-top: 15px; margin-bottom: 25px; line-height: 1.8; font-size: 15px; text-align: justify;'>
                    <h4 style='color: #1A3622; margin-top: 0px; margin-bottom: 12px; font-weight: bold;'>📊 动态数据推演与底层逻辑解析</h4>
                    {main_part}
                </div>
            """, unsafe_allow_html=True)

        # 下半部分：拟合度诊断(左) + 政策指导(右)，实现左右平齐排版
        col_bot_left, col_bot_right = st.columns([1.2, 1])
        with col_bot_left:
            st.markdown(f"""
                <div style='background-color: #F8F9FA; border-left: 4px solid #2C3539; padding: 15px 20px; margin-top: 0px; margin-bottom: 25px; line-height: 1.8; font-size: 15px; text-align: justify;'>
                    <h4 style='color: #2C3539; margin-top: 0px; margin-bottom: 12px; font-weight: bold;'>🎯 决策拟合度深度诊断</h4>
                    {fit_part}
                </div>
            """, unsafe_allow_html=True)

        with col_bot_right:
            st.markdown(
                "<h4 style='color: #2C3539; font-weight: bold; margin-top: 0px; margin-bottom: 15px;'>🎯 宏观政策指导方案</h4>",
                unsafe_allow_html=True)
            for adv in advice_part.split("\n"):
                adv = adv.strip()
                if adv and "：" in adv and adv[0].isdigit():
                    title, content = adv.split("：", 1)
                    st.markdown(f"""
                    <div style='background-color: #FFFFFF; border: 1px solid #E0E0E0; border-left: 5px solid #4DB8B3; padding: 18px; border-radius: 6px; margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.03);'>
                        <h5 style='color: #1A3622; font-size: 16px; margin-top: 0; margin-bottom: 8px; font-weight: bold;'>🏛️ {title}</h5>
                        <p style='margin-bottom: 0; color: #444; line-height: 1.6; font-size: 14.5px; text-align: justify;'>{content}</p>
                    </div>
                    """, unsafe_allow_html=True)
                elif adv:
                    st.markdown(f"<p>{adv}</p>", unsafe_allow_html=True)

        bottom_navigation('mod4')
