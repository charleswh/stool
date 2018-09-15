import tushare as ts
import os
from datakit.data_local import TDX_ROOT
from glob import glob
from utility import *
from analysis import *
from datakit import *
import datetime
import time
from apscheduler.schedulers.background import BackgroundScheduler

FILE_ROOT = os.path.dirname(os.path.realpath(__file__))
TDX_IMPORT_LIST = os.path.join(FILE_ROOT, 'tdx.txt')
MANUAL_LIST = os.path.join(FILE_ROOT, 'manual.txt')


def import_tdx_list():
    blk_dir = os.path.join(TDX_ROOT, 'T0002', 'blocknew')
    blk_files = glob(os.path.join(blk_dir, '*.blk'))
    choose_range = ['Z1ZT.blk', 'Z2ZT.blk', 'Z3ZT.blk', 'Z4ZT.blk', 'Z5ZT.blk',
                    'TEMPTTA6030.blk', 'TEMPTTA120DAY.blk', 'BBB.blk', 'ZZB.blk']
    var_list = []
    for file in blk_files:
        if os.path.split(file)[-1] not in choose_range:
            continue
        else:
            with open(file, 'r') as f:
                c = f.read().split('\n')
            c = list(map(lambda x: x[1:], c))
        var_list.extend(c)
    var_list = list(filter(None, var_list))
    var_list = list(set(var_list))
    with open(TDX_IMPORT_LIST, 'w') as f:
        f.write('\n'.join(var_list))
    log.info('Successfully import tdx list')


def get_manual_list() -> list:
    with open(MANUAL_LIST, 'r') as f:
        content = f.read()
    return content.split('\n')


def simple_cal_one(code, ktype='D'):
    print('process code {}'.format(code))
    data = ts.get_k_data(code=code, ktype=ktype)
    c = data['close'].sort_index(ascending=False)
    ma24 = c.rolling(window=24).mean().dropna(axis=0).apply(percision, **{'p': 2}).values
    ma24_cur = ma24[0]
    c_cur = c.values[0]
    up_th = 1.5 * 0.01
    down_th = 0.8 * 0.01
    if ma24_cur * (1 - down_th) < c_cur < ma24_cur * (1 + up_th):
        return 1
    else:
        return 0


def simple_ts24_monitor():
    with open(TDX_IMPORT_LIST, 'r') as f:
        code_list = f.read().split('\n')[:10]

    k_types = ['D', '60', '30']

    res = [list(map(simple_cal_one, [code] * 3, k_types)) for code in code_list]
    res = list(map(lambda x:int(''.join(list(map(str, x))), 2), res))
    res = dict(zip(code_list, res))
    print(res)
    return res


def check_trade_time() -> bool:
    trade_date = read_trade_date()
    cur_date = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d')
    if cur_date not in trade_date:
        return False
    else:
        cur_time = datetime.datetime.strftime(datetime.datetime.now(), '%H:%M:%S')
        if ('11:30:00' > cur_time > '9:30:00') or \
                ('15:00:00' > cur_time > '13:00:00'):
            return True
        else:
            return False


def my_job():
    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))


def monitor_main():
    aa = check_trade_time()
    mode = {'apscheduler.executors.processpool':
                {'type': 'processpool', 'max_workers': '2'}}
    scheduler = BackgroundScheduler(mode)
    scheduler.add_job(my_job, 'cron', second='*/5')
    scheduler.add_job(my_job, 'cron', second='*/3')
    scheduler.start()

    print('Press ctrl+{} to exit monitor.'.format('Break' if os.name == 'nt' else 'C'))
    try:
        while True:
            sleep(1)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()


if __name__ == '__main__':
    #simple_cal_one('300106', ktype='30')
    # simple_ts24_monitor()
    monitor_main()
