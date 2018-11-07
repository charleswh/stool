import os
import numpy as np
import pandas as pd
from functools import reduce
import tushare as ts
from tqdm import tqdm, trange
from setting.settings import ZT_FILE, ZB_FILE, ZT_REC, ZB_REC, LB_REC, ZT_REASON_FILE, ZT_RSN_REC, \
                             TDX_ROOT, OUT_DIR, EXE_7Z
from datakit.datakit import get_k_interface, get_trade_date_list, get_valid_trade_date


def gen_cfg_bytes(name, file):
    file = file.upper()
    n_bytes = bytes(name, encoding='gbk')
    f_bytes = bytes(file, encoding='gbk')
    n_container = bytearray(50)
    f_container = bytearray(70)
    n_container[0:len(n_bytes)] = n_bytes
    f_container[0:len(f_bytes)] = f_bytes
    return n_container + f_container


def gen_blk(stocks, name):
    name = name.upper()
    if stocks is None:
        stocks = ['']
    else:
        stocks = list(map(lambda x: '1{}'.format(x) if x[0] == '6' else '0{}'.format(x), stocks))
    with open(os.path.join(OUT_DIR, name + '.blk'), 'w') as f:
        f.write('\n'.join(stocks))


def zt_process():
    zt_data = pd.read_csv(ZT_FILE)
    ret_cur_zt_codes = None
    ret_cur_cont_zt_codes = None
    ret_zt_num = []
    ret_cont_zt_num = []
    trade_days = get_trade_date_list()
    date_delta = 0
    for i in trange(1, ascii=True, desc='CheckZT'):
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
        # ret_zt_num.append(len(cur_zt_codes))
        # ret_cont_zt_num.append(len(cont_zt))
    # return (ret_cur_zt_codes, ret_cur_cont_zt_codes, ret_zt_num, ret_cont_zt_num)
    return (ret_cur_zt_codes, ret_cur_cont_zt_codes)


def zzb_process():
    print('Collecting ZB...')
    zzb = pd.read_csv(ZB_FILE)
    cur_date = get_k_interface(zzb.columns[0]).iloc[-1].loc['date']
    zzb = zzb.iloc[0]
    zzb = zzb[zzb > 0].index.values
    cur_zzb_codes = []
    for code in zzb:
        last_date = get_k_interface(code).iloc[-1].loc['date']
        if last_date == cur_date:
            cur_zzb_codes.append(code)
    return cur_zzb_codes


def update_rec(var_list, file):
    cur_date = get_valid_trade_date()
    if not os.path.exists(file):
        with open(file, 'w') as f:
            f.write('{},{}\n'.format(cur_date, ' '.join(var_list)))
    else:
        with open(file, 'r') as f:
            cont = list(filter(None, f.read().split('\n')))
        if cur_date in ''.join(cont):
            return None
        else:
            cont.append('{},{}'.format(cur_date, ' '.join(var_list)))
            with open(file, 'w') as f:
                f.write('\n'.join(cont))


def update_zt_rsn_rec(zt_list):
    cur_date = get_valid_trade_date()
    with open(ZT_REASON_FILE, 'r') as f:
        rsn_list = f.read().split('\n')
    rsn_list = list(filter(lambda x: x.split(',')[0] in zt_list, rsn_list))
    rsn_list = list(map(lambda x: ':'.join(x.split(',')), rsn_list))
    if not os.path.exists(ZT_RSN_REC):
        with open(ZT_RSN_REC, 'w') as f:
            f.write('{},{}\n'.format(cur_date, ' '.join(rsn_list)))
    else:
        with open(ZT_RSN_REC, 'r') as f:
            cont = list(filter(None, f.read().split('\n')))
        if cur_date in ''.join(cont):
            return None
        else:
            cont.append('{},{}'.format(cur_date, ' '.join(rsn_list)))
            with open(ZT_RSN_REC, 'w') as f:
                f.write('\n'.join(cont))



def get_zzz():
    if not os.path.exists(ZT_REC):
        return None
    else:
        pre_date = get_valid_trade_date(delta=-1)
        with open(ZT_REC, 'r') as f:
            cont = list(filter(None, f.read().split('\n')))
        cont = list(filter(lambda x: pre_date in x, cont))
        return cont[0].split(',')[-1].split(' ')


def get_once_zt():
    if not os.path.exists(ZT_REC):
        return None
    else:
        cur_date = get_valid_trade_date()
        with open(ZT_REC, 'r') as f:
            cont = list(filter(None, f.read().split('\n')))
        cont = list(filter(lambda x: cur_date not in x, cont)) if len(cont) > 1 else cont
        cont = cont if len(cont) <= 10 else cont[-10:]
        cont = list(map(lambda x: x.split(',')[-1].split(' '), cont))
        return list(set(list(reduce(lambda x, y: x + y, cont))))


def blk_process():
    ttt, bbb = zt_process()
    zzb = zzb_process()
    zzz = get_zzz()
    ccc = get_once_zt()
    update_rec(ttt, ZT_REC)
    update_rec(bbb, LB_REC)
    update_rec(zzb, ZB_REC)
    update_zt_rsn_rec(ttt)
    gen_blk(ttt, 'ttt')
    gen_blk(bbb, 'bbb')
    gen_blk(zzb, 'zzb')
    gen_blk(zzz, 'zzz')
    gen_blk(ccc, 'ccc')
    blk_list = []
    blk_list.append(gen_cfg_bytes('临时', 'eee'))
    blk_list.append(gen_cfg_bytes('逆回购', 'nhg'))
    blk_list.append(gen_cfg_bytes('指数', 'zss'))
    blk_list.append(gen_cfg_bytes('人气股', 'rqg'))
    blk_list.append(gen_cfg_bytes('今日涨停', 'ttt'))
    blk_list.append(gen_cfg_bytes('昨日涨停', 'zzz'))
    blk_list.append(gen_cfg_bytes('十日涨停', 'ccc'))
    blk_list.append(gen_cfg_bytes('炸板', 'zzb'))
    blk_list.append(gen_cfg_bytes('连板', 'bbb'))
    with open(os.path.join(OUT_DIR, 'blocknew.cfg'), 'wb') as f:
        for blk in blk_list:
            f.write(blk)

    from glob import glob
    import shutil
    from utility.misc import run_cmd
    blk_backup_dir = os.path.join(OUT_DIR, 'blk_backup')
    if not os.path.exists(blk_backup_dir):
        os.mkdir(blk_backup_dir)

    cur_date = get_valid_trade_date()
    tdx_blk_dst = os.path.join(TDX_ROOT, 'T0002', 'blocknew')
    filter_func = lambda x: x.split('.')[-1] == 'blk' or x.split('.')[-1] == 'cfg'
    if os.path.exists('{}.7z'.format(cur_date)):
        pass
    else:
        blk_backup_dir = os.path.join(blk_backup_dir, cur_date)
        if not os.path.exists(blk_backup_dir):
            os.mkdir(blk_backup_dir)
        print('Backup old block files...')
        pre_blk_files = glob(os.path.join(tdx_blk_dst, '*'))
        pre_blk_files = list(filter(filter_func, pre_blk_files))
        for file in pre_blk_files:
            shutil.copy(file, blk_backup_dir)
        cmd = '{} a -t7z {} {}'.format(EXE_7Z, blk_backup_dir, os.path.join(blk_backup_dir, '*'))
        run_cmd(cmd)
        shutil.rmtree(blk_backup_dir)
    print('Update new block files...')
    new_blk_files = glob(os.path.join(OUT_DIR, '*'))
    new_blk_files = list(filter(filter_func, new_blk_files))
    for file in new_blk_files:
        shutil.copy(file, tdx_blk_dst)


def post_process():
    blk_process()


if __name__ == '__main__':
    get_zzz()
    post_process()