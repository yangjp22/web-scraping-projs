#!/usr/bin/env python
# coding: utf-8

import requests
import pandas as pd
from lxml import etree
import re
import gevent
from gevent import monkey
from urllib import parse


def getHtml(url):
    headers = {
        'Cookie': '__cfduid=d1623f4d7911ad55e242e9e220c21dbbf1562507100; _ga=GA1.2.1495779873.1562507105; _gid=GA1.2.1919867462.1562507105; ASP.NET_SessionId=2wppyyej311dketw5gqaigpq; ARRAffinity=5eeab78d6455543a22f554067b5ffc2554ae5a81fdb79bf3895f6432e74245ad; ai_user=e3lZW|2019-07-07T13:45:14.230Z; Skanska.NW.CookiesAccepted.31276=1; __atuvc=11%7C28; __atuvs=5d22075063dad9ea006; ai_session=bBO60|1562511057404|1562511373544.515',
        'authority': 'www.usa.skanska.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    response.encoding = response.apparent_encoding
    return response


def parse_page(one, two=None, take=8):
    baseUrl = 'https://www.usa.skanska.com/api/projectsearch?'
    data = {
        'Language': 'en-US',
        'SearchQuery': '',
        'SearchYear': '',
        'SectionFilters': '',
        'Skip': 0,
        'Take': take,
        'Cache': False,
        'epslanguage': 'en-US',
        'ExcludeByDataBaseId': 0,
        'SortOrder': 'PublishedDate',
        'CategoryFilter[]': one,
        'CategoryFilter*': two
    }
    x = parse.urlencode(data)
    if two == None:
        final_url = baseUrl + x.split('CategoryFilter%2A')[0].strip("&")

    else:
        final_url = baseUrl + x.replace('%2A', '%5B%5D')

    inner_html = getHtml(final_url).json()

    return inner_html


def get_infos(html):

    fact_reg = '//div[@class="info-box"]/div'
    obj = etree.HTML(html)
    facts = obj.xpath(fact_reg)

    if len(facts) == 0:
        facts = None
    else:
        fact = []
        for item in facts:
            cont = '\n'.join([single.strip() for single in item.xpath(
                'string(.)').strip().split('\n')])
            fact.append(cont)
        facts = '\n'.join(fact)

    return facts


def parse_links(name, inner_html):
    projects = inner_html['ProjectHits']
    inner_items = []
    for each in projects:
        inner_dict = {}
        url = 'https://www.usa.skanska.com' + each['SearchHitUrl']
        city = each['City']
        clientname = ','.join(each['ClientNames'])
        content = each['ProjectTranslation']['Description'].replace(
            '<p>', '').replace('</p>', '')
        facts = get_infos(getHtml(url).text)
        inner_dict['city'] = city
        inner_dict['clientname'] = clientname
        inner_dict['content'] = content
        inner_dict['type'] = name
        inner_dict['facts'] = facts
        inner_items.append(inner_dict)
    return inner_items


def crwaler(name, lists, one, two=None):
    page = parse_page(one, two)['TotalMatching']
    new_html = parse_page(one, two, take=page)
    links = parse_links(name, new_html)
    lists.extend(links)


monkey.patch_all()
item_dict = {'Mixed Use': [314, 317], 'Commercial': [342, 535],
             'Government': [354, None], 'Higher Education': [107, 329],
             'K-12 Education': [654, 106], 'Hotel': [236, None],
             'Hospital': [561, 39]}
finals = []
gens = []
for key in item_dict:
    gen = gevent.spawn(crwaler, key, finals,
                       item_dict[key][0], two=item_dict[key][1])
    gens.append(gen)

gevent.joinall(gens)

data = pd.DataFrame(finals)
data.to_csv('./skanska.csv', index=False)

