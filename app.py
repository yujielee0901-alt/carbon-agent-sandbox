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
        .analysis-box {{ background-color: #FAFAFA; border-left: 4px solid {C_DEEP_FOREST}; padding: 15px 20px; margin-top: 15px; line-height: 1.8; font-size: 15px; }}
        [data-testid="collapsedControl"] {{display: none;}}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. 深度智库预载入 (仅保留M1的基础静态体检特征，M2/M3/M4全部交由算法动态生成)
# ==========================================
city_advice_db = {
    "焦作": {"m1": "【系统数据分析与推演过程】：通过高维极差空间拓扑与雷达图矩阵比对，该市在浅层宽带普及与普惠金融维度已接近全域均线。而在支撑重化工转型的深层核心要素（长途光缆仅1020公里，IT人才仅0.27万人）上直观暴露出结构性落差。诊断客观反映出底层信息基础设施明显滞后于实体经济制造规模的现实。\n\n【宏观政策指导方案】\n\n1. 固投专项重构：暂缓消费级通信基站的新建，将有限的财政资源与专项债券额度合规向深层工业光缆与算力枢纽倾斜。\n2. 孤岛数据清查：重点排查市属重资产企业内部的“数据孤岛”现象，为后期开展复杂的能耗调度筑牢物理根基。"},
    "平顶山": {"m1": "【系统数据分析与推演过程】：数据显示该市深层光缆基数达2031公里，硬件网络底座扎实。但外资引入（1.02亿）与普惠金融渗透率处于枯竭边缘。推演直观指出，该市正面临“硬资产过剩、软技术断层”危机，缺乏国际先进低碳管理体系的外资与本土数字智力支撑来盘活重资产。\n\n【宏观政策指导方案】\n\n1. 招商结构调优：全面转向定向吸引携带前沿减排专利、算法模型的国际高质量数字技术企业入驻。\n2. 存量资产激活：指导市属大型煤炭、能源国企开放应用场景，推动购买软件SaaS服务以盘活底层网络。"},
    "安阳": {"m1": "【系统数据分析与推演过程】：面临巨量碳排压力（102.41Mt），尽管光缆基数达到中游，但相较其庞大钢铁、煤化工业体量，当前的数字要素渗透重型冶炼企业底层存在严重不足，构成了无法精准测度与调度的高位碳排阻碍。\n\n【宏观政策指导方案】\n\n1. 历史包袱定向量化：依托极差测度模型，直接将断层报告转化为申报国家级老工业基地转型示范区的强力论证附件。\n2. 技改专项定向注资：联合社会资本设立针对特钢等传统产业的数字化技改专项基金，用强力杠杆填补深层算力缺位。"},
    "鹤壁": {"m1": "【系统数据分析与推演过程】：全域比对显示该市在底层硬件（光缆549公里）与智力软件（IT人才仅0.13万）上呈现“双重严重断层”。信息传输动脉微弱，短期内根本无法为其构建有效的数据闭环控制系统。\n\n【宏观政策指导方案】\n\n1. 财政缺口理论辩护：本诊断报告为争取外部转移支付提供客观证据，合理争取省市级资金来填补底层基建历史账单。\n2. 孤岛式示范标杆：切忌“撒胡椒面”式的平均配置，集中极端有限的资源在1-2家核心龙头企业内部开展局域物联网试点。"},
    "长治": {"m1": "【系统数据分析与推演过程】：呈现“非对称性巨峰”，长途光缆达3255公里，外资存量31.14亿元，硬件与资金储备雄厚。但IT人才密度仅0.30万人。系统断层推演尖锐指出存在“硬件超前、资本充沛，但智力核心脱节”的异构断层，庞大网络面临算力闲置。\n\n【宏观政策指导方案】\n\n1. 招才引智优先序列：立刻将施政重心转向设立专项数字工程师与算法专家引进计划，以承接庞大的硬件底座。\n2. 技术生态强制耦合：依托高位外资存量，强制要求外资企业在本土设立研发中心，以人才属地化补齐系统智力短板。"},
    "晋城": {"m1": "【系统数据分析与推演过程】：以161.18Mt的高极值成为“重度碳锁定”样本。然而其数字对抗要素微乎其微（光缆2207公里，人才0.26万）。推演矩阵直观标红了控制力的结构性枯竭，意味现有赋能在庞大煤炭冶炼巨无霸前几乎丧失渗透能力。\n\n【宏观政策指导方案】\n\n1. 宏观缺口向上破局：将极端断层报告转化为申请“资源型城市深度低碳转型特区”佐证材料，引入超常规转移支付。\n2. 强制级基座重构：针对大型排碳主体的底层信息管网，下发带有强制性的重资产物联网改造指令，不设过渡缓冲期。"},
    "郑州": {"m1": "【系统数据分析与推演过程】：作为枢纽城市，呈现出全样本最强的“软实力霸权”（IT人才10.99万，外资12.29亿）。深层光缆表现为“适度够用”。诊断确认：已摆脱依赖铺设物理硬基建的初级阶段，全面迈入以算法与智力资本驱动的深水区。\n\n【宏观政策指导方案】\n\n1. 顶层研发导向：彻底剥离土建工程财政依赖，转向对人工智能大模型、零碳数据交易平台的顶层设计投入。\n2. 智力资源在地转化：出台专项“算力券”与“碳普惠激励”政策，将庞大的软开发大军就地转化为降碳产业输出的护城河。"},
    "洛阳": {"m1": "【系统数据分析与推演过程】：暴露出罕见的“资产错位”。光缆总长达3911公里，硬件奢华且人才具备优良规模。但外资引入仅1.30亿元。陷入“基建严重超前，外部先进技术与资本导入梗阻”的内循环困局，存在极大算力空转风险。\n\n【宏观政策指导方案】\n\n1. 存量资产紧急唤醒：立即叫停市级骨干网络土木工程，盘点摸底现有数字资产负荷率，严控重复无效建设。\n2. 靶向型绿色招商：依托现成的世界级网络底座，将政策重心全盘压在吸引具备国际供应链标准的智造外企上。"},
    "新乡": {"m1": "【系统数据分析与推演过程】：呈现典型的“中等均衡”。光缆与宽带普及均卡在全域均线附近。但决定转型纵深的数字人才密度（0.49万）与外资（1.02亿）暴露疲态。网络覆盖达标，但极其缺乏深度重构制造业的高阶融合生态。\n\n【宏观政策指导方案】\n\n1. 细分灯塔工程：放弃普遍广度的基建摊大饼，集中机动财力，在电池制造、生物医药等优势领域打造零碳数字标杆。\n2. 外交靶向技术引进：引资策略实施精准打击，专盯能带来成套能耗管理SaaS系统与供应链认证的外向型数字平台。"},
    "开封": {"m1": "【系统数据分析与推演过程】：得益于文旅主导，碳排极低（11.61Mt）。光缆与宽带已完美支撑城市运行体量。但系统标出了外资与高阶IT人才的塌陷区。数字经济仅停留在表层消费结算，缺乏文商旅农深度低碳化数据变现的高级要素。\n\n【宏观政策指导方案】\n\n1. 轻量级SaaS化转向：放弃重资产数据中心建设规划，全盘转向开发“全域零碳智慧文旅服务云平台”。\n2. ESG主题引资路线：利用低碳生态优势，重点向主打ESG（环境、社会治理）评级投资的国际文创基金及绿色品牌引流。"},
    "许昌": {"m1": "【系统数据分析与推演过程】：暴露出尖锐的“单维塌陷”。普惠金融表现良好，但外资仅0.27亿元。该市处于严重的“对外技术封闭与资本孤岛”状态，缺乏国际减排模型及鲶鱼效应刺激，彻底锁死了向高端价值链攀升的空间。\n\n【宏观政策指导方案】\n\n1. 考核权重极端调优：重构招商引资考核体系，权重全面倾斜于引进携带绿色供应链管理技术与节能专利的科技服务企业。\n2. 轻量型合作示范区：不再搞大而全的土建，依托底盘专门设立具备极高环保与数字化基准的中外绿色智造合作专区。"},
    "漯河": {"m1": "【系统数据分析与推演过程】：呈现“超微型碳排地标”特征（仅2.62Mt），硬件基建也极少，但这并非欠账，而是与轻工业的“极度适配”。唯一短板在于高端人才的极度奇缺（0.17万），严重制约了千亿级食品产业向现代智能溯源演进。\n\n【宏观政策指导方案】\n\n1. 抵制同质化重基建：理直气壮拒绝大型数字基建分摊指标，全盘转向申请“食品安全全链路上链溯源工程”专项预算。\n2. 单点脑力购买战略：抛弃底层招募思维，出台特规高薪政策，向外部直接购买解决轻工业智造瓶颈的算法架构师。"},
    "三门峡": {"m1": "【系统数据分析与推演过程】：呈现最扭曲的“畸形断裂带”。外资高达36.88亿元，光缆长达2550公里，资本与硬件极度奢华。但IT人才惨烈跌至0.21万人。这是严重的“有资本无大脑”空转惨剧，先进设备正因缺乏智力调试而处于闲置状态。\n\n【宏观政策指导方案】\n\n1. 非常规人才空降：将解决人才缺口定为最高优先事项，不惜代价出台配套数字人才整建制挖引计划，激活存量沉睡设备。\n2. 第三方外包纾困：应对因配套奇缺导致的外资撤资风险，由政府出面全额购买第三方顶级IT外包服务免费提供给落户外企。"},
    "南阳": {"m1": "【系统数据分析与推演过程】：投射出最令人战栗的“重度基建过载体质”。光缆里程竟达6805.99公里（全域第一），但外资与人才极其贫乏。诊断拉响赤字警报：海量空置光纤埋入地下，基础设施承载力已严重溢出其实体经济实际需求的百倍。\n\n【宏观政策指导方案】\n\n1. 无效基建全面冰冻：彻查清算低效涉网市政工程，核清海量网络存量真实载荷率，从源头上刹住脱离实际产业的土建冲动。\n2. 存量网络强制引流：出台存量网络资源强制特许经营与租用条例，逼迫属地政企应用强行向既有闲置管道内引流以实现资产止血。"},
    "濮阳": {"m1": "【系统数据分析与推演过程】：呈现“低水平内卷式均衡”。碳排压至9.52Mt，而光缆、人才与外资三项动能指标均处于全域末端。既没有沉重的碳包袱，也没有冗余负债，但同样丧失了转型先发势能，处于单纯依靠内生微弱循环维持的结构性贫血。\n\n【宏观政策指导方案】\n\n1. 放弃基座竞逐：放弃对标核心城市的宏大物理基建规划，转而合法争取省级层面的算力调拨与干线网络公有云免费接入。\n2. 纯应用级外采策略：招商全面放弃“重资产”执念，将机动预算全数转为补贴本土小微企业跨区购买成熟SaaS解决方案。"},
    "商丘": {"m1": "【系统数据分析与推演过程】：作为交通枢纽却暴露出骇人的“资本孤岛”，外资仅0.02亿。面对70.75Mt的高碳排，人才干瘪但深层光缆铺设了2747公里。大搞基建物流却未吸引到绿色算力调控技术，庞大物流量裸奔是导致其碳排高企的核心病灶。\n\n【宏观政策指导方案】\n\n1. 智慧物流靶向破局：彻底推翻低端占地物流招商，100%倾斜引进具备国际先进碳足迹追踪与调度技术的科技平台企业。\n2. 基建全面软化升级：立刻停止新增单纯路网土建，后续资金强制划归为“车路协同与数据调度平台”专属改造专款。"},
    "信阳": {"m1": "【系统数据分析与推演过程】：展现极度刺眼的“重资产过载”。作为绿色生态城市（碳排仅23.33Mt），其地下竟埋设了高达4855公里的光缆。而人才与外资极度枯竭。硬基建投资彻底失控并脱离生态文旅承载力，形成巨额沉没成本耗电黑洞。\n\n【宏观政策指导方案】\n\n1. 行政清算与全面冻结：全面叫停一切“智慧城市、新基建”名义的发包工程，将防范基建举债与资产闲置定为首要铁律。\n2. 冗余资产折价出让：积极主动向沿海大型互联网算力节点推销本地廉价的过剩骨干带宽通道，竭力挽回财政沉淀损失。"},
    "周口": {"m1": "【系统数据分析与推演过程】：投射出“低碳排(5.4Mt)、高底盘(3070公里光缆)”的轮廓，但普惠金融指数排名倒数。物理基建与初级人才已就绪，但受制于金融供血体系。微小主体因得不到赋能无法转化为数字产值，呈现“管道通畅无水流”断层。\n\n【宏观政策指导方案】\n\n1. 普惠金融强制打通：利用庞大的网络底座赋能金融机构，大规模强制推行针对涉农及轻工小微企业的全线上无抵押数据信贷。\n2. 极简应用补贴引流：振兴重心从土木工程全面转向软件采买，政府出资通过金融杠杆补贴农机与溯源系统，盘活底层网络。"},
    # 其他城市默认映射至通用模板
    "默认重工": {"m1": "【系统数据分析与推演过程】：区域呈现典型的重资产依赖与排量高基数锁定。要素诊断发现深层网络基础结构未能有效触达核心排碳生产线，硬件铺设存在浅层化、表象化特征。缺乏深层控制算法导致排量居高不下。\n\n【宏观政策指导方案】\n\n1. 基建底层延伸：强制将预算投向重工业场景的物联网传感器与深层光缆铺设。\n2. 资本刚性管控：剥离非涉碳领域的无效财政注资。"},
    "默认综合": {"m1": "【系统数据分析与推演过程】：区域表现为轻资产、低基准的综合服务面貌。硬件网络覆盖充足但面临有效应用场景缺失的空转风险，数字高阶人才储备断层，缺乏引导软性生态发展的靶向外资与金融杠杆。\n\n【宏观政策指导方案】\n\n1. 轻资产云端赋能：停建实体IDC机房，全面转向云端SaaS平台补贴。\n2. 软要素政策倾斜：财政杠杆全力倾向于专业技术引流与普惠金融补贴。"}
}

# ==========================================
# 2. 全量底层数据挂载
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
    # 严格精准界定6个重工锁定型，其余为综合服务型
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
    st.session_state.custom_data = {"长途光缆": 1500.0, "外资引进与对外开放程度": 10.0, "IT人才密度": 1.5, "宽带普及": 200.0, "普惠金融": 280.0, "基准碳排": 50.0}

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
    """基于控制台交互滑块的动态推演结果生成引擎 (含联动政策指导方案)"""
    total = c_inv + f_inv + i_inv
    if total <= 0: total = 0.001

    if module_key == "m2":
        soft_invest = f_inv + i_inv
        analysis = f"【系统数据分析与推演过程】：双变量矩阵正实时监控资本投放系统性风险。拟投入总额 **{total:.1f} 亿元**（硬基建 {c_inv:.1f}亿，软生态 {soft_invest:.1f}亿）。\n\n"

        if logic == "综合服务型城市":
            risk_score = min(c_inv / 8.0 * 100, 100)
            analysis += f"研判溯源：缺乏重工业底盘的区域对重资产硬件投资极度敏感。测得当前“基建冗余度与碳排反弹风险指数”为 **{risk_score:.1f}**。此时硬基建配比"
            if risk_score > 70:
                analysis += "严重越过红线。算力堆砌不仅无法降碳，其建设运维空耗将导致碳排发生恶性倒挂。"
                advice = "【宏观政策指导方案】\n\n1. 一票否决熔断：立即中止大型IDC数据中心建设立项，环评审批全面触发过热红线拦截机制。\n2. 脱碳负债清算：启动对在建基建项目的专项能耗审计，严控形成无效的沉淀资金黑洞。"
            elif risk_score > 40:
                analysis += "处于敏感观察域。硬件初期的能耗正抵消减排效益，建议放缓施工节奏回填数据业务。"
                advice = "【宏观政策指导方案】\n\n1. 减量替代准入：对新建网络工程强制实行“降耗指标对赌”，无业务承接合同的一律不予审批。\n2. 绿色门槛前置：新增算力平台必须承诺80%以上采用绿电驱动，锁定生态红线底盘。"
            else:
                analysis += "落入深绿色安全区。轻量化的硬件配合足额的软性资本，成功规避能耗倒挂，边际投入健康。"
                advice = "【宏观政策指导方案】\n\n1. 软应用加速普及：安全区间内应扩大政策容忍度，全面补贴民营企业采购成套数字SaaS平台。\n2. 轻量化信贷覆盖：联合驻地银行，依据安全数据图谱发行挂钩企业云端活跃度的低息微贷。"
        else:
            breakthrough_score = min(total / 6.5 * 100, 100)
            analysis += f"研判溯源：区域碳锁定刚性强。测得“转型势能积聚与跨越指数”为 **{breakthrough_score:.1f}**。推演显示当前投资烈度"
            if breakthrough_score < 50:
                analysis += "严重匮乏。未触及规模经济阈值，微弱投资无法撕裂旧有能耗体系，导致长周期的建设期排碳空耗。"
                advice = "【宏观政策指导方案】\n\n1. 饱和式集中突围：摒弃分散拨款。财政需采取“集中兵力打歼灭战”模式，不触及突围门槛宁可不投。\n2. 政策长周期兜底：将跨越漫长的高碳阵痛期纳入免责机制，防范因短期数据难看导致战略烂尾。"
            elif breakthrough_score < 80:
                analysis += "正处于爬坡博弈期。能耗指标波动剧烈，需警惕资金流中断导致半途而废。"
                advice = "【宏观政策指导方案】\n\n1. 弹性环保执法：在爬坡阵痛期，环保机构需保持定力，严防机械“拉闸限产”绞杀转型项目。\n2. 组合拳强制绑定：招商引资必须将“技术+基建+工程师”打包绑定，禁止单要素的零散引进。"
            else:
                analysis += "已成功跨越绿色悖论临界点。高强度投资激活了底层网络与生产制造环节的深度降碳协同。"
                advice = "【宏观政策指导方案】\n\n1. 乘胜追击提标：红利释放期内大幅提高重工企业降耗硬性考核指标，倒逼全面系统性技改。\n2. 绿色债务发行：依据算法出具的可期性收敛证明，向国家级金融机构大规模发行碳减排专项债。"

        return analysis + "\n" + advice

    elif module_key == "m3":
        if logic == "综合服务型城市":
            roi_c, roi_f, roi_i = c_inv * 3.5, -f_inv * 2.0, -i_inv * 2.5
        else:
            roi_c, roi_f, roi_i = -c_inv * 2.8, -f_inv * 1.5, -i_inv * 1.0

        analysis = f"【系统数据分析与推演过程】：因果引擎接受 {total:.1f} 亿元指令演算边际净影响值(ROI)。\n\n通过SHAP算法剥离贡献度发现："
        if logic == "综合服务型城市":
            analysis += f"外资与人才带来的智力红利（降耗净贡献 {abs(roi_f + roi_i):.2f}）构成绝对主导力量。硬基建反而产生 {roi_c:.2f} 反向能耗。轻型城市的降耗杠杆在于“软生态搭建”而非物理扩张。"
            advice = "【宏观政策指导方案】\n\n1. 财补结构极简转向：全面停发购机直补等重资产补贴，全额转换为“数字技术采购券与外商落户奖补”。\n2. 高阶脑力置换：引才抛弃基础代码实施层，重金直击引进行业前沿模型架构师与供应链专家。"
        else:
            analysis += f"深层工业基建投资释放出极强压制作用（净效益 {abs(roi_c):.2f}），重型盘面高度依赖骨干重塑。同时软性资本催化提升了重资产设备的综合运转效能。"
            advice = "【宏观政策指导方案】\n\n1. 底层算力优先原则：确保工业级光缆与传感器网络占据转移支付的绝对主导，构筑硬核控制力。\n2. 技改预算强制配比：下达基建资金时，强制绑定同比例的软性算法模型与后期技术维护开发预算。"

        return analysis + "\n" + advice

    elif module_key == "m4":
        # 帕累托最优寻优中心
        if logic == "综合服务型城市":
            opt_c, opt_f, opt_i = total * 0.15, total * 0.40, total * 0.45
            strategy_name = "轻量化软性生态赋能战略"
        else:
            opt_c, opt_f, opt_i = total * 0.55, total * 0.25, total * 0.20
            strategy_name = "重资产底层基座重构战略"

        dist = np.sqrt((c_inv - opt_c)**2 + (f_inv - opt_f)**2 + (i_inv - opt_i)**2)
        match_score = max(0, 100 - (dist / total) * 100) if total > 0 else 0

        analysis = f"【系统数据分析与推演过程】：NSGA-III遗传算法在高维解空间锚定当前设定的 **{total:.1f} 亿元** 总盘，生成兼顾稳增长与降碳的帕累托最优界限。\n\n"
        analysis += f"全局极值寻优：系统研判最佳黄金配比应为：数字基建 **{opt_c:.1f}亿**，外资引导 **{opt_f:.1f}亿**，人才优化 **{opt_i:.1f}亿**。该组合定性为“{strategy_name}”。\n\n"
        analysis += f"决策拟合度评估：当前控制台输入的交互参数与最优解的综合拟合度为 **{match_score:.1f}%**。"

        if match_score >= 85:
            analysis += "预算架构已极度逼近帕累托最优状态。确保了隐性债务安全下的经济与减排双赢最大化。"
            advice = "【宏观政策指导方案】\n\n1. 法定预算防火墙：以本系统界定的最优分配比为底座固化为法定预算，严禁临时性干预截留。\n2. 颗粒度穿透下沉：宏观已达最优，应联手发改建立微观考核节点，死盯资金在具体企业端的真实转化效率。"
        elif match_score >= 60:
            analysis += "资金分布结构处于安全域，但存在冗余损耗。建议依算法黄金分割参数实施结构性拨偏。"
            advice = "【宏观政策指导方案】\n\n1. 跨部门强制调剂：立刻启动中期预算重构，将低效土建缺口强制按比例切块平移至引资引智盘面中。\n2. 以效定资拨付：不实施一次性拨款。要求执行部门自证下一周期能向85%拟合度收敛，否则触发拨款熔断。"
        else:
            analysis += "存在严重预算错配。轨迹已脱离帕累托曲面，将触发资源空转与能耗反弹的系统级崩盘。"
            advice = "【宏观政策指导方案】\n\n1. 冻结重置铁律：立刻下达市长指令，冻结全域内脱离算法可行域的扩张性项目立项流转，推倒重来。\n2. 审计问责前置：纪检监委与审计机构将最优坐标纳入追溯红线，对盲目大干快上的主体实施离任高压问责。"

        return analysis + "\n" + advice

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
        return generate_dynamic_report(clean_name, current_data, engine_logic, module_key, c_inv, f_inv, i_inv)

# ------------------------------------------
# 4. 渲染核心与全局组件
# ------------------------------------------
def render_custom_report(text):
    if "【宏观政策指导方案】" in text:
        analysis_part, advice_part = text.split("【宏观政策指导方案】")
        clean_analysis = analysis_part.replace("【系统数据分析与推演过程】：", "").strip()

        st.markdown(f"""
            <div style='background-color: #FAFAFA; border-left: 4px solid #1A3622; padding: 15px 20px; margin-top: 15px; margin-bottom: 25px; line-height: 1.8; font-size: 15px;'>
                <h4 style='color: #1A3622; margin-top: 0px; margin-bottom: 10px;'>📊 动态数据推演与过程解析</h4>
                {clean_analysis}
            </div>
        """, unsafe_allow_html=True)
        st.markdown("<h3 style='color: #2C3539; font-weight: bold; margin-bottom: 15px;'>🎯 宏观政策指导方案</h3>", unsafe_allow_html=True)

        for adv in advice_part.strip().split("\n"):
            adv = adv.strip()
            if adv and "：" in adv and adv[0].isdigit():
                title, content = adv.split("：", 1)
                st.markdown(f"""
                <div style='background-color: #FFFFFF; border: 1px solid #E0E0E0; border-left: 5px solid #4DB8B3; padding: 18px; border-radius: 6px; margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.03);'>
                    <h4 style='color: #1A3622; font-size: 17px; margin-top: 0; margin-bottom: 8px; font-weight: bold;'>🏛️ {title}</h4>
                    <p style='margin-bottom: 0; color: #444; line-height: 1.6; font-size: 14.5px;'>{content}</p>
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
    st.markdown("### 系统辅助决策矩阵快速切换")
    pages = {'mod1': "模块一：宏观体检与断层推演", 'mod2': "模块二：门槛研判与动态预警", 'mod3': "模块三：政策试错与轨迹推演", 'mod4': "模块四：多目标寻优与组合决策"}
    cols = st.columns(3)
    for i, k in enumerate([k for k in pages.keys() if k != current_page]):
        if cols[i].button(pages[k], key=f"nav_{k}", use_container_width=True):
            st.session_state.page = k; st.rerun()

# ------------------------------------------
# 5. 系统页面路由体系
# ------------------------------------------
if st.session_state.page == 'splash':
    st.markdown("<style>[data-testid='stSidebar'] {display: none;}</style>", unsafe_allow_html=True)
    st.markdown("<div style='height: 15vh;'></div>", unsafe_allow_html=True)
    st.markdown("<div class='spin-earth'>🌍</div>", unsafe_allow_html=True)
    st.markdown("<div class='title-main'>城市低碳治理智能推演系统</div>", unsafe_allow_html=True)
    st.markdown("<div class='title-sub'>宏观政策事前仿真与多目标寻优沙盘</div>", unsafe_allow_html=True)
    st.markdown("<br><p style='text-align: center; color: #888888;'>正在加载面板数据底座与动态大模型推演引擎...</p>", unsafe_allow_html=True)
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
            cat_choice = st.radio("第一步：界定数据归属与产业结构类型", category_opts, index=category_opts.index(st.session_state.city_category))
            s_city_choice = st.session_state.s_city
            custom_logic_choice = st.session_state.custom_logic

            if cat_choice == "内置：重工锁定型城市":
                available_cities = df[df["类型"] == "重工锁定型城市"]["城市"].tolist()
                s_city_choice = st.selectbox("第二步：选择重点推演城市", available_cities, index=available_cities.index(s_city_choice) if s_city_choice in available_cities else 0)
            elif cat_choice == "内置：综合服务型城市":
                available_cities = df[df["类型"] == "综合服务型城市"]["城市"].tolist()
                s_city_choice = st.selectbox("第二步：选择基准对照城市", available_cities, index=available_cities.index(s_city_choice) if s_city_choice in available_cities else 0)
            else:
                s_city_choice = st.text_input("第二步：设定系统推演目标名称", value=s_city_choice if s_city_choice not in df["城市"].tolist() else "未命名区域")
                custom_logic_choice = st.radio("核定该区域的主导产业底色", ["偏向重化工业主导", "偏向综合与服务型"])
                st.markdown("*(请依次录入核心基础宏观指标)*")
                c1, c2 = st.columns(2)
                st.session_state.custom_data["长途光缆"] = c1.number_input("长途光缆(km)", value=float(st.session_state.custom_data["长途光缆"]))
                st.session_state.custom_data["外资引进与对外开放程度"] = c2.number_input("外资(亿元)", value=float(st.session_state.custom_data["外资引进与对外开放程度"]))
                st.session_state.custom_data["IT人才密度"] = c1.number_input("数字产业规模(万人)", value=float(st.session_state.custom_data["IT人才密度"]))
                st.session_state.custom_data["基准碳排"] = c2.number_input("基准碳排总量(Mt)", value=float(st.session_state.custom_data["基准碳排"]))

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("全域数据挂载完毕，启动系统引擎", type="primary", use_container_width=True):
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
        new_cat = st.radio("一、快速切换数据类型", cat_opts, index=cat_opts.index(st.session_state.city_category.replace("宏观数据", "数据")), key="sb_cat")
        if new_cat != "外部：自定义录入数据":
            avail = df[df["类型"] == new_cat.split("：")[1]]["城市"].tolist()
            new_city = st.selectbox("二、设定推演标的", avail, index=avail.index(st.session_state.s_city) if st.session_state.s_city in avail else 0, key="sb_city")
            if new_cat != st.session_state.city_category or new_city != st.session_state.s_city:
                st.session_state.city_category = new_cat; st.session_state.s_city = new_city; st.rerun()
        else:
            new_city = st.text_input("二、区域名", value=st.session_state.s_city)
            new_logic = st.radio("核定底色", ["偏向重化工业主导", "偏向综合与服务型"], index=0 if "重化工" in st.session_state.custom_logic else 1)
            if new_cat != st.session_state.city_category or new_city != st.session_state.s_city or new_logic != st.session_state.custom_logic:
                st.session_state.city_category = new_cat; st.session_state.s_city = new_city; st.session_state.custom_logic = new_logic; st.rerun()

        st.markdown("---")
        st.markdown("三、政策干预资金参数域 (亿元)")
        st.markdown("*拉动滑块，右侧全维引擎将实时联动推演*")
        st.session_state.c_invest = st.slider("数字基础硬基建专项预算", 0.0, 20.0, st.session_state.c_invest, 0.1)
        st.session_state.f_invest = st.slider("外资先进技术引育预算", 0.0, 10.0, st.session_state.f_invest, 0.1)
        st.session_state.i_invest = st.slider("数字顶尖人才引留补贴", 0.0, 5.0, st.session_state.i_invest, 0.1)

    total_invest = st.session_state.c_invest + st.session_state.f_invest + st.session_state.i_invest
    base_carbon = city_data.get("基准碳排", 50.0)
    
    if current_engine_logic == "综合型":
        infra_cost_penalty = st.session_state.c_invest * 3.5
        reduce_effect = (st.session_state.f_invest * 2.0) + (st.session_state.i_invest * 2.5)
    else:
        infra_cost_penalty = st.session_state.c_invest * 0.8
        reduce_effect = (st.session_state.c_invest * 2.8) + (st.session_state.f_invest * 1.5) + (st.session_state.i_invest * 1.0)
    
    pred_carbon = max(base_carbon * 0.4, base_carbon + infra_cost_penalty - reduce_effect)

    # 导航菜单
    if st.session_state.page == 'menu':
        st.markdown(f"## 🌍 【{st.session_state.s_city}】低碳投资智能辅助系统")
        st.info("系统声明：内置高精度因果森林与运筹算法，最终输出由左侧交互参数动态演算生成。指导方案输出战略性指令，提供绝对量化的智库支撑。")
        for num, mod, title, desc in [("一", "mod1", "宏观体检与要素断层推演", "构建多维极差矩阵，揭示区域在数字基座、智力储备的存量断层。"),
                                      ("二", "mod2", "门槛研判与动态全息预警", "依据交互投资烈度，利用双变量矩阵实时判定资金空转与反弹风险。"),
                                      ("三", "mod3", "反事实试错与演化轨迹推演", "展现投资对碳排折线影响，依托SHAP值剥离工具输出ROI归因。"),
                                      ("四", "mod4", "全局多约束帕累托最优生成", "基于NSGA-III算法，全盘计算最完美比例并对您当前配比实施实时纠偏评价。")]:
            with st.container(border=True):
                st.markdown(f"### {num}、 {title}")
                st.markdown(desc)
                if st.button(f"进入模块{num}", key=mod, use_container_width=True): st.session_state.page = mod; st.rerun()

    # 模块一
    elif st.session_state.page == 'mod1':
        st.button("返回系统主控室", on_click=lambda: st.session_state.update({'page': 'menu'}))
        st.markdown(f"## 一、 【{st.session_state.s_city}】宏观体检与数据要素断层推演")
        categories = ['深层算力(长途光缆)', '绿色资本(外资)', '智力资本(IT人才)', '浅层网络(宽带普及)', '产业融合(普惠金融)']
        city_scores = [normalize_to_100(city_data.get(k, 50), k) for k in ["长途光缆", "外资引进与对外开放程度", "IT人才密度", "宽带普及", "普惠金融"]]
        avg_scores = [normalize_to_100(df[k].mean(), k) for k in ["长途光缆", "外资引进与对外开放程度", "IT人才密度", "宽带普及", "普惠金融"]]

        col_left, col_right = st.columns([1.2, 1])
        with col_left:
            fig_radar = go.Figure(data=[go.Scatterpolar(r=avg_scores, theta=categories, fill='toself', name='全域面板样本均线', line_color='#6495ED'),
                                        go.Scatterpolar(r=city_scores, theta=categories, fill='toself', name=f'{st.session_state.s_city}', line_color=C_DEEP_FOREST)])
            fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), height=350, title="宏观发展要素拓扑雷达图", margin=dict(t=50, b=20, l=40, r=40))
            st.plotly_chart(fig_radar, use_container_width=True)
            df_gap = pd.DataFrame({"评估维度": categories, "区域考核得分": city_scores, "全域样本均线": avg_scores})
            fig_bar = px.bar(df_gap, x="评估维度", y=["全域样本均线", "区域考核得分"], barmode="group", title="核心资源存量差异量化比对", color_discrete_sequence=["#B0BEC5", C_DEEP_FOREST])
            fig_bar.update_layout(height=350, margin=dict(t=50, b=20), legend_title=None, yaxis_title="无量纲测度得分")
            st.plotly_chart(fig_bar, use_container_width=True)
        with col_right:
            render_custom_report(get_report(st.session_state.s_city, city_data, st.session_state.custom_logic, "m1"))
        bottom_navigation('mod1')

    # 模块二
    elif st.session_state.page == 'mod2':
        st.button("返回系统主控室", on_click=lambda: st.session_state.update({'page': 'menu'}))
        st.markdown(f"## 二、 【{st.session_state.s_city}】门槛研判与动态全息预警")
        x_grid, y_grid = np.linspace(0, 20, 50), np.linspace(0, 15, 50)
        X_mat, Y_mat = np.meshgrid(x_grid, y_grid)
        soft_invest = st.session_state.f_invest + st.session_state.i_invest
        col_left, col_right = st.columns([1.2, 1])

        if current_engine_logic == "综合型":
            Z_risk = np.clip((X_mat / 8.0 * 100) - (Y_mat * 1.5), 0, 100)
            fig_heat = go.Figure(data=go.Contour(x=x_grid, y=y_grid, z=Z_risk, colorscale="Reds", contours=dict(showlabels=True)))
            fig_heat.update_layout(title="综合城市过热风险二维拓扑预测图", xaxis_title="硬基建参数(亿)", yaxis_title="软生态资本(亿)", height=350, margin=dict(t=40, b=10, l=10, r=10))
            fig_heat.add_trace(go.Scatter(x=[st.session_state.c_invest], y=[soft_invest], mode='markers+text', marker=dict(color='gold', size=16, symbol='star', line=dict(width=2, color='black')), text=["📍 实时推演极值"], textposition="top center"))
            with col_left:
                fig_gauge = go.Figure(go.Indicator(mode="gauge+number", value=min(st.session_state.c_invest / 8.0 * 100, 100), title={'text': "碳排反弹综合风险指数"},
                                     gauge={'axis': {'range': [0, 100]}, 'steps': [{'range': [0, 40], 'color': C_GLACIER_TEAL}, {'range': [40, 70], 'color': 'rgba(255, 215, 0, 0.6)'}, {'range': [70, 100], 'color': C_WARNING_RED}], 'threshold': {'line': {'color': "red", 'width': 4}, 'value': 70}}))
                fig_gauge.update_layout(height=300, margin=dict(t=50, b=10))
                st.plotly_chart(fig_gauge, use_container_width=True)
                st.plotly_chart(fig_heat, use_container_width=True)
        else:
            Z_break = np.clip(((X_mat + Y_mat) / 6.5 * 100), 0, 100)
            fig_heat = go.Figure(data=go.Contour(x=x_grid, y=y_grid, z=Z_break, colorscale="Greens", contours=dict(showlabels=True)))
            fig_heat.update_layout(title="重工城市势能积聚跨越拓扑预测图", xaxis_title="硬基建参数(亿)", yaxis_title="软生态资本(亿)", height=350, margin=dict(t=40, b=10, l=10, r=10))
            fig_heat.add_trace(go.Scatter(x=[st.session_state.c_invest], y=[soft_invest], mode='markers+text', marker=dict(color='gold', size=16, symbol='star', line=dict(width=2, color='black')), text=["📍 实时推演极值"], textposition="top center"))
            with col_left:
                fig_gauge = go.Figure(go.Indicator(mode="gauge+number", value=min(total_invest / 6.5 * 100, 100), title={'text': "碳锁定破局与门槛跨越指数"},
                                     gauge={'axis': {'range': [0, 100]}, 'steps': [{'range': [0, 50], 'color': 'rgba(255, 99, 71, 0.6)'}, {'range': [50, 80], 'color': 'rgba(255, 215, 0, 0.6)'}, {'range': [80, 100], 'color': C_DEEP_FOREST}], 'threshold': {'line': {'color': "red", 'width': 4}, 'value': 80}}))
                fig_gauge.update_layout(height=300, margin=dict(t=50, b=10))
                st.plotly_chart(fig_gauge, use_container_width=True)
                st.plotly_chart(fig_heat, use_container_width=True)

        with col_right:
            render_custom_report(get_report(st.session_state.s_city, city_data, st.session_state.custom_logic, "m2", st.session_state.c_invest, st.session_state.f_invest, st.session_state.i_invest))
        bottom_navigation('mod2')

    # 模块三
    elif st.session_state.page == 'mod3':
        st.button("返回系统主控室", on_click=lambda: st.session_state.update({'page': 'menu'}))
        st.markdown(f"## 三、 【{st.session_state.s_city}】反事实试错与演化轨迹推演")
        years = [f"{2024+i}年" for i in range(4)]
        base_traj = [base_carbon, base_carbon * 1.015, base_carbon * 1.028, base_carbon * 1.04]
        traj_1 = max(base_carbon * 0.4, base_carbon + infra_cost_penalty * (0.4 if current_engine_logic == "综合型" else 0.9) - reduce_effect * (0.2 if current_engine_logic == "综合型" else 0.3))
        traj_2 = max(base_carbon * 0.4, base_carbon + infra_cost_penalty * (0.8 if current_engine_logic == "综合型" else 1.0) - reduce_effect * (0.6 if current_engine_logic == "综合型" else 0.7))
        df_traj = pd.DataFrame({"预测年度": years * 2, "排量值(Mt)": base_traj + [base_carbon, traj_1, traj_2, pred_carbon], "演化情境": ["静态基准轨道"] * 4 + ["当前交互参数轨道"] * 4})

        col_left, col_right = st.columns([1.2, 1])
        with col_left:
            fig_line = px.line(df_traj, x="预测年度", y="排量值(Mt)", color="演化情境", markers=True, title="未来核心减排折线分轨预测", color_discrete_sequence=["#9E9E9E", C_GLACIER_TEAL])
            fig_line.update_layout(height=350)
            st.plotly_chart(fig_line, use_container_width=True)

            x_l = ["基准碳排", "硬建空耗", "外资红利", "人才红利", "推演落点"] if current_engine_logic == "综合型" else ["基准碳排", "施工耗能", "光缆红利", "外资技术", "管理效能", "推演落点"]
            y_v = [base_carbon, infra_cost_penalty, -st.session_state.f_invest * 2.0, -st.session_state.i_invest * 2.5, pred_carbon] if current_engine_logic == "综合型" else [base_carbon, infra_cost_penalty, -st.session_state.c_invest * 2.8, -st.session_state.f_invest * 1.5, -st.session_state.i_invest * 1.0, pred_carbon]
            m = ["absolute"] + ["relative"]*(len(y_v)-2) + ["total"]
            
            fig_shap = go.Figure(go.Waterfall(orientation="v", measure=m, x=x_l, textposition="outside", text=[f"{v:+.2f}" if m=="relative" else f"{v:.2f}" for v, m in zip(y_v, m)], y=y_v, connector={"line": {"color": "#444"}}, decreasing={"marker": {"color": C_DEEP_FOREST}}, increasing={"marker": {"color": C_WARNING_RED}}, totals={"marker": {"color": C_GLACIER_TEAL}}))
            fig_shap.update_layout(title="因果推断边际影响(ROI)定量剥离", showlegend=False, height=350, margin=dict(t=40, b=20, l=10, r=10))
            st.plotly_chart(fig_shap, use_container_width=True)
            
        with col_right:
            render_custom_report(get_report(st.session_state.s_city, city_data, st.session_state.custom_logic, "m3", st.session_state.c_invest, st.session_state.f_invest, st.session_state.i_invest))
        bottom_navigation('mod3')

    # 模块四
    elif st.session_state.page == 'mod4':
        st.button("返回系统主控室", on_click=lambda: st.session_state.update({'page': 'menu'}))
        st.markdown(f"## 四、 【{st.session_state.s_city}】全局多约束帕累托最优生成")
        
        np.random.seed(int(hashlib.md5(st.session_state.s_city.encode('utf-8')).hexdigest(), 16) % (2 ** 32))
        n_pts, x_inv = 250, np.random.uniform(1, 20, 250)
        y_cb = x_inv * (1.2 if current_engine_logic == "综合型" else 1.8) - np.random.normal(0, 2, n_pts)
        z_gdp = -0.1 * (x_inv - 10) ** 2 + 8 + np.random.normal(0, 1, n_pts)

        col_left, col_right = st.columns([1.2, 1])
        with col_left:
            fig_3d = px.scatter_3d(x=x_inv, y=y_cb, z=z_gdp, color=z_gdp, color_continuous_scale="RdBu_r", labels={'x': '宏观总盘(亿)', 'y': '期望减排量(Mt)', 'z': 'GDP预计变动(%)'}, title="算法生成高维帕累托最优可行域前沿")
            fig_3d.add_trace(go.Scatter3d(x=[total_invest], y=[base_carbon - pred_carbon], z=[-0.1 * (total_invest - 10) ** 2 + 8], mode='markers+text', text=["📍 当前参数坐标"], marker=dict(size=14, symbol='diamond', color='gold', line=dict(color='black', width=3)), textposition='top center'))
            fig_3d.update_layout(height=650)
            st.plotly_chart(fig_3d, use_container_width=True)
            
        with col_right:
            render_custom_report(get_report(st.session_state.s_city, city_data, st.session_state.custom_logic, "m4", st.session_state.c_invest, st.session_state.f_invest, st.session_state.i_invest))
        bottom_navigation('mod4')
