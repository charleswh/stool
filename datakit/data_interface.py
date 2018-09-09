import tushare as ts
import os
import pandas as pd
import numpy as np
from utility import *
from datakit import *


CSV_PREFIX = dict(zip(KTYPE, PERIORD_TAG))


def read_trade_date(start_year=None):
    df = None
    if not os.path.exists(TRADE_DATE_FILE):
        download_trade_data(start_year)
    else:
        df = pd.read_csv(TRADE_DATE_FILE, header=None)
    if start_year is not None:
        df = df[df.iloc[:, 0].str.find(start_year) == 0]
    return df.values


def read_local_data(code, ktype='D', item='close', pos=0, count=None):
    """
    run time: less than 2ms
    item: date,open,close,high,low,volume,code
    """
    file = os.path.join(CSV_DIR, '{}_{}.csv'.format(CSV_PREFIX[ktype], code))
    if not os.path.exists(file):
        log.error('No local data file: {}!'.format(file))
    df = pd.read_csv(file,
                     nrows=(count - pos) if count is not None else count,
                     usecols=[item])
    if pos != 0:
        df.drop([abs(pos) - 1], inplace=True)
    if count is not None and df.shape[0] < count:
        df = pd.concat([df, pd.DataFrame(np.zeros((count - df.shape[0], df.shape[1])),
                                         columns=df.columns)])
    return df


if __name__ == '__main__':
    aa = read_trade_date()
    print(aa)
