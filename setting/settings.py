import os
import platform

class Setting:
    # env
    OFFICE_TDX_ROOT = 'e:\\software\\new_jyplug'
    HOME_TDX_ROOT = 'o:\\Program Files\\new_jyplug'
    TDX_ROOT = OFFICE_TDX_ROOT if platform.node() == 'NeilWang-L10' else HOME_TDX_ROOT
    # path
    ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    OUT_DIR = os.path.join(ROOT, 'out_dir')
    TIP_FOLDER = os.path.join(OUT_DIR, 'tips')
    BIN_ROOT = os.path.join(ROOT, 'bins')
    SETTING_ROOT = os.path.join(ROOT, 'setting')
    MONITOR_ROOT = os.path.join(ROOT, 'monitor')
    # files
    CSV_DIR = os.path.join(OUT_DIR, 'data_csv')
    INFO_FILE = os.path.join(OUT_DIR, 'info.csv')
    CONCEPT_FILE = os.path.join(OUT_DIR, 'concept.csv')
    ZT_REASON_FILE = os.path.join(OUT_DIR, 'zt_reason.csv')
    TRADE_DATE_FILE = os.path.join(OUT_DIR, 'trade_date.csv')
    ZT_FILE = os.path.join(OUT_DIR, 'zt.csv')
    ZB_FILE = os.path.join(OUT_DIR, 'zb.csv')
    ZT_RSN_REC = os.path.join(OUT_DIR, 'zhangting_reason.rec')
    ZT_REC = os.path.join(OUT_DIR, 'zhangting.rec')
    ZB_REC = os.path.join(OUT_DIR, 'zhaban.rec')
    LB_REC = os.path.join(OUT_DIR, 'lianban.rec')
    EXE_CLICKIT = os.path.join(BIN_ROOT, 'ClickIt.exe')
    EXE_7Z = os.path.join(BIN_ROOT, '7z.exe')
    CHROME_EXE = os.path.join(BIN_ROOT, 'chromedriver.exe')
    T0002_LIST = os.path.join(SETTING_ROOT, 't0002.list')
    RAW_IP_FILE = os.path.join(SETTING_ROOT, 'raw_ips.txt')
    CONNECTABLE_IP = os.path.join(SETTING_ROOT, 'connectable_ip.txt')
    PROXY_IP_LIB = os.path.join(SETTING_ROOT, 'ip.txt')
    PROXY_IP_LIB_BACKUP = os.path.join(SETTING_ROOT, 'ip_backup.txt')
    CUSTOM_TRADING = os.path.join(SETTING_ROOT, 'trading.py')
    TDX_IMPORT_LIST = os.path.join(MONITOR_ROOT, 'tdx.txt')
    MANUAL_LIST = os.path.join(MONITOR_ROOT, 'manual.txt')
    MRZTBFP_PAPER_URLS = os.path.join(SETTING_ROOT, 'mrztbfp_url.txt')

    # wencai
    BASE_LIST = os.path.join(SETTING_ROOT, 'wencai_blk.txt')
    OFF_COOKIE = r'pgv_si=s6860581888; tvfe_boss_uuid=4302b4ce8e2b01b5; qv_swfrfh=www.a-site.cn; qv_swfrfc=v20; qv_swfrfu=http://www.a-site.cn/article/865624.html; qqmusic_fromtag=66; douyu_loginKey=2db1606fce1d37928d0aef1440e91f61; pgv_pvi=2295221248; 3g_guest_id=-8822659296773763072; pgv_info=ssid=s8638106408&ssi=s5578869165&pgvReferrer=; pgv_pvid=4577485018; ptisp=cnc; RK=rGEmxdWvFj; ptcz=a485dc4c55b47c027d7c48a611b68fb9e7a4397acdb665b2a00fb48e8a461429; pt2gguin=o0051682577; o_cookie=51682577; user_id=null; session_id=null; rewardsn=; wxtokenkey=777; _qpsvr_localtk=0.804020716922089; verifysession=h0128655617061338d7b683c005588962b54177a88b709528394bb0a0bd5eb15385d80f1e910927a6ac; pac_uid=1_51682577; ua_id=dWayl9iIPqBQL3DqAAAAAG3Qdx2Bf7T-knxZ3YZpcKU=; cert=Z5TwwLc8YRKVwZhGECVXYjIcvQbcamT9; sig=h014a23f2e55aee481c417b2de1e5e73cfabc805a0ef8f8ede46650df4e85065ea06a460de52b7cfc34; qb_qua=; qb_guid=81685f2fc5f24825aeac1e565e586366; Q-H5-GUID=81685f2fc5f24825aeac1e565e586366; NetType=; mm_lang=zh_CN; uuid=168fa2821b6e6125c56193d5f28b269e; bizuin=3556648282; ticket=c67e481434fa0754f017adc64fd43d6bc4e11a77; ticket_id=gh_b5f02cb25880; noticeLoginFlag=1; data_bizuin=3556648282; data_ticket=brr/81h80Q5ax4/S0SpjT5ujnr78rWCwSuNNLKGkIKbbuP9DkUvvf4ArH/S9CSyW; slave_sid=RW5qVDBpSGw4azVoOW56ajExYXVmakhkT2UwclBrNjlzRGt6MUplbUVGdnZjTU9OcjhTekJLUmdna2U3V2ZyZHhKV0JoY0pycDN0NUczaHRrN3p6b3J5cFRJdlZwX1BIMFhOOEdLT2c5SVhTR2p2NjZPRE03TkdtR2xXSHB6QXFRY0pnT0V1ZDJCU2tNU21Z; slave_user=gh_b5f02cb25880; xid=94298d78ac6a5cc9676b22900b99aa1b; openid2ticket_oWiX-01EwniiVdCbUEGiajb3aof4=3HYGbiarJeqy0btqJAMCjn81MoGSUVimvLNmajw+eoU='
    TOKEN = r'1098835852'
    BIZ = r'MzAxMDYxNDQ4NA=='
    UIN = r'NzgzNzc2NTIw'
    # need update per day
    WECHAT_COOKIE = r'rewardsn=; wxtokenkey=777; wxuin=783776520; devicetype=Windows10; version=62060728; lang=zh_CN; pass_ticket=W3Njchcfr8FlLLi+ZqW6izag96DgaG+FM/fSaj7HoF7zhIzg6884ktafAOLtONRs; wap_sid2=CIj23fUCElx5OTQweHhGRDA1ek01SXZYUWF5WHNjSVBESEFjVDNCRzJzMTBaTjM1b3pzTVpodm5jbjV2SkRCd1A0SEpFZWpWUjVfLW5aUk0zSUVYY3ZLSTVTZ2xqLVlEQUFBfjD4kfLjBTgNQAE='
    APPMSG_TOKEN = r'998_4Ints0NDf%2BX%2FZ3Yg46pf7hOguVweDnOGxzF-jfbdCfXhppSBB2RzfrG3HCtDwMT61GzlCA26q6azdtTa'


    # constant values
    PROXY_TIMEOUT = 2
    MAX_TASK_NUM = 16
    KTYPE = ['D', '60', '30', '15', '5']
    PERIORD_TAG = ['day', 'min60', 'min30', 'min15', 'min5']
    USER_AGENTS = [
        "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
        "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
        "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
        "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
        "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
        "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
        "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
        "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
        "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
        "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
        "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
        "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.11 TaoBrowser/2.0 Safari/536.11",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71 Safari/537.1 LBBROWSER",
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; LBBROWSER)",
        "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E; LBBROWSER)",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.84 Safari/535.11 LBBROWSER",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E)",
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; QQBrowser/7.0.3698.400)",
        "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SV1; QQDownload 732; .NET4.0C; .NET4.0E; 360SE)",
        "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E)",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1",
        "Mozilla/5.0 (iPad; U; CPU OS 4_2_1 like Mac OS X; zh-cn) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8C148 Safari/6533.18.5",
        "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.0b13pre) Gecko/20110307 Firefox/4.0b13pre",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:16.0) Gecko/20100101 Firefox/16.0",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11",
        "Mozilla/5.0 (X11; U; Linux x86_64; zh-CN; rv:1.9.2.10) Gecko/20100922 Ubuntu/10.10 (maverick) Firefox/3.6.10",
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    ]

    def __init__(self):
        if not os.path.exists(self.OUT_DIR):
            os.mkdir(self.OUT_DIR)
        if not os.path.exists(self.TIP_FOLDER):
            os.mkdir(self.TIP_FOLDER)
        if not os.path.exists(self.CSV_DIR):
            os.mkdir(self.CSV_DIR)


sets = Setting()

