import requests
import random
import re
import os
import time
import pandas as pd
import numpy as np
import base64
import hashlib
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from utility.log import log
from utility.task import MultiTasks
from utility.timekit import sleep
from setting.settings import USER_AGENTS, PROXY_LIST, MAX_TASK_NUM, CHROME_EXE

IP_TEST_WEB = 'http://2018.ip138.com/ic.asp'
g_host_ip = None


def get_random_header():
    headers = {'User-Agent': random.choice(USER_AGENTS),
               'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
               'Accept-Encoding': 'gzip'}
    return headers


def html_by_chrome(url):
    opt = Options()
    opt.add_argument('--headless')
    brower = webdriver.Chrome(CHROME_EXE, options=opt)
    brower.get(url)
    return brower.page_source


def check_ip_valid(ip, port, timeout=1):
    global g_host_ip
    timeout = int(timeout)
    whole_ip = {'http': ':'.join((ip, port))}
    try:
        start = time.clock()
        req = requests.get(IP_TEST_WEB, get_random_header(), proxies=whole_ip, timeout=timeout)
        end = time.clock()
        cost = int((end - start) * 1000)
        if req.status_code == 200:
            req.encoding = 'gbk'
            result = re.search('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', req.text)
            result = result.group()
            if result == ip or result != g_host_ip:
                # print('{}:{}, VALID'.format(ip, port))
                return str(cost)
            else:
                # print('{}:{}, INVALID'.format(ip, port))
                return None
    except Exception as err:
        # if 'timeout' in str(err):
        #     print('{} timeout of {}'.format(ip, timeout))
        # else:
        #     print('IP check fail: {}'.format(err))
        return None


def check_ip_batch(ip_list: list, mt=None, timeout=1):
    from setting.settings import PROXY_TIMEOUT
    if mt is not None:
        ret_ips = mt.run_list_tasks(func=check_ip_valid, var_args=ip_list,
                                    fix_args={'timeout': PROXY_TIMEOUT},
                                    en_bar=1, desc='CheckRawIPs')
        res = np.c_[np.array(ip_list), np.array(ret_ips)].tolist()
    else:
        res = []
        for ip in ip_list:
            print('Checking IP: {}:{}'.format(*ip))
            res.append([*ip, check_ip_valid(*ip, timeout)])
    res = list(filter(lambda x: x[2] is not None, res))
    log.info('{} valid raw IPs.'.format(len(res)))
    return res


# 0.5%
def xici():
    url_base = 'http://www.xicidaili.com/{}/'
    raw_ips = []
    for sub in ('nn', 'nt', 'wn', 'wt'):
        sub_url = url_base.format(sub) + '/{}'
        for page in range(1, 4):
            url = sub_url.format(page)
            req = requests.get(url, headers=get_random_header())
            req.encoding = 'utf-8'
            pat = re.compile(
                '<td class="country">.*?alt="Cn" />.*?</td>.*?<td>(.*?)</td>.*?<td>(.*?)</td>', re.S)
            raw_ips.extend(pat.findall(req.text))
    log.info('Got {} raw IPs from <xici>'.format(len(raw_ips)))
    return raw_ips


# 8%
def ip3366():
    ip3366_url = 'http://www.ip3366.net/free/'
    raw_ips = []
    for style in range(1, 5):
        url = ip3366_url + '?stype={}'.format(style)
        for page in range(1, 8):
            url = url + '&page={}'.format(page)
            req = requests.get(url, headers=get_random_header())
            req.encoding = 'gb2312'
            pat = re.compile('<tr>.*?<td>(.*?)</td>.*?<td>(.*?)</td>', re.S)
            raw_ips.extend(pat.findall(req.text))
            sleep(1)
        sleep(3)
    log.info('Got {} raw IPs from <ip3366>'.format(len(raw_ips)))
    return raw_ips


# 0.01%
def data5u():
    base_url = r'http://www.data5u.com/free/{}/index.shtml'
    raw_ips = []
    for sub in ('gngn', 'gnpt', 'gwgn', 'gwpt'):
        url = base_url.format(sub)
        req = requests.get(url, headers=get_random_header())
        req.encoding = 'utf-8'
        pat = re.compile(r'<ul class="l2">.*?<li>(.*?)</li>.*?<li class="port .*?">(.*?)</li>', re.S)
        raw_ips.extend(pat.findall(req.text))
    log.info('Got {} raw IPs from <data5u>'.format(len(raw_ips)))
    return raw_ips


# 1%
def kuai(proxies=None):
    base_url = 'https://www.kuaidaili.com/free/{}/'
    raw_ips = []
    proxy = proxies.pop() if proxies is not None else None
    for sub in ('inha', 'intr'):
        s_url = base_url.format(sub) + '{}/'
        for page in range(1, 11):
            url = s_url.format(page)
            while True:
                p_ip = {'http': 'http://{}'.format(proxy),
                        'https': 'https://{}'.format(proxy)} if proxy is not None else None
                try:
                    req = requests.get(url, proxies=p_ip, headers=get_random_header(), timeout=0.8)
                except Exception as err:
                    proxy = proxies.pop() if proxies is not None and len(proxies) > 0 else None
                    continue
                req.encoding = 'utf-8'
                if req.text[:3] != '-10':
                    break
            pat = re.compile('<td data-title="IP">(.*?)</td>.*?<td data-title="PORT">(.*?)</td>', re.S)
            raw_ips.extend(pat.findall(req.text))
    log.info('Got {} raw IPs from <kuai>'.format(len(raw_ips)))
    return raw_ips


# 5%
def ip66():
    base_url = 'http://www.66ip.cn/areaindex_{}/1.html'
    raw_ips = []
    for sub in range(1, 35):
        url = base_url.format(sub)
        req = requests.get(url, headers=get_random_header())
        h = html_by_chrome(url)
        if req.status_code == 521:
            continue
        req.encoding = 'gb2312'
        pat = re.compile(r'<tr><td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td><td>(\d{1,5})</td>', re.S)
        raw_ips.extend(pat.findall(req.text))

    e_base = 'http://www.66ip.cn/nmtq.php?getnum=50&isp=0&anonymoustype=3&start=&ports=&export=' \
             '&ipaddress=&area=1&proxytype=2&api=66ip'
    for _ in range(5):
        req = requests.get(e_base, headers=get_random_header())
        req.encoding = 'gbk'
        pat = re.compile(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d{1,5})')
        raw_ips.extend(pat.findall(req.text))
        sleep(2)
    log.info('Got {} raw IPs from <ip66>'.format(len(raw_ips)))
    return raw_ips


# 40+%
def xiaohuan():
    date = time.strftime('%Y/%m/%d', time.localtime())
    hour = time.strftime('%H', time.localtime())
    base_url = 'https://ip.ihuan.me/today/{}/{:02d}.html'
    url = base_url.format(date, int(hour))
    req = requests.get(url, headers=get_random_header())
    req.encoding = 'utf-8'
    pat = re.compile('(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d{1,5}).*?', re.S)
    raw_ips = pat.findall(req.text)
    if len(raw_ips) == 0:
        url = base_url.format(date, int(hour) - 1)
        req = requests.get(url, headers=get_random_header())
        req.encoding = 'utf-8'
        raw_ips = pat.findall(req.text)
    log.info('Got {} raw IPs from <xiaohuan>'.format(len(raw_ips)))
    return raw_ips


# 10+%
def lingdu():
    base_url = 'https://www.nyloner.cn/proxy'
    retry_count = 0
    raw_ips = []
    opt = Options()
    opt.add_argument('--headless')
    brower = webdriver.Chrome(CHROME_EXE, options=opt)
    brower.get(base_url)
    pat = re.compile(r'<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>.*?<td>(\d{1,5})</td>', re.S)
    while True:
        html = brower.page_source
        ips = pat.findall(html)
        if len(ips) == 0:
            retry_count += 1
            if retry_count == 3:
                break
            continue
        raw_ips.extend(ips)
        try:
            brower.find_element_by_id('next-page').click()
        except Exception as err:
            break
    log.info('Got {} raw IPs from <lingdu>'.format(len(raw_ips)))
    return raw_ips


def get_proxy_ip():
    if not os.path.exists(PROXY_LIST):
        return None
    else:
        with open(PROXY_LIST, 'r') as f:
            ret = f.read().split('\n')
            ret = list(map(lambda x: x.split(','), ret))
            ret = list(map(lambda x: '{}:{}'.format(x[0], x[1]), ret))
        return ret


def down_proxy_ip():
    global g_host_ip
    req = requests.get(IP_TEST_WEB)
    req.encoding = 'gbk'
    g_host_ip = re.search('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', req.text).group()
    raw_ips = []
    try:
        raw_ips.extend(xiaohuan())
    except Exception as err:
        print(err)
    # try:
    #     raw_ips.extend(ip66())
    # except Exception as err:
    #     print(err)
    try:
        raw_ips.extend(kuai(get_proxy_ip()))
    except Exception as err:
        print(err)
    try:
        raw_ips.extend(ip3366())
    except Exception as err:
        print(err)
    try:
        raw_ips.extend(xici())
    except Exception as err:
        print(err)
    try:
        raw_ips.extend(data5u())
    except Exception as err:
        print(err)

    if os.path.exists(PROXY_LIST):
        with open(PROXY_LIST, 'r') as f:
            ip_pre_list = f.read().split('\n')
            raw_ips.extend(list(map(lambda x: x.split(',')[:2], ip_pre_list)))

    df = pd.DataFrame(raw_ips, columns=['ip', 'port'])
    raw_ips = df.drop_duplicates(['ip', 'port'], 'first').values.tolist()

    with MultiTasks(32) as mt:
        valid_ips = check_ip_batch(raw_ips, mt)

    valid_ips.sort(key=lambda x: int(x[2]))
    with open(PROXY_LIST, 'w') as f:
        f.write('\n'.join(list(map(lambda x: ','.join(x), valid_ips))))


if __name__ == '__main__':
    ip66()
    down_proxy_ip()
