#!/usr/bin/env python
# coding: utf-8

import requests
import pandas as pd
from lxml import etree
import re
import gevent
from gevent import monkey
from urllib import parse
import json

monkey.patch_all()


def get_html(url):
    headers = {
        'Cookie': 'sucuri_cloudproxy_uuid_29232f6f8=556b4f084be81b3108dd16c8a1eef1c6; _ga=GA1.2.867706341.1562527044; _gid=GA1.2.1124933227.1562527044; PHPSESSID=g72qk5clc9csoglt74ldf39ij3; cookies-privacy=1',
        'authority': 'www.aecom.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    response.encoding = response.apparent_encoding
    return response


def parse_page(market):
    baseUrl = 'https://www.mortenson.com/projects?'
    data = {
        'industry': market,
    }
    x = parse.urlencode(data)
    final_url = baseUrl + x
    inner_html = get_html(final_url).text

    page_obj = etree.HTML(inner_html)
    id_reg = '//section[@class="container-project-footer"]/a/@data-parent-item-id'
    page_reg = '//section[@class="container-project-footer"]/span/text()'

    ids = page_obj.xpath(id_reg)[0].strip()
    max_page = int(page_obj.xpath(page_reg)[0].split('of')[-1].strip())

    name_reg = '//div[@class="overlay"]/span[1]/text()'
    location_reg = '//div[@class="overlay"]/span[2]/span/text()'
    link_reg = '//div[@class="overlay"]/a/@href'

    names = [single_.strip() for single_ in page_obj.xpath(name_reg)[:-1]]
    locations = page_obj.xpath(location_reg)[:-1]
    links = page_obj.xpath(link_reg)[:-1]

    return ids, max_page, names, links, locations


def create_url(ids, max_page, market):
    base_ = 'https://www.mortenson.com/Services/ScService.svc/GetProjectList?'
    numbers = max_page // 9

    zetas = []
    for i in range(1, numbers + 1):
        data = {
            'parentItemId': ids,
            'pageNumber': i,
            'industry': market
        }
        x_ = parse.urlencode(data)
        url_ = base_ + x_
        print(url_)
        json_html = json.loads(json.loads(get_html(url_).text)['d'])['Items']
        zetas.extend(json_html)
        
    return zetas


def get_infos(html):

    inner_obj = etree.HTML(html)

    cont_reg = '//div[@class="containerProjectBlock"]/p[position() > 1]'
    conts = inner_obj.xpath(cont_reg)
    conts = '\n'.join([ijk.xpath('string(.)').strip() for ijk in conts])

    all_ = html.split('<h3')[1:]
    facts = []
    for x_ in all_:
        key = x_.split('</h3>')[0].split('>')[-1].strip()
        value_reg = re.compile('>(.*?)</|/>\n(.*?)<br')
        values = re.findall(value_reg, x_.split('</div')[0])
        alpha = []
        for value in values[1:]:
            ijk = ''.join(value).split('</')[0].split('>')[-1]
            alpha.append(ijk)

        facts.append(key + ': ' + ', '.join(alpha))

    facts = '\n'.join(facts)

    return conts, facts


def get_links(lists, market):

    ids, max_page, top_9_names, top_9_links, top_9_locations = parse_page(
        market)

    for title, link, location in zip(top_9_names, top_9_links, top_9_locations):
        inner_dict = {}
        inner_dict['title'] = title
        inner_dict['location'] = location
        inner_dict['link'] = link

        inner_html = get_html(link).text
        print(link)
        content, fact = get_infos(inner_html)

        inner_dict['content'] = content
        inner_dict['fact '] = fact
        inner_dict['type'] = market

        lists.append(inner_dict)

    zetas = create_url(ids, max_page, market)
    for each_item in zetas:
        title = each_item['Title']
        location = each_item['Location']
        next_url = each_item['NavigationUrl']
        inner_html = get_html(next_url).text

        print(next_url)
        content, fact = get_infos(inner_html)

        inner_dict = {}
        inner_dict['title'] = title
        inner_dict['location'] = location
        inner_dict['link'] = link
        inner_dict['content'] = content
        inner_dict['fact '] = fact
        inner_dict['type'] = market
        lists.append(inner_dict)


item_lists = ['Healthcare', 'Federal Government', 'Higher Education']

finals = []
gens = []
for item in item_lists:
    gen = gevent.spawn(get_links, finals, item)
    gens.append(gen)

gevent.joinall(gens)

data = pd.DataFrame(finals)
data.to_csv('./mertenson.csv', index=False)

