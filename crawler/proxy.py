import requests
import random
import re
from crawler.tips import USER_AGENTS


IP_TEST_WEB = 'http://2018.ip138.com/ic.asp'

def get_random_header():
    headers={'User-Agent':random.choice(USER_AGENTS),
             'Accept':"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",'Accept-Encoding':'gzip'}
    return headers


def get_proxies():
    pass


def get_proxies_from_xici():
    xici_url = 'http://www.xicidaili.com/nt/'
    raw_ip = []
    vaild_ip = []
    req = requests.get(IP_TEST_WEB)
    req.encoding = 'gbk'
    host_ip = re.search('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', req.text)
    host_ip = host_ip.group()
    print('Scraw page {}'.format(1))
    url = xici_url + str(1)
    req = requests.get(url, headers=get_random_header())
    req.encoding = 'utf-8'
    pat = re.compile('<td class="country">.*?alt="Cn" />.*?</td>.*?<td>(.*?)</td>.*?<td>(.*?)</td>', re.S)
    raw_ip = pat.findall(req.text)
    for ip in raw_ip[:30]:
        if is_ip_valid(*ip, host=host_ip) is True:
            vaild_ip.append(ip)
        else:
            pass
    with open('proxy_ips.txt', 'w') as f:
        f.write('\n'.join(list(map(lambda x: ':'.join(x), vaild_ip))))


def is_ip_valid(ip, port, host, timeout=10):
    whole_ip = {'http': ':'.join((ip, port))}
    try:
        req = requests.get(IP_TEST_WEB, get_random_header(), proxies=whole_ip, timeout=timeout)
        if req.status_code == 200:
            req.encoding = 'gbk'
            result = re.search('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', req.text)
            result = result.group()
            if result == ip or result != host:
                print('Proxy ip is valid: in -> {}:{}, get -> {}'.format(ip, port, result))
                return True
            elif host is None or result == host:
                    print('Proxy ip is invalid: in -> {}, get -> {}.'.format(ip, result))
                    return False
            else:
                assert 0


    except Exception as err:
        if 'timeout' in str(err):
            print('{} timeout of {}'.format(ip, timeout))
        else:
            print('IP check fail: {}'.format(err))
        return False


if __name__ == '__main__':
    #-get_proxies_from_xici()
    host = '221.223.183.198'
    ip = '120.52.73.173'
    port = '8080'
    is_ip_valid(ip, port, host=host)
    whole_ip = {'http': ':'.join((ip, port))}
    req = requests.get('http://basic.10jqka.com.cn/000760', headers=get_random_header(),
                       proxies=whole_ip, timeout=10)
    aa = 0
