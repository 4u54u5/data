from __future__ import annotations

import datetime as dt
import os
import sqlite3

DB_PATH = os.environ.get("DB_PATH", "radar.db")

SOURCE_REGISTRY = [
    {"name": "The Times of India", "country": "India", "type": "media", "focus": "インド通信・データセンター・政策", "url": "https://timesofindia.indiatimes.com"},
    {"name": "The Economic Times", "country": "India", "type": "media", "focus": "インドビジネス・インフラ投資", "url": "https://economictimes.indiatimes.com"},
    {"name": "VnExpress", "country": "Vietnam", "type": "media", "focus": "ベトナム通信・デジタルインフラ", "url": "https://e.vnexpress.net"},
    {"name": "Vietnam Investment Review", "country": "Vietnam", "type": "media", "focus": "ベトナム投資・インフラ政策", "url": "https://vir.com.vn"},
    {"name": "The Wall Street Journal", "country": "United States", "type": "media", "focus": "AI・データセンター・半導体投資", "url": "https://www.wsj.com"},
    {"name": "Tom's Hardware", "country": "United States", "type": "media", "focus": "GPU・AI チップ・データセンター", "url": "https://www.tomshardware.com"},
    {"name": "Light Reading", "country": "United States", "type": "media", "focus": "通信業界ニュース", "url": "https://www.lightreading.com"},
    {"name": "TeleGeography", "country": "United States", "type": "research", "focus": "通信インフラ調査", "url": "https://www.telegeography.com"},
    {"name": "arXiv", "country": "Japan", "type": "research", "focus": "AI研究・計算基盤論文", "url": "https://arxiv.org"},
]

SCHEMA = """
CREATE TABLE IF NOT EXISTS articles (
  id integer primary key,
  source_name text, source_country text, source_type text, url text unique,
  published_at text, original_title text, original_text text, language text,
  fetched_at text
);
CREATE TABLE IF NOT EXISTS events (
  id integer primary key,
  article_id integer, country text, region text, event_title_ja text,
  summary_ja text, event_type text, impact_direction text,
  confidence_level text, time_horizon text, created_at text,
  original_url text
);
CREATE TABLE IF NOT EXISTS companies (
  id integer primary key,
  name text unique, country text, ticker text, exchange text, sector text, notes text
);
CREATE TABLE IF NOT EXISTS event_company_links (
  id integer primary key,
  event_id integer, company_id integer, relation_type text, confidence text, evidence_text text
);
CREATE TABLE IF NOT EXISTS themes (
  id integer primary key,
  name text unique, description text
);
CREATE TABLE IF NOT EXISTS event_theme_links (
  id integer primary key,
  event_id integer, theme_id integer
);
"""

_ARTICLES = [
    dict(
        url="https://en.wikipedia.org/wiki/List_of_5G_NR_networks",
        source_name="Light Reading / TeleGeography reference",
        source_country="Vietnam",
        source_type="media",
        published_at="2024-10-16",
        original_title="Viettel launches first commercial 5G services in Vietnam",
        original_text="Public network deployment references list Viettel as launching Vietnam's first commercial 5G services in October 2024, following earlier 5G trials and licensing activity. Vietnam's main telecom operators include Viettel, VNPT VinaPhone and MobiFone, making 5G rollout a relevant market event for radio equipment, fibre backhaul, cloud, cybersecurity and domestic digital infrastructure providers.",
        language="en",
    ),
    dict(
        url="https://timesofindia.indiatimes.com/city/lucknow/govt-aims-to-set-up-data-centre-clusters-by-2030/articleshow/129352967.cms",
        source_name="The Times of India",
        source_country="India",
        source_type="media",
        published_at="2026-03-10",
        original_title="Uttar Pradesh aims to set up data centre clusters by 2030",
        original_text="The Uttar Pradesh government said it aims to develop four to five large-scale data centre clusters with a combined capacity of 5 GW by 2030. The state also plans eight data centre parks with a total capacity of 900 MW and about Rs 30,000 crore of investment. Officials said letters of comfort had been issued for multiple data centre park and standalone projects, with projects worth Rs 21,342 crore and 644 MW already secured.",
        language="en",
    ),
    dict(
        url="https://timesofindia.indiatimes.com/business/india-business/indias-telecom-sector-surges-in-2025-5g-rollout-reaches-85-of-population-rural-connectivity-digital-adoption-soar/articleshow/126090344.cms",
        source_name="The Times of India",
        source_country="India",
        source_type="media",
        published_at="2025-12-20",
        original_title="India telecom sector review highlights 5G coverage, broadband growth and indigenous 4G stack",
        original_text="India's telecom sector review said 5G services were available across all states and union territories, covering 99.9 percent of districts and around 85 percent of the population. Operators had installed more than 5.08 lakh 5G base stations and optical fibre length had doubled since 2019. The review also highlighted the National Broadband Mission 2.0, broadband subscriptions close to 100 crore, and an indigenous 4G stack built by C-DOT, Tejas Networks and TCS and deployed by BSNL.",
        language="en",
    ),
    dict(
        url="https://timesofindia.indiatimes.com/business/reliance-and-meta-to-develop-ai-enabled-data-centre-in-jamnagar/articleshow/131624466.cms",
        source_name="The Times of India",
        source_country="India",
        source_type="media",
        published_at="2026-06-10",
        original_title="Reliance and Meta to develop AI-enabled data centre in Jamnagar",
        original_text="Reliance Industries announced a partnership with Meta Platforms for a data centre project in Jamnagar, Gujarat. Reliance Industries will develop a 168 MW AI-enabled data centre within two years, with an option to scale, and Meta will lease the first built-to-suit data centre capacity in India. Reliance will provide design, construction, utilities, renewable power supply, network connectivity and operational services.",
        language="en",
    ),
    dict(
        url="https://economictimes.indiatimes.com/industry/cons-products/electronics/blackstone-backed-airtrunk-to-invest-30-billion-in-india-develop-5-gw-data-centre-capacity-by-2030/articleshow/131524644.cms",
        source_name="The Economic Times",
        source_country="India",
        source_type="media",
        published_at="2026-06-05",
        original_title="Blackstone-backed AirTrunk to invest $30 billion in India, develop 5 GW data centre capacity by 2030",
        original_text="AirTrunk announced plans to invest more than $30 billion, over Rs 3 lakh crore, to develop over 5 gigawatts of digital infrastructure capacity across India by 2030. The programme is backed by Blackstone and the Canada Pension Plan Investment Board and is intended to support cloud and artificial intelligence infrastructure demand. The company entered India through the acquisition of Lumina CloudInfra, with an initial 600 MW pipeline across Mumbai, Chennai and Hyderabad.",
        language="en",
    ),
    dict(
        url="https://www.tomshardware.com/tech-industry/nvidia-market-share-in-china-falls-to-less-than-60-percent-chinese-chip-makers-deliver-1-65-million-ai-gpus-as-the-government-pushes-data-centers-to-use-domestic-chips",
        source_name="Tom's Hardware",
        source_country="China",
        source_type="media",
        published_at="2026-04-01",
        original_title="Chinese AI chip makers gain share as data centers shift to domestic GPUs",
        original_text="Chinese semiconductor firms reportedly delivered 1.65 million AI GPUs in 2025, taking 41 percent of China's domestic AI server market. Nvidia's share fell below 60 percent, while Huawei, Alibaba's T-Head, Baidu's Kunlunxin and Cambricon gained traction. The shift is driven by export controls and government pressure for data centers to use domestic chips, making chip supply a key infrastructure risk and opportunity.",
        language="en",
    ),
    dict(
        url="https://www.investopedia.com/alibaba-shares-jump-on-plan-to-boost-ai-spending-beyond-53b-11816017",
        source_name="Investopedia",
        source_country="China",
        source_type="media",
        published_at="2025-09-24",
        original_title="Alibaba to boost AI spending beyond $53 billion plan",
        original_text="Alibaba said it would expand artificial intelligence investment beyond its previously announced $53 billion plan over three years. The spending is tied to AI models, cloud capacity and infrastructure, and positions Alibaba Cloud as a major Chinese AI infrastructure provider. The plan also reflects China's broader push to build domestic AI compute and cloud capacity amid global competition and chip supply constraints.",
        language="en",
    ),
    dict(
        url="https://arxiv.org/abs/2411.09134",
        source_name="arXiv",
        source_country="Japan",
        source_type="research",
        published_at="2024-11-14",
        original_title="ABCI 3.0 evolves Japan's leading open AI infrastructure",
        original_text="ABCI 3.0 is described as a large-scale open AI infrastructure operated by AIST and expected to be fully operational in January 2025. The system includes 6,128 NVIDIA H200 GPUs, all-flash storage and multi-exaflop AI computing performance. It is intended to accelerate research and development, evaluation and workforce development for advanced AI and generative AI technologies in Japan.",
        language="en",
    ),
    dict(
        url="https://www.wsj.com/articles/softbank-corp-to-build-large-scale-ai-data-center-at-sharp-s-sakai-plant-6287eab3",
        source_name="The Wall Street Journal",
        source_country="Japan",
        source_type="media",
        published_at="2024-06-07",
        original_title="SoftBank to build large-scale AI data center at Sharp's Sakai plant",
        original_text="SoftBank Corp. announced plans to build a large-scale AI data center at Sharp's Sakai plant in Osaka. The facility is intended to support SoftBank's generative AI development and other AI-related businesses, with full-scale operations expected in 2025. The project connects telecom, AI compute, power and data center redevelopment themes in Japan.",
        language="en",
    ),
    dict(
        url="https://www.wsj.com/tech/nvidia-foxconn-to-build-ai-factory-in-taiwan-99dfad89",
        source_name="The Wall Street Journal",
        source_country="Taiwan",
        source_type="media",
        published_at="2025-05-19",
        original_title="Nvidia, Foxconn and Taiwan government plan Taiwan AI supercomputer",
        original_text="Nvidia announced plans at Computex Taipei to develop Taiwan's first AI supercomputer with Foxconn and the Taiwan government. Foxconn will provide AI infrastructure, and TSMC researchers are expected to use the system for research and development. The plan positions Taiwan as a strategic AI infrastructure hub connected to semiconductors, advanced packaging, networking and data center demand.",
        language="en",
    ),
    dict(
        url="https://www.tomshardware.com/tech-industry/semiconductors/taiwan-announces-3bn-spend-on-ai-island-ambitions",
        source_name="Tom's Hardware",
        source_country="Taiwan",
        source_type="media",
        published_at="2025-11-18",
        original_title="Taiwan to spend $3 billion turning nation into AI island",
        original_text="Taiwan committed more than NT$100 billion, about US$3.2 billion, to an AI Island initiative. The plan targets top-tier national compute capacity and includes next-generation hardware, silicon photonics, quantum computing and AI robotics. Key infrastructure includes a national AI data center in Tainan and private-sector projects such as an Nvidia and Foxconn AI facility in Kaohsiung using Blackwell systems, while power supply and grid constraints remain important risks.",
        language="en",
    ),
    dict(
        url="https://www.wsj.com/tech/ai/canadian-government-plans-360-million-tech-growth-fund-in-effort-to-drive-sovereign-ai-industry-aef5d3e2",
        source_name="The Wall Street Journal",
        source_country="Canada",
        source_type="media",
        published_at="2026-06-05",
        original_title="Canada plans AI for All strategy and sovereign compute funding",
        original_text="Canada announced an AI for All strategy including a C$500 million Canadian Tech Growth Fund, C$700 million to expand sovereign computing and additional support for AI safety and healthcare AI. The strategy emphasizes domestic compute, data, talent and infrastructure. It follows broader Canadian efforts, including Alberta's AI Data Centres Strategy targeting large-scale AI data center investment by 2030.",
        language="en",
    ),
    dict(
        url="https://www.wsj.com/tech/ai/broadcom-apollo-blackstone-launch-35-billion-ai-infrastructure-platform-8fc8f65e",
        source_name="The Wall Street Journal",
        source_country="United States",
        source_type="media",
        published_at="2026-06-09",
        original_title="Broadcom, Apollo and Blackstone launch $35 billion AI infrastructure platform",
        original_text="Broadcom, Apollo Global Management and Blackstone launched the AI XPV Platform, a $35 billion AI infrastructure financing platform intended to deliver more than 20 GW of compute capacity by 2028. The first phase supports Anthropic's expansion of over 1 GW of compute infrastructure through a leasing arrangement with Fluidstack. The event shows how chips, networking, private credit and data center capacity are converging in North American AI infrastructure.",
        language="en",
    ),
]

_EVENTS = [
    dict(
        article_idx=0,
        country="Vietnam", region="Asia",
        event_title_ja="Viettel、ベトナム初の商用5Gサービスを開始",
        summary_ja="公開ネットワーク展開情報では、Viettelが2024年10月にベトナム初の商用5Gサービスを開始したと整理されている。VNPT、MobiFoneを含む主要通信事業者の5G展開は、基地局設備、光ファイバー回線、クラウド、サイバーセキュリティ、国内デジタルインフラの関連需要につながる可能性がある。",
        event_type="telecom_infra", impact_direction="neutral", confidence_level="high", time_horizon="short_term",
    ),
    dict(
        article_idx=1,
        country="India", region="Asia",
        event_title_ja="ウッタル・プラデシュ州、2030年までにデータセンタークラスター整備を目指す",
        summary_ja="ウッタル・プラデシュ州政府は、2030年までに合計5GW規模の大型データセンタークラスターを4から5か所整備する方針を示した。8つのデータセンターパーク、合計900MW、約3,000億ルピー規模の投資も計画されており、電力、建設、通信接続関連の需要が見込まれる。",
        event_type="policy", impact_direction="positive", confidence_level="high", time_horizon="long_term",
    ),
    dict(
        article_idx=2,
        country="India", region="Asia",
        event_title_ja="インド通信セクター、5G普及・光ファイバー拡大・国産4Gスタックを強調",
        summary_ja="インドの通信セクターレビューでは、5Gが全州・連邦直轄領で提供され、地区の99.9%、人口の約85%をカバーしたとされる。5G基地局は50.8万局超、光ファイバー網も2019年比で倍増。C-DOT、Tejas Networks、TCS、BSNLによる国産4Gスタックも注目点。",
        event_type="telecom_infra", impact_direction="negative_or_watch", confidence_level="high", time_horizon="short_term",
    ),
    dict(
        article_idx=3,
        country="India", region="Asia",
        event_title_ja="RelianceとMeta、ジャムナガルでAI対応データセンターを開発へ",
        summary_ja="Reliance IndustriesはMetaと組み、グジャラート州ジャムナガルでAI対応データセンターを開発する。初期容量は168MWで、Metaがインド初の専用データセンター容量をリースする計画。設計、建設、電力、接続、運用をReliance側が担う。",
        event_type="market_expansion", impact_direction="positive", confidence_level="medium", time_horizon="short_term",
    ),
    dict(
        article_idx=4,
        country="India", region="Asia",
        event_title_ja="AirTrunk、インドで300億ドル超・5GW規模のデータセンター投資計画",
        summary_ja="AirTrunkは2030年までにインドで5GW超のデジタルインフラ容量を整備する計画を発表した。BlackstoneとCPP Investmentsが支援し、クラウドとAI需要を取り込む狙い。ムンバイ、チェンナイ、ハイデラバードを中心に初期600MWのパイプラインを持つ。",
        event_type="corporate_investment", impact_direction="positive", confidence_level="high", time_horizon="short_term",
    ),
    dict(
        article_idx=5,
        country="China", region="Asia",
        event_title_ja="中国AIチップ企業、国内データセンター向けGPUで存在感を拡大",
        summary_ja="2025年に中国半導体企業が国内AIサーバー市場で大きくシェアを伸ばし、Huawei、Alibaba系T-Head、Baidu系Kunlunxin、Cambriconなどが存在感を高めたと報じられている。米国の輸出規制と国内チップ利用を促す政策が背景で、AIデータセンターの調達、性能、供給リスクに直結する。",
        event_type="policy", impact_direction="negative_or_watch", confidence_level="medium", time_horizon="short_term",
    ),
    dict(
        article_idx=6,
        country="China", region="Asia",
        event_title_ja="Alibaba、530億ドル超のAI投資計画をさらに拡大へ",
        summary_ja="Alibabaは3年間で530億ドル規模としていたAI投資計画をさらに拡大する方針を示した。AIモデル、クラウド容量、データセンター基盤への投資が中心で、Alibaba Cloudを中国のAIインフラ中核プレイヤーとして位置づける動き。輸出規制や国内チップ供給制約の中で、中国のクラウド・計算資源整備が加速している。",
        event_type="corporate_investment", impact_direction="positive", confidence_level="high", time_horizon="short_term",
    ),
    dict(
        article_idx=7,
        country="Japan", region="Asia",
        event_title_ja="AISTのABCI 3.0、日本のオープンAI計算基盤を拡張",
        summary_ja="ABCI 3.0はAISTが運用する大規模オープンAIインフラで、NVIDIA H200 GPUを6,128基搭載し、2025年1月の本格稼働が予定されている。生成AIの研究開発、評価、人材育成を支える基盤として、日本のAIインフラ政策・産業利用の観点で注目される。",
        event_type="market_expansion", impact_direction="positive", confidence_level="medium", time_horizon="short_term",
    ),
    dict(
        article_idx=8,
        country="Japan", region="Asia",
        event_title_ja="SoftBank、シャープ堺工場跡地で大規模AIデータセンターを整備へ",
        summary_ja="SoftBankは大阪・堺のシャープ工場を活用し、大規模AIデータセンターを整備する計画を発表した。生成AI開発やAI関連事業に使う方針で、本格稼働は2025年を見込む。通信キャリア、電力、データセンター再開発、AI計算基盤が交差する日本の重要イベント。",
        event_type="data_center", impact_direction="negative_or_watch", confidence_level="high", time_horizon="short_term",
    ),
    dict(
        article_idx=9,
        country="Taiwan", region="Asia",
        event_title_ja="Nvidia・Foxconn・台湾政府、台湾AIスーパーコンピューター計画を推進",
        summary_ja="NvidiaはComputex Taipeiで、Foxconnおよび台湾政府とAIスーパーコンピューターを整備する計画を示した。FoxconnがAIインフラを提供し、TSMCの研究開発利用も想定される。台湾の半導体エコシステムとAI計算基盤の結びつきを強めるイベント。",
        event_type="policy", impact_direction="neutral", confidence_level="high", time_horizon="short_term",
    ),
    dict(
        article_idx=10,
        country="Taiwan", region="Asia",
        event_title_ja="台湾、AI Island構想に約32億ドル規模を投じる方針",
        summary_ja="台湾はAI Island構想として1,000億台湾ドル超を投じ、国家レベルの計算能力強化を進める。台南の国家AIデータセンターや、NvidiaとFoxconnによる高雄のAI施設が焦点。半導体、AIサーバー、冷却、電力網、データセンター運用に波及する一方、電力供給制約は重要な確認事項。",
        event_type="policy", impact_direction="negative_or_watch", confidence_level="medium", time_horizon="medium_term",
    ),
    dict(
        article_idx=11,
        country="Canada", region="Asia",
        event_title_ja="カナダ、AI for All戦略と主権AIコンピュート支援を発表",
        summary_ja="カナダ政府はAI for All戦略として、国内AI企業支援、主権コンピュート拡張、AI安全性、医療AIなどへの資金投入を打ち出した。国内の計算資源、データ、人材、インフラを重視する内容で、アルバータ州のAIデータセンター誘致政策とも合わせて、北米のAIインフラ投資テーマとして注目される。",
        event_type="policy", impact_direction="positive", confidence_level="high", time_horizon="short_term",
    ),
    dict(
        article_idx=12,
        country="United States", region="Asia",
        event_title_ja="Broadcom・Apollo・Blackstone、350億ドルのAIインフラ基盤を立ち上げ",
        summary_ja="Broadcom、Apollo Global Management、BlackstoneはAI XPV Platformを立ち上げ、2028年までに20GW超の計算容量提供を目指す。初期フェーズではAnthropic向けに1GW超の計算インフラ拡張を支援する。半導体、ネットワーク、データセンター、民間信用が結びつく北米AIインフラの重要イベント。",
        event_type="corporate_investment", impact_direction="positive", confidence_level="medium", time_horizon="short_term",
    ),
]

_COMPANIES = [
    ("AirTrunk", "Australia", "data center"),
    ("Blackstone", "United States", "investment"),
    ("Canada Pension Plan Investment Board", "Canada", "investment"),
    ("Reliance Industries", "India", "data center"),
    ("Reliance Jio", "India", "telecom"),
    ("Meta", "United States", "cloud / AI"),
    ("Bharti Airtel", "India", "telecom"),
    ("Tata Communications", "India", "telecom"),
    ("Sterlite Technologies", "India", "fiber"),
    ("AdaniConneX", "India", "data center"),
    ("BSNL", "India", "telecom"),
    ("C-DOT", "India", "telecom equipment"),
    ("Tejas Networks", "India", "telecom equipment"),
    ("TCS", "India", "IT services"),
    ("Viettel", "Vietnam", "telecom"),
    ("VNPT", "Vietnam", "telecom"),
    ("MobiFone", "Vietnam", "telecom"),
    ("FPT", "Vietnam", "cloud"),
    ("CMC Telecom", "Vietnam", "cloud"),
    ("Ericsson", "Sweden", "telecom equipment"),
    ("Nokia", "Finland", "telecom equipment"),
    ("Huawei", "China", "telecom equipment"),
    ("ZTE", "China", "telecom equipment"),
    ("Samsung", "Korea", "telecom equipment"),
    ("Qualcomm", "United States", "semiconductor"),
    ("Chunghwa Telecom", "Taiwan", "telecom"),
    ("Taiwan Mobile", "Taiwan", "telecom"),
    ("Far EasTone", "Taiwan", "telecom"),
    ("TSMC", "Taiwan", "semiconductor"),
    ("Foxconn", "Taiwan", "AI infrastructure"),
    ("Nvidia", "United States", "AI infrastructure"),
    ("MediaTek", "Taiwan", "semiconductor"),
    ("NTT", "Japan", "telecom"),
    ("NTT DATA", "Japan", "data center"),
    ("KDDI", "Japan", "telecom"),
    ("SoftBank", "Japan", "telecom / AI infrastructure"),
    ("Sharp", "Japan", "electronics"),
    ("Sakura Internet", "Japan", "cloud / HPC"),
    ("AIST", "Japan", "AI infrastructure"),
    ("Alibaba", "China", "cloud / AI"),
    ("Alibaba Cloud", "China", "cloud"),
    ("Tencent", "China", "cloud / AI"),
    ("Baidu", "China", "AI"),
    ("Cambricon", "China", "AI chips"),
    ("OpenAI", "United States", "AI"),
    ("Oracle", "United States", "cloud / data center"),
    ("MGX", "United Arab Emirates", "investment"),
    ("Anthropic", "United States", "AI"),
    ("Broadcom", "United States", "semiconductor / networking"),
    ("Apollo Global Management", "United States", "investment"),
    ("Fluidstack", "United States", "AI infrastructure"),
    ("Government of Canada", "Canada", "government"),
    ("Government of Alberta", "Canada", "government"),
    ("Wonder Valley", "Canada", "data center"),
    ("Larsen & Toubro", "India", "civil / construction"),
    ("Shapoorji Pallonji", "India", "construction"),
    ("KEC International", "India", "power / EPC"),
    ("Hitachi Energy India", "India", "power equipment"),
    ("Delta Electronics", "Taiwan", "power / cooling"),
    ("Quanta Computer", "Taiwan", "server / data center"),
    ("Wistron", "Taiwan", "server / data center"),
    ("Acer e-Enabling Data Center", "Taiwan", "data center services"),
    ("Obayashi", "Japan", "construction"),
    ("Kajima", "Japan", "construction"),
    ("Shimizu", "Japan", "construction"),
    ("Taisei", "Japan", "construction"),
    ("Takasago Thermal Engineering", "Japan", "HVAC"),
    ("Shinryo", "Japan", "HVAC / MEP"),
    ("Daikin", "Japan", "HVAC"),
    ("Nippon Koei", "Japan", "engineering"),
    ("China State Construction Engineering", "China", "construction"),
    ("China Railway Construction", "China", "civil engineering"),
    ("China Energy Engineering", "China", "power / EPC"),
    ("Vertiv", "United States", "power / cooling"),
    ("Schneider Electric", "France", "power / cooling"),
    ("Eaton", "Ireland", "power equipment"),
    ("Johnson Controls", "United States", "HVAC"),
    ("Carrier", "United States", "HVAC"),
    ("Trane Technologies", "Ireland", "HVAC"),
    ("AECOM", "United States", "engineering"),
    ("Jacobs", "United States", "engineering"),
    ("Bechtel", "United States", "construction / EPC"),
    ("PCL Construction", "Canada", "construction"),
    ("EllisDon", "Canada", "construction"),
    ("WSP", "Canada", "engineering"),
    ("Stantec", "Canada", "engineering"),
    ("Black & McDonald", "Canada", "MEP / construction"),
    ("Singtel", "Singapore", "subsea / telecom"),
    ("NEC", "Japan", "telecom / submarine cable"),
    ("Fujitsu", "Japan", "IT infrastructure"),
    ("Cisco", "United States", "network equipment"),
    ("Arista Networks", "United States", "network equipment"),
]

_THEMES = ["telecom", "data center", "fiber", "power", "semiconductor", "industrial park", "cybersecurity", "5G"]

# (event_idx, company_name, relation_type)
_EVENT_COMPANY_LINKS = [
    (0, "Viettel", "actor"),
    (0, "VNPT", "actor"),
    (0, "MobiFone", "actor"),
    # event 1 - no companies
    (2, "C-DOT", "actor"),
    (2, "Tejas Networks", "actor"),
    (2, "TCS", "actor"),
    (2, "BSNL", "actor"),
    (2, "Bharti Airtel", "mentioned"),
    (3, "Reliance Industries", "partner"),
    (3, "Meta", "partner"),
    (3, "Reliance Jio", "partner"),
    (4, "AirTrunk", "actor"),
    (4, "Blackstone", "investor"),
    (4, "Canada Pension Plan Investment Board", "investor"),
    (5, "Huawei", "mentioned"),
    (5, "Alibaba", "mentioned"),
    (5, "Baidu", "mentioned"),
    (5, "Cambricon", "mentioned"),
    (5, "Nvidia", "mentioned"),
    (5, "ZTE", "mentioned"),
    (6, "Alibaba", "actor"),
    (6, "Alibaba Cloud", "actor"),
    (7, "AIST", "actor"),
    (7, "Nvidia", "mentioned"),
    (8, "SoftBank", "actor"),
    (8, "Sharp", "mentioned"),
    (9, "Nvidia", "beneficiary"),
    (9, "Foxconn", "beneficiary"),
    (9, "TSMC", "beneficiary"),
    (10, "Nvidia", "mentioned"),
    (10, "Foxconn", "mentioned"),
    (10, "TSMC", "mentioned"),
    (11, "Government of Canada", "actor"),
    (11, "Government of Alberta", "actor"),
    (12, "Broadcom", "investor"),
    (12, "Apollo Global Management", "investor"),
    (12, "Blackstone", "investor"),
    (12, "Anthropic", "mentioned"),
    (12, "Fluidstack", "mentioned"),
]

# (event_idx, theme_name)
_EVENT_THEME_LINKS = [
    (0, "5G"), (0, "telecom"),
    (1, "data center"), (1, "power"),
    (2, "5G"), (2, "telecom"), (2, "fiber"),
    (3, "data center"), (3, "power"),
    (4, "data center"), (4, "power"),
    (5, "semiconductor"), (5, "data center"),
    (6, "data center"), (6, "semiconductor"),
    (7, "data center"), (7, "semiconductor"),
    (8, "data center"), (8, "power"),
    (9, "semiconductor"), (9, "data center"),
    (10, "semiconductor"), (10, "data center"), (10, "power"),
    (11, "data center"),
    (12, "data center"), (12, "semiconductor"),
]


def connect() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)


def register_functions(conn: sqlite3.Connection) -> None:
    def now():
        return dt.datetime.utcnow().isoformat()
    conn.create_function("now", 0, now)


def html_escape(s) -> str:
    if s is None:
        return ""
    s = str(s)
    s = s.replace("&", "&amp;")
    s = s.replace("<", "&lt;")
    s = s.replace(">", "&gt;")
    s = s.replace('"', "&quot;")
    s = s.replace("'", "&#x27;")
    return s


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA)
    conn.commit()


def seed(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    now_ts = dt.datetime.utcnow().isoformat()

    # Insert articles and collect their IDs
    article_ids = []
    for art in _ARTICLES:
        cur.execute(
            "INSERT OR IGNORE INTO articles (source_name, source_country, source_type, url, published_at, original_title, original_text, language, fetched_at) VALUES (?,?,?,?,?,?,?,?,?)",
            (art["source_name"], art["source_country"], art["source_type"], art["url"],
             art["published_at"], art["original_title"], art["original_text"], art["language"], now_ts),
        )
        cur.execute("SELECT id FROM articles WHERE url=?", (art["url"],))
        article_ids.append(cur.fetchone()[0])

    # Insert events and collect their IDs
    event_ids = []
    for ev in _EVENTS:
        art_id = article_ids[ev["article_idx"]]
        art = _ARTICLES[ev["article_idx"]]
        cur.execute(
            "INSERT OR IGNORE INTO events (article_id, country, region, event_title_ja, summary_ja, event_type, impact_direction, confidence_level, time_horizon, created_at, original_url) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (art_id, ev["country"], ev["region"], ev["event_title_ja"], ev["summary_ja"],
             ev["event_type"], ev["impact_direction"], ev["confidence_level"], ev["time_horizon"],
             now_ts, art["url"]),
        )
        cur.execute("SELECT id FROM events WHERE article_id=? AND event_title_ja=?", (art_id, ev["event_title_ja"]))
        event_ids.append(cur.fetchone()[0])

    # Insert companies
    for (name, country, sector) in _COMPANIES:
        cur.execute(
            "INSERT OR IGNORE INTO companies (name, country, sector) VALUES (?,?,?)",
            (name, country, sector),
        )

    # Insert themes
    for theme in _THEMES:
        cur.execute("INSERT OR IGNORE INTO themes (name) VALUES (?)", (theme,))

    # Insert event-company links
    for (ev_idx, company_name, relation_type) in _EVENT_COMPANY_LINKS:
        ev_id = event_ids[ev_idx]
        cur.execute("SELECT id FROM companies WHERE name=?", (company_name,))
        row = cur.fetchone()
        if row:
            company_id = row[0]
            cur.execute(
                "INSERT OR IGNORE INTO event_company_links (event_id, company_id, relation_type) VALUES (?,?,?)",
                (ev_id, company_id, relation_type),
            )

    # Insert event-theme links
    for (ev_idx, theme_name) in _EVENT_THEME_LINKS:
        ev_id = event_ids[ev_idx]
        cur.execute("SELECT id FROM themes WHERE name=?", (theme_name,))
        row = cur.fetchone()
        if row:
            theme_id = row[0]
            cur.execute(
                "INSERT OR IGNORE INTO event_theme_links (event_id, theme_id) VALUES (?,?)",
                (ev_id, theme_id),
            )

    conn.commit()


def _expectation(impact_direction: str, confidence_level: str) -> dict:
    if impact_direction == "positive" and confidence_level == "high":
        return {"expectation_score": 82, "expectation_level": "high_expectation", "expectation_reason": "高信頼度・ポジティブ評価のイベント"}
    if impact_direction == "positive" and confidence_level == "medium":
        return {"expectation_score": 65, "expectation_level": "medium_expectation", "expectation_reason": "中信頼度・ポジティブ評価のイベント"}
    if impact_direction == "neutral":
        return {"expectation_score": 55, "expectation_level": "medium_expectation", "expectation_reason": "中立的なイベント、継続監視推奨"}
    # negative_or_watch
    return {"expectation_score": 40, "expectation_level": "low_expectation", "expectation_reason": "要注意イベント、リスク管理が必要"}


def _growth(event_type: str, time_horizon: str) -> dict:
    type_map = {
        "corporate_investment": (80, "high_growth"),
        "market_expansion": (80, "high_growth"),
        "policy": (65, "medium_growth"),
        "telecom_infra": (70, "medium_growth"),
        "data_center": (75, "medium_growth"),
    }
    score, level = type_map.get(event_type, (55, "watch_growth"))

    horizon_map = {
        "short_term": "1-2年",
        "medium_term": "2-4年",
        "long_term": "3-5年以上",
    }
    growth_horizon = horizon_map.get(time_horizon, "不明")

    drivers_map = {
        "corporate_investment": "民間投資の拡大とAI・クラウドインフラ需要の増加",
        "market_expansion": "新市場参入と既存インフラ拡張による成長機会",
        "policy": "政府主導の政策支援とインフラ整備計画",
        "telecom_infra": "通信ネットワークの高度化と5G・光ファイバー展開",
        "data_center": "データセンター需要拡大と電力・冷却設備需要",
    }
    risks_map = {
        "corporate_investment": "投資実行の遅延、規制リスク、資金調達環境の変化",
        "market_expansion": "競合激化、許認可リスク、需要予測の不確実性",
        "policy": "政策変更リスク、予算配分の変化、実施体制の不確実性",
        "telecom_infra": "設備調達リスク、電波割当の遅延、競合他社の動向",
        "data_center": "電力供給制約、用地確保の困難、建設コストの上昇",
    }

    return {
        "growth_score": score,
        "growth_level": level,
        "growth_horizon": growth_horizon,
        "growth_drivers": drivers_map.get(event_type, "市場動向の詳細な調査が必要"),
        "growth_risks": risks_map.get(event_type, "リスク要因の特定が必要"),
    }


def load_events(conn: sqlite3.Connection) -> list[dict]:
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("""
        SELECT e.*, a.source_name, a.published_at AS article_published_at, a.url AS article_url
        FROM events e
        LEFT JOIN articles a ON e.article_id = a.id
        ORDER BY e.id
    """)
    rows = cur.fetchall()

    # Fetch all companies once
    cur.execute("SELECT id, name, country, sector FROM companies")
    all_companies = {r["id"]: dict(r) for r in cur.fetchall()}

    # Fetch all themes once
    cur.execute("SELECT id, name FROM themes")
    all_themes = {r["id"]: r["name"] for r in cur.fetchall()}

    events = []
    for row in rows:
        ev = dict(row)

        # Companies linked to this event
        cur.execute("""
            SELECT ecl.company_id, ecl.relation_type, ecl.confidence, ecl.evidence_text
            FROM event_company_links ecl
            WHERE ecl.event_id = ?
        """, (ev["id"],))
        company_links = cur.fetchall()

        companies = []
        for cl in company_links:
            c = all_companies.get(cl["company_id"])
            if c:
                companies.append({
                    "name": c["name"],
                    "country": c["country"],
                    "sector": c["sector"] or "",
                    "relation_type": cl["relation_type"],
                })

        # Themes
        cur.execute("""
            SELECT etl.theme_id FROM event_theme_links etl WHERE etl.event_id = ?
        """, (ev["id"],))
        theme_links = cur.fetchall()
        themes = [all_themes[tl["theme_id"]] for tl in theme_links if tl["theme_id"] in all_themes]

        executing_companies = [c for c in companies if c["relation_type"] == "actor"]
        funding_sources = [c for c in companies if c["relation_type"] == "investor"]

        # Procurement categories
        procurement_categories = []
        has_dc = "data center" in themes
        has_telecom = "5G" in themes or "telecom" in themes

        if has_telecom:
            telecom_eq = [c for c in all_companies.values()
                          if c["sector"] and "telecom equipment" in c["sector"]]
            if telecom_eq:
                procurement_categories.append({
                    "category": "基地局・通信設備",
                    "companies": [{"name": c["name"], "country": c["country"]} for c in telecom_eq],
                })

        if has_dc:
            construction = [c for c in all_companies.values()
                            if c["sector"] and ("construction" in c["sector"] or "EPC" in c["sector"])]
            if construction:
                procurement_categories.append({
                    "category": "データセンター建設",
                    "companies": [{"name": c["name"], "country": c["country"]} for c in construction],
                })
            power_cool = [c for c in all_companies.values()
                          if c["sector"] and ("power" in c["sector"] or "cooling" in c["sector"] or "HVAC" in c["sector"])]
            if power_cool:
                procurement_categories.append({
                    "category": "電力・冷却",
                    "companies": [{"name": c["name"], "country": c["country"]} for c in power_cool],
                })
            cloud_ai = [c for c in all_companies.values()
                        if c["sector"] and ("cloud" in c["sector"] or "AI" in c["sector"])]
            if cloud_ai:
                procurement_categories.append({
                    "category": "クラウド・AI",
                    "companies": [{"name": c["name"], "country": c["country"]} for c in cloud_ai],
                })

        exp = _expectation(ev["impact_direction"], ev["confidence_level"])
        grw = _growth(ev["event_type"], ev["time_horizon"])

        events.append({
            **ev,
            "source_name": ev.get("source_name"),
            "published_at": ev.get("article_published_at") or ev.get("published_at"),
            "companies": companies,
            "themes": themes,
            "executing_companies": executing_companies,
            "funding_sources": funding_sources,
            "procurement_categories": procurement_categories,
            **exp,
            **grw,
        })

    conn.row_factory = None
    return events
