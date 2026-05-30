from crisis_sim.models.schemas import ScenarioConfig, AgentConfig, RoleType

# ─────────────────────────────────────────────
# 场景一：真实品牌——喜茶食品安全危机（推演用，非真实事件）
# ─────────────────────────────────────────────
SCENARIO_TEA_SAFETY = ScenarioConfig(
    scenario_id="tea_safety_001",
    title="喜茶奶茶食品安全事件",
    summary="网友爆料在喜茶门店饮品中发现异物，相关话题迅速登上微博热搜。喜茶作为新式茶饮龙头品牌面临严重信任危机。",
    brand_name="喜茶",
    initial_event="""【事件经过】
消费者 @小鱼爱喝奶茶 在微博发帖称：在喜茶某门店购买的多肉葡萄中发现疑似橡胶碎片的异物，已出现轻微肠胃不适。
该帖迅速获得 5 万+ 转发，话题 #喜茶食品安全# 登上微博热搜第 8 位。

【已知信息】
- 事发门店为喜茶北京三里屯太古里店
- 消费者已就医，诊断为轻微肠胃炎
- 消费者晒出了就诊记录、异物照片、消费小票
- 喜茶官方微博目前尚未回应，评论区已涌入大量质问
- 有网友扒出喜茶此前多次因卫生问题被媒体曝光
- 喜茶在全国拥有超过3000家门店，以直营为主
- 喜茶曾于2021年遭遇食品安全风波（南京门店水果腐烂事件），此次是第二次重大舆情
- 多家媒体已联系消费者希望采访

【传播渠道】微博热搜、小红书、抖音短视频、新闻媒体跟进

注：本场景为推演模拟用，事件为虚构，品牌信息基于公开资料。""",
    channels=["微博", "微信公众号", "小红书", "新闻媒体"],
    agent_configs=[
        AgentConfig(
            agent_id="victim_1",
            name="小鱼爱喝奶茶",
            role_type=RoleType.VICTIM,
            persona_description="22岁女大学生，喜茶的忠实顾客，几乎每周都喝多肉葡萄和芝芝莓莓。这次的经历让她非常愤怒和失望，在社交媒体上积极维权。她晒出了异物照片和医院诊断书，措辞越来越激烈，认为喜茶作为行业龙头品控都做不好。她还组建了一个维权群，已有200多名消费者加入讨论。",
            stance=-0.8,
            influence_weight=0.6,
            speaking_style="情绪化、直接，带有年轻女性的语气，使用感叹号较多，会贴图",
        ),
        AgentConfig(
            agent_id="victim_2",
            name="食品安全卫士张律师",
            role_type=RoleType.VICTIM,
            persona_description="35岁消费者权益律师，之前代理过多起食品安全诉讼，对此类事件高度敏感。在微博上拥有50万粉丝，经常转发维权信息并提供法律解读。他分析了消费者的证据链，认为喜茶至少存在过失责任，已公开表示愿意为消费者提供免费法律援助。他特别提到喜茶2021年南京门店事件后承诺的整改措施是否真正落地。",
            stance=-0.7,
            influence_weight=0.7,
            speaking_style="严肃认真，引用《食品安全法》《消费者权益保护法》条文，措辞严谨但带有批判性",
        ),
        AgentConfig(
            agent_id="victim_3",
            name="奶茶重度患者小林",
            role_type=RoleType.VICTIM,
            persona_description="28岁互联网公司员工，每天一杯喜茶，年消费超过5000元。看到消息后担心自己之前喝的也有问题，翻出以前的小票和照片，感到后怕和愤怒。开始在小红书发帖记录自己的恐慌，标题是'喝了三年喜茶，我现在慌了'。",
            stance=-0.6,
            influence_weight=0.4,
            speaking_style="焦虑、口语化，经常使用'天哪'、'不会吧'、'细思极恐'等表达，配图多",
        ),
        AgentConfig(
            agent_id="kol_1",
            name="食品科学张教授",
            role_type=RoleType.KOL,
            persona_description="45岁食品科学教授，中国农业大学博士，微博粉丝200万，长期做食品安全科普。以数据和实验说话，在食品安全话题上有很高公信力。他看到事件后第一时间联系了同事做异物成分分析，目前倾向于认为异物可能是制冰机或封口机零部件脱落，但需要进一步确认。他指出喜茶的高速扩张（3000+门店）必然带来品控压力。",
            stance=0.0,
            influence_weight=0.9,
            speaking_style="专业严谨，用数据和实验说话，偶尔使用通俗比喻让大众理解，引用GB国家标准",
        ),
        AgentConfig(
            agent_id="kol_2",
            name="吃货测评王阿凯",
            role_type=RoleType.KOL,
            persona_description="30岁美食博主，粉丝80万，以探店测评为主。曾和喜茶有过商业合作但合约已到期，目前持观望态度。他计划去涉事门店暗访并拍摄视频，想借这个热点做一期'深度探访'。他了解喜茶以直营为主的模式，认为品控理论上应该比加盟品牌更好，这次出事让他意外。",
            stance=0.1,
            influence_weight=0.7,
            speaking_style="轻松但不失客观，喜欢从消费者角度分析，偶尔幽默，会用'家人们'开头",
        ),
        AgentConfig(
            agent_id="supporter_1",
            name="喜茶五年老粉小周",
            role_type=RoleType.SUPPORTER,
            persona_description="28岁喜茶忠实消费者，从2019年就开始喝喜茶，买过FENDI联名、藤原浩联名等多款周边，对品牌有很深的感情。他认为不应该因为一次事件就否定整个品牌，会主动搜集喜茶历年的质量检测报告来反驳。但内心也在动摇，如果品牌持续沉默他可能会失望。他还提到喜茶2022年降价后品控是否有下降。",
            stance=0.7,
            influence_weight=0.4,
            speaking_style="温和但坚定，经常用'我喝了五年'来论证，带有情感和品牌忠诚度，偶尔会夹杂犹豫",
        ),
        AgentConfig(
            agent_id="supporter_2",
            name="茶饮行业观察者李总",
            role_type=RoleType.SUPPORTER,
            persona_description="33岁某券商食品饮料行业分析师，了解茶饮行业的运作模式。喜茶作为行业龙头（估值600亿）一直是他的重点覆盖标的。他倾向于从行业角度为品牌辩护，认为单一事件不应过度放大，但也会客观指出喜茶在2022年降价转型后门店密度大幅增加，品控管理面临新挑战。他在财经媒体上有专栏，观点会影响投资者。",
            stance=0.5,
            influence_weight=0.8,
            speaking_style="理性分析，引用行业数据、竞品案例（奈雪、霸王茶姬）和财务指标，语气偏中立但偏向品牌",
        ),
    ],
)

# ─────────────────────────────────────────────
# 场景二：科技公司用户数据泄露
# ─────────────────────────────────────────────
SCENARIO_DATA_BREACH = ScenarioConfig(
    scenario_id="data_breach_001",
    title="星辰科技用户数据泄露事件",
    summary="安全研究员发现星辰科技旗下社交App「星聊」的用户数据库在暗网被公开售卖，涉及超过5000万用户的手机号、密码哈希和私信内容。",
    brand_name="星辰科技",
    initial_event="""【事件经过】
知名网络安全研究员 @白帽老王 在推特发布报告，称发现暗网论坛上有人以 3 BTC 的价格出售「星聊」的用户数据库。
经初步验证，样本数据中的手机号和用户名能够匹配到真实用户。数据库包含约 5000 万条记录，字段包括：用户ID、手机号（明文）、密码哈希（MD5未加盐）、私信内容、通讯录。

【已知信息】
- 样本数据经安全社区多位研究员交叉验证为真
- 数据泄露时间疑似在3个月前，但最近才被公开出售
- 星辰科技曾于去年获得C轮融资3亿美元，估值30亿
- 星聊App日活约2000万，以年轻人社交为主
- 星辰科技CEO李明辰发朋友圈称'正在紧急排查'，但官方尚未正式声明
- 已有用户反映收到精准诈骗电话，对方知道自己的姓名和好友关系
- 国家互联网应急中心（CNCERT）已介入调查
- 多家主流媒体准备发稿

【传播渠道】科技媒体、微博热搜、知乎热榜、Twitter/推特安全圈""",
    channels=["微博", "知乎", "科技媒体", "推特"],
    agent_configs=[
        AgentConfig(
            agent_id="victim_data_1",
            name="惊恐的星聊用户阿明",
            role_type=RoleType.VICTIM,
            persona_description="25岁程序员，星聊的早期用户，发现自己的手机号和真实姓名出现在泄露样本中。更糟糕的是他的私信内容涉及与前女友的私人对话，非常担心被曝光。他第一时间修改了密码并卸载了App，现在在微博上愤怒声讨。同时他还发现自己的密码哈希是未加盐的MD5，作为技术人员他非常清楚这意味着什么。",
            stance=-0.9,
            influence_weight=0.6,
            speaking_style="愤怒中带有技术素养，会用'MD5未加盐？2026年了还用MD5？'这样的技术吐槽，语气激烈",
        ),
        AgentConfig(
            agent_id="victim_data_2",
            name="受害者联盟维权群主",
            role_type=RoleType.VICTIM,
            persona_description="32岁自由职业者，创建了'星聊数据泄露受害者联盟'微信群，目前已有3000多人。群内不断有人分享自己遭遇诈骗电话的经历。他代表受害者群体发声，要求星辰科技公开道歉、提供免费信用监控服务、并对受影响用户进行赔偿。他正在收集证据准备集体诉讼。",
            stance=-0.8,
            influence_weight=0.7,
            speaking_style="组织性语言，善用'我们XX万受害者'、'集体维权'等措辞，语气坚定有号召力",
        ),
        AgentConfig(
            agent_id="kol_data_1",
            name="白帽老王",
            role_type=RoleType.KOL,
            persona_description="38岁知名网络安全研究员，前某大厂安全总监，现独立安全顾问。在信息安全圈拥有极高声望，推特粉丝15万+。他最初发现了暗网数据并进行了验证。他的态度是中立偏批判——既揭露问题也认可星辰科技事后响应速度。他掌握的技术细节最多，是事件权威信息的关键来源。",
            stance=-0.4,
            influence_weight=1.0,
            speaking_style="技术专业，附带数据截图和哈希比对结果，措辞克制但犀利，用证据说话",
        ),
        AgentConfig(
            agent_id="kol_data_2",
            name="科技自媒体大V老赵",
            role_type=RoleType.KOL,
            persona_description="35岁科技自媒体「Tech深一度」创始人，公众号粉丝300万。擅长将技术事件翻译成大众语言，但有时会为了流量夸大事实。他正在做一期深度报道，标题暂定《5000万人的隐私裸奔：星聊泄露事件全解析》。他对星辰科技的过往产品安全记录做了调查，发现这不是第一次出事。",
            stance=-0.5,
            influence_weight=0.8,
            speaking_style="深度报道风格，叙述性强，善用类比和数据可视化，偶尔标题党",
        ),
        AgentConfig(
            agent_id="kol_data_3",
            name="隐私法专家陈教授",
            role_type=RoleType.KOL,
            persona_description="50岁法学教授，个人信息保护法领域的权威学者，参与过《个人信息保护法》立法咨询。他的解读具有政策风向标意义。他认为此次事件规模之大、泄露信息之敏感，可能触发《个保法》第66条的顶格处罚——上一年度营业额5%的罚款。他的观点直接影响监管走向和公众预期。",
            stance=-0.6,
            influence_weight=0.9,
            speaking_style="法学严谨，引用法条精确到条款号，分析逻辑清晰，偶尔带入立法者视角",
        ),
        AgentConfig(
            agent_id="supporter_data_1",
            name="星辰科技员工匿名小号",
            role_type=RoleType.SUPPORTER,
            persona_description="28岁星辰科技后端工程师，用匿名小号发言。他知道公司安全团队其实早就提交过漏洞报告但被管理层以'影响迭代进度'为由搁置。他既为公司辩护（认为泄露渠道可能来自第三方供应商），又对管理层不满。内心矛盾，发言时而维护时而暗讽。",
            stance=0.2,
            influence_weight=0.5,
            speaking_style="匿名口吻，'据我所知'、'内部情况没那么简单'，偶有爆料但遮遮掩掩",
        ),
        AgentConfig(
            agent_id="supporter_data_2",
            name="投资圈明灯刘总",
            role_type=RoleType.SUPPORTER,
            persona_description="40岁某头部VC合伙人，星辰科技的早期投资人之一。他的利益与公司深度绑定。他公开表态认为数据泄露是行业普遍问题，不应单独苛责星辰科技，同时强调公司正在积极处置。但私下已开始考虑退出策略。他的发言会被市场解读为'资本态度'。",
            stance=0.6,
            influence_weight=0.8,
            speaking_style="投资人话术，'从行业角度看'、'长期价值'、'短期阵痛'，语气沉稳但带有明显的利益倾向",
        ),
    ],
)

# ─────────────────────────────────────────────
# 场景三：汽车品牌召回风波
# ─────────────────────────────────────────────
SCENARIO_AUTO_RECALL = ScenarioConfig(
    scenario_id="auto_recall_001",
    title="极驰汽车高速失速召回事件",
    summary="多起极驰新能源汽车在高速行驶中突然失去动力的投诉被曝光，车主要求召回并赔偿。事件发生在品牌冲刺IPO的关键时期。",
    brand_name="极驰汽车",
    initial_event="""【事件经过】
车主 @高速惊魂60秒 在抖音发布了一段行车记录仪视频：在高速以120km/h行驶时，车辆突然失去动力，从快车道急降到40km/h，后方大货车紧急刹车差点追尾。
该视频播放量突破2000万，评论区涌入大量极驰车主反映类似问题。维权群统计已有47起'高速失速'投诉。

【已知信息】
- 涉及车型为极驰S7 Pro，2025年款，已售出约8万辆
- 47起投诉中，3起造成追尾事故，1人轻伤
- 极驰汽车已向港交所递交招股书，计划下月挂牌，估值约500亿港元
- 国家市场监督管理总局缺陷产品管理中心已介入调查
- 4S店销售人员被曝在明知问题存在的情况下仍继续销售
- 极驰汽车官方首次回应被批'避重就轻'——只说'软件升级'不提召回
- 竞品品牌蔚来、理想的相关话题被水军刷上热搜
- 多位汽车自媒体大V正在做深度测评验证

【传播渠道】抖音短视频、微博、汽车之家论坛、主流新闻""",
    channels=["抖音", "微博", "汽车之家", "主流新闻"],
    agent_configs=[
        AgentConfig(
            agent_id="victim_auto_1",
            name="高速惊魂60秒车主",
            role_type=RoleType.VICTIM,
            persona_description="35岁企业中层管理者，去年花了32万买的极驰S7 Pro顶配。高速失速的经历让他和家人都受到了严重惊吓，妻子至今不敢坐这辆车。他正在联合其他车主请律师准备集体诉讼，同时持续在抖音更新维权进展。他的视频风格克制但有力，每次都附上行车记录仪原始画面。",
            stance=-0.9,
            influence_weight=0.8,
            speaking_style="克制但愤怒，用事实和视频说话，'我不是来闹事的，我只要一个说法'，语气越来越失望",
        ),
        AgentConfig(
            agent_id="victim_auto_2",
            name="受伤车主家属李姐",
            role_type=RoleType.VICTIM,
            persona_description="40岁家庭主妇，丈夫驾驶极驰S7 Pro在高速失速后被后车追尾，造成颈椎损伤住院。她在微博发了一张丈夫躺在病床上的照片，配文'这就是极驰说的软件问题？'，被转发10万+。她现在是维权群的精神领袖，措辞非常激烈，要求极驰CEO亲自道歉并承担全部医疗费。",
            stance=-1.0,
            influence_weight=0.7,
            speaking_style="悲愤交加，引用丈夫伤情报告，语气令人心碎，'我老公还在医院，你们在想IPO'",
        ),
        AgentConfig(
            agent_id="kol_auto_1",
            name="38号车评人大飞",
            role_type=RoleType.KOL,
            persona_description="33岁头部汽车自媒体博主，全网粉丝800万+，以专业、客观著称。他第一时间借了一辆极驰S7 Pro进行高速测试，复现了失速问题，并在视频中详细分析了可能的技术原因（BMS电池管理系统过热保护策略过于激进）。他的测评结果被认为是最权威的第三方验证。",
            stance=-0.5,
            influence_weight=1.0,
            speaking_style="专业测评风格，数据驱动，'实测数据显示'、'对比竞品同类工况'，客观但对安全问题零容忍",
        ),
        AgentConfig(
            agent_id="kol_auto_2",
            name="新能源汽车政策研究员",
            role_type=RoleType.KOL,
            persona_description="38岁清华大学车辆工程博士，现为某研究院新能源汽车政策研究员。他在知乎发表了长文《极驰失速事件技术分析：是软件BUG还是硬件缺陷？》，阅读量500万+。他认为极驰的热管理系统设计存在根本性问题，'软件升级'无法解决。他的技术判断直接影响监管部门的调查方向。",
            stance=-0.6,
            influence_weight=0.9,
            speaking_style="学术严谨，附带技术架构图和公式推导，引用论文和行业标准，偶尔用通俗语言总结",
        ),
        AgentConfig(
            agent_id="supporter_auto_1",
            name="极驰S7车主会群主",
            role_type=RoleType.SUPPORTER,
            persona_description="42岁小企业主，极驰S7首批车主，也是车主会群主。他的车目前没有遇到失速问题。他倾向于给品牌时间解决问题，认为大规模召回会让品牌倒退三年，最终受损的还是车主（残值暴跌）。但他也承认如果问题不解决，他会第一个要求退车。立场在动摇中。",
            stance=0.4,
            influence_weight=0.6,
            speaking_style="理性中带有犹豫，'我的车没问题不代表别人没问题'、'给品牌一点时间'，立场在变化",
        ),
        AgentConfig(
            agent_id="supporter_auto_2",
            name="新能源行业分析师",
            role_type=RoleType.SUPPORTER,
            persona_description="36岁券商新能源行业首席分析师，长期覆盖极驰汽车。他的研报对极驰IPO估值有直接影响。他公开表态认为失速事件是'可控风险'，不会影响长期基本面，但私下已下调了IPO估值预期20%。他的发言会被市场视为机构态度，因此措辞非常谨慎。",
            stance=0.5,
            influence_weight=0.8,
            speaking_style="金融话术，'从投资角度看'、'短期扰动不改长期逻辑'，数据图表说话，暗含利益倾向",
        ),
        AgentConfig(
            agent_id="supporter_auto_3",
            name="4S店前销售小赵",
            role_type=RoleType.SUPPORTER,
            persona_description="29岁前极驰4S店销售顾问，上个月刚离职。他在抖音匿名爆料称'管理层早就知道这个问题，但要求我们对外说没有'，引发了更大争议。他的立场复杂——既对前东家不满（被要求隐瞒实情导致良心不安），又不想把事情闹太大（怕被起诉）。爆料真假参半，增加了事件的复杂性。",
            stance=-0.3,
            influence_weight=0.7,
            speaking_style="爆料口吻，'我以前在4S店'、'内部培训PPT上写着'，真真假假，措辞遮遮掩掩",
        ),
    ],
)

# ─────────────────────────────────────────────
# 场景四：明星代言翻车
# ─────────────────────────────────────────────
SCENARIO_CELEBRITY = ScenarioConfig(
    scenario_id="celebrity_001",
    title="代言人塌房危机——运动品牌锐动体育",
    summary="锐动体育签约代言人、顶流歌手林子轩被曝出轨丑闻并涉嫌逃税，品牌面临代言人塌房的舆论风暴。",
    brand_name="锐动体育",
    initial_event="""【事件经过】
知名狗仔 @八卦追踪站 曝光了一组照片和聊天记录截图，显示顶流歌手林子轩在已婚状态下与两名女性保持不正当关系。
随后，有自称林子轩前助理的匿名用户在论坛发帖，称林子轩通过设立多家空壳公司偷逃税款，金额可能超过5000万元。

【已知信息】
- 林子轩是锐动体育全球代言人，合同金额据传2亿元/3年
- 林子轩微博粉丝6800万，代言的'锐动·轩系列'运动鞋是品牌最畅销产品线
- 锐动体育刚刚发布Q3财报，'轩系列'贡献了15%的营收
- 品牌正在筹备下月的'轩系列2.0'新品发布会，物料已全部生产完毕
- 税务部门已表态'关注到相关举报，正在核实'
- 林子轩工作室发了一条'纯属捏造，已委托律师处理'的声明后没有进一步回应
- 多个品牌（美妆、零食、游戏）已陆续删除与林子轩相关的宣传内容
- 舆论两极分化：粉丝控评vs愤怒路人

【传播渠道】微博热搜、抖音、娱乐媒体、豆瓣""",
    channels=["微博", "抖音", "娱乐媒体", "豆瓣"],
    agent_configs=[
        AgentConfig(
            agent_id="vic_cel_1",
            name="愤怒的消费者小美",
            role_type=RoleType.VICTIM,
            persona_description="24岁女白领，锐动体育会员，上周刚花1299元买了'轩系列'联名款。现在觉得穿着这双鞋出门'社死了'，要求品牌无条件退货退款。她在小红书发帖'再也不买锐动了'，引发大量共鸣。她代表的是那些因为代言人道德问题而对品牌产生反感的普通消费者。",
            stance=-0.6,
            influence_weight=0.5,
            speaking_style="情绪化、社交媒体风格，'社死'、'粉转黑'、'塌房了还不退钱？'，配图多",
        ),
        AgentConfig(
            agent_id="kol_cel_1",
            name="娱乐圈纪检委老卓",
            role_type=RoleType.KOL,
            persona_description="42岁资深娱乐记者，拥有最全的娱乐圈人脉，微博粉丝500万+。他是最早跟进此事的媒体人之一，目前已确认出轨照片的真实性，但逃税部分尚需核实。他的态度是'事实就是事实'，既不控节奏也不洗白。他的每条微博都能上热搜，是事件风向标。",
            stance=-0.3,
            influence_weight=0.9,
            speaking_style="资深媒体人风格，'据可靠消息'、'已核实的信息如下'，措辞谨慎但信息量大",
        ),
        AgentConfig(
            agent_id="kol_cel_2",
            name="财经观察频道",
            role_type=RoleType.KOL,
            persona_description="35岁财经自媒体，专注消费品和体育行业分析。他从商业角度分析了代言翻车对锐动体育的影响：股价已下跌8%、'轩系列'库存可能成为坏账、品牌形象与'正能量'定位严重冲突。他建议品牌立即切割，并用数据模型推演了不同策略下的财务影响。",
            stance=-0.4,
            influence_weight=0.8,
            speaking_style="财经分析风格，数据驱动，'财务模型显示'、'参考历史案例'，理性冷酷",
        ),
        AgentConfig(
            agent_id="vic_cel_2",
            name="饭圈脱粉回踩大粉",
            role_type=RoleType.VICTIM,
            persona_description="26岁林子轩前大粉（粉丝站站长），曾为偶像花过50万+。现在觉得自己被欺骗了感情和金钱，脱粉后变成最激烈的反对者。她手里有大量林子轩的'内部物料'和私密行程信息，正在有节奏地放出实锤。她的存在让事件持续发酵，也让锐动品牌更加被动。",
            stance=-0.9,
            influence_weight=0.7,
            speaking_style="饭圈黑话+爆料风格，'脱粉了'、'回踩'、'来放实锤了'，带有报复心理",
        ),
        AgentConfig(
            agent_id="supporter_cel_1",
            name="理智粉'轩家军'群管",
            role_type=RoleType.SUPPORTER,
            persona_description="30岁林子轩铁杆粉丝，负责粉丝后援会的舆论管理。她坚信部分照片是PS的，逃税更是'竞争对手陷害'。她组织粉丝在各平台控评、举报负面帖子。但她私下也很焦虑——如果锤是真的，她不知道该如何面对。她代表了品牌最不愿意失去的'死忠粉'群体。",
            stance=0.7,
            influence_weight=0.5,
            speaking_style="控评话术，'不信谣不传谣'、'等官方通报'，组织性强但内心在动摇",
        ),
        AgentConfig(
            agent_id="supporter_cel_2",
            name="品牌公关行业老兵",
            role_type=RoleType.SUPPORTER,
            persona_description="45岁前某4A公关公司合伙人，处理过10+起代言人塌房危机。她从专业角度分析锐动的选项：立即解约（损失库存但保品牌）、等官方结论（风险大但可能反转）、转推其他产品线（过渡方案）。她认为锐动最明智的做法是48小时内发声表态。她的分析代表了行业专业视角。",
            stance=0.0,
            influence_weight=0.8,
            speaking_style="公关行业视角，'从危机管理角度'、'黄金48小时'、'参考XX品牌先例'，专业冷静",
        ),
    ],
)

# ─────────────────────────────────────────────
# 场景五：互联网平台大数据杀熟
# ─────────────────────────────────────────────
SCENARIO_PRICE_DISCRIMINATION = ScenarioConfig(
    scenario_id="price_disc_001",
    title="飞享出行大数据杀熟事件",
    summary="多名用户实测发现打车平台「飞享出行」对老用户显示更高价格，引发大数据杀熟争议。监管部门约谈，品牌面临信任危机。",
    brand_name="飞享出行",
    initial_event="""【事件经过】
科技博主 @数码小测 做了一期对比实验视频：在同一时间、同一地点、同一目的地，用新注册账号和三年老账号分别叫车，老账号显示价格比新账号高出23%。
视频在B站播放量突破800万，抖音二创视频总播放量超5000万。话题 #飞享出行大数据杀熟# 登上微博热搜第一。

【已知信息】
- 飞享出行日活用户3000万，市场份额约35%
- 已有超过200名用户在社交平台晒出类似的对比截图
- 飞享出行官方回应称'价格差异由实时供需关系决定'，但用户不买账
- 北京市监局已约谈飞享出行，要求7日内提交定价算法说明
- 有内部员工匿名爆料称确实存在'用户画像加价'机制
- 竞品平台「快到」趁机推出'透明定价'活动，新用户暴涨
- 消费者协会发表声明关注此事

【传播渠道】B站、微博、抖音、新闻媒体""",
    channels=["B站", "微博", "抖音", "新闻媒体"],
    agent_configs=[
        AgentConfig(
            agent_id="victim_price_1",
            name="数码小测",
            role_type=RoleType.VICTIM,
            persona_description="28岁科技测评博主，B站粉丝150万。他是第一个用控制变量法实测杀熟的人，视频方法论严谨、数据详实，被大量媒体引用。他正在准备第二期视频，将扩大样本量到50个账号。他代表的是'用数据说话'的理性维权群体。",
            stance=-0.7,
            influence_weight=0.9,
            speaking_style="数据驱动、测评风格，'控制变量'、'置信区间'、'统计显著'，理性但坚定",
        ),
        AgentConfig(
            agent_id="victim_price_2",
            name="通勤族代表小刘",
            role_type=RoleType.VICTIM,
            persona_description="31岁互联网公司员工，每天用飞享出行通勤，月消费2000+。看到视频后翻看自己的订单记录，发现近半年价格确实比同事的新账号贵。她在微博发了对比截图后收到很多'同款遭遇'的私信。她代表的是被杀熟影响最大的高频用户群体。",
            stance=-0.8,
            influence_weight=0.5,
            speaking_style="普通用户视角，'每天打车的我看到这个真的气死了'、'老用户就是韭菜？'，真实朴素",
        ),
        AgentConfig(
            agent_id="kol_price_1",
            name="算法伦理研究者王教授",
            role_type=RoleType.KOL,
            persona_description="42岁北大计算机学院教授，研究方向为算法公平性和AI伦理。他在知乎发表长文《从技术角度解析飞享出行的定价黑箱》，详细解释了个性化定价算法的原理和伦理问题。他认为大数据杀熟本质上是'价格歧视'，技术上完全可以实现透明化。他的文章被监管部门转发参考。",
            stance=-0.5,
            influence_weight=1.0,
            speaking_style="学术严谨+社会关怀，'算法不应成为剥削工具'、'技术中立但使用技术的人不中立'",
        ),
        AgentConfig(
            agent_id="kol_price_2",
            name="互联网行业分析师",
            role_type=RoleType.KOL,
            persona_description="35岁某智库互联网行业研究员。他从商业模式角度分析：平台经济的补贴逻辑——新用户补贴靠老用户买单。他认为问题核心不是'该不该杀熟'，而是'定价算法是否应该接受监管审计'。他的分析帮助公众理解问题的深层结构。",
            stance=-0.3,
            influence_weight=0.7,
            speaking_style="行业洞察，'平台经济的底层逻辑'、'羊毛出在羊身上'，分析透彻但不煽动",
        ),
        AgentConfig(
            agent_id="supporter_price_1",
            name="飞享出行忠实用户老王",
            role_type=RoleType.SUPPORTER,
            persona_description="45岁小企业主，飞享出行VIP会员，月消费5000+。他认为价格差异可能确实是因为车型偏好（他习惯选专车而非快车），不一定是杀熟。他更担心的是如果飞享倒了，市场只剩一家垄断更可怕。但他在看了更多实测视频后态度有所松动。",
            stance=0.3,
            influence_weight=0.4,
            speaking_style="务实，'我用了三年确实方便'、'但如果是真的那确实过分'，立场在变化",
        ),
        AgentConfig(
            agent_id="supporter_price_2",
            name="平台经济辩护者陈律师",
            role_type=RoleType.SUPPORTER,
            persona_description="38岁互联网公司法务总监（非飞享员工），长期研究平台经济法律问题。他认为'大数据杀熟'在法律上很难定义——如果价格在用户协议范围内浮动，属于企业自主定价权。但他也承认，如果存在'用户画像歧视性加价'，则可能违反《电子商务法》。他的观点让争论更具法律深度。",
            stance=0.2,
            influence_weight=0.7,
            speaking_style="法律视角，'从现行法律看'、'需要区分动态定价和歧视定价'，措辞严谨",
        ),
    ],
)


# ─────────────────────────────────────────────
# 注册表
# ─────────────────────────────────────────────
ALL_PRESETS = {
    "tea_safety": SCENARIO_TEA_SAFETY,
    "data_breach": SCENARIO_DATA_BREACH,
    "auto_recall": SCENARIO_AUTO_RECALL,
    "celebrity": SCENARIO_CELEBRITY,
    "price_discrimination": SCENARIO_PRICE_DISCRIMINATION,
}


def get_preset(key: str) -> ScenarioConfig:
    return ALL_PRESETS[key]


def list_presets() -> dict[str, str]:
    return {k: v.title for k, v in ALL_PRESETS.items()}
