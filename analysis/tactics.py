import pandas as pd
import numpy as np
import os
import tushare as ts
from tqdm import tqdm, trange
from setting.settings import ZT_FILE, ZZB_FILE
from datakit.datakit import get_k_interface, get_trade_date


def gen_bll_cfg(name, file, shortcut=None):
    file = file.upper()
    n_bytes = bytes(name, encoding='gbk')
    if shortcut is not None:
        s_bytes = bytes('shortcut', encoding='gbk')
        file = 'P{}'.format(file)
    else:
        s_bytes = None
    f_bytes = bytes(file, encoding='gbk')
    n_container = bytearray(50)
    f_container = bytearray(70)
    n_container[0:len(n_bytes)] = n_bytes
    if shortcut is not None:
        f_container[0:len(s_bytes)] = s_bytes
        f_container[len(s_bytes)+1:len(s_bytes)+1 + len(f_bytes)] = f_bytes
    else:
        f_container[0:len(f_bytes)] = f_bytes
    with open('blocknew.cfg', 'wb') as f:
        f.write(n_container)
        f.write(f_container)


def gen_blk(stocks, name):
    name = name.upper()
    stocks = list(map(lambda x: '1{}'.format(x) if x[0] == '6' else '0{}'.format(x), stocks))
    with open(name + '.blk', 'w') as f:
        f.write('\n'.join(stocks))


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
        df_l = get_k_interface(cur_zt.index[0])
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
            df = get_k_interface(code, ktype='D')
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


def zzb_process():
    zzb = pd.read_csv(ZZB_FILE)
    cur_date = get_k_interface(zzb.columns[0]).iloc[-1].loc['date']
    zzb = zzb.iloc[0]
    zzb = zzb[zzb > 0].index.values
    cur_zzb_codes = []
    for code in zzb:
        last_date = get_k_interface(code).iloc[-1].loc['date']
        if last_date == cur_date:
            cur_zzb_codes.append(code)
    return cur_zzb_codes


def post_process():
    zzb_process()
    #ttt, bbb, c, d = zt_process()
    # aa = ['000068', '300083', '002076', '600758', '002708', '600173', '000622', '002377', '600156', '002762', '002848', '603398', '300686', '000800', '002909', '300610', '603081', '600211', '300643', '000150', '603701', '603078', '000526', '600159', '000608', '000668', '600250', '300472', '600240', '000031', '002899', '002059', '002929', '603583', '603637', '603032', '002902', '603089', '000413', '000780', '002201', '600684', '600249', '000691', '603778', '000927', '600792', '000517', '600743', '600393', '600162']
    # gen_blk(aa, 'ttt')

if __name__ == '__main__':
    post_process()