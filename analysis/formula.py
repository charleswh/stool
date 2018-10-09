import datetime
import pandas as pd
import numpy as np
from tqdm import tqdm
import tushare as ts
from datakit import *
from setting.settings import INFO_FILE



def ta24(code, ktype='D'):
    data = ts.get_k_data(code=code, ktype=ktype)
    c = data.loc[:, 'close']
    l = data.loc[:, 'low']
    ma5 = c.rolling(window=5).mean()
    ma24 = c.rolling(window=24).mean()
    cross(l.values, ma24.values)

def cross(a: np.ndarray, b: np.ndarray):
    c = a > b
    diff = (a - b)[::-1]

    dbg = 0


if __name__ == '__main__':
    ta24('600532')
