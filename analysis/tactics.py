import pandas as pd
import numpy as np
import tushare as ts
from tqdm import tqdm, trange
from setting.settings import ZT_FILE
from datakit.datakit import get_k_data_local, get_trade_date


def zt_process():
    zt_data = pd.read_csv(ZT_FILE)
    ret_cur_zt_codes = None
    ret_cur_cont_zt_codes = None
    ret_zt_num = []
    ret_cont_zt_num = []
    trade_days = get_trade_date()
    date_delta = 0
    for i in trange(10, ascii=True, desc='CheckZT'):
        cur = zt_data.iloc[0 + i]
        cur_zt = cur[cur == 1]
        df_l = get_k_data_local(cur_zt.index[0], ktype='D')
        while True:
            today = df_l.iloc[-1].loc['date'] - pd.Timedelta(days=i + date_delta)
            if today.strftime('%Y-%m-%d') in trade_days:
                break
            else:
                date_delta += 1
                continue
        cur_zt_codes = []
        for code in tqdm(cur_zt.index, ascii=True, desc='Day{}'.format(i), leave=False):
            t = zt_data.loc[:, code]
            a = t.where(t > 100).dropna()
            df = get_k_data_local(code, ktype='D')
            date_c = df.iloc[-1].loc['date'] - pd.Timedelta(days=i+date_delta)
            if len(a) != 0 and 0 not in t.iloc[i:a.index[0]].values:
                low = df[df['date'] == date_c].loc[:, 'low'].values[0]
                close = df[df['date'] == date_c].loc[:, 'close'].values[0]
                if low != close:
                    pass
                else:
                    continue
            if today != date_c:
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