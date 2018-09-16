# -*- coding:utf-8 -*-
import re
import os
import pandas as pd
import numpy as np
import tushare as ts
from analysis.formula import zt, zb, ltsz, pcp, tor
from crawler.tips import download_tips_worker, save_tips_worker, copy_diff_tips
from utility.log import log
from utility.task import MultiTasks, MAX_TASK_NUM
from utility.timekit import sleep, time_str, TimerCount, print_run_time
from utility.settings import OUT_DIR, MAX_TASK_NUM, KTYPE, PERIORD_TAG


FILE_ROOT = os.path.dirname(os.path.realpath(__file__))
CSV_DIR = os.path.join(OUT_DIR, 'data_csv')
INFO_FILE = os.path.join(OUT_DIR, 'info.csv')
CONCEPT_FILE = os.path.join(OUT_DIR, 'concept.csv')
TRADE_DATE_FILE = os.path.join(OUT_DIR, 'trade_date.csv')
INFO_TOTAL_COL = ['name', 'industry', 'area', 'pe', 'outstanding', 'totals',
                  'totalAssets', 'liquidAssets', 'fixedAssets', 'reserved',
                  'reservedPerShare', 'esp', 'bvps', 'pb', 'timeToMarket',
                  'undp', 'perundp', 'rev', 'profit', 'gpr', 'npr', 'holders']


def get_local_info(code, item):
    if not os.path.exists(INFO_FILE):
        log.error('No local info file: {}!'.format(INFO_FILE))
    infos = pd.read_csv(INFO_FILE,
                        usecols=[item],
                        columns={'code': str}).set_index('code')
    return infos.loc[code, item]


def get_all_codes():
    info_file = os.path.join(FILE_ROOT, INFO_FILE)
    if not os.path.exists(info_file):
        log.info('No local info file: {}, get all codes online.'.format(info_file))
        ret = ts.get_stock_basics().index
    else:
        ret = pd.read_csv(info_file, dtype={'code': str}).loc[:, 'code']
    return ret


def download_trade_data():
    if not os.path.exists(TRADE_DATE_FILE):
        df = ts.trade_cal()
        df = df[df['isOpen'] == 1]
        df.to_csv(TRADE_DATE_FILE, columns=['calendarDate'], header=False, index=False,
                  encoding='utf-8-sig')
    else:
        pass


@print_run_time
def down_info_data(update=True):
    basic_infos = None
    if update is True:
        keep_cols = ['name', 'outstanding', 'timeToMarket']
        basic_infos = ts.get_stock_basics()
        useless_cols = list(set(basic_infos.columns).difference(set(keep_cols)))
        basic_infos = basic_infos.drop(columns=useless_cols)
        basic_infos = basic_infos[basic_infos['name'].str.find('*') == -1]
        basic_infos = basic_infos[basic_infos['timeToMarket'] != 0]
    else:
        if os.path.exists(INFO_FILE):
            basic_infos = pd.read_csv(INFO_FILE)
        else:
            log.error('No info file <{}>!'.format(INFO_FILE))
    basic_infos = basic_infos.reset_index()
    return basic_infos


def download_basic_worker(code):
    ret = {}
    datas = None
    try:
        datas = list(map(ts.get_k_data, [code] * 5, [''] * 5, [''] * 5, KTYPE))
    except Exception as err:
        log.err('Download {} fail.'.format(code))
        log.error(err)
    ret[code] = datas
    return ret


def save_basic_worker(stock):
    for code in stock:
        for i in range(5):
            file_name = '{}\\{}_{}.csv'.format(CSV_DIR, PERIORD_TAG[i], code)
            stock[code][i].sort_index(ascending=False).to_csv(file_name, index=False)


@print_run_time
def update_local_database(mode):
    if not os.path.exists(CSV_DIR):
        os.mkdir(CSV_DIR)
    info_data = down_info_data()
    codes = list(info_data['code'])
    download_trade_data()
    mt = MultiTasks()
    if mode == 'basic' or mode == 'all':
        sub_size = int((len(codes) + MAX_TASK_NUM) / MAX_TASK_NUM)
        sub_code = [list(codes[i:i + sub_size]) for i in range(0, len(codes), sub_size)]
        basic = mt.run_tasks(func=download_basic_worker, var_args=sub_code, en_bar=True,
                             desc='Down-Basic', merge_result=False)
        mt.run_tasks(func=save_basic_worker, var_args=basic, en_bar=True, desc='Save-Basic')
    if mode == 'info' or mode == 'all':
        sub_size = int((info_data.shape[0] + MAX_TASK_NUM) / MAX_TASK_NUM)
        sub_item = [list(info_data['code'][i:i + sub_size]) for i in range(0, info_data.shape[0], sub_size)]
        zt = mt.run_tasks(func=zt, var_args=sub_item, en_bar=True, desc='Cal-ZT')
        zb = mt.run_tasks(func=zb, var_args=sub_item, en_bar=True, desc='Cal-ZB')
        pcp = mt.run_tasks(func=pcp, var_args=sub_item, en_bar=True, desc='Cal-PCP')
        t = info_data.loc[:, ('code', 'outstanding')].values
        sub_item = [t[i:i + sub_size] for i in range(0, info_data.shape[0], sub_size)]
        tor = mt.run_tasks(func=tor, var_args=sub_item, en_bar=True, desc='Cal-TOR')
        ltsz = mt.run_tasks(func=ltsz, var_args=sub_item, en_bar=True, desc='Cal-LTSZ')

        updated_info = pd.concat([info_data,
                                  pd.Series(zt, name='zt'),
                                  pd.Series(zb, name='zb'),
                                  pd.Series(tor, name='tor'),
                                  pd.Series(pcp, name='pcp'),
                                  pd.Series(ltsz, name='ltsz')], axis=1)
        updated_info.to_csv(INFO_FILE, encoding='utf-8-sig')
    if mode == 'tips':
        import random
        multi = 0
        if multi:
            sub_size = int((len(codes) + MAX_TASK_NUM) / MAX_TASK_NUM)
            sub_code = [codes[i:i + sub_size] for i in range(0, len(codes), sub_size)]
            results = mt.run_tasks(func=download_tips_worker, var_args=sub_code,
                                   en_bar=True, desc='DownTips')
        else:
            results = []
            from tqdm import tqdm
            counter = 0
            for code in tqdm(codes, ascii=True, desc='DownTips'):
                aa = download_tips_worker(code)
                results.append(aa)
                sleep(random.randint(0, 6) * 0.1)
                if counter == 30:
                    counter = 0
                    sleep(1)
                else:
                    counter += 1
        try:
            with TimerCount('concept make time'):
                c = '\n'.join(list(map(lambda x:','.join((x['code'], ' '.join(x['concept']))), results)))
            with open(CONCEPT_FILE, 'w') as f:
                f.write(c)
        except Exception as err:
            print(err)
        sub_size = int((len(codes) + MAX_TASK_NUM) / MAX_TASK_NUM)
        sub_item = [results[i:i + sub_size] for i in range(0, len(results), sub_size)]
        mt.run_tasks(func=save_tips_worker, var_args=sub_item, fix_args=TIP_FILE,
                     en_bar=True, desc='Save-Tips')
        copy_diff_tips()

    mt.close_tasks()


if __name__ == '__main__':
    pass
    # save_tips_worker(download_tips_worker('300071'))
    # with TimerCount('Test of Download'):
    #     update_local_database('tips')
    # from selenium import webdriver
    # with TimerCount('selenium test'):
    #     url = THS_F10_URL.format('000760')
    #     driver = webdriver.Chrome()
    #     driver.get(url)
    #     data = driver.page_source.encode('utf-8', 'ignore')
    #
    # print(data)
