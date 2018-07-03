from miscs import *
from datakit import *
import datetime


def percision(x, p):
    return float('{:.0{}f}'.format(float(x), p))


def MA(code, ktype, period):
    close_price = get_local_data(code, ktype, 'close', period)
    close_price = close_price.sort_index(ascending=True)
    moving_average = close_price.rolling(window=period).mean()
    return moving_average.iloc[-1]


def TOR(code, ktype='D'):
    """
    CalculateTurnOverRatio of given ktype.
    """
    current_vol = get_local_data(code, ktype, 'volume', 1)
    total_vol = get_local_info(code, 'outstanding')
    toa = current_vol / (total_vol * 10000)
    return float(toa)


def PCP(code, ktype='D'):
    """
    Calculate Price Change Percentage
    """
    close, pre_close = get_local_data(code, ktype, 'close', 2)
    return percision(((close - pre_close)/pre_close), 4) * 100


def ZT(code):
    close, pre_close = get_local_data(code, 'D', 'close', 2)
    check_window = get_local_data(code, 'D', item='close', count=30)
    check_pct = check_window.sort_index(ascending=False).pct_change().sort_index(ascending=True)
    check_pct = check_pct.apply(percision, **{'p': 4})
    zt_price = percision(pre_close * 1.1, 2)
    # a1_v = ts.get_realtime_quotes(code).loc[0:, 'a1_v'][0]
    # and a1_v == ''
    return close >= zt_price and False in (check_pct.fillna(1) > 0.0995) and not TingPai(code)


def ZB(code):
    close, pre_close = get_local_data(code, 'D', 'close', 2)
    high = get_local_data(code, 'D', 'high', 1)[0]
    zt_price = percision(pre_close * 1.1, 2)
    return close != high and high >= zt_price and not TingPai(code)


def TingPai(code):
    last_date = get_local_data(code, 'D', 'date', 1)[0]
    last_date = datetime.datetime.strptime(last_date, '%Y-%m-%d')
    cur_date = datetime.datetime.today().strftime('%Y-%m-%d')
    cur_date = datetime.datetime.strptime(cur_date, '%Y-%m-%d')
    return not last_date < cur_date


if __name__ == '__main__':
    # aa = MA('300139', 'D', 10)
    # bb = TOR('300139', 'D')
    TingPai('000408')
    codes = get_codes()
    codes = codes
    with TimerCount('test'):
        aa = codes.apply(ZT)
    pass
