# -*- coding:utf-8 -*-
import os
import pandas as pd
import tushare as ts
from analysis import formula
from utility.log import log
from utility.task import MultiTasks
from utility.timekit import print_run_time
from setting.settings import CSV_DIR, INFO_FILE, TRADE_DATE_FILE, KTYPE, PERIORD_TAG



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
def down_local_data():
    info = ts.get_today_all().sort_values(by='changepercent', ascending=False)
    info.to_csv(INFO_FILE, index=False, encoding='utf-8-sig')
    codes = list(info['code'])
    download_trade_data()
    with MultiTasks() as mt:
        basic = mt.run_list_tasks(func=download_basic_worker, var_args=codes, en_bar=True,
                                  desc='Down-Basic')
        mt.run_list_tasks(func=save_basic_worker, var_args=basic, en_bar=True, desc='Save-Basic')


if __name__ == '__main__':
    down_local_data()
    # save_tips_worker(download_tips_worker('300071'))
    # with TimerCount('Test of Download'):
    #     down_local_data('tips')
    # from selenium import webdriver
    # with TimerCount('selenium test'):
    #     url = THS_F10_URL.format('000760')
    #     driver = webdriver.Chrome()
    #     driver.get(url)
    #     data = driver.page_source.encode('utf-8', 'ignore')
    #
    # print(data)
