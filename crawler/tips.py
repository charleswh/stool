import re
import os
import requests
from tqdm import tqdm
import tushare as ts
from utility.log import log
from utility.timekit import time_str, print_run_time
from utility.task import MultiTasks
from crawler.proxy import get_random_header, get_proxy_ip
from setting.settings import TDX_ROOT, TIP_FOLDER, CONCEPT_FILE, ZT_REASON_FILE, VALID_PROXIES

TIP_FILE = os.path.join(TIP_FOLDER, '{}.html')


def save_tips(info):
    file = TIP_FILE.format(info['code'])
    yw = info['business'] if info['business'] is not None else '-'
    tc = ', '.join(info['concept']) if info['concept'] is not None else '-'
    if info['zhangting'] is not None:
        zt = '{}, {}'.format(*info['zhangting'][:2])
        ztyy = info['zhangting'][2] if info['zhangting'][2] is not None else '-'
    else:
        zt = '-'
        ztyy = '-'
    content = '<head><meta http-equiv="Content-Type" content="text/html; charset=gbk" /></head>\n' \
              '<body bgcolor="#070608"></body>\n' \
              '<p><span style="color:#3CB371;line-height:1.3;font-size:14px;font-family:微软雅黑;">' \
              '业务：{}<br />题材：{}<br />涨停：{}<br />涨停原因：{}</span></p>'.format(yw, tc, zt, ztyy)
    with open(file, 'w') as f:
        f.write(content)


def copy_tips_files():
    import filecmp
    import shutil
    print('Copy tips files to tdx folder...')
    dst_tip_dir = os.path.join(TDX_ROOT, 'T0002', 'tips')
    dir_diff = filecmp.dircmp(TIP_FOLDER, dst_tip_dir)
    print('copy tips files from {} to {}...'.format(TIP_FOLDER, dst_tip_dir))
    diffs = dir_diff.diff_files
    list(map(shutil.copy,
             [os.path.join(TIP_FOLDER, x) for x in diffs],
             [os.path.join(dst_tip_dir, x) for x in diffs]))


def modify_tips(args):
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


def get_single_html(code, proxy_ip=None, timeout=None):
    url = 'http://basic.10jqka.com.cn/{}'.format(code)
    p_ip = {'http': 'http://{}'.format(proxy_ip),
            'https': 'https://{}'.format(proxy_ip)} if proxy_ip is not None else None
    try:
        req = requests.get(url=url, headers=get_random_header(), proxies=p_ip, timeout=timeout)
        html = req.content.decode('gbk')
        if req.status_code == 200 and len(html) > 500:
            return html
    except Exception as err:
        return None


def parse_html(html):
    info_dict = {}
    pat = re.compile(r'主营业务：.*?<a.*?>(.*?)</a>.*', re.S)
    find = pat.findall(html)
    if len(find) == 1:
        info_dict['business'] = find[0]
    elif len(find) == 0:
        info_dict['business'] = None
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


def down_tips_worker(code, proxy_ip=None, timeout=None, retry=3):
    info = {}
    for _ in range(retry):
        html = get_single_html(code, proxy_ip, timeout)
        if html is None or html == '':
            return None
        info = parse_html(html)
        if info['business'] is None and info['concept'] is None and info['zhangting'] is None:
            continue
        else:
            break
    info['code'] = code
    save_tips(info)
    cct = ','.join([code, ' '.join(info['concept']) if info['concept'] is not None else '-'])
    if info['zhangting'] is not None and len(info['zhangting']) > 2 and \
            info['zhangting'][1] is not None:
        rsn = info['zhangting'][1].split('：')
        rsn = ','.join([code, rsn[-1]]) if len(rsn) > 1 else '-'
    else:
        rsn = '-'
    return (cct, rsn)


def down_tips():
    codes = ts.get_stock_basics().index.values.tolist()
    with open(VALID_PROXIES, 'r') as f:
        proxies_ori = f.read().split('\n')
    res = []
    proxies = proxies_ori
    proxy_expire_flag = -1
    p = proxies.pop(0)
    for code in tqdm(codes, ascii=True, desc='DownTips'):
        if codes.index(code) == int(len(codes) * 2 / 3):
            proxies = proxies_ori
        while True:
            ret = down_tips_worker(code, proxy_ip=p, timeout=2)
            if ret is not None:
                break
            elif len(proxies) > 0:
                p = proxies.pop(0)
                continue
            elif p is None:
                proxy_expire_flag = codes.index(code)
                continue
            else:
                p = None
                continue
        if proxy_expire_flag != -1 and ret is None:
            break
        res.append(ret)
    if len(res) > 0:
        print('{} proxies remaining.'.format(len(proxies)))
        var = list(map(lambda x: x[0], res))
        var = '\n'.join(var)
        with open(CONCEPT_FILE, 'w') as f:
            f.write(var)
        var = list(map(lambda x: x[1], res))
        var = '\n'.join(var)
        with open(ZT_REASON_FILE, 'w') as f:
            f.write(var)
    if proxy_expire_flag != -1:
        log.info('Not all tips downed, updated {}'.format(proxy_expire_flag))


def down_tips_():
    codes = ts.get_stock_basics().index.values.tolist()
    with open(VALID_PROXIES, 'r') as f:
        proxies = f.read().split('\n')
    res = []

    def worker(code, proxies_list, timeout=2):
        pass
    proxies = proxies_ori
    proxy_expire_flag = -1
    p = proxies.pop(0)
    for code in tqdm(codes, ascii=True, desc='DownTips'):
        if codes.index(code) == int(len(codes) * 2 / 3):
            proxies = proxies_ori
        while True:
            ret = down_tips_worker(code, proxy_ip=p, timeout=2)
            if ret is not None:
                break
            elif len(proxies) > 0:
                p = proxies.pop(0)
                continue
            elif p is None:
                proxy_expire_flag = codes.index(code)
                continue
            else:
                p = None
                continue
        if proxy_expire_flag != -1 and ret is None:
            break
        res.append(ret)
    if len(res) > 0:
        var = list(map(lambda x: x[0], res))
        var = '\n'.join(var)
        with open(CONCEPT_FILE, 'w') as f:
            f.write(var)
        var = list(map(lambda x: x[1], res))
        var = '\n'.join(var)
        with open(ZT_REASON_FILE, 'w') as f:
            f.write(var)
    if proxy_expire_flag != -1:
        log.info('Not all tips downed, updated {}'.format(proxy_expire_flag))


def pip_checker(proxy_ip, code, timeout=None):
    html = get_single_html(code, proxy_ip, timeout)
    if html is None or html == '':
        return None
    else:
        return proxy_ip


def check_valid_proxy_ip():
    proxies = get_proxy_ip()
    code = ts.get_stock_basics().index.values.tolist()[0]
    with MultiTasks(64) as mt:
        res = mt.run_list_tasks(pip_checker,
                                var_args=proxies,
                                fix_args={'code': code, 'timeout': 2},
                                en_bar=True, desc='CheckIP')
    valid_proxies = list(filter(None, res))
    print('{} valid IPs.'.format(len(valid_proxies)))
    with open(VALID_PROXIES, 'w') as f:
        f.write('\n'.join(valid_proxies))


if __name__ == '__main__':
    # down_tips_worker('600695')
    down_tips_()
    # check_valid_proxy_ip()
