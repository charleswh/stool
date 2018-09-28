# -*- coding:utf-8 -*-
import os
import pandas as pd
import tushare as ts
from analysis import formula
from crawler.tips import down_tips, TIP_FILE
from utility.log import log
from utility.task import MultiTasks
from utility.timekit import sleep, print_run_time
from setting.settings import CSV_DIR, INFO_FILE, CONCEPT_FILE, TRADE_DATE_FILE, \
    MAX_TASK_NUM, KTYPE, PERIORD_TAG

FILE_ROOT = os.path.dirname(os.path.realpath(__file__))
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
    if not os.path.exists(INFO_FILE):
        log.info('No local info file: {}, get all codes online.'.format(INFO_FILE))
        ret = ts.get_stock_basics().index
    else:
        ret = pd.read_csv(INFO_FILE, dtype={'code': str}).loc[:, 'code']
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
        basic = mt.run_list_tasks(func=download_basic_worker, var_args=codes, en_bar=True,
                                  desc='Down-Basic')
        mt.run_list_tasks(func=save_basic_worker, var_args=basic, en_bar=True, desc='Save-Basic')
    if mode == 'info' or mode == 'all':
        zt = mt.run_list_tasks(func=formula.zt, var_args=info_data.shape[0], en_bar=True,
                               desc='Cal-ZT')
        zb = mt.run_list_tasks(func=formula.zb, var_args=info_data.shape[0], en_bar=True,
                               desc='Cal-ZB')
        pcp = mt.run_list_tasks(func=formula.pcp, var_args=info_data.shape[0], en_bar=True,
                                desc='Cal-PCP')
        t = info_data.loc[:, ('code', 'outstanding')].values
        tor = mt.run_list_tasks(func=formula.tor, var_args=t, en_bar=True, desc='Cal-TOR')
        ltsz = mt.run_list_tasks(func=formula.ltsz, var_args=t, en_bar=True, desc='Cal-LTSZ')

        updated_info = pd.concat([info_data,
                                  pd.Series(zt, name='zt'),
                                  pd.Series(zb, name='zb'),
                                  pd.Series(tor, name='tor'),
                                  pd.Series(pcp, name='pcp'),
                                  pd.Series(ltsz, name='ltsz')], axis=1)
        updated_info.to_csv(INFO_FILE, encoding='utf-8-sig')
    if mode == 'tips':
        down_tips(codes)
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
