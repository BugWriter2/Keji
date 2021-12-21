"""
Code is stolen from https://github.com/AnJT/mirai
"""

import asyncio
import json

import aiohttp
import re

import random
import time
import datetime
import requests
from fake_useragent import UserAgent
from bs4 import BeautifulSoup as BS


ua = UserAgent().random
print(ua)


def get_new_headers():
    headers = {"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
              "Accept-Encoding": "gzip, deflate, br",
              "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
              "User-Agent": ua}
    return headers

def get_new_cookies():
    url = 'https://v.sogou.com/v?ie=utf8&query=&p=40030600'
    # proxies = {"http": "http://" + '127.0.0.1:10808'}
    headers = {'User-Agent': ua}
    rst = requests.get(url=url,
                       headers=headers,
                       allow_redirects=False)
    cookies = rst.cookies.get_dict()
    return cookies
    
async def news_result(html):
    soup = BS(html, 'html.parser')
    ul = soup.find(class_="news-list")
    for li in ul.find_all('li'):
        try:
            url = li.a['href']
            div = li.find_all('div')[1]
            if div.div.a.text == '易即今日':
                print(f'url found: {url}')
                return url
            print(div.div.a.text)
        except Exception as e:
            print(e)

async def url_decode(r): 
    url = 'https://weixin.sogou.com' + r
    b = random.randint(0, 99)
    a = url.index('url=')
    a = url[a + 30 + b:a + 31 + b:]
    url += '&k=' + str(b) + '&h=' + a
    return url


async def search(session, cookies, headers, query):
    print(f'searching {query}...')
    url = 'https://weixin.sogou.com/weixin'
    params = {
        'type': 2,
        's_from': 'input',
        'ie': 'uft8',
        '_sug_': 'n',
        '_sug_type_': '',
        'query': query
    }
    async with session.get(url=url, params=params, headers=headers, cookies=cookies, ssl=False) as resp:
        html = await resp.text()  
        # print(html)
        url = await news_result(html)
        return url


async def getBriefing():
    async with aiohttp.ClientSession() as session:
        month = datetime.datetime.now().month
        day = datetime.datetime.now().day
        query = f'今日简报({month}月{day}日)易即今日'
        headers = get_new_headers()
        cookies = get_new_cookies()
        url = await search(session, cookies, headers, query)
        if url is None:
            query = f'“今日简报({month}月{day}日)” 易即今日'
            url = await search(session, cookies, headers, query)
        url = await url_decode(url)
        url = 'https://weixin.sogou.com/weixin'
        params = {
            'wx_fmt': 'jpeg'
        }  
        # print(cookies)
        async with session.get(url=url, params=params, ssl=False, cookies=cookies, headers=headers) as resp:
            text = await resp.text()
            # print(text)
            pattern = r"url \+= '(.*?)';"
            url_list = re.finditer(pattern, text, re.S)
            # print(url_list)
            url = ''
            for u in url_list:
                url += u.group(1)
            url = url.replace('http', 'https')
            # print(url)
        async with session.get(url=url, params=params, ssl=False, cookies=cookies, headers=headers) as resp:
            text = await resp.text()
            bs = BS(text, "html.parser")
            url = bs.find('div', id='img_list').img.get('src')
#             print(url)
        async with session.get(url=url,  ssl=False, cookies=cookies, headers=headers) as resp:
            with open('./output/img/news.jpg', 'wb') as file:
                bs = await toBtyes(resp)
                file.write(bs)
        
#         with open('./output/news.md', 'w') as file:
#                 file.write(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
#                 file.write('\n')
#                 file.write(f'![](./output/picture.jpg)')
    return 'output/img/news.jpg'


async def toBtyes(resp):
    empty_bytes = b''
    result = empty_bytes
    while True:
        chunk = await resp.content.read(8)
        if chunk == empty_bytes:
            break
        result += chunk
    return result


if __name__ == '__main__':
    asyncio.run(getBriefing())
