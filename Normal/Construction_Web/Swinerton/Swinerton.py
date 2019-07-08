#!/usr/bin/env python
# coding: utf-8


import requests
import pandas as pd
from lxml import etree
import re
import gevent
from gevent import monkey
from urllib import parse


def gethtml(url):
    headers = {
        'Cookie': '_ga=GA1.2.1062770350.1562542561; _gid=GA1.2.420871618.1562542561; aviaCookieConsent=a6fe7a635a3ae90b600d28d9abace894',
        'authority': 'swinerton.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    response.encoding = response.apparent_encoding
    return response


def parse_page(item):
    baseUrl = 'https://swinerton.com/projects/?'
    data = {
        '_sft_market': item
    }
    x = parse.urlencode(data)
    final_url = baseUrl + x
    inner_html = gethtml(final_url).text
    return inner_html


def get_infos(html):
    inner_obj = etree.HTML(html)

    title_reg = '//div[@class="avia_textblock  "]/h3/text()'
    attribute_reg = '//div[@class="avia_textblock  "]/p'

    title = inner_obj.xpath(title_reg)
    if len(title) == 0:
        title = None
    else:
        title = title[0].strip()

    attributes = inner_obj.xpath(attribute_reg)
    if len(attributes) == 0:
        attribute = None

    else:
        attribute = []
        for single in attributes:
            one = single.xpath('string(.)')
            single = ': '.join([each.strip() for each in one.split('\n')])
            attribute.append(single)
        attribute = '\n'.join(attribute)

    return title, attribute


def get_links(item, lists):
    html = parse_page(item)
    obj = etree.HTML(html)

    link_reg = '//a[contains(@class, "av-masonry-entry ")]/@href'
    links = obj.xpath(link_reg)

    for link in links:
        print(link)
        inner_dict = {}
        inner_html = gethtml(link).text
        title, attributes = get_infos(inner_html)
        inner_dict['link'] = link
        inner_dict['type'] = item
        inner_dict['title'] = title
        inner_dict['attributes'] = attributes
        lists.append(inner_dict)


monkey.patch_all()
item_lists = ['education', 'government', 'healthcare', 'higher-education',
              'k-12-education', 'multifamily-residential', 'community-college']
gens = []
finals = []

for item in item_lists:
    gens.append(gevent.spawn(get_links, item, finals))

gevent.joinall(gens)

df = pd.DataFrame(finals)
df.to_csv('./Swinerton.csv', index=False)

