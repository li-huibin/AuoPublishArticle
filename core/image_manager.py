# -*- coding: utf-8 -*-
"""
图片管理器 - 负责搜索、下载、上传图片
支持 Unsplash、Pexels、Pixabay 等免费图库 API
"""
import os
import requests
import time
import random
import hashlib
from typing import Optional, List, Dict, Tuple


class ImageManager:
    """图片管理器类"""

    # 中英文关键词映射表 - 用于将中文主题翻译成英文搜索关键词
    KEYWORD_TRANSLATIONS = {
        # 科技类
        "人工智能": ["artificial intelligence", "AI", "machine learning", "deep learning", "neural network",
                     "cognitive computing", "intelligent system", "computer vision"],
        "AI": ["artificial intelligence", "machine intelligence", "deep learning", "AI model", "intelligent automation",
               "AI system", "cognitive AI"],
        "机器人": ["robot", "robotics", "automation", "industrial robot", "service robot", "android", "mechatronics",
                   "robot arm"],
        "无人驾驶": ["autonomous vehicle", "self-driving car", "driverless car", "automated driving",
                     "autonomous transport", "robotaxi", "autonomous mobility"],
        "自动驾驶": ["self-driving", "autonomous driving", "driverless technology", "automated vehicle",
                     "autonomous navigation", "ADAS", "vehicle autonomy"],
        "区块链": ["blockchain", "distributed ledger", "cryptocurrency", "smart contract", "bitcoin", "ethereum",
                   "tokenization", "decentralized finance"],
        "大数据": ["big data", "data analytics", "data science", "data mining", "data lake", "data warehouse",
                   "predictive analytics", "business intelligence"],
        "云计算": ["cloud computing", "cloud services", "IaaS", "PaaS", "SaaS", "cloud infrastructure",
                   "cloud platform", "hybrid cloud"],
        "5G": ["5G", "5G network", "telecommunication", "wireless communication", "mobile broadband", "network slicing",
               "edge computing", "cellular technology"],
        "元宇宙": ["metaverse", "virtual reality", "VR", "augmented reality", "AR", "mixed reality", "digital universe",
                   "virtual world", "immersive experience"],
        "算法": ["algorithm", "computational algorithm", "model", "optimization", "AI algorithm", "sorting algorithm",
                 "search algorithm", "predictive model"],
        "芯片": ["chip", "semiconductor", "processor", "integrated circuit", "IC", "microchip", "CPU", "GPU", "ASIC"],
        "手机": ["smartphone", "mobile phone", "cellphone", "iphone", "android phone", "handset", "mobile device",
                 "smart device"],
        "电脑": ["computer", "laptop", "desktop", "PC", "workstation", "notebook", "personal computer", "server"],
        "互联网": ["internet", "web", "online", "digital network", "web platform", "internet ecosystem",
                   "network connectivity"],
        "科技": ["technology", "tech", "innovation", "high-tech", "digital technology", "technical innovation",
                 "technology industry"],

        # 商业与经济类
        "经济": ["economy", "economic", "macroeconomics", "microeconomics", "economic growth", "economic development",
                 "GDP", "fiscal"],
        "金融": ["finance", "financial services", "banking", "investment", "capital markets", "private equity",
                 "asset management", "fintech"],
        "股市": ["stock market", "equities", "share market", "trading", "stock exchange", "market index", "securities",
                 "investment market"],
        "创业": ["startup", "entrepreneurship", "venture creation", "new venture", "business launch", "entrepreneur",
                 "startup ecosystem"],
        "公司": ["company", "corporation", "enterprise", "business", "firm", "limited company", "organization",
                 "business entity"],
        "企业": ["enterprise", "business", "corporation", "organization", "company group", "commercial enterprise",
                 "industrial enterprise"],
        "市场": ["market", "marketplace", "commerce", "retail market", "consumer market", "trade", "market demand",
                 "market analysis"],
        "投资": ["investment", "investing", "capital investment", "venture capital", "private equity",
                 "investment portfolio", "asset allocation"],
        "货币": ["currency", "money", "fiat currency", "digital currency", "foreign exchange", "cash", "monetary unit",
                 "cryptocurrency"],
        "银行": ["bank", "banking", "financial institution", "commercial bank", "retail bank", "investment bank",
                 "branch", "credit union"],

        # 产业类
        "制造业": ["manufacturing", "production", "industrial manufacturing", "factory", "assembly line",
                   "mass production", "manufacturing process"],
        "能源": ["energy", "power industry", "electricity", "renewable energy", "oil and gas", "energy transition",
                 "power generation", "clean energy"],
        "汽车": ["automotive", "car industry", "vehicle manufacturing", "auto industry", "transportation",
                 "electric vehicle", "EV", "automobile"],
        "航空航天": ["aerospace", "aviation", "aircraft", "spacecraft", "airline", "rocket", "aerospace engineering",
                     "space technology"],
        "建筑": ["construction", "building", "architecture", "civil engineering", "infrastructure",
                 "construction project", "real estate development"],
        "交通物流": ["logistics", "transportation", "supply chain", "shipping", "freight", "distribution",
                     "logistics management", "cargo transport"],
        "零售": ["retail", "retail industry", "store", "merchandise", "consumer retail", "brick-and-mortar",
                 "omnichannel retail", "e-commerce retail"],
        "医疗健康": ["healthcare", "medical care", "health system", "hospital", "clinical services", "patient care",
                     "health industry", "medical technology"],
        "生物技术": ["biotechnology", "biotech", "genetics", "life science", "bioengineering",
                     "pharmaceutical research", "biopharma", "genomic technology"],
        "教育培训": ["education", "training", "e-learning", "online education", "tutoring", "academic training",
                     "professional development", "education technology"],
        "媒体": ["media", "broadcasting", "press", "journalism", "publishing", "digital media", "news media",
                 "content media"],
        "保险": ["insurance", "insurance policy", "risk management", "underwriting", "health insurance",
                 "property insurance", "insurance industry", "coverage"],
        "房地产": ["real estate", "property", "housing", "commercial property", "land development",
                   "real estate market", "residential property", "property investment"],
        "酒店": ["hospitality", "hotel", "resort", "lodging", "accommodation", "hospitality industry", "hotel chain",
                 "guest service"],
        "饮食": ["food and beverage", "F&B", "catering", "restaurant", "food service", "food industry", "culinary",
                 "food production"],
        "时尚服装": ["fashion", "apparel", "textile", "garment", "clothing", "fashion industry", "fashion design",
                     "fashion retail"],
        "体育健康": ["sports", "fitness", "wellness", "athletics", "recreation", "sports industry",
                     "health and fitness", "sporting events"],
        "环境保护": ["environmental protection", "sustainability", "green technology", "ecology", "conservation",
                     "environmental management", "climate action"],
        "科研": ["research", "science", "laboratory", "experiment", "scientific research", "R&D",
                 "research institution", "innovation research"],
        "政府": ["government", "public sector", "administration", "policy", "public service", "government affairs",
                 "regulatory body"],
        "国防": ["defense", "military", "armed forces", "national security", "defense industry", "security services",
                 "military technology"],
        "通信": ["telecommunication", "telecom", "network", "broadband", "wireless communication",
                 "communications infrastructure", "telecom services"],
        "公用事业": ["utilities", "power grid", "water supply", "sewage", "gas service", "utility management",
                     "public utility"],
        "人力资源": ["human resources", "HR", "recruitment", "talent management", "staffing", "personnel management",
                     "workforce development"],
        "市场营销": ["marketing", "advertising", "branding", "promotion", "digital marketing", "marketing strategy",
                     "market promotion", "advertising campaign"],
        "电子商务": ["e-commerce", "online retail", "digital commerce", "e-shop", "online marketplace",
                     "ecommerce platform", "online shopping"],
        "游戏娱乐": ["gaming", "entertainment", "esports", "interactive media", "game development",
                     "digital entertainment", "video games", "entertainment content"],
        "材料": ["materials", "advanced materials", "composites", "metals", "polymers", "material science",
                 "specialty materials"],
        "化工": ["chemical", "chemicals", "petrochemical", "industrial chemistry", "chemical engineering",
                 "chemical manufacturing", "process chemistry"],
        "矿业": ["mining", "minerals", "ore extraction", "quarrying", "mineral resources", "mining industry",
                 "mine operations"],
        "农林牧渔": ["agriculture", "farming", "forestry", "animal husbandry", "fishing", "agriculture industry",
                     "agribusiness", "aquaculture"],
        "海洋": ["marine", "ocean", "maritime", "shipping", "naval", "marine industry", "oceanography",
                 "maritime transport"],
        "咨询": ["consulting", "management consulting", "business advisory", "strategy consulting", "consultancy",
                 "consulting services"],
        "创投": ["venture capital", "startup funding", "angel investment", "private equity", "venture fund",
                 "investment capital", "VC"],
        "可再生能源": ["renewable energy", "solar power", "wind power", "hydropower", "clean energy", "green energy",
                       "sustainable energy"],
        "数字化转型": ["digital transformation", "digitization", "digitalization", "industry 4.0",
                       "smart manufacturing", "digital business", "digital strategy"],
        "网络安全": ["cybersecurity", "information security", "data protection", "network security", "cyber defense",
                     "security operations", "cyber risk"],
        "人工智能伦理": ["AI ethics", "ethical AI", "AI governance", "responsible AI", "AI fairness",
                         "algorithmic transparency"],

        # 社会与热点类
        "事件": ["event", "incident", "occurrence", "happening", "news event", "case", "development"],
        "新闻": ["news", "media report", "journalism", "press", "news coverage", "headline", "breaking news"],
        "社会": ["society", "social issues", "community", "public", "social development", "social affairs"],
        "城市": ["city", "urban", "metropolis", "municipality", "urban planning", "city development", "urban life"],
        "生活": ["life", "lifestyle", "living", "everyday life", "daily life", "life quality"],
        "家庭": ["family", "household", "domestic life", "parenting", "family relations", "home life"],
        "教育": ["education", "learning", "schooling", "academic", "educational system", "education reform",
                 "teaching"],
        "医疗": ["healthcare", "medical", "hospital", "clinic", "medical services", "health service", "clinical care"],
        "健康": ["health", "wellness", "fitness", "healthy living", "medical health", "public health", "wellbeing"],
        "环境": ["environment", "nature", "ecology", "sustainability", "environmental protection", "green development",
                 "ecological"],
        "气候": ["climate", "climate change", "weather", "global warming", "climate policy", "climate action",
                 "environmental change"],
        "政策": ["policy", "government policy", "public policy", "regulation", "policy making", "policy reform",
                 "legislation"],
        "法律": ["law", "legal", "justice", "court", "legislation", "legal system", "law enforcement",
                 "legal regulation"],
        "安全": ["security", "safety", "protection", "public safety", "security management", "risk prevention",
                 "emergency response"],

        # 社会/热点类 —— 高考相关
        "高考": ["college entrance exam", "gaokao", "national college entrance examination", "university entrance exam",
                 "higher education entrance exam"],
        "高考改革": ["gaokao reform", "college entrance exam reform", "higher education entrance reform",
                     "admissions reform", "exam policy change"],
        "高考志愿": ["college application", "university application", "gaokao volunteer", "admission choices",
                     "application preferences", "college preference submission"],
        "高考分数": ["gaokao score", "exam score", "admission score", "college entrance score", "cut-off score",
                     "score report"],
        "分数线": ["cut-off line", "admission threshold", "score line", "minimum admission score", "college cut-off"],
        "录取": ["admission", "university admission", "college acceptance", "admittance", "enrollment",
                 "admission result"],
        "自主招生": ["independent enrollment", "self-recruitment", "independent admission", "school-based admission",
                     "college self-enrollment"],
        "复读": ["repeat year", "retake exam", "repeat student", "re-taking gaokao", "second year review"],
        "高三": ["senior three", "grade 12", "third year of high school", "final high school year", "senior year"],
        "补习": ["tutoring", "cram school", "coaching class", "after-school tutoring", "extra lessons"],
        "学区房": ["school district housing", "school district house", "education property", "school-zone housing",
                   "district house"],
        "教育公平": ["education equity", "equal education", "fair education", "educational fairness",
                     "equal access to education"],
        "志愿填报": ["application selection", "major selection", "university preference", "college choice submission",
                     "volunteer filing"],
        "高校": ["universities", "colleges", "higher education institutions", "academy", "tertiary institutions",
                 "university campus"],

        # 文化与娱乐类
        "电影": ["movie", "film", "cinema", "motion picture", "film industry", "movie release", "cineaste"],
        "音乐": ["music", "song", "concert", "musician", "audio", "music industry", "album", "soundtrack"],
        "游戏": ["game", "gaming", "video game", "esports", "gameplay", "game development",
                 "interactive entertainment"],
        "体育": ["sports", "athletics", "competition", "fitness", "sporting event", "sports industry",
                 "physical education"],
        "艺术": ["art", "artist", "gallery", "creative arts", "fine arts", "art exhibition", "visual arts"],
        "文化": ["culture", "heritage", "tradition", "arts and culture", "cultural industry", "cultural heritage",
                 "cultural exchange"],
        "旅游": ["travel", "tourism", "trip", "journey", "vacation", "travel industry", "tourist destination",
                 "holiday travel"],
        "美食": ["food", "cuisine", "restaurant", "dining", "gastronomy", "culinary arts", "food culture",
                 "food industry"],
        "时尚": ["fashion", "style", "trend", "clothing", "apparel", "fashion design", "fashion trend",
                 "fashion industry"],

        # 母婴类
        "母婴": ["mother and baby", "maternal and infant", "mom and baby", "mother-child care", "parent-child"],
        "孕妇": ["pregnant woman", "expectant mother", "pregnancy", "maternity", "prenatal care"],
        "产妇": ["postpartum mother", "new mother", "maternal recovery", "postnatal care", "maternity patient"],
        "产前": ["prenatal", "before birth", "pre-birth", "antenatal", "prenatal care"],
        "产后": ["postpartum", "after birth", "postnatal", "postnatal recovery", "postpartum care"],
        "月子": ["confinement", "postpartum confinement", "mooncake period", "postpartum rest", "yuezi care"],
        "月嫂": ["maternity matron", "postpartum nanny", "confinement nurse", "mothercare nanny", "yuesao"],
        "育儿": ["parenting", "childcare", "raising children", "child rearing", "baby care"],
        "宝宝": ["baby", "infant", "newborn", "little one", "toddler"],
        "新生儿": ["newborn", "neonate", "infant care", "new baby", "neonatal"],
        "婴幼儿": ["infant and toddler", "babies and young children", "early childhood", "baby and toddler care",
                   "child development"],
        "哺乳": ["breastfeeding", "nursing", "lactation", "breast milk feeding", "nursing care"],
        "母乳": ["breast milk", "maternal milk", "breastfeeding", "lactation", "human milk"],
        "配方奶": ["formula milk", "infant formula", "baby formula", "formula feeding", "milk powder"],
        "奶粉": ["milk powder", "formula powder", "baby formula", "infant nutrition", "powdered milk"],
        "亲子": ["parent-child", "family bonding", "parenting interaction", "child and parent", "family time"],
        "亲子教育": ["parent-child education", "family education", "early parent education", "parenting education",
                     "child guidance"],
        "早教": ["early education", "preschool education", "early childhood education", "infant education",
                 "early learning"],
        "早教机构": ["early education center", "preschool institution", "early learning center",
                     "child development center", "early education provider"],
        "育婴师": ["infant nanny", "baby nurse", "childcare specialist", "babysitting professional",
                   "maternal-infant care specialist"],
        "育儿知识": ["parenting knowledge", "childcare tips", "parenting guidance", "child rearing advice",
                     "baby care knowledge"],
        "孕期": ["pregnancy period", "gestation", "prenatal period", "expecting period", "pregnancy care"],
        "孕产": ["maternity", "pregnancy and childbirth", "maternal care", "prenatal and postnatal", "maternity care"],
        "产检": ["prenatal checkup", "maternal examination", "antenatal screening", "pregnancy checkup",
                 "prenatal examination"],
        "宝宝用品": ["baby products", "infant supplies", "baby gear", "childcare products", "baby essentials"],
        "母婴用品": ["maternal and infant products", "mom and baby supplies", "baby care goods", "maternity products",
                     "parent-baby items"],
        "亲子活动": ["parent-child activities", "family activities", "parenting events", "child-family events",
                     "family interactive events"],
        "妈妈群": ["mom group", "mothers' community", "parenting circle", "mom forum", "mother support group"],

        # 中国节日类
        "春节": ["Spring Festival", "Chinese New Year", "Lunar New Year", "Spring Festival holiday",
                 "New Year celebration"],
        "元宵节": ["Lantern Festival", "Yuanxiao Festival", "lantern show", "tangyuan", "first full moon festival"],
        "清明节": ["Qingming Festival", "Tomb Sweeping Day", "Qingming holiday", "ancestor worship", "sweeping tombs"],
        "端午节": ["Dragon Boat Festival", "Duanwu Festival", "dragon boat racing", "zongzi", "double fifth festival"],
        "中秋节": ["Mid-Autumn Festival", "Moon Festival", "mooncake festival", "family reunion",
                   "autumn moon celebration"],
        "重阳节": ["Double Ninth Festival", "Chongyang Festival", "seniors day", "climbing mountains",
                   "chrysanthemum festival"],
        "七夕节": ["Qixi Festival", "Chinese Valentine’s Day", "double seventh festival", "love festival",
                   "Qixi romance"],
        "元旦": ["New Year's Day", "January 1st", "Gregorian New Year", "New Year celebration", "holiday New Year"],
        "劳动节": ["Labor Day", "May Day", "International Workers' Day", "labor holiday", "worker's day"],
        "国庆节": ["National Day", "China National Day", "October 1st", "Golden Week", "national holiday"],
        "重阳节": ["Double Ninth Festival", "Chongyang Festival", "senior day", "mountain climbing festival",
                   "chrysanthemum day"],
        "儿童节": ["Children's Day", "Kids' Day", "June 1st", "children's festival", "family children's holiday"],
        "教师节": ["Teacher's Day", "Teachers' Festival", "education celebration", "teacher appreciation",
                   "September 10th"],
        "妇女节": ["Women's Day", "International Women's Day", "March 8th", "women's holiday",
                   "female empowerment day"],
        "植树节": ["Arbor Day", "Tree Planting Day", "March 12th", "green day", "environmental planting day"],
        "春节联欢晚会": ["Spring Festival Gala", "CCTV New Year's Gala", "New Year’s Eve show", "gala dinner show",
                         "Spring Festival evening party"],
        "年夜饭": ["reunion dinner", "New Year's Eve dinner", "family feast", "Spring Festival dinner",
                   "family reunion meal"],
        "拜年": ["New Year greetings", "pay respects for New Year", "Spring Festival greetings", "New Year visits",
                 "lunar new year wishes"],
        "压岁钱": ["New Year money", "lucky money", "red envelope", "hongbao", "lucky cash gift"],
        "赏月": ["moon watching", "moon appreciation", "moon viewing", "Mid-Autumn moon viewing",
                 "moon festival celebration"],

        # 教育学科类目
        "教育学": ["education science", "pedagogy", "educational theory", "education studies", "educational research"],
        "学科": ["subject", "discipline", "academic subject", "field of study", "area of study"],
        "课程": ["curriculum", "course", "syllabus", "teaching plan", "coursework"],
        "教学": ["teaching", "instruction", "instructional", "pedagogy", "classroom teaching"],
        "教材": ["textbook", "teaching material", "course material", "educational material", "learning resources"],
        "考试": ["exam", "test", "assessment", "evaluation", "academic exam", "entrance exam"],
        "语文": ["Chinese language", "Chinese literature", "language arts", "Mandarin", "Chinese language arts"],
        "数学": ["mathematics", "math", "algebra", "geometry", "calculus", "mathematical"],
        "英语": ["English", "English language", "English education", "foreign language", "English study"],
        "物理": ["physics", "physical science", "mechanics", "optics", "electromagnetism", "physics education"],
        "化学": ["chemistry", "chemical science", "organic chemistry", "inorganic chemistry", "chemistry education"],
        "生物": ["biology", "life science", "biological science", "bioscience", "biology education"],
        "历史": ["history", "historical studies", "world history", "Chinese history", "historical education"],
        "地理": ["geography", "geographical science", "human geography", "physical geography", "geoscience"],
        "政治": ["politics", "political science", "civics", "political education", "government studies"],
        "音乐": ["music", "music education", "musical arts", "vocal music", "instrumental music"],
        "美术": ["art", "fine arts", "visual arts", "art education", "drawing", "painting"],
        "体育": ["physical education", "PE", "sports", "athletics", "fitness education", "sports education"],
        "信息技术": ["information technology", "IT", "computer science", "ICT", "digital literacy",
                     "technology education"],
        "心理学": ["psychology", "educational psychology", "mental health", "psychological education",
                   "psychology study"],
        "实验": ["experiment", "laboratory", "practical experiment", "science lab", "lab activity"],
        "作业": ["homework", "assignment", "schoolwork", "exercise", "study assignment"],
        "课堂": ["classroom", "class session", "lesson", "class teaching", "lecture"],
        "成绩": ["grades", "scores", "academic performance", "results", "marks"],
        "教师": ["teacher", "educator", "instructor", "teaching staff", "faculty"],
        "学生": ["student", "pupil", "learner", "schoolchild", "student body"],
        "学术": ["academic", "scholarly", "academia", "academic research", "scholastic"],
        "学术研究": ["academic research", "scholarly research", "research study", "education research",
                     "research project"],
        "远程教育": ["distance education", "online education", "remote learning", "e-learning", "virtual classroom"],
        "素质教育": ["quality education", "holistic education", "well-rounded education", "comprehensive education",
                     "whole-person education"],
        "教育评估": ["education assessment", "educational evaluation", "assessment of learning", "learning evaluation",
                     "academic assessment"],
        "教育资源": ["educational resources", "learning materials", "teaching resources", "education materials",
                     "instructional resources"],
        "师资": ["teaching staff", "faculty", "teacher resources", "educational personnel",
                 "human resources in education"],
        "课堂管理": ["classroom management", "discipline management", "classroom discipline", "teaching management",
                     "classroom organization"],
        "校本课程": ["school-based curriculum", "local curriculum", "customized curriculum", "school curriculum",
                     "school-designed course"],
        "素养": ["literacy", "competency", "core competence", "student literacy", "quality education"],
        "学前教育": ["preschool education", "early childhood education", "pre-kindergarten", "kindergarten education",
                     "early years education"],
        "职业教育": ["vocational education", "technical education", "vocational training", "career education",
                     "job skills training"],
        "高等教育": ["higher education", "tertiary education", "university education", "college education",
                     "postsecondary education"],
        "基础教育": ["basic education", "primary and secondary education", "elementary education",
                     "compulsory education", "fundamental education"],
        "综合素质": ["comprehensive quality", "all-round development", "overall competency", "holistic competence",
                     "well-rounded ability"],

        # 专业类目
        "法学": ["law", "legal studies", "jurisprudence", "law major", "legal education", "law profession"],
        "知识产权法": ["intellectual property law", "IP law", "patent law", "copyright law", "trademark law"],
        "国际法": ["international law", "public international law", "international legal studies", "global law",
                   "transnational law"],
        "经济法": ["economic law", "business law", "commercial law", "corporate law", "financial law"],
        "医学": ["medicine", "medical science", "clinical medicine", "medical major", "healthcare science"],
        "临床医学": ["clinical medicine", "clinical medical science", "medical clinic", "clinical practice",
                     "doctor training"],
        "口腔医学": ["stomatology", "dentistry", "oral medicine", "dental medicine", "dental science"],
        "中医学": ["traditional Chinese medicine", "TCM", "Chinese medical science", "herbal medicine",
                   "acupuncture studies"],
        "中西医结合": ["integrated traditional Chinese and Western medicine", "integrative medicine",
                       "combined medical science"],
        "公共卫生与预防医学": ["public health", "preventive medicine", "epidemiology", "health prevention",
                               "population health"],
        "护理学": ["nursing", "nursing science", "clinical nursing", "health nursing", "nurse education"],
        "助产学": ["midwifery", "maternal nursing", "birth attendant training", "midwife education"],
        "康复治疗学": ["rehabilitation therapy", "rehabilitation science", "physical therapy", "occupational therapy"],
        "药学": ["pharmacy", "pharmaceutical science", "drug science", "pharmaceutics", "medication science"],
        "中药学": ["Chinese herbal medicine", "traditional pharmacy", "TCM pharmacy", "herbal pharmacology"],
        "药物制剂": ["pharmaceutical formulation", "drug formulation", "medicinal preparation", "dosage form science"],
        "基础医学": ["basic medicine", "fundamental medical science", "medical basics", "preclinical medicine"],
        "医学检验技术": ["medical laboratory technology", "clinical laboratory science", "medical testing",
                         "laboratory diagnostics"],
        "医学影像学": ["medical imaging", "radiology", "imaging diagnostics", "medical picture analysis"],
        "营养学": ["nutrition science", "dietary science", "nutritional studies", "food and nutrition"],
        "计算机科学与技术": ["computer science and technology", "computer engineering", "computing science", "CS major",
                             "information technology major"],
        "软件工程": ["software engineering", "software development", "application engineering", "software design",
                     "programming engineering"],
        "网络工程": ["network engineering", "computer network engineering", "network technology", "network systems"],
        "信息安全": ["information security", "cybersecurity", "computer security", "data security", "network security"],
        "电子科学与技术": ["electronic science and technology", "electronics engineering", "electronic information",
                           "electronic systems"],
        "微电子科学与工程": ["microelectronics science and engineering", "integrated circuit engineering",
                             "microchip engineering", "semiconductor science"],
        "光电信息科学与工程": ["optoelectronic information science and engineering", "optoelectronics",
                               "photoelectric engineering"],
        "通信工程": ["communication engineering", "telecommunications engineering", "wireless engineering",
                     "telecom engineering"],
        "自动化": ["automation", "automation engineering", "control automation", "industrial automation",
                   "automatic control"],
        "测控技术与仪器": ["measurement and control technology", "instrumentation engineering",
                           "sensor and control systems"],
        "机械工程": ["mechanical engineering", "mechanical design", "machine engineering", "engineering mechanics"],
        "机械设计制造及其自动化": ["mechanical design manufacturing and automation", "mechanical manufacturing",
                                   "automated machinery engineering"],
        "车辆工程": ["vehicle engineering", "automotive engineering", "vehicle design", "automotive technology"],
        "材料科学与工程": ["materials science and engineering", "materials engineering", "advanced materials",
                           "material science"],
        "化学工程与工艺": ["chemical engineering and technology", "process engineering", "chemical process",
                           "industrial chemistry"],
        "安全工程": ["safety engineering", "industrial safety", "risk engineering", "occupational safety"],
        "环境工程": ["environmental engineering", "ecological engineering", "environment protection engineering",
                     "environmental science"],
        "给排水科学与工程": ["water supply and drainage science and engineering", "hydraulic engineering",
                             "plumbing engineering"],
        "建筑环境与能源应用工程": ["building environment and energy application engineering",
                                   "building energy engineering", "HVAC engineering"],
        "土木工程": ["civil engineering", "structural engineering", "construction engineering",
                     "infrastructure engineering"],
        "道路桥梁与渡河工程": ["road, bridge and river-crossing engineering", "transport infrastructure engineering",
                               "bridge engineering"],
        "勘查技术与工程": ["surveying and mapping engineering", "geological exploration engineering",
                           "survey engineering"],
        "建筑学": ["architecture", "architectural design", "building design", "architecture major"],
        "城乡规划": ["urban and rural planning", "city planning", "urban planning", "spatial planning"],
        "风景园林": ["landscape architecture", "garden design", "landscape design", "environmental landscape"],
        "艺术设计": ["art design", "creative design", "visual arts design", "applied arts"],
        "环境设计": ["environmental design", "space design", "interior environment design", "environmental planning"],
        "工业设计": ["industrial design", "product design", "industrial product design", "design engineering"],
        "产品设计": ["product design", "product development", "industrial product design", "creative product design"],
        "视觉传达设计": ["visual communication design", "graphic design", "visual design", "communication design"],
        "数字媒体艺术": ["digital media art", "new media art", "digital art", "interactive media art"],
        "动画": ["animation", "animation design", "digital animation", "animation production", "animated media"],
        "服装与服饰设计": ["fashion and apparel design", "clothing design", "fashion design", "apparel design"],
        "音乐学": ["musicology", "music studies", "music education", "music theory", "music major"],
        "音乐表演": ["music performance", "instrumental performance", "vocal performance", "performance arts"],
        "舞蹈编导": ["dance choreography", "dance performance", "dance directing", "dance art"],
        "戏剧影视文学": ["drama and film literature", "theater and film studies", "dramatic writing",
                         "film literature"],
        "播音与主持艺术": ["broadcasting and hosting arts", "broadcast hosting", "announcing arts", "presenting arts"],
        "录音艺术": ["recording arts", "audio production", "sound engineering", "sound design"],
        "新闻传播学": ["journalism and communication", "media studies", "mass communication", "news media"],
        "新闻学": ["journalism", "news reporting", "media journalism", "press studies"],
        "广播电视编导": ["radio and television directing", "broadcast directing", "TV production", "media directing"],
        "广告学": ["advertising", "advertising studies", "advertising communication", "creative advertising"],
        "公共关系学": ["public relations", "PR studies", "communication management", "corporate communication"],
        "网络与新媒体": ["internet and new media", "digital media", "online media", "new media studies"],
        "会计学": ["accounting", "accountancy", "financial accounting", "management accounting", "accounting major"],
        "财务管理": ["financial management", "corporate finance", "finance management", "business finance"],
        "金融学": ["finance", "financial studies", "investment finance", "financial economics", "money management"],
        "金融工程": ["financial engineering", "quantitative finance", "financial modeling", "risk engineering"],
        "投资学": ["investment", "investment studies", "investment management", "capital investment"],
        "保险学": ["insurance", "insurance studies", "risk management", "insurance management"],
        "国际经济与贸易": ["international economics and trade", "global trade", "international business",
                           "cross-border commerce"],
        "工商管理": ["business administration", "business management", "corporate management", "management studies"],
        "市场营销": ["marketing", "marketing management", "brand management", "digital marketing",
                     "marketing strategy"],
        "人力资源管理": ["human resource management", "HR management", "talent management", "personnel management"],
        "物流管理": ["logistics management", "supply chain management", "distribution management",
                     "transport logistics"],
        "电子商务": ["e-commerce", "online commerce", "digital commerce", "electronic business",
                     "ecommerce management"],
        "旅游管理": ["tourism management", "travel management", "hospitality and tourism", "tourism industry"],
        "酒店管理": ["hotel management", "hospitality management", "lodging management", "hotel administration"],
        "公共事业管理": ["public affairs management", "public service management", "community management",
                         "public sector administration"],
        "行政管理": ["administrative management", "administration studies", "office management",
                     "government administration"],
        "社会工作": ["social work", "community service", "social welfare", "social worker training"],
        "劳动与社会保障": ["labor and social security", "employment and social security", "social protection",
                           "labor relations"],
        "教育学": ["education science", "pedagogy", "education major", "education studies", "teaching science"],
        "教育技术学": ["educational technology", "edtech", "instructional technology", "teaching technology"],
        "教育管理": ["education management", "school management", "educational administration", "education leadership"],
        "教育心理学": ["educational psychology", "learning psychology", "student psychology",
                       "psychology of education"],
        "特殊教育": ["special education", "inclusive education", "special needs education", "disability education"],
        "学前教育": ["preschool education", "early childhood education", "kindergarten education",
                     "preprimary education"],
        "小学教育": ["primary education", "elementary education", "primary school teaching",
                     "elementary school education"],
        "中学教育": ["secondary education", "middle school education", "high school education",
                     "junior high education"],
        "体育教育": ["physical education", "sports education", "PE education", "athletic education"],
        "音乐教育": ["music education", "music teaching", "music pedagogy", "music classroom"],
        "美术教育": ["art education", "art teaching", "art pedagogy", "visual arts education"],
        "汉语言文学": ["Chinese language and literature", "Chinese literature", "language and literature",
                       "Mandarin studies"],
        "汉语国际教育": ["Chinese international education", "Teaching Chinese as a Foreign Language", "TCFL",
                         "Chinese language teaching"],
        "英语": ["English", "English studies", "English major", "English language education", "English literature"],
        "商务英语": ["business English", "English for business", "corporate English", "commercial English"],
        "翻译": ["translation", "interpreting", "translation studies", "language translation", "interpretation"],
        "日语": ["Japanese", "Japanese language", "Japan studies", "Japanese major"],
        "德语": ["German", "German language", "German studies", "German major"],
        "法语": ["French", "French language", "French studies", "French major"],
        "西班牙语": ["Spanish", "Spanish language", "Spanish studies", "Spanish major"],
        "俄语": ["Russian", "Russian language", "Russian studies", "Russian major"],
        "历史学": ["history", "historical studies", "history major", "world history", "Chinese history"],
        "哲学": ["philosophy", "philosophical studies", "philosophy major", "ethics", "philosophy theory"],
        "社会学": ["sociology", "social studies", "society studies", "social science", "social research"],
        "政治学与行政学": ["political science and administration", "public administration", "politics studies",
                           "government studies"],
        "国际关系": ["international relations", "global relations", "diplomacy studies", "foreign affairs"],
        "外交学": ["diplomacy", "foreign service", "international diplomacy", "diplomatic studies"],
        "心理学": ["psychology", "psychological studies", "mental health studies", "behavioral science"],
        "法医学": ["forensic medicine", "medical jurisprudence", "forensic science", "forensic pathology"],
        "地理信息科学": ["geographic information science", "GIS", "geospatial science", "spatial information"],
        "测绘工程": ["surveying and mapping engineering", "geomatics engineering", "survey engineering",
                     "mapping engineering"],
        "生态学": ["ecology", "ecological science", "environmental ecology", "eco science"],
        "农业资源与环境": ["agricultural resources and environment", "agriculture environment studies",
                           "agrarian environment"],
        "农学": ["agronomy", "agriculture", "agricultural science", "crop science"],
        "园艺": ["horticulture", "garden cultivation", "plant cultivation", "horticultural science"],
        "林学": ["forestry", "forest science", "forest ecology", "silviculture"],
        "动物科学": ["animal science", "animal husbandry", "livestock science", "animal production"],
        "动物医学": ["veterinary medicine", "animal medical science", "veterinary science", "veterinary studies"],
        "水产养殖学": ["aquaculture", "fisheries science", "aquatic farming", "fishery cultivation"],
        "食品科学与工程": ["food science and engineering", "food technology", "food safety", "nutrition engineering"],
        "环境科学": ["environmental science", "ecological science", "environment studies", "environmental research"],
        "能源与动力工程": ["energy and power engineering", "power engineering", "energy engineering",
                           "thermal power engineering"],
        "材料科学": ["materials science", "material engineering", "advanced materials", "material science research"],
        "可持续发展": ["sustainable development", "sustainability studies", "green development",
                       "environmental sustainability"],
        "海洋科学": ["marine science", "oceanography", "marine ecology", "ocean science"],
        "航空航天工程": ["aerospace engineering", "aviation engineering", "astronautical engineering",
                         "space engineering"],
        "飞行器设计与工程": ["aircraft design and engineering", "aeronautical design", "flight vehicle engineering"],
        "飞行技术": ["flight technology", "aviation technology", "pilot technology", "aviation operations"],
        "物业管理": ["property management", "real estate management", "facility management", "estate management"],

        # 通用概念
        "未来": ["future", "tomorrow", "vision", "forward", "next generation", "future trends", "future outlook"],
        "历史": ["history", "past", "historical", "heritage", "historical background", "historical development"],
        "时间": ["time", "clock", "hour", "moment", "duration", "timeline", "timeframe", "period"],
        "空间": ["space", "universe", "cosmos", "astronomy", "spatial", "outer space", "space exploration"],
        "问题": ["problem", "issue", "challenge", "difficulty", "matter", "concern", "obstacle", "problem solving"],
        "解决": ["solution", "solve", "resolve", "answer", "fix", "remedy", "problem resolution"],
        "变化": ["change", "transformation", "transition", "evolution", "shift", "change management", "variation"],
        "发展": ["development", "growth", "progress", "expansion", "advance", "development trend", "evolution"],
        "创新": ["innovation", "creative", "invention", "new", "breakthrough", "innovative technology",
                 "creative idea"],
        "挑战": ["challenge", "obstacle", "difficulty", "struggle", "test", "competitive challenge"],
        "机遇": ["opportunity", "chance", "possibility", "potential", "advantage", "business opportunity"],
        "矛盾": ["conflict", "contradiction", "tension", "debate", "paradox", "inconsistency"],
        "观点": ["opinion", "perspective", "viewpoint", "idea", "stance", "point of view", "insight"],
        "分析": ["analysis", "analyze", "study", "research", "assessment", "evaluation", "data analysis"],
        "背景": ["background", "context", "foundation", "basis", "setting", "historical background",
                 "contextual background"],
        "启示": ["insight", "inspiration", "lesson", "wisdom", "takeaway", "revelation"],
        "建议": ["suggestion", "advice", "recommendation", "tip", "guidance", "proposal", "consultation"],
    }

    # 兜底通用关键词（当所有特定关键词都找不到图片时使用）
    FALLBACK_KEYWORDS = [
        "technology", "business", "abstract", "concept", "modern",
        "digital", "future", "innovation", "connection", "network",
        "city", "people", "office", "work", "data", "chart",
        "communication", "information", "knowledge", "wisdom"
    ]

    # 章节类型关键词 - 为不同类型的章节提供多样化的关键词
    SECTION_TYPE_KEYWORDS = {
        # 事件/故事类章节 - 更具体、场景化
        "事件": ["accident", "incident", "scene", "moment", "street", "road", "city life", "news event"],
        "事儿": ["story", "scene", "moment", "daily life", "urban", "street", "city"],
        "背景": ["history", "background", "context", "timeline", "evolution", "past", "retro"],
        "数据": ["data", "statistics", "chart", "graph", "dashboard", "analytics", "numbers", "report"],
        "分析": ["analysis", "thinking", "brainstorm", "mind map", "strategy", "planning", "deep thought"],
        "观点": ["opinion", "debate", "discussion", "conversation", "meeting", "forum", "different views"],
        "矛盾": ["conflict", "tension", "balance", "scale", "dilemma", "challenge", "opposite"],
        "问题": ["problem", "challenge", "puzzle", "question mark", "thinking", "solution"],
        "本质": ["essence", "core", "center", "focus", "depth", "deep", "fundamental"],
        "启示": ["insight", "inspiration", "lightbulb", "idea", "epiphany", "wisdom", "learning"],
        "建议": ["advice", "guidance", "direction", "path", "roadmap", "plan", "next step"],
        "未来": ["future", "vision", "tomorrow", "forward", "horizon", "predict", "forecast"],
        "怎么办": ["solution", "action", "step", "path", "forward", "progress", "way forward"],
    }

    # 视觉多样性关键词 - 用于增加图片视觉风格的多样性
    VISUAL_VARIETY_KEYWORDS = [
        ["close up", "detail", "macro"],
        ["wide shot", "panoramic", "landscape"],
        ["aerial view", "from above", "bird's eye"],
        ["night", "evening", "dark"],
        ["sunset", "sunrise", "golden hour"],
        ["blur", "bokeh", "shallow depth of field"],
        ["black and white", "monochrome"],
        ["vintage", "retro", "old style"],
        ["minimal", "simple", "clean"],
        ["busy", "crowded", "complex"],
    ]

    def __init__(self, cache_dir: str = "data/images", wechat_client=None):
        """
        初始化图片管理器

        Args:
            cache_dir: 图片缓存目录
            wechat_client: 微信客户端实例（用于上传图片）
        """
        self.cache_dir = cache_dir
        self.wechat_client = wechat_client

        # 确保缓存目录存在
        os.makedirs(self.cache_dir, exist_ok=True)

        # 加载 API 配置
        self.unsplash_access_key = os.environ.get("UNSPLASH_ACCESS_KEY", "")
        self.pexels_api_key = os.environ.get("PEXELS_API_KEY", "")
        self.pixabay_api_key = os.environ.get("PIXABAY_API_KEY", "")

        # 默认图片源
        self.default_source = os.environ.get("IMAGE_DEFAULT_SOURCE", "unsplash")

        # 请求超时设置
        self.timeout = 30

        # 调试模式（输出更详细的日志）
        self.debug = True

        # 记录已使用的图片ID，避免重复
        self.used_image_ids = set()

        # 章节计数器，用于增加关键词多样性
        self.section_count = 0

    def search_images(self, keyword: str, count: int = 1, source: str = None) -> List[Dict]:
        """
        搜索相关图片

        Args:
            keyword: 搜索关键词
            count: 需要的图片数量
            source: 图片源 (unsplash/pexels/pixabay)，None 则自动选择

        Returns:
            图片信息列表，每个包含 url、thumbnail、author 等字段
        """
        if not source:
            source = self._get_available_source()

        if not source:
            print("[!] 没有可用的图片 API 源")
            return []

        print(f"[*] 正在从 {source} 搜索图片: '{keyword}'")

        try:
            if source == "unsplash":
                return self._search_unsplash(keyword, count)
            elif source == "pexels":
                return self._search_pexels(keyword, count)
            elif source == "pixabay":
                return self._search_pixabay(keyword, count)
            else:
                print(f"[!] 不支持的图片源: {source}")
                return []
        except Exception as e:
            print(f"[!] 搜索图片失败: {e}")
            return []

    def _get_available_source(self) -> Optional[str]:
        """获取可用的图片源"""
        if self.unsplash_access_key:
            return "unsplash"
        if self.pexels_api_key:
            return "pexels"
        if self.pixabay_api_key:
            return "pixabay"
        return None

    def _search_unsplash(self, keyword: str, count: int) -> List[Dict]:
        """从 Unsplash 搜索图片"""
        if not self.unsplash_access_key:
            print("[!] 未配置 UNSPLASH_ACCESS_KEY")
            return []

        url = "https://api.unsplash.com/search/photos"
        params = {
            "query": keyword,
            "per_page": min(count * 5, 50),  # 获取更多结果以便筛选
            "client_id": self.unsplash_access_key
        }

        resp = requests.get(url, params=params, timeout=self.timeout)
        resp.raise_for_status()
        data = resp.json()

        results = []
        for item in data.get("results", []):
            results.append({
                "id": item["id"],
                "url": item["urls"]["small"],  # 使用 small 尺寸而不是 regular，文件更小
                "thumbnail": item["urls"]["thumb"],
                "author": item["user"]["name"],
                "link": item["links"]["html"],
                "source": "unsplash",
                "description": item.get("description", "") or item.get("alt_description", "")
            })

        if self.debug:
            print(f"[*] Unsplash 返回了 {len(results)} 张图片")

        # 如果有结果，进行简单的相关性筛选，而不是随机选择
        if len(results) > count:
            results = self._rank_and_select_images(results, keyword, count)
        else:
            results = results[:count]

        if self.debug and results:
            print(f"[+] 最终选择了 {len(results)} 张图片")

        return results

    def _search_pexels(self, keyword: str, count: int) -> List[Dict]:
        """从 Pexels 搜索图片"""
        if not self.pexels_api_key:
            print("[!] 未配置 PEXELS_API_KEY")
            return []

        url = "https://api.pexels.com/v1/search"
        headers = {"Authorization": self.pexels_api_key}
        params = {
            "query": keyword,
            "per_page": min(count * 5, 80)  # 获取更多结果以便筛选
        }

        resp = requests.get(url, headers=headers, params=params, timeout=self.timeout)
        resp.raise_for_status()
        data = resp.json()

        results = []
        for item in data.get("photos", []):
            results.append({
                "id": str(item["id"]),
                "url": item["src"]["medium"],  # 使用 medium 尺寸，文件更小
                "thumbnail": item["src"]["small"],
                "author": item["photographer"],
                "link": item["url"],
                "source": "pexels",
                "description": item.get("alt", "")
            })

        if self.debug:
            print(f"[*] Pexels 返回了 {len(results)} 张图片")

        # 如果有结果，进行简单的相关性筛选
        if len(results) > count:
            results = self._rank_and_select_images(results, keyword, count)
        else:
            results = results[:count]

        return results

    def _search_pixabay(self, keyword: str, count: int) -> List[Dict]:
        """从 Pixabay 搜索图片"""
        if not self.pixabay_api_key:
            print("[!] 未配置 PIXABAY_API_KEY")
            return []

        url = "https://pixabay.com/api/"
        params = {
            "key": self.pixabay_api_key,
            "q": keyword,
            "per_page": min(count * 5, 200),  # 获取更多结果以便筛选
            "image_type": "photo",
            "safesearch": "true"
        }

        resp = requests.get(url, params=params, timeout=self.timeout)
        resp.raise_for_status()
        data = resp.json()

        results = []
        for item in data.get("hits", []):
            results.append({
                "id": str(item["id"]),
                "url": item["webformatURL"],  # 使用 webformat 而不是 largeImageURL，文件更小
                "thumbnail": item["previewURL"],
                "author": item["user"],
                "link": item["pageURL"],
                "source": "pixabay",
                "description": item.get("tags", "")
            })

        if self.debug:
            print(f"[*] Pixabay 返回了 {len(results)} 张图片")

        # 如果有结果，进行简单的相关性筛选
        if len(results) > count:
            results = self._rank_and_select_images(results, keyword, count)
        else:
            results = results[:count]

        return results

    def _rank_and_select_images(self, images: List[Dict], keyword: str, count: int) -> List[Dict]:
        """
        根据关键词对图片进行简单的相关性评分并选择最好的
        会跳过已使用的图片，避免重复

        Args:
            images: 图片列表
            keyword: 搜索关键词
            count: 需要选择的数量

        Returns:
            选择后的图片列表
        """
        keyword_lower = keyword.lower()
        keyword_words = set(keyword_lower.split())

        scored_images = []
        for img in images:
            # 跳过已使用的图片
            img_id = img.get("id")
            if img_id and img_id in self.used_image_ids:
                if self.debug:
                    print(f"[*] 跳过已使用图片: {img_id}")
                continue

            score = 0
            desc = img.get("description", "").lower()

            # 简单评分：描述中包含关键词的得分更高
            for word in keyword_words:
                if word and len(word) > 2:  # 只考虑较长的词
                    if word in desc:
                        score += 10

            # 随机加分，增加多样性
            score += random.randint(0, 10)

            scored_images.append((score, img))

        # 按分数排序，选择分数最高的
        scored_images.sort(key=lambda x: x[0], reverse=True)
        selected = [img for (score, img) in scored_images[:count]]

        # 记录已使用的图片
        for img in selected:
            img_id = img.get("id")
            if img_id:
                self.used_image_ids.add(img_id)
                if self.debug:
                    print(f"[*] 记录已使用图片: {img_id}")

        if self.debug and scored_images:
            available = len(scored_images)
            top_score = scored_images[0][0] if scored_images else 0
            print(f"[*] 最高相关性分数: {top_score}, 可选图片: {available}")

        return selected

    def reset_used_images(self):
        """重置已使用图片记录，用于新文章"""
        self.used_image_ids = set()
        self.section_count = 0
        if self.debug:
            print(f"[*] 已重置已使用图片记录和章节计数器")

    def _get_section_type_keywords(self, clean_section: str) -> List[str]:
        """
        根据章节标题获取章节类型关键词，增加多样性

        Args:
            clean_section: 清理后的章节标题

        Returns:
            章节类型关键词列表
        """
        type_keywords = []

        # 匹配章节类型
        for type_name, keywords in self.SECTION_TYPE_KEYWORDS.items():
            if type_name in clean_section:
                type_keywords.extend(keywords)
                break

        # 如果没有匹配到，根据章节序号返回通用多样性关键词
        if not type_keywords:
            # 根据章节序号选择不同的视觉风格关键词
            idx = self.section_count % len(self.VISUAL_VARIETY_KEYWORDS)
            type_keywords.extend(self.VISUAL_VARIETY_KEYWORDS[idx])

        return type_keywords

    def download_image(self, url: str, save_path: str = None) -> Optional[str]:
        """
        下载图片到本地

        Args:
            url: 图片 URL
            save_path: 保存路径，None 则自动生成

        Returns:
            保存的文件路径，失败返回 None
        """
        if not save_path:
            # 基于 URL 哈希生成文件名
            url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
            ext = self._get_extension_from_url(url)
            save_path = os.path.join(self.cache_dir, f"img_{url_hash}{ext}")

        # 如果已缓存，直接返回
        if os.path.exists(save_path):
            if self.debug:
                print(f"[*] 使用缓存图片: {os.path.basename(save_path)}")
            return save_path

        try:
            print(f"[*] 正在下载图片: {url[:60]}...")
            resp = requests.get(url, timeout=self.timeout)
            resp.raise_for_status()

            with open(save_path, "wb") as f:
                f.write(resp.content)

            print(f"[+] 图片已保存: {save_path}")
            return save_path
        except Exception as e:
            print(f"[!] 下载图片失败: {e}")
            return None

    def _get_extension_from_url(self, url: str) -> str:
        """从 URL 提取文件扩展名"""
        url_lower = url.lower()
        if ".jpg" in url_lower or ".jpeg" in url_lower:
            return ".jpg"
        elif ".png" in url_lower:
            return ".png"
        elif ".gif" in url_lower:
            return ".gif"
        elif ".webp" in url_lower:
            return ".webp"
        return ".jpg"  # 默认

    def upload_to_wechat(self, image_path: str) -> Optional[str]:
        """
        上传图片到微信素材库

        Args:
            image_path: 本地图片路径

        Returns:
            微信 media_id，失败返回 None
        """
        if not self.wechat_client:
            print("[!] 未配置微信客户端，无法上传图片")
            return None

        try:
            print(f"[*] 正在上传图片到微信: {os.path.basename(image_path)}")
            media_id = self.wechat_client.upload_image(image_path)
            if media_id:
                print(f"[+] 上传成功，Media ID: {media_id}")
            return media_id
        except Exception as e:
            print(f"[!] 上传到微信失败: {e}")
            return None

    def get_related_image(self, topic: str, section_title: str = "",
                         images_per_section: int = 1, source: str = None,
                         upload_to_wechat: bool = False) -> List[Dict]:
        """
        获取某个章节的相关图片（完整流程：搜索 -> 下载 -> 上传）

        Args:
            topic: 文章主题
            section_title: 章节标题
            images_per_section: 每节图片数量
            source: 图片源
            upload_to_wechat: 是否上传到微信

        Returns:
            图片信息列表，每个包含 local_path、media_id（如果上传了）、url 等
        """
        # 增加章节计数器
        self.section_count += 1

        # 生成搜索关键词
        keywords = self._generate_search_keywords(topic, section_title)

        if self.debug:
            print(f"\n[*] 图片搜索关键词列表:")
            for i, kw in enumerate(keywords[:5], 1):  # 只显示前5个
                print(f"  {i}. {kw}")
            if len(keywords) > 5:
                print(f"  ... 还有 {len(keywords) - 5} 个")

        images = []
        for keyword in keywords:
            if len(images) >= images_per_section:
                break

            # 搜索图片
            image_infos = self.search_images(keyword, count=images_per_section - len(images), source=source)
            if not image_infos:
                continue

            for image_info in image_infos:
                if len(images) >= images_per_section:
                    break

                # 下载图片
                local_path = self.download_image(image_info["url"])
                if not local_path:
                    continue

                result = {
                    "local_path": local_path,
                    "image_url": image_info["url"],
                    "thumbnail": image_info["thumbnail"],
                    "author": image_info["author"],
                    "link": image_info["link"],
                    "source": image_info["source"],
                    "keyword": keyword
                }

                # 上传到微信
                if upload_to_wechat:
                    media_id = self.upload_to_wechat(local_path)
                    if media_id:
                        result["media_id"] = media_id

                images.append(result)
                if self.debug:
                    print(f"[+] 已获取图片 (关键词: {keyword})")

        if self.debug and images:
            print(f"[*] 共获取 {len(images)} 张图片")

        return images

    def _generate_search_keywords(self, topic: str, section_title: str) -> List[str]:
        """
        生成搜索关键词列表（按优先级排序）
        优先使用英文关键词，因为图库主要是英文内容
        会结合章节标题生成更具体的关键词，并增加多样性

        Args:
            topic: 文章主题
            section_title: 章节标题

        Returns:
            关键词列表
        """
        keywords = []

        # 1. 清理章节标题
        clean_section = ""
        if section_title:
            clean_section = self._clean_section_title(section_title)

        # 2. 生成英文关键词（优先）
        topic_english = self._translate_to_english(topic)

        # 3. 获取章节类型关键词（用于增加多样性）
        section_type_keywords = self._get_section_type_keywords(clean_section or "通用")

        if self.debug:
            print(f"[*] 章节 {self.section_count} - 类型关键词: {section_type_keywords[:3]}")

        # 4. 生成多样化的关键词组合
        if clean_section:
            section_english = self._translate_to_english(clean_section)

            # 组合1：章节类型 + 主题（高优先级，增加多样性）
            for stk in section_type_keywords[:3]:
                for tk in topic_english[:2]:
                    keywords.append(f"{stk} {tk}")
                    keywords.append(f"{tk} {stk}")

            # 组合2：章节 + 主题（具体）
            for sk in section_english[:2]:
                for tk in topic_english[:2]:
                    if sk != tk:
                        keywords.append(f"{sk} {tk}")
                        keywords.append(f"{tk} {sk}")

            # 单独章节关键词
            keywords.extend(section_english)
        else:
            # 没有章节标题时，用章节类型 + 主题
            for stk in section_type_keywords[:4]:
                for tk in topic_english[:2]:
                    keywords.append(f"{stk} {tk}")

        # 5. 章节类型关键词单独使用
        keywords.extend(section_type_keywords)

        # 6. 主题关键词
        keywords.extend(topic_english)

        # 7. 保留原始中文作为 fallback（某些图库可能支持中文）
        if clean_section:
            keywords.append(f"{topic} {clean_section}")
            keywords.append(clean_section)
        keywords.append(topic)

        # 8. 添加兜底通用关键词
        keywords.extend(self.FALLBACK_KEYWORDS)

        # 去重并返回
        result = list(dict.fromkeys(keywords))

        if self.debug:
            print(f"[*] 从主题 '{topic}' + 章节 '{clean_section}' (第{self.section_count}章) 生成了 {len(result)} 个搜索关键词")

        return result

    def _translate_to_english(self, chinese_text: str) -> List[str]:
        """
        将中文文本翻译成英文搜索关键词（使用预定义的映射表）

        Args:
            chinese_text: 中文文本

        Returns:
            英文关键词列表
        """
        results = []

        # 首先尝试精确匹配整个文本
        text_clean = chinese_text.strip()
        if text_clean in self.KEYWORD_TRANSLATIONS:
            results.extend(self.KEYWORD_TRANSLATIONS[text_clean])

        # 然后尝试匹配子字符串
        for cn_word, en_words in self.KEYWORD_TRANSLATIONS.items():
            if cn_word in chinese_text and cn_word != text_clean:
                results.extend(en_words)

        # 如果没有找到任何匹配，尝试一些简单的通用词
        if not results:
            # 提取文本中的核心概念（这里做简单处理）
            if "AI" in chinese_text or "智能" in chinese_text:
                results.extend(["artificial intelligence", "AI", "technology"])
            elif "科技" in chinese_text:
                results.extend(["technology", "tech", "innovation"])
            elif "经济" in chinese_text or "金融" in chinese_text:
                results.extend(["economy", "finance", "business"])
            elif "社会" in chinese_text:
                results.extend(["society", "people", "community"])
            else:
                # 最兜底的：使用一些通用科技/商业词汇
                results.extend(["technology", "business", "abstract", "concept"])

        # 去重并返回
        return list(dict.fromkeys(results))

    def _clean_section_title(self, title: str) -> str:
        """清理章节标题，移除编号等"""
        import re
        # 移除 "01 标题" 格式中的数字编号
        cleaned = re.sub(r'^\d+\s*', '', title.strip())
        # 移除常见的章节词
        for word in ["事件", "背景", "分析", "观点", "建议", "解读", "洞察", "启示"]:
            if cleaned == word:
                return ""
        return cleaned

    def get_image_html(self, image_info: Dict, caption: str = "", use_media_id: bool = False) -> str:
        """
        生成图片 HTML

        Args:
            image_info: 图片信息
            caption: 图片说明文字
            use_media_id: 是否使用微信 media_id（True=微信发布用，False=本地预览用）

        Returns:
            HTML 字符串
        """
        # 选择图片源
        img_src = None

        if use_media_id:
            # 微信发布模式：优先使用 media_id
            if "media_id" in image_info and image_info["media_id"]:
                img_src = image_info["media_id"]
                if self.debug:
                    print(f"[*] 使用微信 media_id: {img_src[:20]}...")
            elif "image_url" in image_info:
                # 降级：如果没有 media_id，使用 URL
                img_src = image_info["image_url"]
                if self.debug:
                    print(f"[*] media_id 不可用，降级使用 URL")
        else:
            # 本地预览模式：强制使用 image_url
            if "image_url" in image_info:
                img_src = image_info["image_url"]
                if self.debug:
                    print(f"[*] 本地预览模式，使用图片 URL")
            elif "media_id" in image_info:
                # 本地预览时，如果只有 media_id，警告并返回空
                print(f"[!] 警告：本地预览模式下，只有 media_id 没有 image_url，跳过该图片")
                return ""

        if not img_src:
            print(f"[!] 警告：没有可用的图片源，跳过该图片")
            return ""

        # 图片样式：固定高度 + object-fit 确保所有图片显示尺寸一致
        style = "width: 100%; max-width: 800px; height: 450px; object-fit: cover; border-radius: 8px; margin: 15px auto; display: block; box-shadow: 0 2px 8px rgba(0,0,0,0.1);"

        html_parts = [f'<img src="{img_src}" style="{style}">']

        # 图片说明（可选）
        if caption:
            caption_style = "text-align: center; color: #999; font-size: 14px; margin-bottom: 20px;"
            html_parts.append(f'<p style="{caption_style}">{caption}</p>')

        return "\n".join(html_parts)

    def cleanup_old_images(self, max_age_hours: int = 24):
        """
        清理旧的缓存图片

        Args:
            max_age_hours: 最大保留时间（小时）
        """
        if not os.path.exists(self.cache_dir):
            return

        now = time.time()
        max_age_seconds = max_age_hours * 3600

        cleaned_count = 0
        for filename in os.listdir(self.cache_dir):
            filepath = os.path.join(self.cache_dir, filename)
            if os.path.isfile(filepath):
                age = now - os.path.getmtime(filepath)
                if age > max_age_seconds:
                    try:
                        os.remove(filepath)
                        cleaned_count += 1
                    except Exception as e:
                        print(f"[!] 无法删除 {filename}: {e}")

        if cleaned_count > 0:
            print(f"[*] 已清理 {cleaned_count} 个旧图片文件")
