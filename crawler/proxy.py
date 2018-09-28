import requests
import random
import re
import os
import time
import pandas as pd
import numpy as np
from utility.log import log
from setting.settings import USER_AGENTS, PROXY_LIST, PROXY_BAK, MAX_TASK_NUM
from utility.task import MultiTasks

IP_TEST_WEB = 'http://2018.ip138.com/ic.asp'
g_host_ip = None


def get_random_header():
    headers = {'User-Agent': random.choice(USER_AGENTS),
               'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
               'Accept-Encoding': 'gzip'}
    return headers


def check_ip_valid(ip, port, timeout=1):
    global g_host_ip
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
    if mt is not None:
        ret_ips = mt.run_list_tasks(func=check_ip_valid, var_args=ip_list, en_bar=True)
        res = np.c_[np.array(ip_list), np.array(ret_ips)].tolist()
        res = list(filter(lambda x: x[2] is not None, res))
        return res
    else:
        pass


def xici(mt=None):
    xici_url = 'http://www.xicidaili.com/nt/'
    print('Scraw page {}'.format(1))
    url = xici_url + str(1)
    req = requests.get(url, headers=get_random_header())
    req.encoding = 'utf-8'
    pat = re.compile('<td class="country">.*?alt="Cn" />.*?</td>.*?<td>(.*?)</td>.*?<td>(.*?)</td>',
                     re.S)
    raw_ips = pat.findall(req.text)
    valid_ip = check_ip_batch(raw_ips, mt)
    log.info('Got {} valid IPs from <xici>'.format(len(valid_ip)))
    return valid_ip


def ip3366(mt=None):
    ip3366_url = 'http://www.ip3366.net/free/'
    valid_ip = []
    for style in range(1, 4):
        url = ip3366_url + '?stype={}'.format(style)
        for page in range(1, 3):
            url = url + '&page={}'.format(page)
            req = requests.get(url, headers=get_random_header())
            req.encoding = 'gb2312'
            pat = re.compile('<tr>.*?<td>(.*?)</td>.*?<td>(.*?)</td>', re.S)
            raw_ips = pat.findall(req.text)
            valid_ip.extend(check_ip_batch(raw_ips, mt))
    log.info('Got {} valid IPs from <ip3366>'.format(len(valid_ip)))
    return valid_ip


def data5u(mt=None):
    base_url = r'http://www.data5u.com/free/{}/index.shtml'
    valid_ip = []
    for sub in ('gngn', 'gnpt'):
        url = base_url.format(sub)
        req = requests.get(url, headers=get_random_header())
        req.encoding = 'utf-8'
        pat = re.compile(r'<ul class="l2">.*?<li>(.*?)</li>.*?<li class="port .*?">(.*?)</li>',
                         re.S)
        raw_ips = pat.findall(req.text)
        valid_ip.extend(check_ip_batch(raw_ips, mt))
    log.info('Got {} valid IPs from <data5u>'.format(len(valid_ip)))
    return valid_ip


def kuai(mt=None):
    base_url = 'https://www.kuaidaili.com/free/{}/'
    valid_ip = []
    for sub in ('inha', 'intr'):
        s_url = base_url.format(sub) + '{}/'
        for page in range(1, 3):
            url = s_url.format(page)
            req = requests.get(url, headers=get_random_header())
            req.encoding = 'utf-8'
            pat = re.compile('<td data-title="IP">(.*?)</td>.*?<td data-title="PORT">(.*?)</td>',
                             re.S)
            raw_ips = pat.findall(req.text)
            valid_ip.extend(check_ip_batch(raw_ips, mt))
    log.info('Got {} valid IPs from <kuai>'.format(len(valid_ip)))
    return valid_ip


def xiaohuan(mt=None):
    date = time.strftime('%Y/%m/%d', time.localtime())
    hour = time.strftime('%H', time.localtime())
    base_url = 'https://ip.ihuan.me/today/{}/{}.html'
    url = base_url.format(date, hour)
    req = requests.get(url, headers=get_random_header())
    req.encoding = 'utf-8'
    pat = re.compile('(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d{1,5}).*?', re.S)
    raw_ips = pat.findall(req.text)
    if len(raw_ips) == 0:
        url = base_url.format(date, int(hour) - 1)
        req = requests.get(url, headers=get_random_header())
        req.encoding = 'utf-8'
        raw_ips = pat.findall(req.text)
    valid_ip = check_ip_batch(raw_ips, mt)
    log.info('Got {} valid IPs from <xiaohuan>'.format(len(valid_ip)))
    return valid_ip


def get_proxy_ip():
    global g_host_ip
    req = requests.get(IP_TEST_WEB)
    req.encoding = 'gbk'
    g_host_ip = re.search('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', req.text)
    g_host_ip = g_host_ip.group()
    # start
    # ip = [*xici(), *ip3366()]
    # ip = [*ip3366()]
    # ip = data5u()
    # ip = kuai()
    ip = []
    mt = MultiTasks()
    ip = xiaohuan(mt)
    if os.path.exists(PROXY_LIST):
        with open(PROXY_LIST, 'r') as f:
            ip_pre_list = f.read().split('\n')
            ip_pre_list = list(map(lambda x: x.split(',')[:2], ip_pre_list))
            ip.extend(check_ip_batch(ip_pre_list, mt))
    ip.sort(key=lambda x: int(x[2]))
    df = pd.DataFrame(ip, columns=['ip', 'port', 'cost'])
    df = df.drop_duplicates(['ip', 'port'], 'first')
    ip = df.values.tolist()
    with open(PROXY_LIST, 'w') as f:
        f.write('\n'.join(list(map(lambda x: ','.join(x), ip))))


if __name__ == '__main__':
    get_proxy_ip()
