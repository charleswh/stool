# -*- coding:utf-8 -*-
import calculation as cal
import tushare as ts
from miscs import *
import pandas as pd
import os
import multiprocessing as mp
import ctypes

KTYPE = ['D', '60', '30', '15', '5']
KSUB = {'D': 'day', '60': 'M60', '30': 'M30', '15': 'M15', '5': 'M5'}
DATESTAMP_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data.datestamp')
INFO_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'info.csv')
TRADE_DATE_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'trade_date.csv')
INFO_TOTAL_COL = ['name', 'industry', 'area', 'pe', 'outstanding', 'totals',
                  'totalAssets', 'liquidAssets', 'fixedAssets', 'reserved',
                  'reservedPerShare', 'esp', 'bvps', 'pb', 'timeToMarket', 'undp',
                  'perundp', 'rev', 'profit', 'gpr', 'npr', 'holders']


@print_run_time
def get_trade_date(start_year=None):
    if not os.path.exists(TRADE_DATE_FILE):
        df = ts.trade_cal()
        df = df[df['isOpen'] == 1]
        df.to_csv(TRADE_DATE_FILE, encoding='utf-8-sig')
    else:
        df = pd.read_csv(TRADE_DATE_FILE)
    if start_year is not None:
        df = df[df['calenderDate'].str.find(start_year) == 0]
    return df


def check_subdirs():
    for i in KSUB.values():
        sub = os.path.join(os.path.dirname(os.path.realpath(__file__)), i)
        if not os.path.exists(sub):
            os.mkdir(sub)


def down_info_data(update=False):
    basic_infos = None
    if update is True:
        keep_cols = ['name', 'outstanding', 'timeToMarket']
        with TimerCount('Get info data...'):
            basic_infos = ts.get_stock_basics()
        useless_cols = list(set(basic_infos.columns).difference(set(keep_cols)))
        # remove useless columns
        basic_infos = basic_infos.drop(columns=useless_cols)
        # remove ST stocks
        basic_infos = basic_infos[basic_infos['name'].str.find('*') == -1]
        # remove unlisted new shares
        basic_infos = basic_infos[basic_infos['timeToMarket'] != 0]
    else:
        if os.path.exists(INFO_FILE):
            basic_infos = pd.read_csv(INFO_FILE)
        else:
            log.error('No info file <{}>!'.format(INFO_FILE))
    return basic_infos


def save_local_data(df, code, ktype):
    if not isinstance(df, pd.DataFrame):
        return False
    elif df.empty:
        return False
    root = os.path.dirname(os.path.realpath(__file__))
    sub = os.path.join(root, KSUB[ktype])
    file = os.path.join(sub, '{}.csv'.format(code))
    cols = ['date', 'open', 'close', 'high', 'low', 'volume']
    df = df.sort_index(ascending=False)
    df.to_csv(file, columns=cols, index=False)


def update_bar(counter, finish_flag, multi_count, bar_max):
    import tqdm
    print('Start downloading basic data...')
    with tqdm.tqdm(total=bar_max, ascii=True) as tbar:
        while counter.value <= bar_max:
            tbar.update(counter.value - tbar.n)
            if finish_flag and len(finish_flag) == multi_count:
                tbar.update(bar_max - tbar.n)
                break
    print('Done')


def download(para):
    codes, counter, finish, lock = para
    ret = {}
    for code in codes:
        try:
            datas = list(map(ts.get_k_data, [code] * 5, [''] * 5, [''] * 5, KTYPE))
        except Exception as err:
            log.err('Download {} fail.'.format(code))
            log.error(err)
        list(map(save_local_data, datas, [code] * 5, KTYPE))

        with lock:
            counter.value += 1
    finish[os.getpid()] = True
    return ret


def down_basic_data(codes):
    progress_total = mp.cpu_count() * 4
    progress_for_job = progress_total - 1
    unitsize = int((len(codes) + progress_for_job) / progress_for_job)
    codes_cut = [codes[i:i + unitsize] for i in range(0, len(codes), unitsize)]
    with TimerCount('Prepare multiprocess pool'):
        pool = mp.Pool(progress_total)
        m = mp.Manager()
        lock = m.Lock()
        counter = m.Value(ctypes.c_uint32, 0)
        finish_flag = m.dict()
        args = [(x, counter, finish_flag, lock) for x in codes_cut]
    pool.apply_async(update_bar, args=(counter, finish_flag, progress_for_job, len(codes)))
    pool.map(download, args)
    pool.close()
    pool.join()


def get_more_infos(info):
    from tqdm import tqdm
    info = info.reset_index()
    lastest_trade_date = get_local_data(info.iloc[0]['code'], 'D', 'date', 1).iloc[0]
    tqdm.pandas(desc='Get ZT', ascii=True)
    zt = info['code'].progress_apply(cal.ZT, args=[lastest_trade_date]).rename('zt')
    tqdm.pandas(desc='Get ZB', ascii=True)
    zb = info['code'].progress_apply(cal.ZB).rename('zb')
    # bb = pd.concat([info, zt, zb], axis=1)
    # bb.to_csv('aa.csv', encoding='utf-8-sig')
    # a=0


@print_run_time
def update_local_database(update_infos=True):
    check_subdirs()
    info_data = down_info_data(update_infos)
    # down_basic_data(sorted(info_data.index))
    get_more_infos(info_data)


def get_local_data(code, ktype, item, count=None, date=None):
    root = os.path.dirname(os.path.realpath(__file__))
    sub = os.path.join(root, KSUB[ktype])
    file = os.path.join(sub, '{}.csv'.format(code))
    if not os.path.exists(file):
        log.error('No local data file: {}!'.format(file))
        assert 0
    if date is None:
        df = pd.read_csv(file, nrows=count)
    else:
        df = pd.read_csv(file)
        df = df[df['date'] <= date].iloc[:count, :]
    return df.loc[:, item]


def get_local_info(code, item):
    info_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), INFO_FILE)
    if not os.path.exists(info_file):
        log.error('No local info file: {}!'.format(info_file))
    infos = pd.read_csv(info_file, dtype={'code': str}).set_index('code')
    return infos.loc[code, item]


def get_codes():
    info_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), INFO_FILE)
    if not os.path.exists(info_file):
        log.error('No local info file: {}!'.format(info_file))
    return pd.read_csv(info_file, dtype={'code': str}).loc[:, 'code']


if __name__ == '__main__':
    with TimerCount('Test of Download all:'):
        update_local_database()
