# -*- coding:utf-8 -*-
from bs4 import BeautifulSoup
import os
import re
from urllib.request import Request, urlopen
from utility import *
from datakit import *

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


def download_stock_tips_m(codes):
    sub_size = int((len(codes) + MAX_TASK_NUM) / MAX_TASK_NUM)
    sub_code = [codes[i:i + sub_size] for i in range(0, len(codes), sub_size)]
    results = multi_task(func=download_tips_worker, var_args=sub_code, manual_task_num=8,
                         enable_bar=True, desc='Down-Tips')

    if not os.path.exists(TIP_FOLDER):
        os.mkdir(TIP_FOLDER)
    sub_item = [results[i:i + sub_size] for i in range(0, len(results), sub_size)]
    multi_task(func=save_tips_worker, var_args=sub_item, enable_bar=True, desc='Save-Tips',
               manual_task_num=4)


def download_stock_tips(codes):
    codes = codes
    import random
    if not os.path.exists(TIP_FOLDER):
        os.mkdir(TIP_FOLDER)

    var = 0
    mt = MultiTasks()
    if var:
        sub_size = int((len(codes) + 2) / 2)
        sub_code = [codes[i:i + sub_size] for i in range(0, len(codes), sub_size)]
        results = mt.run_tasks(func=download_tips_worker, var_args=sub_code, en_bar=True, desc='Down-Tips')
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


def update_tips(args):
    back_color, font_color, font_type = args
    from glob import glob
    files = glob(TIP_FOLDER + '\\*')
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

    a = 0


if __name__ == '__main__':
    pass
    # download_tips_worker([['000012'], 1, 1, 1])
    # codes = get_all_codes()
    # download_stock_tips(codes)d
