#!/usr/bin/env python
# coding: utf-8

import requests
import pandas as pd
from lxml import etree
import re
from urllib import parse
import gevent
from gevent import monkey


def gethtml(url):
    headers = {
        'Cookie': 'has_js=1; _ga=GA1.2.1719013560.1562545535; _gid=GA1.2.1545089207.1562545535; device=3; device_type=0',
        'authority': 'www.clarkconstruction.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    response.encoding = response.apparent_encoding
    return response


def get_infos(html):

    inner_obj = etree.HTML(html)

    label_reg = '//div[@class="field-label"]'
    labels = inner_obj.xpath(label_reg)

    if len(labels) == 0:
        attributes = None
    else:
        combine = ''
        for each in labels:
            key = each.xpath('./text()')[0].strip()
            values = ' '.join([single.strip() for single in each.xpath(
                'string(./following-sibling::div[1])').split('\n')])
            values = values.split('Additional')[0]
            combine += key + values + '\n'
        attributes = combine.strip('\n')

    content_reg = '//div[contains(@class,"field-type-text-long")]'
    contents = inner_obj.xpath(content_reg)
    if len(contents) == 0:
        contents = None
    else:
        content = '\n'.join([single.xpath('string(.)').strip()
                             for single in contents])

    return attributes, content


def get_links(item, lists):
    baseUrl = 'https://www.clarkconstruction.com/our-work/sector/'
    final_url = baseUrl + item

    html = gethtml(final_url).text
    obj = etree.HTML(html)

    link_reg = '//span[@class="field-content"]/a/@href'
    title_reg = '//span[@class="field-content"]/a/text()'

    links = obj.xpath(link_reg)[45:]
    titles = obj.xpath(title_reg)[38:]

    for link, title in zip(links, titles):
        inner_dict = {}
        link = 'https://www.clarkconstruction.com' + link
        inner_html = gethtml(link).text
        attribute, content = get_infos(inner_html)
        inner_dict['type'] = item
        inner_dict['link'] = link
        inner_dict['attribute'] = attribute
        inner_dict['content'] = content
        inner_dict['title'] = title

        lists.append(inner_dict)



monkey.patch_all()

item_lists = ['government', 'education',
              'healthcare', 'mixed-use-retail', 'residential']
finals = []
gens = []

for item in item_lists:
    gens.append(gevent.spawn(get_links, item, finals))

gevent.joinall(gens)


df = pd.DataFrame(finals)
df.to_csv('./clark.csv', index=False)

