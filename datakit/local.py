# -*- coding:utf-8 -*-
import analysis as cal
import tushare as ts
from utility import *
import pandas as pd
import numpy as np
import os
import platform

KTYPE = ['D', '60', '30', '15', '5']
KSUB = {'D': 'day', '60': 'M60', '30': 'M30', '15': 'M15', '5': 'M5'}
AA = ['day', 'M60', 'M30', 'M15', 'M5']
# PERIORD_TAG = {'D': 'day', '60': 'min60', '30': 'min30', '15': 'min15', '5': 'min5'}
FILE_ROOT = os.path.dirname(os.path.realpath(__file__))
CSV_SUB = os.path.join(FILE_ROOT, 'data_csv')
PERIORD_TAG = ['day', 'min60', 'min30', 'min15', 'min5']
DATESTAMP_FILE = os.path.join(FILE_ROOT, 'data.datestamp')
INFO_FILE = os.path.join(FILE_ROOT, 'info.csv')
TRADE_DATE_FILE = os.path.join(FILE_ROOT, 'trade_date.csv')
INFO_TOTAL_COL = ['name', 'industry', 'area', 'pe', 'outstanding', 'totals',
                  'totalAssets', 'liquidAssets', 'fixedAssets', 'reserved',
                  'reservedPerShare', 'esp', 'bvps', 'pb', 'timeToMarket',
                  'undp', 'perundp', 'rev', 'profit', 'gpr', 'npr', 'holders']
HDF_FILE = os.path.join(FILE_ROOT, 'database.h5')
THS_F10_URL = 'http://basic.10jqka.com.cn/{}'
FILE_ROOT = os.path.dirname(os.path.realpath(__file__))
TIP_FOLDER = os.path.join(FILE_ROOT, 'tips')
TIP_FILE = os.path.join(TIP_FOLDER, '{}.html')
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
TDX_ROOT = 'e:\\software\\zd_zsone' if platform.node() == 'NeilWang-L10' \
    else 'o:\\workspace\\zd_zsone'


def read_local_data(code, ktype, item, pos=0, count=None):
    file = os.path.join(CSV_SUB, '{}_{}.csv'.format(KSUB[ktype], code))
    if not os.path.exists(file):
        log.error('No local data file: {}!'.format(file))
        assert 0
    df = pd.read_csv(file,
                     nrows=(count - pos) if count is not None else count,
                     usecols=[item])
    if pos != 0:
        df.drop([abs(pos) - 1], inplace=True)
    if count is not None and df.shape[0] < count:
        df = pd.concat([df, pd.DataFrame(np.zeros((count - df.shape[0],
                                                   df.shape[1])),
                                         columns=df.columns)])
    return df


def get_local_info(code, item):
    if not os.path.exists(INFO_FILE):
        log.error('No local info file: {}!'.format(INFO_FILE))
    infos = pd.read_csv(INFO_FILE,
                        usecols=[item],
                        columns={'code': str}).set_index('code')
    return infos.loc[code, item]


def get_all_codes():
    info_file = os.path.join(FILE_ROOT, INFO_FILE)
    if not os.path.exists(info_file):
        log.info('No local info file: {}, get all codes online.'.format(info_file))
        ret = ts.get_stock_basics().index
    else:
        ret = pd.read_csv(info_file, dtype={'code': str}).loc[:, 'code']
    return ret


def get_trade_date(start_year=None):
    if not os.path.exists(TRADE_DATE_FILE):
        df = ts.trade_cal()
        df = df[df['isOpen'] == 1]
        df.to_csv(TRADE_DATE_FILE, encoding='utf-8-sig')
    else:
        df = pd.read_csv(TRADE_DATE_FILE)
    if start_year is not None:
        df = df[df['calendarDate'].str.find(start_year) == 0]
    return df


def down_trade_data(start_year=None):
    if not os.path.exists(TRADE_DATE_FILE):
        df = ts.trade_cal()
        df = df[df['isOpen'] == 1]
        df = df[df['calendarDate'].str.find(start_year) == 0]
        df.to_csv(TRADE_DATE_FILE, encoding='utf-8-sig')
    else:
        pass


def open_url_ret_html(url):
    import random
    user_agent = random.choice(USER_AGENTS)
    headers = {'User-Agent': user_agent, 'Connection': 'keep-alive'}
    req = Request(url, headers=headers)
    content = None
    try:
        content = urlopen(req)
    except Exception as err:
        log.error('{}, {}'.format(err, url))
    html = content.read().decode('gbk')
    return html


def update_tips(args):
    back_color, font_color, font_type, place = args
    from glob import glob
    _dir = TIP_FOLDER if place == 'local' else os.path.join(TDX_ROOT, 'T0002', 'tips')
    files = glob(_dir + '\\*')
    for file in files:
        with open(file, 'r') as f:
            c = f.read()
            pattern = re.compile(r'bgcolor="(.*)"></body>')
            u = pattern.sub('bgcolor="{}"></body>'.format(back_color), c)
            pattern = re.compile(r'style="color:.*?;')
            u = pattern.sub('style="color:{};'.format(font_color), u)
            pattern = re.compile(r'font-family:.*?;')
            u = pattern.sub('font-family:{};'.format(font_type), u)
        if u != c:
            with open(file, 'w') as f:
                f.write(u)


@print_run_time
def copy_diff_tips():
    import filecmp
    import shutil
    dst_tip_dir = os.path.join(TDX_ROOT, 'T0002', 'tips')
    dir_diff = filecmp.dircmp(TIP_FOLDER, dst_tip_dir)
    diffs = dir_diff.diff_files
    list(map(shutil.copy,
             [os.path.join(TIP_FOLDER, x) for x in diffs],
             [os.path.join(dst_tip_dir, x) for x in diffs]))


@print_run_time
def down_info_data(update=True):
    basic_infos = None
    if update is True:
        keep_cols = ['name', 'outstanding', 'timeToMarket']
        basic_infos = ts.get_stock_basics()
        useless_cols = list(set(basic_infos.columns).difference(set(keep_cols)))
        basic_infos = basic_infos.drop(columns=useless_cols)
        basic_infos = basic_infos[basic_infos['name'].str.find('*') == -1]
        basic_infos = basic_infos[basic_infos['timeToMarket'] != 0]
    else:
        if os.path.exists(INFO_FILE):
            basic_infos = pd.read_csv(INFO_FILE)
        else:
            log.error('No info file <{}>!'.format(INFO_FILE))
    basic_infos = basic_infos.reset_index()
    return basic_infos


def download_basic_worker(code):
    ret = {}
    datas = None
    try:
        datas = list(map(ts.get_k_data, [code] * 5, [''] * 5, [''] * 5, KTYPE))
    except Exception as err:
        log.err('Download {} fail.'.format(code))
        log.error(err)
    ret[code] = datas
    return ret


def save_basic_worker(stock):
    # write with csv format
    for code in stock:
        for i in range(5):
            file_name = '{}\\{}_{}.csv'.format(CSV_SUB, PERIORD_TAG[i], code)
            stock[code][i].sort_index(ascending=False).to_csv(file_name, index=False)
    # # write with csv format
    # hdf = pd.HDFStore(HDF_FILE)
    # from tqdm import tqdm
    # for code in tqdm(data, ascii=True):
    #     for i in range(5):
    #         table_name = '{}_{}'.format(PERIORD_TAG[i], code)
    #         hdf[table_name] = data[code][i].sort_index(ascending=False)
    # hdf.close()

    # write with pickle format
    # from tqdm import tqdm
    # for code in tqdm(data, ascii=True):
    #     for i in range(5):
    #         table_name = './aa/{}_{}.csv'.format(PERIORD_TAG[i], code)
    #         data[code][i].sort_index(ascending=False).to_pickle(table_name


def business_filter(tag):
    return tag.name == 'td' and '主营业务' in tag.get_text()


def concept_filter(tag):
    return tag.name == 'td' and '概念强弱排名' in tag.get_text()


def zt_reason_filter(tag):
    return tag.name == 'tr' and '涨停揭秘' in tag.get_text()


def download_tips_worker(code):
    import random
    sleep(random.randint(0, 7) * 0.1)
    info_dict = {}
    info_dict['code'] = code
    url = THS_F10_URL.format(code)
    html = open_url_ret_html(url)
    # soup = BeautifulSoup(html, "lxml-xml")
    soup = BeautifulSoup(html, "html.parser")
    # dbg_a = soup.prettify()
    find_res = soup.find_all(business_filter)
    if len(find_res) != 0:
        info_dict['business'] = find_res[0].a['title']
    find_res = soup.find_all(concept_filter)
    if len(find_res) != 0:
        for tag in find_res[0].find_all('a'):
            if '详情' not in tag.text:
                info_dict.setdefault('concept', []).append(tag.text)
    find_res = soup.find_all(zt_reason_filter)
    if len(find_res) != 0:
        info_dict.setdefault('zhangting', []).append(find_res[0].td.text)
        tmp = re.search(r'(\d+:\d+).*：(.*).*', find_res[0].span.text.strip())
        if tmp:
            info_dict.setdefault('zhangting', []).extend(tmp.groups())
            info_dict.setdefault('zhangting', []).append(find_res[0].div.text.strip())
    return info_dict


def save_tips_worker(item):
    file = TIP_FILE.format(item['code'])
    yw = item['business'] if 'business' in item.keys() else '--'
    tc = ', '.join(item['concept']) if 'concept' in item.keys() else '--'
    zt = ' : '.join(item['zhangting'][:3]) if 'zhangting' in item.keys() else '--'
    ztyy = item['zhangting'][3] if 'zhangting' in item.keys() else '--'
    content = '<head><meta http-equiv="Content-Type" content="text/html; charset=gbk" /></head>\n' \
              '<body bgcolor="#070608"></body>\n' \
              '<p><span style="color:#FFE500;line-height:1.3;font-size:14px;font-family:等线;">' \
              '业务：{}<br />题材：{}<br />涨停：{}<br />涨停原因：{}</span></p>'.format(yw, tc, zt, ztyy)
    with open(file, 'w') as f:
        f.write(content)


@print_run_time
def update_local_database(mode):
    if not os.path.exists(CSV_SUB):
        os.mkdir(CSV_SUB)
    info_data = down_info_data()
    codes = list(info_data['code'])
    down_trade_data('2018')
    mt = MultiTasks()
    if mode == 'basic' or mode == 'all':
        sub_size = int((len(codes) + MAX_TASK_NUM) / MAX_TASK_NUM)
        sub_code = [list(codes[i:i + sub_size]) for i in range(0, len(codes), sub_size)]
        basic = mt.run_tasks(func=download_basic_worker, var_args=sub_code, en_bar=True,
                             desc='Down-Basic', merge_result=False)
        mt.run_tasks(func=save_basic_worker, var_args=basic, en_bar=True, desc='Save-Basic')
    if mode == 'info' or mode == 'all':
        sub_size = int((info_data.shape[0] + MAX_TASK_NUM) / MAX_TASK_NUM)
        sub_item = [list(info_data['code'][i:i + sub_size]) for i in range(0, info_data.shape[0], sub_size)]
        zt = mt.run_tasks(func=cal.zt, var_args=sub_item, en_bar=True, desc='Cal-ZT')
        zb = mt.run_tasks(func=cal.zb, var_args=sub_item, en_bar=True, desc='Cal-ZB')
        pcp = mt.run_tasks(func=cal.pcp, var_args=sub_item, en_bar=True, desc='Cal-PCP')
        t = info_data.loc[:, ('code', 'outstanding')].values
        sub_item = [t[i:i + sub_size] for i in range(0, info_data.shape[0], sub_size)]
        tor = mt.run_tasks(func=cal.tor, var_args=sub_item, en_bar=True, desc='Cal-TOR')
        ltsz = mt.run_tasks(func=cal.ltsz, var_args=sub_item, en_bar=True, desc='Cal-LTSZ')

        updated_info = pd.concat([info_data,
                                  pd.Series(zt, name='zt'),
                                  pd.Series(zb, name='zb'),
                                  pd.Series(tor, name='tor'),
                                  pd.Series(pcp, name='pcp'),
                                  pd.Series(ltsz, name='ltsz')], axis=1)
        updated_info.to_csv(INFO_FILE, encoding='utf-8-sig')
    if mode == 'tips':
        import random
        if not os.path.exists(TIP_FOLDER):
            os.mkdir(TIP_FOLDER)
        var = 0
        if var:
            sub_size = int((len(codes) + 2) / 2)
            sub_code = [codes[i:i + sub_size] for i in range(0, len(codes), sub_size)]
            results = mt.run_tasks(func=download_tips_worker, var_args=sub_code,
                                   en_bar=True, desc='Down-Tips')
        else:
            results = []
            from tqdm import tqdm
            counter = 0
            for code in tqdm(codes, ascii=True):
                aa = download_tips_worker(code)
                results.append(aa)
                sleep(random.randint(0, 6) * 0.1)
                if counter == 150:
                    counter = 0
                    sleep(2)
                else:
                    counter += 1
        sub_size = int((len(codes) + MAX_TASK_NUM) / MAX_TASK_NUM)
        sub_item = [results[i:i + sub_size] for i in range(0, len(results), sub_size)]
        mt.run_tasks(func=save_tips_worker, var_args=sub_item, en_bar=True, desc='Save-Tips')
        copy_diff_tips()

    mt.close_tasks()


def sasadf(a, b):
    asdfasdf = 0

if __name__ == '__main__':
    with TimerCount('Test of Download'):
        update_local_database('tips')
