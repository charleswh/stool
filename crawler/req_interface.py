import requests
import random
from urllib import parse
from setting.settings import sets
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class WebChrome(object):
    def __init__(self):
        self.brower = None

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def start(self):
        opt = Options()
        opt.add_argument('--headless')
        opt.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
        self.brower = webdriver.Chrome(sets.CHROME_EXE, options=opt)

    def close(self):
        self.brower.quit()

    def get(self, url):
        self.brower.get(url)
        return self.brower.page_source


def get_random_header():
    headers = {'User-Agent': random.choice(sets.USER_AGENTS),
               'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
               'Accept-Encoding': 'gzip'}
    return headers


def web_req(url, params=None, proxy=None, timeout=None, cookie=None):
    return requests.get(url, params=params, headers=get_random_header(), proxies=proxy, timeout=timeout)

# def web_chrome(url, need_brower=False):
# #     opt = Options()
# #     opt.add_argument('--headless')
# #     opt.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
# #     brower = webdriver.Chrome(sets.CHROME_EXE, options=opt)
# #     brower.get(url)
# #     content = brower.page_source
# #     if need_brower:
# #         return content, brower
# #     else:
# #         brower.quit()
# #         return content

def url2wiz(url):
    url = parse.quote(url)
    url = url.replace('/', '%2F')
    t = r'http://note.wiz.cn/url2wiz?url={}&folder=%2F{}%2F&user={}&content-only=false'
    t = t.format(url, 'tmp', 'charleswh')
    with WebChrome() as wc:
        wc.get(t)
    # web_chrome(t)
