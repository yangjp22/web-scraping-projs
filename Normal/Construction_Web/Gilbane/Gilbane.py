#!/usr/bin/env python
# coding: utf-8

import requests
from lxml import etree
import re
import pandas as pd
import gevent
from gevent import monkey


def download(url, params=None, datas=None, method='get'):
    if url is None:
        return
    sess = requests.Session()
    headers = {
        'cookie': 'wp-session=db36a0b93c0091e789f7188ad076ca6d; site-visited=yes; office-location=RI%2C%2CProvidence%2Chttps%3A%2F%2Fwww.gilbaneco.com%2Flocations%2Fprovidence-rhode-island%2F; _ga=GA1.2.1487181666.1561564106; _gid=GA1.2.259433025.1561564106; __atssc=google%3B1; __hstc=37448447.5e84b15e88c98f1ec4c4953bcae80c00.1561564108705.1561564108705.1561564108705.1; hubspotutk=5e84b15e88c98f1ec4c4953bcae80c00; __hssrc=1; tk_ai=woo%3ABUYxKl5aZplQogedenWWPK0E; project-location=0; _gat=1; __atuvc=17%7C26; __atuvs=5d13d43a3a33efc3001',
        'origin': 'https://www.gilbaneco.com',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36'
    }
    if method == 'get':
        response = sess.get(url, headers=headers, params=params)
    else:
        response = sess.post(url, headers=headers, data=datas)

    if response.status_code == 200:
        response.encoding = response.apparent_encoding
        return response
    else:
        return


def get_info(html):
    inner_obj = etree.HTML(html)

    content_reg = '//div[@class="project-content"]/p/text()'
    contents = inner_obj.xpath(content_reg)
    if len(contents) == 0:
        contents = None
    else:
        contents = '\n'.join([single.strip() for single in contents])

    stats_reg = '//div[@class="callout quickstats"]/div/dl/dd'
    first_stats = inner_obj.xpath(stats_reg)
    if len(first_stats) == 0:
        stats = None
    else:
        stats = []
        for item in first_stats:
            cont = ': '.join(
                [zeta.strip() for zeta in item.xpath('string(.)').strip().split(':')])
            stats.append(cont)
        stats = '\n'.join(stats)

    return stats, contents


def get_links(html, item_name):
    links = html.split('<a class=')[1:]
    infos = []
    for each in links:
        info_dict = {}
        each_link = ''.join(each.split('href=')[1].split('"')[
                            1].split('\\')).strip()
        each_html = download(each_link).text
        Stats, Content = get_info(each_html)
        info_dict['Link'] = each_link
        info_dict['Stats'] = Stats
        info_dict['Content'] = Content
        info_dict['Type'] = item_name
        infos.append(info_dict)
    return infos


def create_url(single_item, lists):
    base_url = 'https://www.gilbaneco.com/wp-admin/admin-ajax.php?action=filter_projects'
    datas = {'action': 'filter_projects',
             'filterMarket': single_item,
             'filterLocation': 0}
    html = download(base_url, datas=datas, method='post').text
    final = get_links(html, item_name)
    lists.extend(final)


item_lists = ['commercial-corporate', 'healthcare', 'k12-schools', 'mixed-use',
              'municipalgovernment', 'college-university', 'hotel-residential']
finals = []
gens = []
for item_name in item_lists:
    gens.append(gevent.spawn(create_url, item_name, finals))

monkey.patch_all()
gevent.joinall(gens)

df = pd.DataFrame(finals)
df.to_csv('./glibane.csv', index=False)

