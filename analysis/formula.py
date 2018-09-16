import datetime
import pandas as pd
import numpy as np
from tqdm import tqdm
import tushare as ts
from datakit import *


def percision(x, p):
    return float('{:.0{}f}'.format(float(x), p))


def ma(code, ktype: str = 'D', period: int = 5):
    close_price = read_local_data(code, ktype, item='close', count=60)
    close_price = close_price.sort_index(ascending=True)
    moving_average = close_price.rolling(window=period).mean().dropna(axis=0)
    return moving_average.iloc[:, 0].apply(percision, **{'p': 2}).values.reshape(
        moving_average.shape)
    # return percision(moving_average.iloc[0], 2)


def tor(code, total_vol, ktype='D'):
    current_vol = read_local_data(code, ktype, 'volume', count=1).iloc[0]
    toa = current_vol / (total_vol * 10000)
    return percision(toa, 2)


def pcp(code, ktype='D'):
    close, pre_close = list(read_local_data(code, ktype, 'close', count=2).iloc[:, 0])
    if pre_close == 0:
        cur_open = read_local_data(code, ktype, 'open', count=1).iloc[:, 0]
        pre_close = cur_open
    return percision(((close - pre_close) / pre_close), 4) * 100


def _zt_status(para):
    pre_c, c = para
    zt_price = percision(pre_c * 1.1, 2)
    return c >= zt_price


def zt(code, start_pos=0):
    """
    cal zhang ting
    :param code:
    :param start_pos:
    :return: zhang ting days
    """
    check_window = read_local_data(code, 'D', pos=start_pos,
                                   item='close', count=30).sort_index(ascending=False)
    check_window = check_window[check_window != 0]
    last_zt_status = check_window.rolling(window=2).apply(_zt_status, raw=False)
    last_zt_status.sort_index(ascending=True, inplace=True)
    continue_zt_num = 0
    for i in last_zt_status.values:
        if i == 1:
            continue_zt_num += 1
        else:
            break
    if 0 in list(last_zt_status.iloc[:, 0]):
        return continue_zt_num
    else:
        return 0


def zb(code, start_pos=0):
    """
    cal zha ban
    :param code:
    :param start_pos:
    :return:
    """
    close, pre_close = list(
        read_local_data(code, 'D', item='close', pos=start_pos, count=2).iloc[:, 0])
    high = read_local_data(code, 'D', 'high', pos=start_pos, count=1).iloc[0, 0]
    zt_price = percision(pre_close * 1.1, 2)
    return close != high and high >= zt_price


def tp(code, latest_trade_date):
    date = read_local_data(code, 'D', 'date', 1).iloc[0]
    date = datetime.datetime.strptime(date, '%Y-%m-%d')
    trade_date = datetime.datetime.strptime(latest_trade_date, '%Y-%m-%d')
    return date < trade_date


def ltsz(code, total_vol):
    """
    cal liu tong shi zhi
    :param code:
    :param total_vol:
    :return:
    """
    close = read_local_data(code, 'D', 'close', count=1).iloc[0]
    return percision(close * total_vol, 2)


def statistics(mode, date=None):
    info = pd.read_csv(INFO_FILE, dtype={'code': str})
    # date = dk.read_local_data(info.iloc[0]['code'], 'D', 'date', 1).iloc[0] if date is None else date
    s_periord = 5
    l = [{}] * s_periord
    for i in range(s_periord):
        tqdm.pandas(desc='zt of {} days ago'.format(i), ascii=True)
        l[i]['zt'] = info['code'].progress_apply(zt, args=[i * -1]).rename('zt')
        a = 0


def ta24(code, ktype='D'):
    data = ts.get_k_data(code=code, ktype=ktype)
    ma5 = data.loc['close'].rolling(window=5).mean()
    ma24 = data.loc['close'].rolling(window=24).mean()


def cross(a: np.ndarray, b: np.ndarray):
    min_length = min(a.shape[0], b.shape[0])
    c = a > b
    dbg = 0


if __name__ == '__main__':
    ma24 = ma('300071', period=24)
    l = read_local_data('300071', item='low', count=60)
    cross(l.values, ma24)
