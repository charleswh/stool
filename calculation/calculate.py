import datakit as dk
import datetime
import pandas as pd
from tqdm import tqdm
import tushare as ts


def percision(x, p):
    return float('{:.0{}f}'.format(float(x), p))


def ma(code, ktype, period):
    close_price = dk.read_local_data(code, ktype, 'close', period)
    close_price = close_price.sort_index(ascending=True)
    moving_average = close_price.rolling(window=period).mean()
    return moving_average.iloc[-1]


def tor(para, ktype='D'):
    c = para['code']
    total_vol = para['outstanding']
    current_vol = dk.read_local_data(c, ktype, 'volume', count=1).iloc[0]
    toa = current_vol / (total_vol * 10000)
    return percision(toa, 2)


def pcp(code, ktype='D'):
    close, pre_close = list(dk.read_local_data(code, ktype, 'close', count=2).iloc[:, 0])
    if pre_close == 0:
        cur_open = dk.read_local_data(code, ktype, 'open', count=1).iloc[:, 0]
        pre_close = cur_open
    return percision(((close - pre_close)/pre_close), 4) * 100


def _zt_status(para):
    pre_c, c = para
    zt_price = percision(pre_c * 1.1, 2)
    return c >= zt_price


def zt(code, start_pos):
    check_window = dk.read_local_data(code, 'D', pos=start_pos,
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


def zb(code, start_pos):
    close, pre_close = list(dk.read_local_data(code, 'D', item='close', pos=start_pos, count=2).iloc[:, 0])
    high = dk.read_local_data(code, 'D', 'high', pos=start_pos, count=1).iloc[0, 0]
    zt_price = percision(pre_close * 1.1, 2)
    return close != high and high >= zt_price


def tp(code, latest_trade_date):
    date = dk.read_local_data(code, 'D', 'date', 1).iloc[0]
    date = datetime.datetime.strptime(date, '%Y-%m-%d')
    trade_date = datetime.datetime.strptime(latest_trade_date, '%Y-%m-%d')
    return date < trade_date


def ltsz(para):
    code = para['code']
    total_vol = para['outstanding']
    close = dk.read_local_data(code, 'D', 'close', count=1).iloc[0]
    return percision(close * total_vol, 2)


def statistics(mode, date=None):
    info = pd.read_csv(dk.INFO_FILE, dtype={'code': str})
    #date = dk.read_local_data(info.iloc[0]['code'], 'D', 'date', 1).iloc[0] if date is None else date
    s_periord = 5
    l = [{}] * s_periord
    for i in range(s_periord):
        tqdm.pandas(desc='zt of {} days ago'.format(i), ascii=True)
        l[i]['zt'] = info['code'].progress_apply(zt, args=[i * -1]).rename('zt')
        a=0


def ta24(code, ktype='D'):
    data = ts.get_k_data(code=code, ktype=ktype)
    ma5 = data.loc['close'].rolling(window=5).mean()
    ma24 = data.loc['close'].rolling(window=24).mean()



if __name__ == '__main__':
    # aa = ma('300139', 'D', 10)
    # bb = tor('300139', 'D')
    # cc = statistics(0)
    ta24('603595', '60')
    pass
