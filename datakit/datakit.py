# -*- coding:utf-8 -*-
import os
import datetime
import pandas as pd
import numpy as np
import tushare as ts
from functools import reduce
from utility.log import log
from utility.task import MultiTasks
from utility.timekit import print_run_time
from setting.settings import sets


class DataKit:
    def __init__(self):
        self.ohlc_dict = {'open': 'first', 'close': 'last', 'high': 'max',
                          'low': 'min', 'volume': 'sum', 'code': 'last'}
        self.max_zt_days = 30
        self.max_zb_days = 30

    def gen_k_120(self, code):
        try:
            m60 = self.get_k(code, ktype='60')
            if m60 is not None:
                m60.set_index(['date'], inplace=True)
                if m60.shape[0] % 2 == 1:
                    pass
                m120 = m60.resample('120T').agg(self.ohlc_dict).dropna()
                new_index = m60.index[1::2]
                if new_index.shape[0] == m120.shape[0]:
                    file_name = os.path.join(sets.CSV_DIR, '{}_{}.csv'.format('min120', code))
                    m120.reset_index().to_csv(file_name, index=False)
                else:
                    pass
            else:
                pass
        except Exception as err:
            log.error('{}, {}'.format(code, err))

    def d_k_worker(self, code):
        datas = []
        # for kt in sets.KTYPE:
        #     datas.append(ts.get_k_data(code, ktype=kt, retry_count=99))
        datas.append(ts.get_k_data(code, ktype='D', retry_count=99))
        return {code: datas}

    def s_k_worker(self, stock):
        for code in stock:
            #for i in range(5):
            for i in range(1):
                file_name = os.path.join(sets.CSV_DIR, '{}_{}.csv'.format(sets.PERIORD_TAG[i], code))
                stock[code][i].to_csv(file_name, index=False)

    def zt(self, code):
        try:
            day = self.get_k(code)
            c = day.loc[:, 'close']
            zt = c.rolling(window=2).apply(func=lambda x: x[1] >= round(x[0] * 1.1, 2), raw=True)[::-1]
        except Exception as err:
            print(code)
            print(err)
            assert 0
        if len(zt) >= self.max_zt_days:
            ret = zt.values[:self.max_zt_days]
        else:
            ret = np.r_[zt.values, np.zeros(self.max_zt_days - len(zt))]
        return {code: ret}

    def zb(self, code):
        try:
            day = self.get_k(code)
            if len(day) == 1:
                return {code: np.zeros(self.max_zb_days)}
            c = day.loc[:, 'close']
            h = day.loc[:, 'high']
            c_h = (c.values != h.values)[1:]
            c = c[:-1]
            h = h[1:]
            c = c * 1.1
            c = c.rolling(window=1).apply(self.round, args=[2], raw=True)
            h = h.rolling(window=1).apply(self.round, args=[2], raw=True)
            zzb = ((h.values >= c.values) & c_h)[::-1]
            if not self.is_trade_time() and h.values[-1] >= c.values[-1] and c_h[-1] == False:
                if ts.get_realtime_quotes(code).loc[:, 'ask'].iloc[0] != '0.000':
                    zzb[0] = True
            zzb = zzb + 0
            if len(zzb) >= self.max_zb_days:
                ret = zzb[:self.max_zb_days]
            else:
                ret = np.r_[zzb, np.zeros(self.max_zb_days - len(zzb))]
            return {code: ret}
        except Exception as err:
            print(code)
            print(err)

    def round(self, val, ndigits):
        for _ in range(ndigits):
            val *= 10
        ret_val = int(val)
        if val >= ret_val + 0.5:
            ret_val += 1
        for _ in range(ndigits):
            ret_val /= 10
        return ret_val

    def is_trade_time(self):
        trade_date = self.get_trade_date_list()
        cur_date = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d')
        if cur_date not in trade_date:
            return False
        else:
            cur_time = datetime.datetime.strftime(datetime.datetime.now(), '%H:%M:%S')
            if ('11:30:00' > cur_time > '9:30:00') or ('15:00:00' > cur_time > '13:00:00'):
                return True
            else:
                return False

    def get_info(self, code, item):
        if not os.path.exists(sets.INFO_FILE):
            log.error('No local info file: {}!'.format(sets.INFO_FILE))
        infos = pd.read_csv(sets.INFO_FILE,
                            usecols=[item],
                            columns={'code': str}).set_index('code')
        return infos.loc[code, item]

    def get_codes(self):
        if not os.path.exists(sets.INFO_FILE):
            log.info('No local info file: {}, get all codes online.'.format(sets.INFO_FILE))
            ret = ts.get_stock_basics().index
        else:
            ret = pd.read_csv(sets.INFO_FILE, dtype={'code': str}).loc[:, 'code']
        return ret

    def get_k(self, code, ktype='D', ds='local'):
        valid_dates = self.get_trade_date_list()
        date = self.get_datetime_now()
        date_str = date.strftime('%Y-%m-%d')
        day_begin = pd.datetime(year=date.year, month=date.month, day=date.month, hour=9, minute=30)
        day_end = pd.datetime(year=date.year, month=date.month, day=date.month, hour=15, minute=30)
        if ds == 'online' and date_str in valid_dates and day_begin <= date <= day_end:
            return ts.get_k_data(code=code, ktype=ktype)
        else:
            file = os.path.join(sets.CSV_DIR, '{}_{}.csv'.\
                                format(sets.PERIORD_TAG[sets.KTYPE.index(ktype)], code))
            return pd.read_csv(file, parse_dates=['date']) if os.path.exists(file) else None

    def down_trade(self):
        if os.path.exists(sets.TRADE_DATE_FILE):
            return None
        df = ts.trade_cal()
        df = df[df['isOpen'] == 1]
        df.to_csv(sets.TRADE_DATE_FILE, columns=['calendarDate'], header=False,
                  index=False, encoding='utf-8-sig')

    def get_datetime_now(self, str_ret=False):
        now = pd.datetime.now()
        return now.strftime('%Y-%m-%d %H:%M:%S') if str_ret is True else now

    def get_valid_trade_date(self, delta=0):
        trade_dates = self.get_trade_date_list()
        cur_date = self.get_datetime_now()
        ret_date = None
        while True:
            if cur_date.strftime('%Y-%m-%d') in trade_dates:
                ret_date_idx = trade_dates.index(cur_date.strftime('%Y-%m-%d')) + delta
                ret_date = trade_dates[ret_date_idx]
                break
            else:
                cur_date += pd.Timedelta(days=-1)
        return ret_date

    def get_trade_date_list(self):
        if not os.path.exists(sets.TRADE_DATE_FILE):
            self.down_trade()
        return pd.read_csv(sets.TRADE_DATE_FILE, header=None).iloc[:, 0].values.tolist()

    @print_run_time
    def down_k(self):
        info = ts.get_today_all().sort_values(by='changepercent', ascending=False)
        info.drop_duplicates(inplace=True)
        # info = info[info['changepercent'] > 7]
        info = info[~info['name'].str.contains('ST')]
        info = info[~info['name'].str.contains('退市')]

        info.to_csv(sets.INFO_FILE, index=False, encoding='utf-8-sig')
        codes = list(info['code'])
        zt_codes = list(info[info['changepercent'] > 7]['code'])
        # codes = self.get_codes()[:200]
        self.down_trade()
        with MultiTasks() as mt:
            basic = mt.run_list_tasks(func=self.d_k_worker, var_args=codes, en_bar=True, desc='DownBasic')
            mt.run_list_tasks(func=self.s_k_worker, var_args=basic, en_bar=True, desc='SaveBasic')
            # mt.run_list_tasks(func=self.gen_k_120, var_args=codes, en_bar=True, desc='GenM120')
            res = mt.run_list_tasks(func=self.zt, var_args=zt_codes, en_bar=True, desc='GenZT')
            res = reduce(lambda x, y: {**x, **y}, res)
            df = pd.DataFrame(res).fillna(999)
            df.to_csv(sets.ZT_FILE, index=False)
            res = mt.run_list_tasks(func=self.zb, var_args=codes, en_bar=True, desc='GenZB')
            res = reduce(lambda x, y: {**x, **y}, res)
            res = pd.DataFrame(res).fillna(999)
            res.to_csv(sets.ZB_FILE, index=False)


data_kit = DataKit()


if __name__ == '__main__':
    # function test code
    data_kit.zb('600226')
    data_kit.down_k()
