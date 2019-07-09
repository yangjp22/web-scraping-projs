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
        'Referer': 'https://structuretone.com/',
        'Cookie': 'nelioab_userid=7b1bc4a9-63af-41fc-8943-a177ced67b3c; _vwo_uuid_v2=D33ABADE527843AE17752CADA7B4B5A46|f7dd1c75e5206b766cb0e3bfbc8f1bc5; PHPSESSID=b89d9393e9bf7b48a8ebda36b6be7ce7; _gcl_au=1.1.623975361.1562619411; _ga=GA1.2.266236407.1562619411; _gid=GA1.2.1208055012.1562619411',
        #         'Host': 'structuretone.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36'
    }
    response = requests.get(url, headers=headers, verify=False)
    response.encoding = response.apparent_encoding
    return response


def post_html(url, data):
    headers = {
        'Referer': 'https://structuretone.com/',
        'Cookie': 'nelioab_userid=7b1bc4a9-63af-41fc-8943-a177ced67b3c; _vwo_uuid_v2=D33ABADE527843AE17752CADA7B4B5A46|f7dd1c75e5206b766cb0e3bfbc8f1bc5; PHPSESSID=b89d9393e9bf7b48a8ebda36b6be7ce7; _gcl_au=1.1.623975361.1562619411; _ga=GA1.2.266236407.1562619411; _gid=GA1.2.1208055012.1562619411',
        #         'Host': 'structuretone.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36'
    }
    response = requests.post(url, headers=headers, data =data, verify=False)
    response.encoding = response.apparent_encoding
    return response


def get_url(sector, location, security, page=1):
    base_url = 'https://structuretone.com/wp-admin/admin-ajax.php'
    data = {
        'action': 'load_posts_by_ajax',
        'page': page,
        'jsargs[post_type]': 'projects',
        'jsargs[posts_per_page]': 10,
        'jsargs[post_status]': 'publish',
        'jsargs[orderby]': 'date',
        'jsargs[order]': 'DESC',
        'jsargs[tax_query][0][taxonomy]': 'sectors',
        'jsargs[tax_query][0][field]': 'slug',
        'jsargs[tax_query][0][terms]': sector,
        'jsargs[tax_query][1][taxonomy]': 'locations',
        'jsargs[tax_query][1][field]': 'slug',
        'jsargs[tax_query][1][terms]': location,
        'jsargs[paged]': '1',
        'max_page': 'reset',
        'filterstatus': '1',
        'filter_values[]': sector,
        'filter_values[]': location,
        'security': security
    }
    html = post_html(base_url, data)

    return html


def get_page(sector, location, security):
    html = get_url(sector, location, security).text
    max_page = int(html.split('max_num_page')
                   [-1].split('}"')[0].split(':')[-1])
    for i in range(1, max_page + 1):
        page_html = get_url(sector, location, security, page=i).text
        yield page_html


def get_infos(html):
    inner_obj = etree.HTML(html)

    key_reg = '//div[@class="lftClmn"]/p/text()'
    value_reg = '//div[@class="rgtClmn"]'
    keys = inner_obj.xpath(key_reg)
    values = inner_obj.xpath(value_reg)
    if len(keys) == 0:
        fact = None
    else:
        fact = []
        for key_, value_ in zip(keys, values):
            key_ = key_.strip()
            value = ', '.join([single_.strip() for single_ in value_.xpath(
                'string(.)').strip().split('\r') if len(single_.split()) > 0])
            fact.append(key_ + ': ' + value)
        fact = '\n'.join(fact)

    return fact


def get_links(lists, sector, location, security):
    if get_page(sector, location, security) == None:
        pass
    else:
        for page_html in get_page(sector, location, security):
            links = page_html.split('<a href=')[1:]
            for link in links:
                inner_dict = {}
                link_ = link.replace('\\', '').split('"')[1]
                html_ = get_html(link_).text
                fact_ = get_infos(html_)
                inner_dict['fact'] = fact_
                inner_dict['link'] = link_
                inner_dict['type'] = sector
                lists.append(inner_dict)


item_dict = {'commercial': '61b61564ba', 'education': '94acb88b19', 'healthcare': '94acb88b19', 'residential': '94acb88b19'
             }
location = ['connecticut', 'massachusetts',
            'new-york', 'new-jersey', 'pennsylvania']

finals = []
gens = []
for loc in location:
    for key in item_dict:
        gens.append(gevent.spawn(get_links, finals, key, loc, item_dict[key]))

gevent.joinall(gens)

data = pd.DataFrame(finals)
data.to_csv('./structuretone.csv', index=False)





