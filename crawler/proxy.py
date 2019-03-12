import re
import os
import time
import pandas as pd
import numpy as np
import base64
import hashlib
import crawler.req_interface as req_i
from utility.log import log
from utility.task import MultiTasks
from utility.timekit import sleep
from setting.settings import sets

IP_TEST_WEB = 'http://2019.ip138.com/ic.asp'
g_host_ip = None


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


def check_ip_batch(ip_list: list, mt=None, timeout=1):
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
    res = list(filter(lambda x: x[2] is not None, res))
    log.info('{} valid raw IPs.'.format(len(res)))
    return res


def get_local_proxy_ip():
    if not os.path.exists(sets.PROXY_LIST):
        return None
    else:
        with open(sets.PROXY_LIST, 'r') as f:
            ret = f.read().split('\n')
            ret = list(map(lambda x: x.split(','), ret))
            ret = list(map(lambda x: '{}:{}'.format(x[0], x[1]), ret))
        return ret


def down_proxy_ip():
    global g_host_ip
    req = req_i.web_req(IP_TEST_WEB)
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
        raw_ips.extend(kuai(get_local_proxy_ip()))
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

    if os.path.exists(sets.PROXY_LIST):
        with open(sets.PROXY_LIST, 'r') as f:
            ip_pre_list = f.read().split('\n')
            raw_ips.extend(list(map(lambda x: x.split(',')[:2], ip_pre_list)))

    df = pd.DataFrame(raw_ips, columns=['ip', 'port'])
    raw_ips = df.drop_duplicates(['ip', 'port'], 'first').values.tolist()

    with MultiTasks(32) as mt:
        valid_ips = check_ip_batch(raw_ips, mt)

    valid_ips.sort(key=lambda x: int(x[2]))
    with open(sets.PROXY_LIST, 'w') as f:
        f.write('\n'.join(list(map(lambda x: ','.join(x), valid_ips))))


if __name__ == '__main__':
    xiaohuan()
    lingdu()
    b = 0

    ip66()
    down_proxy_ip()
