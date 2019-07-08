#!/usr/bin/env python
# coding: utf-8

import requests
import pandas as pd
from lxml import etree
import re
import json
import gevent
from gevent import monkey


monkey.patch_all()


def post_html(url, data):
    headers = {
        'Cookie': 'cusid=1562598643388; cusid=1562598643388; _ga=GA1.2.731925594.1562598644; _gid=GA1.2.1365770648.1562598644; cuvid=c3df43921f7c455ca6b315e7d01acae7; cuvon=1562598664441; __unam=9d675f1-16bd2231783-3c22be3a-6; PHPSESSID=db35q7jooadb0siucaeif26t91; _gali=hospitality',
        'authority': 'www.henselphelps.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36'
    }
    response = requests.post(url, headers=headers, data=data)
    response.encoding = response.apparent_encoding
    return response


def get_html(url):
    headers = {
        'Cookie': 'cusid=1562598643388; cusid=1562598643388; _ga=GA1.2.731925594.1562598644; _gid=GA1.2.1365770648.1562598644; cuvid=c3df43921f7c455ca6b315e7d01acae7; cuvon=1562598664441; __unam=9d675f1-16bd2231783-3c22be3a-6; PHPSESSID=db35q7jooadb0siucaeif26t91; _gali=hospitality',
        'authority': 'www.henselphelps.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    response.encoding = response.apparent_encoding
    return response


def get_infos(html):
    inner_obj = etree.HTML(html)

    content_reg = '//div[@class="small-wrapper about-project"]/p/text()'
    conts = inner_obj.xpath(content_reg)
    if len(conts) == 0:
        content = None
    else:
        content = '\n'.join([single_.strip().strip('&nbsp;')
                             for single_ in conts])

    facts_reg = '//div[@class="widget"]/ul/li'
    facts = inner_obj.xpath(facts_reg)
    if len(facts) == 0:
        fact = None
    else:
        fact = []
        for each_ in facts:
            key = each_.xpath('strong/text()')[0].strip()
            value = each_.xpath('span//text()')[0].strip()
            fact.append(key + ': ' + value)
        fact = '\n'.join(fact)

    return fact, content


def get_links(lists, Id):
    base_url = 'https://www.henselphelps.com/wp-admin/admin-ajax.php'
    data = {
        'protypeId': Id,
        'action': 'projectfilterAjax'
    }
    html = json.loads(post_html(base_url, data).text)['showHtml']
    split_one = html.split('\r\n\r\n\t\t\t<div')[1:]
    
    for each_one in split_one:
        inner_dict = {}
        type_ = each_one.split('<em>')[1].split(
            '</em>')[0].split('project')[0].split('case study')[0].strip()
        title_ = each_one.split('</span>')[0].split('<span>')[1].strip()
        link_ = each_one.split('a href=')[1].split('>')[0].strip().strip('"')

        inner_html = get_html(link_).text
        facts_, contents_ = get_infos(inner_html)

        inner_dict['type'] = type_
        inner_dict['title'] = title_
        inner_dict['link'] = link_
        inner_dict['facts'] = facts_
        inner_dict['contents'] = contents_

        lists.append(inner_dict)


item_lists = [4, 5, 6, 7, 43]

finals = []
gens = []
for item in item_lists:
    gens.append(gevent.spawn(get_links, finals, item))

gevent.joinall(gens)

df = pd.DataFrame(finals)
df.to_csv('./henselphelps.csv', index=False)

