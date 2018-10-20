import pandas as pd
import numpy as np
import tushare as ts
from tqdm import tqdm, trange
from setting.settings import ZT_FILE
from datakit.datakit import get_k_data_local


def zt_process():
    zt_data = pd.read_csv(ZT_FILE)
    ret_cur_zt_codes = None
    ret_cur_cont_zt_codes = None
    ret_zt_num = []
    ret_cont_zt_num = []
    for i in trange(10, ascii=True, desc='CheckZT'):
        cur = zt_data.iloc[0 + i]
        cur_zt = cur[cur == 1]
        today = get_k_data_local(cur_zt.index[0], ktype='D').iloc[-1].loc['date'] - \
                pd.Timedelta(days=i)
        cur_zt_codes = []
        for code in tqdm(cur_zt.index, ascii=True, desc='Day{}'.format(i), leave=False):
            t = zt_data.loc[:, code]
            a = t.where(t > 100).dropna()
            if len(a) != 0 and 0 not in t.iloc[i:a.index[0]].values:
                continue
            if today != get_k_data_local(code, ktype='D').iloc[-1].loc['date'] - \
                pd.Timedelta(days=i):
                continue
            if i == 0 and ts.get_realtime_quotes(code).loc[:, 'ask'].iloc[0] != '0.000':
                continue
            cur_zt_codes.append(code)
        cont_zt = zt_data.loc[:, cur_zt_codes]
        cont_zt = cont_zt.iloc[i + 1][cont_zt.iloc[i + 1] == 1]
        if i == 0:
            ret_cur_zt_codes = cur_zt_codes
            ret_cur_cont_zt_codes = cont_zt.index.values.tolist()
        ret_zt_num.append(len(cur_zt_codes))
        ret_cont_zt_num.append(len(cont_zt))
    return (ret_cur_zt_codes, ret_cur_cont_zt_codes, ret_zt_num, ret_cont_zt_num)

def post_process():
    a, b, c, d = zt_process()
    print(a)
    print(b)
    print(c)
    print(d)


if __name__ == '__main__':
    post_process()