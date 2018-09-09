# coding=utf-8
# 伯拉爱空每日复盘解析，并保存为docx文档
import sys
import re
import os
import http.cookiejar
from urllib.request import HTTPCookieProcessor, build_opener, Request
from urllib.parse import urlencode
from urllib.error import URLError
from crawler.html_parser import parser
from crawler.output2docx import output2docx

HOME_URL = r'https://www.taoguba.com.cn/moreTopic?userID=252069'
HOST_URL = r'https://www.taoguba.com.cn/'
LOGIN_URL = r'https://www.taoguba.com.cn/newLogin'
COOKIE_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'cookie.txt')
PAPER_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'paper.txt')


def create_opener_online_save_cookie(login_url):
    cookie = http.cookiejar.MozillaCookieJar(COOKIE_FILE)
    handler = HTTPCookieProcessor(cookie)
    opener = build_opener(handler)

    info = {'userName': 'charleswh', 'pwd': '0q164b13'}
    postdata = urlencode(info).encode()
    user_agent = r'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ' \
                 r'(KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    headers = {'User-Agent': user_agent, 'Connection': 'keep-alive'}
    print('Try to login, URL = %s' % login_url)
    request = Request(login_url, postdata, headers)

    try:
        response = opener.open(request)
    except URLError as err:
        print('Error code = ', err.code, ':', err.reason)

    print('Login and get cookie successfully.')

    cookie.save(ignore_discard=True, ignore_expires=True)

    print('Save cookie to %s' % COOKIE_FILE)

    return opener


def create_opener_from_exist_cookie(cookie_file=None):
    if cookie_file is None:
        print('Cookie file error.')
        exit(0)
    cookie = http.cookiejar.MozillaCookieJar(cookie_file)
    cookie.load(cookie_file, ignore_discard=True, ignore_expires=True)
    print('Local cookie:')
    for item in cookie:
        print('Name: ', item.name, '\nValue: ', item.value)
    handler = HTTPCookieProcessor(cookie)
    opener = build_opener(handler)
    return opener


def get_sync_list(home_url, opener):
    request = Request(home_url)
    response = None
    try:
        response = opener.open(request)
    except URLError as err:
        print('Open page fail: ', home_url)
        print('Error code = ', err.code, ':', err.reason)

    content = response.read().decode('utf-8')
    pat = re.compile(r'<input type="hidden" name="pageNum" value="(.*)"/>')
    pageNum = int(pat.search(content).group(1))
    pat_paper = re.compile(r'<a.*(Article/.*/1).*title=.*</a>')
    paper_list = pat_paper.findall(content)

    print('Get paper links...')

    if not os.path.exists(PAPER_FILE):
        print(r'No local paper-link list, search all papers and create list...')
        for i in range(1, pageNum + 1):
            print('Process page %d...' % i)
            tmp = 'pageNum=%d&pageNo=%d&sortFlag=T&' % (pageNum, i)
            url_next = ''.join(
                [home_url[:home_url.find('?') + 1], tmp, home_url[home_url.find('?') + 1:]])
            request = Request(url_next)
            response = opener.open(request)
            content = response.read().decode('utf-8')
            paper_list.extend(pat_paper.findall(content))
        print('Saving paper links to local file...')
        with open(PAPER_FILE, 'w') as f:
            for paper in paper_list:
                print(paper, file=f)
        print('Save paper links done.')
    else:
        with open(PAPER_FILE, 'r+') as f:
            file_list = f.readlines()
            while True:
                if 'Article' not in file_list[0]:
                    file_list.pop(0)
                else:
                    break
        pre_paper_list = []
        for i in range(1, pageNum + 1):
            print('Process page %d...' % i)
            tmp = 'pageNum=%d&pageNo=%d&sortFlag=T&' % (pageNum, i)
            url_next = ''.join(
                [home_url[:home_url.find('?') + 1], tmp, home_url[home_url.find('?') + 1:]])
            request = Request(url_next)
            response = opener.open(request)
            content = response.read().decode('utf-8')
            paper_list = pat_paper.findall(content)
            pre_paper_list.extend(paper_list)
            try:
                index = pre_paper_list.index(file_list[0].strip())
                if index == 0:
                    return []
                paper_list = pre_paper_list[:index]
                tmp = '\n'.join(paper_list) + '\n'
                with open(PAPER_FILE, 'w') as f:
                    f.seek(0)
                    f.write(tmp)
                    f.writelines(file_list)
                break
            except ValueError as err:
                continue

    return paper_list


def blakfp_entry(argv=None):
    if not os.path.exists(COOKIE_FILE):
        print('No local cookie file, try to create...')
        opener = create_opener_online_save_cookie(LOGIN_URL)
    else:
        print('Loading local cookie...')
        opener = create_opener_from_exist_cookie(COOKIE_FILE)

    paper_list = get_sync_list(HOME_URL, opener)
    if len(paper_list) == 0:
        print('No new papers need to download.')
        exit(0)

    # paper_list = ['Article/1020181/1']
    paper_list.reverse()
    for paper in paper_list:
        print(paper, end='  ')
        paper_url = HOST_URL + paper
        request = Request(paper_url)
        html = opener.open(request).read().decode('utf-8')
        format_text = parser(html)
        filename = format_text.pop(0) + '.docx'
        output2docx(format_text, filename, opener)


if __name__ == '__main__':
    blakfp_entry()
