#coding = utf - 8

import requests
from bs4 import BeautifulSoup
import re
from urllib.request import urlretrieve
import os

def get_html(url):
    head = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36'}

    response = requests.get(url,headers = head)
    response.raise_for_status()
    response.encoding = response.apparent_encoding
    return response


def get_info(html):
    Soup = BeautifulSoup(html,'lxml')
    content = Soup.select('div#plist option')
    html_title = []
    for each in content:
        html  = each.get('value')
        title = each.get_text()
        html_title.append({'html': 'https://www.bilibili.com' + html,'title':title})
    return html_title

def downloading(html_info):
    filename = os.getcwd() + "\\html.txt"
    with open(filename,'w+') as fp:
        for each in html_info:
            fp.write('\n')
            fp.write("-----------------\n")
            fp.write(each['html']+'\n')

url = 'https://www.bilibili.com/video/av28148692'
html = get_html(url).text
html_infos  = get_info(html)
downloading(html_infos)
