#!/usr/bin/env python
# coding: utf-8

import requests
import pandas as pd
from lxml import etree
import re
import gevent
from gevent import monkey


def getHtml(url):
    headers = {
        'Cookie': 'co=764; __utma=164819386.1948347344.1561496847.1561496847.1561496847.1; __utmc=164819386; __utmz=164819386.1561496847.1.1.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); __hstc=80211592.b3bc35c0093cdd56c74cb9e36cdf8673.1561496847282.1561496847282.1561496847282.1; hubspotutk=b3bc35c0093cdd56c74cb9e36cdf8673; __hssrc=1; __utmt=1; projectsPerPage=21; __atuvc=47%7C26; __atuvs=5d128d20b8ca4b8e02e; __utmb=164819386.48.10.1561496847; __hssc=80211592.48.1561496847282',
        'Host': 'www.turnerconstruction.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    response.encoding = response.apparent_encoding
    return response


def getMaxPage(html, url):
    page_str = 'pagination-list'
    if html.find(page_str) == -1:
        max_page = 1
    else:
        obj = etree.HTML(html)
        reg_page = '//div[@class="pagination-list"]/ul/li[last()- 1]/a/text()'
        max_page = int(obj.xpath(reg_page)[0])

    list_urls = [url + '/%s' % str(j) for j in range(1, max_page + 1)]
    return list_urls


def get_links(html, item):
    link_reg = '//ul[@class="featured-projects-list"]/li/p[1]/a/@href'
    name_reg = '//ul[@class="featured-projects-list"]/li/p[2]/a/text()'
    location_reg = '//ul[@class="featured-projects-list"]/li/p[3]/text()'

    obj = etree.HTML(html)
    links = obj.xpath(link_reg)
    names = obj.xpath(name_reg)
    locations = obj.xpath(location_reg)

    result = []
    for link, name, location in zip(links, names, locations):
        inner_link = 'http://www.turnerconstruction.com' + link
        info_html = getHtml(inner_link).text
        Infos = get_infos(info_html)
        info_dict = {}
        info_dict['Name'] = name
        info_dict['Location'] = location
        info_dict['Link'] = 'http://www.turnerconstruction.com' + link
        info_dict['Info'] = Infos[0]
        info_dict['Description'] = Infos[1]
        info_dict['Type'] = item
        result.append(info_dict)

    return result


def get_infos(html):
    inner_obj = etree.HTML(html)

    feature_reg = '//div[@class="project-description-div"]/ul/li'
    features = inner_obj.xpath(feature_reg)

    clients = []
    for each in features:
        key = each.xpath('./span/text()')
        key = key[0].strip()
        value = each.xpath('./strong/text()')
        if len(value) == 0:
            value = each.xpath('./a/text()')
            if len(value) == 0:
                value = ' '
            else:
                value = ', '.join([single.strip() for single in value])
        else:
            value = value[0].strip()
        clients.append(key + ': ' + value)
    clients = '\n'.join(clients)

    paragraph_reg = '//div[@id="content-side"]/p/text()'
    paragraphs = inner_obj.xpath(paragraph_reg)
    if len(paragraphs) == 0:
        paragraphs = None
    else:
        paragraphs = '\n'.join([single.strip() for single in paragraphs])

    return [clients, paragraphs]


def create_url(item, lists):
    base_url = 'http://www.turnerconstruction.com/experience/projects/'
    item_url = base_url + item + '/north-america'
    res = getHtml(item_url).text
    pages = getMaxPage(res, item_url)
    for page in pages:
        page_html = getHtml(page).text
        lists.extend(get_links(page_html, item))


monkey.patch_all()
item_lists = ['commercial', 'education', 'government',
              'healthcare', 'research-development', 'residential-hotel']
gens = []
final_list = []
for single_item in item_lists:
    gens.append(gevent.spawn(create_url, single_item, final_list))

gevent.joinall(gens)

df = pd.DataFrame(final_list)
df.to_csv('./turner.csv', index=False)

