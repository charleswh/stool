# coding: utf-8
import os
import sys
import html
from tqdm import tqdm
from pprint import pprint
sys.path.append(os.getcwd())
import crawler.req_interface as req_i
# from crawler.wechatarticles.ReadOutfile import Reader
from crawler.wechatarticles import ArticlesAPI
from crawler.wechatarticles.GetUrls import PCUrls, MobileUrls
from setting.settings import sets
from utility.timekit import sleep, int2time
from utility.log import log


def flatten(x):
    return [y for l in x for y in flatten(l)] if type(x) is list else [x]


def transfer_url(url):
    url = html.unescape(html.unescape(url))
    return eval(repr(url).replace('\\', ''))


def get_all_urls(urls, date=False):
    url_lst = []
    for item in urls:
        date_time = int2time(item['comm_msg_info']['datetime'])
        t = transfer_url(item['app_msg_ext_info']['content_url'])
        t = ','.join([date_time, t]) if date is True else t
        url_lst.append(t)
        if 'multi_app_msg_item_list' in item['app_msg_ext_info'].keys():
            for ss in item['app_msg_ext_info']['multi_app_msg_item_list']:
                t = transfer_url(ss['content_url'])
                t = ','.join([date_time, t]) if date is True else t
                url_lst.append(t)

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
    count = 660
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


def save2wiz(offset=0):
    if not os.path.exists(sets.MRZTBFP_PAPER_URLS):
        assert(0)
    with open(sets.MRZTBFP_PAPER_URLS, 'r') as f:
        urls = f.read().split('\n')[::-1]
    for url in tqdm(urls, ascii=True):
        idx = urls.index(url)
        if idx < offset:
            continue
        try:
            req_i.url2wiz(url)
        except Exception as err:
            log.info('Save fail: {}'.format(url))
            print(err)
            sleep(6)
        sleep(2)


if __name__ == '__main__':
    save2wiz()
    # all_gzh_urls(r'010620d4869b88b62bc8890f1271cb9ea5ae2e1a4ddffa1c54abf300c501b1329e8652ec4820c192eeeee284391fb2487c519ce1ef312cb02fb2bad527bbdd9ff8f8b3e7ae85a8c06f2bf08a3211356b')
