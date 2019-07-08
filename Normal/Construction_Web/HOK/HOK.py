#!/usr/bin/env python
# coding: utf-8

import requests
import pandas as pd
from lxml import etree
import re


def getHtml(url):
    headers = {
        'Cookie': '__atssc=google%3B1; __utma=248915102.1454458327.1560219135.1560219135.1560219135.1; __utmc=248915102; __utmz=248915102.1560219135.1.1.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); __utmt=1; __atuvc=14%7C24; __atuvs=5cff0dff9219ee5900d; __utmb=248915102.14.10.1560219135',
        'Host': 'www.hok.com',
        'Referer': 'https://www.hok.com/design/service/architecture/adnoc-headquarters/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    response.encoding = response.apparent_encoding
    return response


def getInfos(html):
    reg_cont = '//div[@class="column-primary column wysiwyg-primary"]//text()'
    info_obj = etree.HTML(html)
    conts = info_obj.xpath(reg_cont)
    if len(conts) == 0:
        conts = None
    else:
        conts = '\n'.join(conts)

    reg_replace = re.compile('<.*?>|&.*?;|.*?">')
    reg_factors = re.compile(
        '<div class="column-small column wysiwyg-lists">(.*?)</div>')
    factors = re.findall(reg_factors, html)
    if len(factors) == 0:
        factors = None
    else:
        zeta = factors[0].split('<h5>')[1:]
        factors = ''
        for each in zeta:
            key = re.sub(reg_replace, ' ', each[: each.index('</h5><p>')])
            inner_value = each.split('</h5><p>')[1]
            inner_value = '\n'.join([jj.strip('<p>') for jj in inner_value.split('</p>')]).replace(
                '<br />', '\n').replace('&ndash;', '-').replace('&nbsp;', ' ').replace('&amp;', '&')
            inner_value = re.sub(reg_replace, '', inner_value)
            inner_value = '\n'.join([kk.strip()
                                     for kk in inner_value.split('\n')])
            factors += key + ': ' + inner_value + '\n'
        factors = factors.strip('\n')
    return [factors, conts]


def getLinks(html):
    obj = etree.HTML(html)
    reg_location = '//h6[@class="location"]/text()'
    reg_alls = re.compile('>Select a Project</option>(.*?)</select>')
    alls = re.findall(reg_alls, html)[0]
    locations = obj.xpath(reg_location)
    items = alls.split('</option><option')
    finalResult = []

    for kk, item in enumerate(items):
        item = item.split('</option>')[0]
        index_links = item.index('value=') + len('value="')
        index_value = item.index('">')
        item_title = item[index_value + 2:]
        item_link = 'https://www.hok.com' + item[index_links: index_value]
        inner_html = getHtml(item_link).text
        inner_info = getInfos(inner_html)
        innerResult = [item_title, locations[kk], item_link]
        innerResult.extend(inner_info)
        finalResult.append(innerResult)
    return finalResult


baseUrl = 'https://www.hok.com/design/service/architecture/'
OrigHtml = getHtml(baseUrl).text
result = getLinks(OrigHtml)

dataSave = pd.DataFrame(
    result, columns=['Title', 'Location', 'Link', 'Factors', 'Content'])
dataSave.to_csv('C:/Users/fred/desktop/HOK.csv', index=False)

