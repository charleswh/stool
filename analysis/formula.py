import pandas as pd
import numpy as np
import numba
from tqdm import tqdm
import tushare as ts
from datakit.local_data import get_k_data_local
from setting.settings import INFO_FILE

np.seterr(invalid='ignore')


def ta24(code, ktype='D', period_sml=5, period_big=24, dist_th=3, data_source='local'):
    if data_source == 'online':
        data = ts.get_k_data(code=code, ktype=ktype)
    elif data_source == 'local':
        data = get_k_data_local(code=code, ktype=ktype)
    else:
        assert 0
    c = data.loc[:, 'close']
    l = data.loc[:, 'low']
    ma_sml = c.rolling(window=period_sml).mean().values[::-1]
    ma_big = c.rolling(window=period_big).mean().values[::-1]
    c = c.values[::-1]
    l = l.values[::-1]
    cp = cross_pos(l, ma_big)
    q = cp >= 2 and (l < ma_big)[:cp].sum() <= 1
    qs = (c > ma_big * 1.07)[:cp].sum() >= 1
    ma_sml_dw = ma_sml[0] - ma_sml[1] <= 0
    ma_big_up = ma_big[0] - ma_big[1] >= 0
    c_ma_big_dist = ((c - ma_big) / ma_big * 100)[0]
    limt = (c > ma_big)[0] == True and c_ma_big_dist < dist_th
    return (q and qs and ma_sml_dw and ma_big_up and limt)


def cross_pos(a: np.ndarray, b: np.ndarray):
    diff = (a - b)
    for i in np.argwhere(diff < 0).flatten():
        if i - 1 in np.argwhere(diff > 0).flatten():
            return i - 1
        else:
            continue


if __name__ == '__main__':
    ta24('600532')
