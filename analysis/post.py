import os
import pandas as pd
from functools import reduce
import tushare as ts
from tqdm import tqdm, trange
from setting.settings import sets
from datakit.datakit import data_kit
from utility.misc import rm_dupl


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
        stocks = rm_dupl(stocks)
        stocks = list(map(lambda x: '1{}'.format(x) if x[0] == '6' else '0{}'.format(x), stocks))
    file = os.path.join(sets.OUT_DIR, name + '.blk')
    if os.path.exists(file):
        os.remove(file)
    with open(file, 'w') as f:
        f.write('\n'.join(stocks))


def zt_process():
    zt_data = pd.read_csv(sets.ZT_FILE)
    ret_zt_codes = None
    ret_cur_lb_codes = None

    ret_n_lb_codes = {'2b': [], '3b': [], '4b+': []}

    trade_days = data_kit.get_trade_date_list()
    date_delta = 0
    for i in trange(1, ascii=True, desc='CheckZT'):
        cur = zt_data.iloc[0 + i]
        cur_zt = cur[cur == 1]
        df_l = data_kit.get_k(cur_zt.index[0])
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
            df = data_kit.get_k(code, ktype='D')
            date_c = df.iloc[-1].loc['date'] - pd.Timedelta(days=i + date_delta)
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
        for code in cont_zt.index:
            if zt_data[code][2] == 0:
                ret_n_lb_codes['2b'].append(code)
            elif zt_data[code][3] == 0:
                ret_n_lb_codes['3b'].append(code)
            else:
                ret_n_lb_codes['4b+'].append(code)
        if i == 0:
            ret_zt_codes = cur_zt_codes
            ret_cur_lb_codes = cont_zt.index.values.tolist()
    return ret_zt_codes, ret_cur_lb_codes, ret_n_lb_codes


def zzb_process():
    print('Collecting ZB...')
    zzb = pd.read_csv(sets.ZB_FILE)
    cur_date = data_kit.get_k(zzb.columns[0]).iloc[-1].loc['date']
    zzb = zzb.iloc[0]
    zzb = zzb[zzb > 0].index.values
    cur_zzb_codes = []
    for code in zzb:
        last_date = data_kit.get_k(code).iloc[-1].loc['date']
        if last_date == cur_date:
            cur_zzb_codes.append(code)
    return cur_zzb_codes


def update_rec(var_list, file):
    cur_date = data_kit.get_valid_trade_date()
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
    cur_date = data_kit.get_valid_trade_date()
    with open(sets.ZT_REASON_FILE, 'r') as f:
        rsn_list = f.read().split('\n')
    rsn_list = list(filter(lambda x: x.split(',')[0] in zt_list, rsn_list))
    rsn_list = list(map(lambda x: ':'.join(x.split(',')), rsn_list))
    if not os.path.exists(sets.ZT_RSN_REC):
        with open(sets.ZT_RSN_REC, 'w') as f:
            f.write('{},{}\n'.format(cur_date, ' '.join(rsn_list)))
    else:
        with open(sets.ZT_RSN_REC, 'r') as f:
            cont = list(filter(None, f.read().split('\n')))
        if cur_date in ''.join(cont):
            return None
        else:
            cont.append('{},{}'.format(cur_date, ' '.join(rsn_list)))
            with open(sets.ZT_RSN_REC, 'w') as f:
                f.write('\n'.join(cont))


def get_zzz():
    if not os.path.exists(sets.ZT_REC):
        return None
    else:
        # pre_date = get_valid_trade_date(delta=-1)
        with open(sets.ZT_REC, 'r') as f:
            cont = list(filter(None, f.read().split('\n')))
        return cont[-1].split(',')[-1].split(' ')


def get_once_zt(days=5):
    if not os.path.exists(sets.ZT_REC):
        return None
    else:
        cur_date = data_kit.get_valid_trade_date()
        with open(sets.ZT_REC, 'r') as f:
            cont = list(filter(None, f.read().split('\n')))
        cont = list(filter(lambda x: cur_date not in x, cont)) if len(cont) > 1 else cont
        cont = cont if len(cont) <= days else cont[-days:]
        cont = list(map(lambda x: x.split(',')[-1].split(' '), cont))
        return list(set(list(reduce(lambda x, y: x + y, cont))))


def get_multi_zt_lb(days=6):
    ret_zt = None
    ret_lb = None
    d = 0
    if not os.path.exists(sets.ZT_REC):
        return None
    else:
        with open(sets.ZT_REC, 'r') as f:
            ret_zt = list(filter(None, f.read().split('\n')))

        if len(ret_zt) - 1 < days + 1:
            d = len(ret_zt) - 1
        else:
            d = days
    ret_zt = list(map(lambda x: x.split(',')[-1].split(' '), ret_zt))
    ret_zt = ret_zt[len(ret_zt) - d - 1:-1][::-1]

    if not os.path.exists(sets.LB_REC):
        return None
    else:
        with open(sets.LB_REC, 'r') as f:
            ret_lb = list(filter(None, f.read().split('\n')))

        if len(ret_lb) - 1 < days + 1:
            d = len(ret_lb) - 1
        else:
            d = days
    ret_lb = list(map(lambda x: x.split(',')[-1].split(' '), ret_lb))
    ret_lb = ret_lb[len(ret_lb) - d - 1:-1][::-1]

    return ret_zt, ret_lb


def blk_process():
    ttt, bbb, nbbb = zt_process()
    zzb = zzb_process()
    # zzz = get_zzz()
    # ccc = get_once_zt()
    update_rec(ttt, sets.ZT_REC)
    update_rec(bbb, sets.LB_REC)
    update_rec(zzb, sets.ZB_REC)
    update_zt_rsn_rec(ttt)
    gen_blk(ttt, 'ttt')
    gen_blk(bbb, 'bbb')
    if os._exists(os.path.join(sets.OUT_DIR, 'zzb.blk')):
        os.rename(os.path.join(sets.OUT_DIR, 'zzb.blk'),
                  os.path.join(sets.OUT_DIR, 'zzzb.blk'))
    gen_blk(zzb, 'zzb')
    # gen_blk(zzz, 'zzz')
    # gen_blk(ccc, 'ccc')
    gen_blk(nbbb['2b'], '2b')
    gen_blk(nbbb['3b'], '3b')
    gen_blk(nbbb['4b+'], '4b')

    if os.path.exists(os.path.join(sets.OUT_DIR, '4bs.blk')):
        with open(os.path.join(sets.OUT_DIR, '4bs.blk'), 'r') as f:
            pre = f.read().split('\n')
        pre = [x[1:] for x in pre]
        pre.extend(nbbb['4b+'])
        pre = list(filter(None, pre))
    else:
        pre = nbbb['4b+']
    gen_blk(pre, '4bs')

    t = get_multi_zt_lb(7)

    blk_list = []
    blk_list.append(gen_cfg_bytes('指数', 'zss'))
    blk_list.append(gen_cfg_bytes('临时', 'eee'))
    blk_list.append(gen_cfg_bytes('观察', 'ggg'))
    blk_list.append(gen_cfg_bytes('逆回购', 'nhg'))
    blk_list.append(gen_cfg_bytes('新股未开', 'xgwk'))
    blk_list.append(gen_cfg_bytes('人气股', 'rqg'))
    blk_list.append(gen_cfg_bytes('今日涨停', 'ttt'))
    # blk_list.append(gen_cfg_bytes('昨日涨停', 'zzz'))
    # blk_list.append(gen_cfg_bytes('五日涨停', 'ccc'))
    blk_list.append(gen_cfg_bytes('炸板', 'zzb'))
    blk_list.append(gen_cfg_bytes('昨日炸板', 'zzzb'))
    blk_list.append(gen_cfg_bytes('连板', 'bbb'))
    blk_list.append(gen_cfg_bytes('2板', '2b'))
    blk_list.append(gen_cfg_bytes('3板', '3b'))
    blk_list.append(gen_cfg_bytes('4板+', '4b'))
    blk_list.append(gen_cfg_bytes('4板数据库', '4bs'))

    blk_list.append(gen_cfg_bytes('题材1', 'tc1'))
    blk_list.append(gen_cfg_bytes('题材2', 'tc2'))
    blk_list.append(gen_cfg_bytes('题材3', 'tc3'))
    blk_list.append(gen_cfg_bytes('题材4', 'tc4'))
    blk_list.append(gen_cfg_bytes('题材5', 'tc5'))
    blk_list.append(gen_cfg_bytes('题材6', 'tc6'))
    blk_list.append(gen_cfg_bytes('题材7', 'tc7'))
    blk_list.append(gen_cfg_bytes('题材8', 'tc8'))

    for i in range(len(t[0])):
        gen_blk(t[0][i], 't{}'.format(i + 1))
        blk_list.append(gen_cfg_bytes('{}日前涨停'.format(i + 1), 't{}'.format(i + 1)))
    for i in range(len(t[1])):
        gen_blk(t[1][i], 'b{}'.format(i + 1))
        blk_list.append(gen_cfg_bytes('{}日前连板'.format(i + 1), 'b{}'.format(i + 1)))

    with open(os.path.join(sets.OUT_DIR, 'blocknew.cfg'), 'wb') as f:
        for blk in blk_list:
            f.write(blk)

    from glob import glob
    import shutil
    from utility.misc import run_cmd
    blk_backup_dir = os.path.join(sets.OUT_DIR, 'blk_backup')
    if not os.path.exists(blk_backup_dir):
        os.mkdir(blk_backup_dir)

    cur_date = data_kit.get_valid_trade_date()
    tdx_blk_dst = os.path.join(sets.TDX_ROOT, 'T0002', 'blocknew')
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
        cmd = '{} a -t7z {} {}'.format(sets.EXE_7Z, blk_backup_dir,
                                       os.path.join(blk_backup_dir, '*'))
        run_cmd(cmd)
        shutil.rmtree(blk_backup_dir)
    print('Update new block files...')
    new_blk_files = glob(os.path.join(sets.OUT_DIR, '*'))
    new_blk_files = list(filter(filter_func, new_blk_files))
    for file in new_blk_files:
        name = os.path.split(file)[-1]
        dst_file = os.path.join(tdx_blk_dst, name)
        print(name)
        if os.path.exists(dst_file):
            os.remove(dst_file)
        shutil.copy(file, dst_file)


if __name__ == '__main__':
    blk_process()
