import re
import os
import random
import requests
from tqdm import tqdm
from bs4 import BeautifulSoup
from utility.log import log
from utility.timekit import time_str, sleep
from setting.settings import TDX_ROOT, TIP_FOLDER
from utility.timekit import print_run_time

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
THS_F10_URL = 'http://basic.10jqka.com.cn/{}'

if not os.path.exists(TIP_FOLDER):
    os.mkdir(TIP_FOLDER)


def business_filter(tag):
    return tag.name == 'td' and '主营业务' in tag.get_text()


def concept_filter(tag):
    return tag.name == 'td' and '概念强弱排名' in tag.get_text()


def zt_reason_filter(tag):
    return tag.name == 'tr' and '涨停揭秘' in tag.get_text()


def download_tips_worker(code):
    info_dict = {}
    info_dict['code'] = code
    url = THS_F10_URL.format(code)
    user_agent = random.choice(USER_AGENTS)
    headers = {'User-Agent': user_agent,
               'Connection': 'keep-alive',
               'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
               'Accept-Encoding': 'gzip'}

    req = requests.get(url, headers=headers)
    if req.status_code != 200:
        log.error('error, code is {}'.format(req.status_code))
        exit(0)

    html = req.content.decode('gbk')
    pat = re.compile(r'主营业务：.*?<a.*?>(.*?)</a>.*', re.S)
    find = pat.findall(html)
    if len(find) == 1:
        info_dict['business'] = find[0]
    elif len(find) == 0:
        info_dict['bussiness'] = None
    else:
        print(code)
        assert 0

    pat = re.compile(r'<a class=\'newtaid\'.*?ifind">(.*?)<', re.S)
    find = pat.findall(html)
    if len(find) > 0:
        info_dict['concept'] = find
    else:
        info_dict['concept'] = None
        print(code)
        assert 0

    if html.find('涨停揭秘'):
        pat = re.compile(
            r'<td class="hltip tc f12">(.*?)</td>.*?<strong class="hltip fl">(.*?)</strong>', re.S)
        find = pat.findall(html)
        date = list(filter(lambda x: '涨停揭秘：' in x, find))[0][0]
        date = time_str(fine=False) if '今天' in date else date
        if date:
            info_dict.setdefault('zhangting', []).append(date)
        else:
            info_dict.setdefault('zhangting', []).append(None)
        pat = re.compile(r'<a class="fr hla gray f12 client.*?<span>\s*(.*?)\s*</span>', re.S)
        find = pat.findall(html)
        if len(find) > 0:
            info_dict.setdefault('zhangting', []).extend(find)
        else:
            info_dict.setdefault('zhangting', []).append(None)
        pat = re.compile(r'涨停原因.*?<div class="check_else">\s*(.*?)\s*</div>', re.S)
        find = pat.findall(html)
        if len(find) > 0:
            info_dict.setdefault('zhangting', []).extend(find)
        else:
            info_dict.setdefault('zhangting', []).append(None)
    else:
        info_dict['zhangting'] = None

    if len(find) > 0:
        info_dict.setdefault('concept', []).append(html)
    else:
        print(code)
        assert 0
    return info_dict


def save_tips_worker(item, tip_file):
    file = tip_file.format(item['code'])
    yw = item['business'] if item['business'] is not None else '--'
    tc = ', '.join(item['concept']) if item['concept'] is not None else '--'
    zt = '{}, {}'.format(*item['zhangting'][:2]) if item['zhangting'] is not None else '--'
    ztyy = item['zhangting'][2] if item['zhangting'][2] is not None else '--'
    content = '<head><meta http-equiv="Content-Type" content="text/html; charset=gbk" /></head>\n' \
              '<body bgcolor="#070608"></body>\n' \
              '<p><span style="color:#3CB371;line-height:1.3;font-size:14px;font-family:微软雅黑;">' \
              '业务：{}<br />题材：{}<br />涨停：{}<br />涨停原因：{}</span></p>'.format(yw, tc, zt, ztyy)
    with open(file, 'w') as f:
        f.write(content)


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


def down_tips(codes: list, mt=None):
    ret_list = []
    counter = 0
    for code in tqdm(codes, ascii=True, desc='DownTips'):
        try:
            aa = download_tips_worker(code)
        except Exception as err:
            aa = None
            print(err)
            print(code)
            exit()
        save_tips_worker(aa, TIP_FILE)
        ret_list.append(aa)
        sleep(random.randint(0, 6) * 0.1)
        if counter == 30:
            counter = 0
            sleep(1)
        else:
            counter += 1
    c = '\n'.join(list(map(lambda x: ','.join((x['code'], ' '.join(x['concept']))), results)))
    with open(CONCEPT_FILE, 'w') as f:
        f.write(c)
    log.info('Make concept list done.')
    # sub_size = int((len(codes) + MAX_TASK_NUM) / MAX_TASK_NUM)
    # sub_item = [results[i:i + sub_size] for i in range(0, len(results), sub_size)]
    # mt.run_tasks(func=save_tips_worker, var_args=sub_item, fix_args=TIP_FILE,
    #              en_bar=True, desc='Save-Tips')
    copy_diff_tips()


if __name__ == '__main__':
    down_tips(['300173'])
