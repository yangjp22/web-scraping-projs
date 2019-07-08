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
        'Cookie': 'sucuri_cloudproxy_uuid_29232f6f8=556b4f084be81b3108dd16c8a1eef1c6; _ga=GA1.2.867706341.1562527044; _gid=GA1.2.1124933227.1562527044; PHPSESSID=g72qk5clc9csoglt74ldf39ij3; cookies-privacy=1',
        'authority': 'www.aecom.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    response.encoding = response.apparent_encoding
    return response


def parse_page(market, page=1):
    baseUrl = 'https://www.aecom.com/projects/?'
    data = {
        'ql[]': 199,
        'qm[]': market,
        'pp': page
    }
    x = parse.urlencode(data)
    final_url = baseUrl + x
    inner_html = getHtml(final_url).text
    return inner_html


def get_infos(html):
    inner_obj = etree.HTML(html)

    cont_reg = '//div[@class="entry-content"]/p/text()'
    conts = inner_obj.xpath(cont_reg)
    conts = '\n'.join([single.strip() for single in conts])

    service_reg = '//aside[@class="related-services"]/ul//text()'
    services = inner_obj.xpath(service_reg)
    services = '\n'.join([single.strip() for single in services])

    location_reg = '//span[@class="aecom-project-location"]/text()'
    locations = inner_obj.xpath(location_reg)[0]
    return services, conts, locations


def get_links(lists, name, market):
    page = 1
    html = parse_page(market, page)
    while 'Load more' in html:
        page += 1
        html = parse_page(market, page)

    obj = etree.HTML(html)

    link_reg = '//li[@class="grid-item"]'
    links = obj.xpath(link_reg)

    result = []
    for each in links:
        inner_dict = {}
        link = each.xpath('./a/@href')[0]
        title = each.xpath('./a/span/text()')[0].strip()
        html_ = getHtml(link).text
        service, contents, locations = get_infos(html_)
        inner_dict['type'] = name
        inner_dict['link'] = link
        inner_dict['title'] = title
        inner_dict['services'] = service
        inner_dict['content'] = contents
        inner_dict['location'] = locations
        result.append(inner_dict)

    lists.extend(result)


monkey.patch_all()
item_dict = {
    'Commercial & Residential': '2452', 'Education': '2457', 'Healthcare': '2463', 'Hotel': '2631', 'Government': '23456'
}
finals = []
gens = []

for key in item_dict:
    gen = gevent.spawn(get_links, finals, key, item_dict[key])
    gens.append(gen)

gevent.joinall(gens)

data = pd.DataFrame(finals)
data.to_csv('./aecom.csv', index=False)

