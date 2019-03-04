# coding: utf-8
import os
import sys
import html
from pprint import pprint
sys.path.append(os.getcwd())
import crawler.req_interface as req_i
# from crawler.wechatarticles.ReadOutfile import Reader
from crawler.wechatarticles import ArticlesAPI
from crawler.wechatarticles.GetUrls import PCUrls, MobileUrls
from setting.settings import sets


def flatten(x):
    return [y for l in x for y in flatten(l)] if type(x) is list else [x]


def transfer_url(url):
    url = html.unescape(html.unescape(url))
    return eval(repr(url).replace('\\', ''))


def get_all_urls(urls):
    url_lst = []
    for item in urls:
        url_lst.append(transfer_url(item['app_msg_ext_info']['content_url']))
        if 'multi_app_msg_item_list' in item['app_msg_ext_info'].keys():
            for ss in item['app_msg_ext_info']['multi_app_msg_item_list']:
                url_lst.append(transfer_url(ss['content_url']))

    return url_lst

#
# def wechat_cookie__appmsg_token():
#     appmsg_token, wechat_cookie = Reader().contral("")


def all_gzh_urls(key):
    if not os.path.exists(sets.MRZTBFP_PAPER_URLS):
        f = open(sets.MRZTBFP_PAPER_URLS, 'w')
        pre_urls = None
    else:
        with open(sets.MRZTBFP_PAPER_URLS, 'r') as f:
            pre_urls = f.read().split('\n')
        pre_urls = list(filter(None, pre_urls))
        pre_urls = None if len(pre_urls) == 0 else pre_urls
        f = open(sets.MRZTBFP_PAPER_URLS, 'w')
    t = PCUrls(biz=sets.BIZ, uin=sets.UIN, cookie=sets.WECHAT_COOKIE)
    count = 0
    url_lst = []
    while True:
        try:
            day_res = t.get_urls(key, offset=count)
        except Exception as err:
            break
        count += 10
        day_res = flatten(day_res)
        day_res = get_all_urls(day_res)
        url_lst.extend(day_res)
        if pre_urls is None:
            pass
        else:
            if pre_urls[0] in url_lst:
                pre_urls.insert(0, url_lst[:url_lst.index(pre_urls[0])])
                url_lst = pre_urls
                break
            else:
                pass
        print('get {} days...'.format(count))
    url_lst = list(filter(None, url_lst))
    if len(url_lst) > 0:
        f.write('\n'.join(url_lst))
    elif pre_urls is not None:
        f.write('\n'.join(pre_urls))
    f.close()


if __name__ == '__main__':
    all_gzh_urls(r'010620d4869b88b6a39280495cdd6f170e39873d711758ed4df1682a8e98c0082b5884507164c65922ddf8f0dcaca7ee2c6a561de18c969aa7b150390e3292f36ebe2eac8d1356c127674380f7d1c0bc')