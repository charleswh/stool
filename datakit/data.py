# -*- coding:utf-8 -*-
import calculation as cal
import tushare as ts
from utility import *
import pandas as pd
import numpy as np
import os

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


def read_local_data(code, ktype, item, pos=0, count=None):
    file = os.path.join(CSV_SUB, '{}_{}.csv'.format(KSUB[ktype], code))
    if not os.path.exists(file):
        log.error('No local data file: {}!'.format(file))
        assert 0
    df = pd.read_csv(file, nrows=(count - pos) if count is not None else count, usecols=[item])
    if pos != 0:
        df.drop([abs(pos) - 1], inplace=True)
    if count is not None and df.shape[0] < count:
        df = pd.concat([df, pd.DataFrame(np.zeros((count - df.shape[0], df.shape[1])),
                                         columns=df.columns)])
    return df


def get_local_info(code, item):
    if not os.path.exists(INFO_FILE):
        log.error('No local info file: {}!'.format(INFO_FILE))
    infos = pd.read_csv(INFO_FILE, usecols=[item], columns={'code': str}).set_index('code')
    return infos.loc[code, item]


def get_all_codes():
    info_file = os.path.join(FILE_ROOT, INFO_FILE)
    if not os.path.exists(info_file):
        log.info('No local info file: {}, get all codes online.'.format(info_file))
        ret = ts.get_stock_basics().index
    else:
        ret = pd.read_csv(info_file, dtype={'code': str}).loc[:, 'code']
    return ret


def get_trade_date(start_year=None):
    if not os.path.exists(TRADE_DATE_FILE):
        df = ts.trade_cal()
        df = df[df['isOpen'] == 1]
        df.to_csv(TRADE_DATE_FILE, encoding='utf-8-sig')
    else:
        df = pd.read_csv(TRADE_DATE_FILE)
    if start_year is not None:
        df = df[df['calendarDate'].str.find(start_year) == 0]
    return df


def down_trade_data(start_year=None):
    if not os.path.exists(TRADE_DATE_FILE):
        df = ts.trade_cal()
        df = df[df['isOpen'] == 1]
        df = df[df['calendarDate'].str.find(start_year) == 0]
        df.to_csv(TRADE_DATE_FILE, encoding='utf-8-sig')
    else:
        pass


def check_subdirs():
    if not os.path.exists(CSV_SUB):
        os.mkdir(CSV_SUB)


@print_run_time
def down_info_data(update=True):
    basic_infos = None
    if update is True:
        keep_cols = ['name', 'outstanding', 'timeToMarket']
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
    basic_infos = basic_infos.reset_index()
    return basic_infos


def save_basic_worker(stock):
    # write with csv format
    for code in stock:
        for i in range(5):
            file_name = '{}\\{}_{}.csv'.format(CSV_SUB, PERIORD_TAG[i], code)
            stock[code][i].sort_index(ascending=False).to_csv(file_name, index=False)
    # # write with csv format
    # hdf = pd.HDFStore(HDF_FILE)
    # from tqdm import tqdm
    # for code in tqdm(data, ascii=True):
    #     for i in range(5):
    #         table_name = '{}_{}'.format(PERIORD_TAG[i], code)
    #         hdf[table_name] = data[code][i].sort_index(ascending=False)
    # hdf.close()

    # write with pickle format
    # from tqdm import tqdm
    # for code in tqdm(data, ascii=True):
    #     for i in range(5):
    #         table_name = './aa/{}_{}.csv'.format(PERIORD_TAG[i], code)
    #         data[code][i].sort_index(ascending=False).to_pickle(table_name


def download_basic_worker(code):
    ret = {}
    datas = None
    try:
        datas = list(map(ts.get_k_data, [code] * 5, [''] * 5, [''] * 5, KTYPE))
    except Exception as err:
        log.err('Download {} fail.'.format(code))
        log.error(err)
    ret[code] = datas
    return ret


@print_run_time
def update_local_database(mode):
    check_subdirs()
    info_data = down_info_data()
    codes = list(info_data['code'])
    down_trade_data('2018')
    mt = MultiTasks()
    if mode == 'basic' or mode == 'all':
        sub_size = int((len(codes) + MAX_TASK_NUM) / MAX_TASK_NUM)
        sub_code = [list(codes[i:i + sub_size]) for i in range(0, len(codes), sub_size)]
        basic = mt.run_tasks(func=download_basic_worker, var_args=sub_code, en_bar=True,
                             desc='Down-Basic', merge_result=False)
        mt.run_tasks(func=save_basic_worker, var_args=basic, en_bar=True, desc='Save-Basic')
    if mode == 'info' or mode == 'all':
        sub_size = int((info_data.shape[0] + MAX_TASK_NUM) / MAX_TASK_NUM)
        sub_item = [list(info_data['code'][i:i + sub_size]) for i in range(0, info_data.shape[0], sub_size)]
        zt = mt.run_tasks(func=cal.zt, var_args=sub_item, en_bar=True, desc='Cal-ZT')
        zb = mt.run_tasks(func=cal.zb, var_args=sub_item, en_bar=True, desc='Cal-ZB')
        pcp = mt.run_tasks(func=cal.pcp, var_args=sub_item, en_bar=True, desc='Cal-PCP')
        t = info_data.loc[:, ('code', 'outstanding')].values
        sub_item = [t[i:i + sub_size] for i in range(0, info_data.shape[0], sub_size)]
        tor = mt.run_tasks(func=cal.tor, var_args=sub_item, en_bar=True, desc='Cal-TOR')
        ltsz = mt.run_tasks(func=cal.ltsz, var_args=sub_item, en_bar=True, desc='Cal-LTSZ')

        updated_info = pd.concat([info_data,
                                  pd.Series(zt, name='zt'),
                                  pd.Series(zb, name='zb'),
                                  pd.Series(tor, name='tor'),
                                  pd.Series(pcp, name='pcp'),
                                  pd.Series(ltsz, name='ltsz')], axis=1)
        updated_info.to_csv(INFO_FILE, encoding='utf-8-sig')
    mt.close_tasks()


if __name__ == '__main__':
    with TimerCount('Test of Download:'):
        update_local_database('info')
