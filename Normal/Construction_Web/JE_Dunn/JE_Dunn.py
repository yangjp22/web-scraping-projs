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
        'Cookie': 'BIGipServer~HTTP-HTTPS~www.app~www_pool=!NUpeNlkpcZss/QpdCUGsZQibFLzLrcxNpuU+Z+MWdgFE7R7iHysdi9mxOkvYOnIMMwShCrNHaF6afe8=; has_js=1; _ga=GA1.2.1027011997.1562607077; _gid=GA1.2.1254186902.1562607077',
        'Host': 'www.jedunn.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    response.encoding = response.apparent_encoding
    return response


def max_page(item):
    url = 'https://www.jedunn.com/grid/count-callback/expertise-work/{}/all'.format(
        item)
    html = get_html(url).text
    page_obj = etree.HTML(html)
    page_reg = '//span[@class="teaser-results"]/text()'
    page = int(page_obj.xpath(page_reg)[0])

    return page


def generate_html(page, item):
    base_url = 'https://www.jedunn.com/grid/ajax-callback/expertise-work/{}/all?page={}'
    numbers = int(page // 12)
    html_s = []
    for i in range(numbers + 1):
        url_ = base_url.format(item, i)
        html__ = get_html(url_).text
        html_s.append(html__)
    return html_s


def get_infos(html):
    inner_obj = etree.HTML(html)

    content_reg = '//div[@class="field-items"]//p/text()'
    conts = inner_obj.xpath(content_reg)
    if len(conts) == 0:
        content = None
    else:
        content = '\n'.join([single_.strip() for single_ in conts])

    key_reg = '//span[contains(@class,"views-label views-label-field-")]/text()'
    value_reg = '//div[@class="field-content"]/text()'
    keys = inner_obj.xpath(key_reg)
    values = inner_obj.xpath(value_reg)
    if len(keys) == 0:
        attribute = None
    else:
        attribute = []
        for key_, value_ in zip(keys, values):
            attribute.append(key_.strip() + ': ' + value_.strip())
        attribute = '\n'.join(attribute)

    return attribute, content


def get_links(lists, item):

    page = max_page(item)
    all_htmls_ = generate_html(page, item)
    for each_html in all_htmls_ :
        each_obj = etree.HTML(each_html)
        all_reg = '//div[contains(@class, "grid-item size-")]'
        alls = each_obj.xpath(all_reg)[1:]
        for all_ in alls:
            inner_dict = {}
            link_ = all_.xpath('a/@href')[0].strip()
            type_ = all_.xpath('a/div/div[@class="tags"]/text()')[0].strip()
            title_ = all_.xpath('a/div[@class="info"]/p/text()')[0].strip()
            link_ = 'https://www.jedunn.com' + link_
            print(link_)
            html_ = get_html(link_).text
            attribute_, content_ = get_infos(html_)

            inner_dict['link'] = link_
            inner_dict['type'] = type_
            inner_dict['title'] = title_
            inner_dict['attribute'] = attribute_
            inner_dict['content'] = content_
       
            lists.append(inner_dict)


item_lists = ['mixed-use-retail', 'multi-family-residential', 'education','government-military','healthcare']

finals = []
gens = []
for item in item_lists:
    gen = gevent.spawn(get_links, finals, item)
    gens.append(gen)

gevent.joinall(gens)

data = pd.DataFrame(finals)
data.to_csv('./jedunn.csv', index=False)


