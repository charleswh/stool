import pandas as pd
import numpy as np
from tqdm import tqdm
import tushare as ts
from datakit import *
from setting.settings import INFO_FILE

np.seterr(invalid='ignore')


def ta24(code, ktype='D'):
    data = ts.get_k_data(code=code, ktype=ktype)
    c = data.loc[:, 'close']
    l = data.loc[:, 'low']
    ma5 = c.rolling(window=5).mean()
    ma24 = c.rolling(window=24).mean()
    a = cross_pos(l.values, ma24.values)
    dgb = 0


def cross_pos(a: np.ndarray, b: np.ndarray):
    diff = (a - b)[::-1]
    p = np.argwhere(diff > 0).flatten()
    n = np.argwhere(diff < 0).flatten()
    for i in n:
        if i - 1 in p:
            return i - 1
        else:
            continue


if __name__ == '__main__':
    ta24('600532')
