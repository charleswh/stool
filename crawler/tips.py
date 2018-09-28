import re
import os
import random
import requests
from tqdm import tqdm
from utility.log import log
from utility.timekit import time_str, sleep
from setting.settings import TDX_ROOT, TIP_FOLDER, USER_AGENTS, CONCEPT_FILE
from utility.timekit import print_run_time

TIP_FILE = os.path.join(TIP_FOLDER, '{}.html')
THS_F10_URL = 'http://basic.10jqka.com.cn/{}'

if not os.path.exists(TIP_FOLDER):
    os.mkdir(TIP_FOLDER)


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


def save_tips_worker(item, tip_file):
    file = tip_file.format(item['code'])
    yw = item['business'] if item['business'] is not None else '--'
    tc = ', '.join(item['concept']) if item['concept'] is not None else '--'
    if item['zhangting'] is not None:
        zt = '{}, {}'.format(*item['zhangting'][:2])
        ztyy = item['zhangting'][2] if item['zhangting'][2] is not None else '--'
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
    c = '\n'.join(list(map(lambda x: ','.join((x['code'], ' '.join(x['concept']))), ret_list)))
    with open(CONCEPT_FILE, 'w') as f:
        f.write(c)
    log.info('Make concept list done.')
    # sub_size = int((len(codes) + MAX_TASK_NUM) / MAX_TASK_NUM)
    # sub_item = [results[i:i + sub_size] for i in range(0, len(results), sub_size)]
    # mt.run_list_tasks(func=save_tips_worker, var_args=sub_item, fix_args=TIP_FILE,
    #              en_bar=True, desc='Save-Tips')
    copy_diff_tips()


if __name__ == '__main__':
    down_tips(['002399'])
