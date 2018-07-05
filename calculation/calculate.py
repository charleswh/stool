import datakit as dk
from miscs import TimerCount
import datetime


def percision(x, p):
    return float('{:.0{}f}'.format(float(x), p))


def MA(code, ktype, period):
    close_price = dk.get_local_data(code, ktype, 'close', period)
    close_price = close_price.sort_index(ascending=True)
    moving_average = close_price.rolling(window=period).mean()
    return moving_average.iloc[-1]


def TOR(para, ktype='D'):
    c = para['code']
    total_vol = para['outstanding']
    current_vol = dk.get_local_data(c, ktype, 'volume', 1).iloc[0]
    toa = current_vol / (total_vol * 10000)
    return float(toa)


def PCP(code, ktype='D'):
    """
    Calculate Price Change Percentage
    """
    close, pre_close = dk.get_local_data(code, ktype, 'close', 2)
    return percision(((close - pre_close)/pre_close), 4) * 100


def _zt_status(para):
    pre_c, c = para
    zt_price = percision(pre_c * 1.1, 2)
    return c >= zt_price


def ZT(code, latest_trade_date):
    check_window = dk.get_local_data(code, 'D', item='close', count=30).sort_index(ascending=False)
    last_zt_status = check_window.rolling(window=2).apply(_zt_status, raw=False).sort_index(ascending=True)
    continue_zt_num = 0
    for i in last_zt_status:
        if i == 1:
            continue_zt_num += 1
        else:
            break
    if 0 in last_zt_status and not TingPai(code, latest_trade_date):
        return continue_zt_num
    else:
        return 0


def ZB(code, latest_trade_date):
    close, pre_close = dk.get_local_data(code, 'D', 'close', 2)
    high = dk.get_local_data(code, 'D', 'high', 1).iloc[0]
    zt_price = percision(pre_close * 1.1, 2)
    return close != high and high >= zt_price and not TingPai(code, latest_trade_date)


def TingPai(code, latest_trade_date):
    date = dk.get_local_data(code, 'D', 'date', 1).iloc[0]
    date = datetime.datetime.strptime(date, '%Y-%m-%d')
    trade_date = datetime.datetime.strptime(latest_trade_date, '%Y-%m-%d')
    return date < trade_date


if __name__ == '__main__':
    # aa = MA('300139', 'D', 10)
    # bb = TOR('300139', 'D')
    cc = ZT('300312', '2018-07-03')
    codes = dk.get_codes()
    codes = codes
    with TimerCount('test'):
        aa = codes.apply(ZT)
    pass
