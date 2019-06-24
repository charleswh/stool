import re
import json
from crawler.req_interface import WebChrome
import urllib.parse
from utility.timekit import print_run_time
from setting.settings import sets
from utility.misc import exclude_item_in_B


class WenCai(object):
    def __init__(self):
        self.chrome = WebChrome()
        self.chrome.start()
        self.base = 'http://www.iwencai.com/stockpick/search?typed=0&f=1&qs=result_original&tid=stockpick&ts=1&w={}'

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.chrome.close()

    def get(self, ask_str):
        urlcoded_str = urllib.parse.quote(ask_str.encode())
        url = self.base.format(urlcoded_str)
        content = self.chrome.get(url)
        cc = self.chrome.get(r'http://www.iwencai.com/stockpick/cache?token=f8eed7f55feed6c2d0cdb8506a88b2ee&p=1&perpage=70&changeperpage=1&showType=[%22%22,%22%22,%22onTable%22,%22onTable%22,%22onTable%22,%22onTable%22,%22onTable%22,%22onTable%22,%22onTable%22,%22onTable%22')
        match = re.search(r'allResult = {(.+)};', content)
        if not match:
            print('No matched js data!')
            assert(0)
        js_data = str(match.group(1))
        js_data = '{{{}}}'.format(js_data)
        js_decode = json.loads(js_data)
        wccode2hq = js_decode['wccode2hq']
        # title = list(map(lambda x:x.replace('&lt;br&gt;', ''), js_decode['title']))
        # result = js_decode['result']
        ret_codes = list(x[0] for x in wccode2hq.values())
        return ret_codes

    def get_multi(self, ask_str_list):
        ret_codes_list = list(map(self.get, ask_str_list))
        return ret_codes_list

    def ask_basic_and_gen_blk(self):
        xingu = self.get(r'上市天数<20个，开板天数(新股)<=0')
        lb_1 = self.get(r'连续涨停天数=1，非st，未停牌')
        lb_2 = self.get(r'连续涨停天数=2，非st，未停牌')
        lb_3 = self.get(r'连续涨停天数=3，非st，未停牌')
        lb_4 = self.get(r'连续涨停天数=2，非st，未停牌')
        zb = self.get(r'最高价等于涨停价，收盘价不等于涨停价，非st')
        lb_1 = exclude_item_in_B(lb_1, xingu)
        lb_2 = exclude_item_in_B(lb_1, xingu)
        lb_3 = exclude_item_in_B(lb_1, xingu)
        lb_4 = exclude_item_in_B(lb_1, xingu)
        zt = lb_1 + lb_2 + lb_3 + lb_4
        lb = lb_2 + lb_3 + lb_4

        # TODO:
        # r'非st，非停牌，概念'


def main():
    args = '本周板块指数创新高 本周成交量/上周成交量 周阳线 由高到低排序'
    args = '板块指数 本周成交量/上周成交量 由高到低排序 周阳线'
    args = '振幅大于14，涨跌幅大于5%，最高价等于涨停价'
    # 所属概念包含XXX 本周成交量/上周成交量 由高到低 周阳线
    # args = '所属概念包含白马股'
    aa = WenCai()
    cc = aa.get('非st，非停牌，主营业务')
    bb = aa.get_multi(['板块指数 本周成交量/上周成交量 由高到低排序 周阳线',
                       '振幅大于14，涨跌幅大于5%，最高价等于涨停价'])
    b = 0


if __name__ == '__main__':
    main()
