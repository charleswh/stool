import re
import os
import random
import requests
from tqdm import tqdm
import tushare as ts
from utility.log import log
from utility.timekit import time_str, sleep, print_run_time
from utility.task import MultiTasks
from crawler.proxy import get_random_header
from setting.settings import TDX_ROOT, TIP_FOLDER, USER_AGENTS, CONCEPT_FILE, PROXY_LIST

TIP_FILE = os.path.join(TIP_FOLDER, '{}.html')


def download_tips_worker(code):
    info_dict = {}
    info_dict['code'] = code
    url = THS_F10_URL.format(code)
    user_agent = random.choice(USER_AGENTS)
    headers = {'User-Agent': user_agent,
               'Connection': 'keep-alive',
               'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
               'Accept-Encoding': 'gzip'}

    proxy_ip = '117.127.0.209:80'
    proxy_ip = {'http': proxy_ip}
    req = requests.get(url, headers=headers, proxies=proxy_ip, timeout=5)
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

    if html.find('涨停揭秘') != -1:
        pat = re.compile(
            r'<td class="hltip tc f12">(.*?)</td>.*?<strong class="hltip fl">(.*?)</strong>', re.S)
        find = pat.findall(html)
        date = None
        try:
            date = list(filter(lambda x: '涨停揭秘：' in x, find))[0][0]
        except IndexError as err:
            pat = re.compile(
                r'<td rowspan="\d+" class="today tc">(.*?)</td>.*?<strong class="hltip fl">(.*?)</strong>',
                re.S)
            find = pat.findall(html)
            date = list(filter(lambda x: '涨停揭秘：' in x, find))[0][0]
        assert 0 if date is None else 1
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
            for i in range(len(find)):
                find[i] = find[i].replace('<span class="hl">', '')
                find[i] = find[i].replace('</span>', '')
            info_dict.setdefault('zhangting', []).extend(find)
        else:
            info_dict.setdefault('zhangting', []).append(None)
    else:
        info_dict['zhangting'] = None

    return info_dict


def save_tips(info):
    file = TIP_FILE.format(info['code'])
    yw = info['business'] if info['business'] is not None else '--'
    tc = ', '.join(info['concept']) if info['concept'] is not None else '--'
    if info['zhangting'] is not None:
        zt = '{}, {}'.format(*info['zhangting'][:2])
        ztyy = info['zhangting'][2] if info['zhangting'][2] is not None else '--'
    else:
        zt = '--'
        ztyy = '--'
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


def get_single_html(code, proxy_queue, p_ip, lock):
    header = get_random_header()
    url = 'http://basic.10jqka.com.cn/{}'.format(code)
    html = None
    while True:
        if len(p_ip) == 0:
            with lock:
                if not proxy_queue.empty():
                    p_ip = proxy_queue.get()
                else:
                    p_ip = None
        proxy_ip = {'http': '{}:{}'.format(*p_ip)} if p_ip is not None else p_ip
        try:
            req = requests.get(url, headers=header, proxies=proxy_ip, timeout=3)
        except Exception as err:
            with lock:
                p_ip = []
            continue
        if req.status_code != 200:
            if proxy is None:
                log.error('All proxies and local IP are blocked by remote.')
                exit(0)
            else:
                with lock:
                    p_ip = []
                continue
        else:
            html = req.content.decode('gbk')
            break
    return html


def parse_html(html):
    info_dict = {}
    pat = re.compile(r'主营业务：.*?<a.*?>(.*?)</a>.*', re.S)
    find = pat.findall(html)
    if len(find) == 1:
        info_dict['business'] = find[0]
    elif len(find) == 0:
        info_dict['bussiness'] = None
    else:
        assert 0

    pat = re.compile(r'<a class=\'newtaid\'.*?ifind">(.*?)<', re.S)
    find = pat.findall(html)
    pat = re.compile(r'<a class=\'newtaid\'.*?emerging">(.*?)<', re.S)
    find.extend(pat.findall(html))
    find = list(filter(lambda x: '详情' not in x or '>>' not in x, find))
    if len(find) > 0:
        info_dict['concept'] = find
    else:
        info_dict['concept'] = None

    if html.find('涨停揭秘') != -1:
        pat = re.compile(
            r'<td class="hltip tc f12">(.*?)</td>.*?<strong class="hltip fl">(.*?)</strong>', re.S)
        find = pat.findall(html)
        date = None
        try:
            date = list(filter(lambda x: '涨停揭秘：' in x, find))[0][0]
        except IndexError as err:
            pat = re.compile(
                r'<td rowspan="\d+" class="today tc">(.*?)</td>.*?<strong class="hltip fl">(.*?)</strong>',
                re.S)
            find = pat.findall(html)
            date = list(filter(lambda x: '涨停揭秘：' in x, find))[0][0]
        assert 0 if date is None else 1
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
            for i in range(len(find)):
                find[i] = find[i].replace('<span class="hl">', '')
                find[i] = find[i].replace('</span>', '')
            info_dict.setdefault('zhangting', []).extend(find)
        else:
            info_dict.setdefault('zhangting', []).append(None)
    else:
        info_dict['zhangting'] = None

    return info_dict


def down_tips_worker(code, proxy_queue, p_ip, lock):
    html = get_single_html(code, proxy_queue, p_ip, lock)
    info = parse_html(html)
    info['code'] = code
    save_tips(info)
    return info


def down_tips():
    codes = ts.get_stock_basics().index.values.tolist()
    with open(PROXY_LIST, 'r') as f:
        proxies = f.read().split('\n')
    proxies = list(map(lambda x: x.split(',')[:2], proxies))
    codes = codes[:50]
    proxies = proxies[:10]
    with MultiTasks(4, tip_depth=len(proxies)) as mt:
        mt.load_tips_queue(proxies)
        res = mt.run_list_tasks(func=down_tips_worker, var_args=codes, en_bar=True, tips=True)

    c = '\n'.join(list(map(lambda x: ','.join((x['code'], ' '.join(x['concept']))), res)))
    with open(CONCEPT_FILE, 'w') as f:
        f.write(c)
    log.info('Make concept list done.')
    copy_diff_tips()


if __name__ == '__main__':
    url = 'http://basic.10jqka.com.cn/300240'
    req = requests.get(url=url, headers=get_random_header())
    req.encoding = 'gbk'
    parse_html(req.text)
    # down_tips()
