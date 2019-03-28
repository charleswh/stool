import re
import os
import time
import numpy as np
import crawler.req_interface as req_i
from utility.log import log
from utility.task import MultiTasks
from utility.misc import rm_dupl
from setting.settings import sets

IP_TEST_WEB = 'http://2019.ip138.com/ic.asp'
g_host_ip = None

"""
Proxy ip source web valid precent:
xiaohuan: 158/348/607 26%
lingdu: 116/425/1430 8+%
ip3366: 8%
ip66: 5%
kuai: 1%
"""
def raw_ip_parse():
    if not os.path.exists(sets.RAW_IP_FILE):
        log.error('Must manual make and prepare {} for proxy ip parsing job.'.format(sets.RAW_IP_FILE))
        exit(0)

    f = open(sets.RAW_IP_FILE, 'r')
    content = f.read()
    f.close()
    ip_list = []
    pat0 = re.compile(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s+(\d{1,5}).*?', re.S)
    pat1 = re.compile(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s*:\s*(\d{1,5}).*?', re.S)
    ip_list.extend(pat0.findall(content))
    ip_list.extend(pat1.findall(content))
    ip_list = rm_dupl(ip_list)
    log.info('Raw ips: {}'.format(len(ip_list)))
    return ip_list


def check_ip_valid(ip, port, timeout=1):
    global g_host_ip
    timeout = int(timeout)
    whole_ip = {'http': ':'.join((ip, port))}
    try:
        start = time.clock()
        req = req_i.web_req(IP_TEST_WEB, proxy=whole_ip, timeout=timeout)
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


def check_ip_batch(ip_list: list, mt=None, timeout=1, drop=True):
    if mt is not None:
        ret_ips = mt.run_list_tasks(func=check_ip_valid, var_args=ip_list,
                                    fix_args={'timeout': sets.PROXY_TIMEOUT},
                                    en_bar=1, desc='CheckRawIPs')
        res = np.c_[np.array(ip_list), np.array(ret_ips)].tolist()
    else:
        res = []
        for ip in ip_list:
            print('Checking IP: {}:{}'.format(*ip))
            res.append([*ip, check_ip_valid(*ip, timeout)])
    res0 = list(filter(lambda x: x[2] is not None, res))
    log.info('{} valid raw IPs.'.format(len(res0)))
    if drop:
        return res0
    else:
        return res


def connectable_ips():
    if not os.path.exists(sets.CONNECTABLE_IP):
        return None
    else:
        with open(sets.CONNECTABLE_IP, 'r') as f:
            ret = f.read().split('\n')
            ret = list(map(lambda x: x.split(':'), ret))
            ret = list(map(lambda x: '{}:{}'.format(x[0], x[1]), ret))
        return ret


def connectable_ip():
    global g_host_ip
    req = req_i.web_req(IP_TEST_WEB)
    req.encoding = 'gbk'
    g_host_ip = re.search('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', req.text).group()

    raw_ips = raw_ip_parse()

    with MultiTasks(32) as mt:
        valid_ips = check_ip_batch(raw_ips, mt)

    valid_ips.sort(key=lambda x: int(x[2]))

    with open(sets.CONNECTABLE_IP, 'w') as f:
        f.write('\n'.join(list(map(lambda x: ':'.join(x), valid_ips))))


def refresh_ip_lib():
    with open(sets.PROXY_IP_LIB, 'r') as f:
        ips = f.read().split('\n')

    ips = list(map(lambda x: x.split(':'), ips))

    with MultiTasks(16) as mt:
        ips = check_ip_batch(ips, mt, False)

    ips.sort(key=lambda x: int(x[2] if x[2] is not None else x[1]))

    if os.path.exists(sets.PROXY_IP_LIB_BACKUP):
        os.remove(sets.PROXY_IP_LIB_BACKUP)

    os.rename(sets.PROXY_IP_LIB, sets.PROXY_IP_LIB_BACKUP)
    with open(sets.PROXY_IP_LIB, 'w') as f:
        f.write('\n'.join(list(map(lambda x: ':'.join(x[:2]), ips))))


if __name__ == '__main__':
    #refresh_ip_lib()
    connectable_ip()
