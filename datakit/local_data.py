# -*- coding:utf-8 -*-
import os
import pandas as pd
import tushare as ts
from utility.log import log
from utility.task import MultiTasks
from utility.timekit import print_run_time
from setting.settings import CSV_DIR, INFO_FILE, TRADE_DATE_FILE, KTYPE, PERIORD_TAG

OHLC_DICT = {'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum',
             'code': 'last'}

def get_local_info(code, item):
    if not os.path.exists(INFO_FILE):
        log.error('No local info file: {}!'.format(INFO_FILE))
    infos = pd.read_csv(INFO_FILE,
                        usecols=[item],
                        columns={'code': str}).set_index('code')
    return infos.loc[code, item]


def get_codes():
    if not os.path.exists(INFO_FILE):
        log.info('No local info file: {}, get all codes online.'.format(INFO_FILE))
        ret = ts.get_stock_basics().index
    else:
        ret = pd.read_csv(INFO_FILE, dtype={'code': str}).loc[:, 'code']
    return ret


def get_k_data_local(code, ktype='D'):
    file = os.path.join(CSV_DIR, '{}_{}.csv'.format(PERIORD_TAG[KTYPE.index(ktype)], code))
    return pd.read_csv(file, parse_dates=['date'])


def down_trade():
    if not os.path.exists(TRADE_DATE_FILE):
        df = ts.trade_cal()
        df = df[df['isOpen'] == 1]
        df.to_csv(TRADE_DATE_FILE, columns=['calendarDate'], header=False, index=False,
                  encoding='utf-8-sig')
    else:
        pass


def get_trade_date():
    df = None
    if not os.path.exists(TRADE_DATE_FILE):
        down_trade()
    else:
        df = pd.read_csv(TRADE_DATE_FILE, header=None)
    return df.values


def down_k_worker(code):
    ret = {}
    datas = None
    try:
        datas = list(map(ts.get_k_data, [code] * 5, [''] * 5, [''] * 5, KTYPE))
    except Exception as err:
        log.err('Download {} fail.'.format(code))
        log.error(err)
    ret[code] = datas
    return ret


def save_k_worker(stock):
    for code in stock:
        for i in range(5):
            file_name = os.path.join(CSV_DIR, '{}_{}.csv'.format(PERIORD_TAG[i], code))
            stock[code][i].to_csv(file_name, index=False)


def ohlcsum(df):
    return {
        'open': df['open'][0],
        'high': df['high'].max(),
        'low': df['low'].min(),
        'close': df['close'][-1],
        'volume': df['volume'].sum()
    }


def gen_120_k_data(code):
    # m60_data = get_k_data_local(code, ktype='60').set_index(['date'])
    m60_data = ts.get_k_data(code, ktype='60')
    aa = m60_data.groupby(m60_data.asof).agg({'low': lambda s: s.min(),
                                              'high': lambda s: s.max(),
                                              'open': lambda s: s[0],
                                              'close': lambda s: s[-1],
                                              'volume': lambda s: s.sum()})
    aa = m60_data.resample('60T', how=OHLC_DICT, closed='left', label='left')


@print_run_time
def down_k_data_local():
    info = ts.get_today_all().sort_values(by='changepercent', ascending=False)
    info.to_csv(INFO_FILE, index=False, encoding='utf-8-sig')
    codes = list(info['code'])
    down_trade()
    with MultiTasks() as mt:
        basic = mt.run_list_tasks(func=down_k_worker, var_args=codes, en_bar=True,
                                  desc='Down-Basic')
        mt.run_list_tasks(func=save_k_worker, var_args=basic, en_bar=True, desc='Save-Basic')


if __name__ == '__main__':
    # down_k_data_local()
    gen_120_k_data('600532')
