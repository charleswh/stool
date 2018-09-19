import requests
import random
import re
import time
from crawler.tips import USER_AGENTS


IP_TEST_WEB = 'http://2018.ip138.com/ic.asp'
g_host_ip = None


def get_random_header():
    headers={'User-Agent':random.choice(USER_AGENTS),
             'Accept':"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",'Accept-Encoding':'gzip'}
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
                print('{}:{}, VALID'.format(ip, port))
                return str(cost)
            else:
                print('{}:{}, INVALID'.format(ip, port))
                return None
    except Exception as err:
        if 'timeout' in str(err):
            print('{} timeout of {}'.format(ip, timeout))
        else:
            print('IP check fail: {}'.format(err))
        return None


def xici():
    xici_url = 'http://www.xicidaili.com/nt/'
    valid_ip = []
    print('Scraw page {}'.format(1))
    url = xici_url + str(1)
    req = requests.get(url, headers=get_random_header())
    req.encoding = 'utf-8'
    pat = re.compile('<td class="country">.*?alt="Cn" />.*?</td>.*?<td>(.*?)</td>.*?<td>(.*?)</td>', re.S)
    raw_ip = pat.findall(req.text)
    for ip in raw_ip:
        cost = check_ip_valid(*ip)
        if cost is not None:
            valid_ip.append([*ip, cost])
        else:
            pass
    return valid_ip


def ip3366():
    ip3366_url = 'http://www.ip3366.net/free/'
    url = None
    valid_ip = []
    for style in range(1, 4):
        url = ip3366_url+'?stype={}'.format(style)
        for page in range(1, 3):
            url = url + '&page={}'.format(page)
            req = requests.get(url, headers=get_random_header())
            req.encoding = 'gb2312'
            pat = re.compile('<tr>.*?<td>(.*?)</td>.*?<td>(.*?)</td>', re.S)
            raw_ip = pat.findall(req.text)
            for ip in raw_ip:
                cost = check_ip_valid(*ip)
                if cost is not None:
                    valid_ip.append([*ip, cost])
                else:
                    pass
    return valid_ip


def half_hour_update():
    url = 'http://7xrnwq.com1.z0.glb.clouddn.com/proxy_list.txt'
    valid_ip = []
    req = requests.get(url, headers=get_random_header())
    req.encoding = 'utf-8'
    raw_list = list(filter(None, req.text.split('\n')))
    for ip in raw_list:
        cost = check_ip_valid(*ip.split(':'))
        if cost is not None:
            valid_ip.append([*ip.split(':'), cost])
        else:
            pass
    return valid_ip


def get_proxy_ip():
    global g_host_ip
    req = requests.get(IP_TEST_WEB)
    req.encoding = 'gbk'
    g_host_ip = re.search('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', req.text)
    g_host_ip = g_host_ip.group()
    # start
    # ip = xici()
    # ip = ip3366()
    ip = half_hour_update()
    with open('proxy_ips.txt', 'a+') as f:
        f.write('\n'.join(list(map(lambda x: ','.join(x), ip))))


if __name__ == '__main__':
    get_proxy_ip()

