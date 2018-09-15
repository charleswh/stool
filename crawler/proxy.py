import requests

def get_proxies():
    pass


def get_proxies_from_xici():
    xici_url = 'http://www.xicidaili.com/nt/'
    raw_ip = []
    vaild_ip = []
    max_page_num = 5
    for page in range(1, max_page_num):
        print('Scraw page {}'.format(page))
        url = xici_url + str(page)
        req = requests.get(url)

