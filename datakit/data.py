# -*- coding:utf-8 -*-
import calculation as cal
import tushare as ts
from miscs import *
import pandas as pd
import numpy as np
import os
import multiprocessing as mp
import ctypes
from functools import reduce
from tqdm import tqdm

KTYPE = ['D', '60', '30', '15', '5']
KSUB = {'D': 'day', '60': 'M60', '30': 'M30', '15': 'M15', '5': 'M5'}
AA = ['day', 'M60', 'M30', 'M15', 'M5']
# PERIORD_TAG = {'D': 'day', '60': 'min60', '30': 'min30', '15': 'min15', '5': 'min5'}
FILE_ROOT = os.path.dirname(os.path.realpath(__file__))
CSV_SUB = os.path.join(FILE_ROOT, 'data_csv')
PERIORD_TAG = ['day', 'min60', 'min30', 'min15', 'min5']
DATESTAMP_FILE = os.path.join(FILE_ROOT, 'data.datestamp')
INFO_FILE = os.path.join(FILE_ROOT, 'info.csv')
TRADE_DATE_FILE = os.path.join(FILE_ROOT, 'trade_date.csv')
INFO_TOTAL_COL = ['name', 'industry', 'area', 'pe', 'outstanding', 'totals',
                  'totalAssets', 'liquidAssets', 'fixedAssets', 'reserved',
                  'reservedPerShare', 'esp', 'bvps', 'pb', 'timeToMarket', 'undp',
                  'perundp', 'rev', 'profit', 'gpr', 'npr', 'holders']
HDF_FILE = os.path.join(FILE_ROOT, 'database.h5')


def get_local_data(code, ktype, item, pos=0, count=None):
    file = os.path.join(CSV_SUB, '{}_{}.csv'.format(KSUB[ktype], code))
    if not os.path.exists(file):
        log.error('No local data file: {}!'.format(file))
        assert 0
    df = pd.read_csv(file, nrows=(count - pos) if count is not None else count, usecols=[item])
    if pos != 0:
        df.drop([abs(pos) - 1], inplace=True)
    if df.shape[0] < count:
        df = pd.concat([df, pd.DataFrame(np.zeros((count - df.shape[0], df.shape[1])),
                                         columns=df.columns)])
    return df


def get_local_info(code, item):
    if not os.path.exists(INFO_FILE):
        log.error('No local info file: {}!'.format(INFO_FILE))
    infos = pd.read_csv(INFO_FILE, usecols=[item], columns={'code': str}).set_index('code')
    return infos.loc[code, item]


def get_codes():
    info_file = os.path.join(FILE_ROOT, INFO_FILE)
    if not os.path.exists(info_file):
        log.error('No local info file: {}!'.format(info_file))
    return pd.read_csv(info_file, dtype={'code': str}).loc[:, 'code']


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


@print_run_time
def down_trade_data(start_year=None):
    if not os.path.exists(TRADE_DATE_FILE):
        df = ts.trade_cal()
        df = df[df['isOpen'] == 1]
        df = df[df['calenderDate'].str.find(start_year) == 0]
        df.to_csv(TRADE_DATE_FILE, encoding='utf-8-sig')
    else:
        pass


def check_subdirs():
    if not os.path.exists(CSV_SUB):
        os.mkdir(CSV_SUB)


def down_info_data(update=True):
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


def save_local_data(data):
    print('Saving basic data to local database...')
    # # write with csv format
    # hdf = pd.HDFStore(HDF_FILE)
    # from tqdm import tqdm
    # for code in tqdm(data, ascii=True):
    #     for i in range(5):
    #         table_name = '{}_{}'.format(PERIORD_TAG[i], code)
    #         hdf[table_name] = data[code][i].sort_index(ascending=False)
    # hdf.close()

    # write with csv format
    for code in tqdm(data, ascii=True):
        for i in range(5):
            file_name = '{}\\{}_{}.csv'.format(CSV_SUB, PERIORD_TAG[i], code)
            data[code][i].sort_index(ascending=False).to_csv(file_name, index=False)
    # write with pickle format
    # from tqdm import tqdm
    # for code in tqdm(data, ascii=True):
    #     for i in range(5):
    #         table_name = './aa/{}_{}.csv'.format(PERIORD_TAG[i], code)
    #         data[code][i].sort_index(ascending=False).to_pickle(table_name


def download(para):
    codes, counter, finish, lock = para
    ret = {}
    datas = None
    for code in codes:
        try:
            datas = list(map(ts.get_k_data, [code] * 5, [''] * 5, [''] * 5, KTYPE))
        except Exception as err:
            log.err('Download {} fail.'.format(code))
            log.error(err)
        # list(map(save_local_data, datas, [code] * 5, KTYPE, [lock] * 5))
        ret[code] = datas
        with lock:
            counter.value += 1
    finish[os.getpid()] = True
    return ret


def update_bar(counter, finish_flag, multi_count, bar_max):
    print('Start downloading basic data...')
    with tqdm(total=bar_max, ascii=True) as tbar:
        while counter.value <= bar_max:
            tbar.update(counter.value - tbar.n)
            if finish_flag and len(finish_flag) == multi_count:
                tbar.update(bar_max - tbar.n)
                break
    print('Done')


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
    results = pool.map(download, args)
    pool.close()
    pool.join()
    results = reduce(lambda x, y: {**x, **y}, results)
    save_local_data(results)
    down_trade_data('2018')


def get_more_infos(info):
    from tqdm import tqdm
    info = info.reset_index()
    lastest_trade_date = get_local_data(info.iloc[0]['code'], 'D', 'date', 1).iloc[0]
    tqdm.pandas(desc='Cal ZhangTing', ascii=True)
    zt = info['code'].progress_apply(cal.zt, args=[lastest_trade_date]).rename('zt')
    tqdm.pandas(desc='Cal ZhaBan', ascii=True)
    zb = info['code'].progress_apply(cal.zb, args=[lastest_trade_date]).rename('zb')
    tqdm.pandas(desc='Cal TurnOverRatio', ascii=True)
    tor = info.progress_apply(cal.tor, axis=1).rename('tor')
    tqdm.pandas(desc='Cal PriceChangePercentage', ascii=True)
    pcp = info['code'].progress_apply(cal.pcp).rename('pcp')
    tqdm.pandas(desc='Cal CirculationMarketValue', ascii=True)
    ltsz = info.progress_apply(cal.ltsz, axis=1).rename('ltsz')
    updated_info = pd.concat([info, zt, zb, tor, pcp, ltsz], axis=1)
    updated_info.to_csv(INFO_FILE, encoding='utf-8-sig')


@print_run_time
def update_local_database(mode):
    check_subdirs()
    info_data = down_info_data()
    if mode != 2:
        down_basic_data(sorted(info_data.index))
    if mode != 1:
        get_more_infos(info_data)


if __name__ == '__main__':
    with TimerCount('Test of Download all:'):
        update_local_database(2)
