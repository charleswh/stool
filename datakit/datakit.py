# -*- coding:utf-8 -*-
import os
import pandas as pd
import numpy as np
import tushare as ts
from functools import reduce
from utility.log import log
from utility.task import MultiTasks
from utility.timekit import print_run_time
from setting.settings import CSV_DIR, INFO_FILE, TRADE_DATE_FILE, KTYPE, PERIORD_TAG, ZT_FILE

OHLC_DICT = {'open': 'first', 'close': 'last', 'high': 'max', 'low': 'min', 'volume': 'sum',
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


def get_k_interface(code, ktype='D', ds='local'):
    valid_dates = get_trade_date()
    date = get_datetime_now()
    date_str = date.strftime('%Y-%m-%d')
    day_begin = pd.datetime(year=date.year, month=date.month, day=date.month, hour=9, minute=30)
    day_end = pd.datetime(year=date.year, month=date.month, day=date.month, hour=15, minute=30)
    if ds == 'online' and date_str in valid_dates and day_begin <= date <= day_end:
        return ts.get_k_data(code=code, ktype=ktype)
    else:
        file = os.path.join(CSV_DIR, '{}_{}.csv'.format(PERIORD_TAG[KTYPE.index(ktype)], code))
        return pd.read_csv(file, parse_dates=['date']) if os.path.exists(file) else None


def down_trade():
    if os.path.exists(TRADE_DATE_FILE):
        return None
    df = ts.trade_cal()
    df = df[df['isOpen'] == 1]
    df.to_csv(TRADE_DATE_FILE, columns=['calendarDate'], header=False, index=False, encoding='utf-8-sig')


def get_datetime_now(str_ret=False):
    now = pd.datetime.now()
    return now.strftime('%Y-%m-%d %H:%M:%S') if str_ret is True else now


def get_trade_date():
    df = None
    if not os.path.exists(TRADE_DATE_FILE):
        down_trade()
    else:
        df = pd.read_csv(TRADE_DATE_FILE, header=None)
    return df.values


def down_k_worker(code):
    datas = []
    for kt in KTYPE:
        datas.append(ts.get_k_data(code, ktype=kt, retry_count=99))
    return {code: datas}


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
    try:
        m60 = get_k_interface(code, ktype='60')
        if m60 is not None:
            m60.set_index(['date'], inplace=True)
            if m60.shape[0] % 2 == 1:
                pass
            m120 = m60.resample('120T').agg(OHLC_DICT).dropna()
            new_index = m60.index[1::2]
            if new_index.shape[0] == m120.shape[0]:
                file_name = os.path.join(CSV_DIR, '{}_{}.csv'.format('min120', code))
                m120.reset_index().to_csv(file_name, index=False)
            else:
                pass
        else:
            pass
    except Exception as err:
        print(code)
        print(err)
        assert 0


def zhangting(code):
    max_zt_days = 30
    try:
        day = get_k_interface(code)
        c = day.loc[:, 'close']
        zt = c.rolling(window=2).apply(func=lambda x: x[1] >= round(x[0] * 1.1, 2), raw=True)[::-1]
    except Exception as err:
        print(code)
        print(err)
        assert 0
    if len(zt) >= max_zt_days:
        ret = zt.values[:max_zt_days]
    else:
        ret = np.r_[zt.values, np.zeros(max_zt_days - len(zt))]
    return {code: ret}


@print_run_time
def down_k_data_local():
    info = ts.get_today_all().sort_values(by='changepercent', ascending=False)
    info.drop_duplicates(inplace=True)
    info = info[~info['name'].str.contains('ST')]
    info = info[~info['name'].str.contains('退市')]
    info.to_csv(INFO_FILE, index=False, encoding='utf-8-sig')
    codes = list(info['code'])
    codes = get_codes()
    down_trade()
    with MultiTasks() as mt:
        basic = mt.run_list_tasks(func=down_k_worker, var_args=codes, en_bar=True, desc='DownBasic')
        mt.run_list_tasks(func=save_k_worker, var_args=basic, en_bar=True, desc='SaveBasic')
        try:
            mt.run_list_tasks(func=gen_120_k_data, var_args=codes, en_bar=True, desc='GenM120')
        except Exception as err:
            print(err)
            assert 0
        res = mt.run_list_tasks(func=zhangting, var_args=codes, en_bar=True, desc='GenZT')
        res = reduce(lambda x, y: {**x, **y}, res)
        df = pd.DataFrame(res).fillna(999)
        df.to_csv(ZT_FILE, index=False)


if __name__ == '__main__':
    pass
    # down_k_worker('600532')
    # generate_zt()
    # zhangting('601162')
