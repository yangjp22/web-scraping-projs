#!/usr/bin/env python
# coding: utf-8

import requests
import pandas as pd
from lxml import etree
import re
import gevent
from gevent import monkey
from urllib import parse

monkey.patch_all()


def get_html(url):
    headers = {
        'cookie': 'has_js=1; _ga=GA1.2.1715326010.1562612082; _gid=GA1.2.1111233499.1562612082',
        'authority': 'www.mccarthy.com',
        'user-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    response.encoding = response.apparent_encoding
    return response


def if_page(sector, page):
    url = 'https://www.mccarthy.com/projects/all?'
    data = {
        'loc': 'All',
        'sector': sector,
        'method': 'All',
        'page': page
    }
    x_ = parse.urlencode(data)
    final_url = url + x_
    html_ = get_html(final_url).text
    return 'Load more' in html_, html_


def parse_max_page(sector):
    page = 0
    page_existing,_ = if_page(sector, page)
    while page_existing:
        page += 1
        page_existing, _ = if_page(sector, page)
    return page


def get_lists(html):
    obj = etree.HTML(html)

    link_reg = '//li[@class=""]/a/@href'
    type_reg = '//span[@class="tag"]/text()'
    title_reg = '//h3/text()'

    links = obj.xpath(link_reg)
    types = obj.xpath(type_reg)
    titles = obj.xpath(title_reg)

    for link_, type_, title_ in zip(links, types, titles):
        yield link_.strip(), type_.strip(), title_.strip()


def get_infos(html):
    inner_obj = etree.HTML(html)

    location_reg = '//div[@class="content inner"]//span[@class="tag"]/text()'
    locations = inner_obj.xpath(location_reg)
    if len(locations) == 0:
        location = None
    else:
        location = locations[0].split('—')[-1].strip()

    conts_reg = '//div[@class="content inner"]//div[@class="field-items"]//p/text()'
    conts = inner_obj.xpath(conts_reg)
    if len(conts) == 0:
        content = None
    else:
        content = '\n'.join([single_.strip() for single_ in conts])

    key_reg = '//div[@class="content inner"]//h4/text()'
    value_reg = '//div[@class="content inner"]//ul'
    keys = inner_obj.xpath(key_reg)
    values = inner_obj.xpath(value_reg)
    if len(keys) == 0:
        fact = None
    else:
        fact = []
        for key_, value_ in zip(keys, values):
            value_s = ', '.join(
                [single_.strip() for single_ in value_.xpath('string(.)').split('\r')])
            fact.append(key_.strip() + ': ' + value_s)
        fact = '\n'.join(fact)
    
    return location, content, fact


def get_links(lists, sector):
    max_page = parse_max_page(sector)
    for i in range(max_page + 1):
        _, html_i = if_page(sector, i)
        for _link, _type, _title in get_lists(html_i):
            inner_dict = {}
            _link = 'https://www.mccarthy.com' + _link
            inner_html = get_html(_link).text
            _location, _content, _fact = get_infos(inner_html)
            
            inner_dict['link'] = _link
            inner_dict['type'] = _type
            inner_dict['title'] = _title
            inner_dict['location'] = _location
            inner_dict['content'] = _content
            inner_dict['fact'] = _fact
            lists.append(inner_dict)


item_dict = {'Education': 16, 'Commercial': 11,
             'Government': 31, 'Healthcare': 36, 'Research': 71}

finals = []
gens = []
for item in item_dict:
    gen = gevent.spawn(get_links, finals, item_dict[item])
    gens.append(gen)

gevent.joinall(gens)

data = pd.DataFrame(finals)
data.to_csv('./mccarthy.csv', index=False)

