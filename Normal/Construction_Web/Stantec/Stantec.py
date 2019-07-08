#!/usr/bin/env python
# coding: utf-8

import requests
import re
from lxml import etree
import pandas as pd


def getHtml(url, params=None):
    headers = {
        'Cookie': 'language=en; _ga=GA1.2.1395522767.1560196786; _gid=GA1.2.372820212.1560196786; _fbp=fb.1.1560196785986.898141374; region=localization:north-america; _hjIncludedInSample=1',
        'Host': 'www.stantec.com',
        'Referer': 'https://www.stantec.com/en/services/landscape-architecture/Projects',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36'
    }
    response = requests.get(url, headers=headers, params=params)
    response.encoding = response.apparent_encoding
    return response


def getInfo(html):
    obj = etree.HTML(html)

    reg_stats_key = '//div[@class="project-overview-module__stats-number"]/text()'
    reg_stats_value = '//p[@class="project-overview-module__stats-caption"]/text()'
    
    stats_key = obj.xpath(reg_stats_key)
    if len(stats_key) == 0:
        final_stats = None
    else:
        stats_value = obj.xpath(reg_stats_value)
        final_stats = ''
        for key, value in zip(stats_key, stats_value):
            final_stats += value.strip() + ': ' + key.strip() + '\n'
        final_stats = final_stats.strip('\n')

    reg_headtitle = '//h3[@class="two-column__headline"]/text()'
    reg_content = '//div[@class="two-column__body"]/p/text()'

    title = obj.xpath(reg_headtitle)
    if len(title) == 0:
        title = None
    else:
        title = ''.join([eachtitle.strip() for eachtitle in title])

    content = obj.xpath(reg_content)
    if len(content) == 0:
        content = None
    else:
        content = '\n'.join([eachii.strip() for eachii in content])

    reg_name = '//dt//text()'
    reg_value = re.compile('<dd>(.*?)</dd>', re.S)
    name = obj.xpath(reg_name)
    final_item = None
    if len(name) != 0:
        value = re.findall(reg_value, html)
        final_item = ''
        for item_name, item_value in zip(name, value):
            medir = '\n'.join(
                [eachitem.strip() for eachitem in item_value.split('\n') if '>' not in eachitem])
            final_item += item_name.strip() + ': ' + medir + '\n'
        final_item.strip('\n')

    return [final_stats, title, content, final_item]


def getLinks(html):
    items = html['pages']
    finalResult = []
    for item in items:
        headline = item['headline']
        subhead = item['subhead']
        lede = item['lede']
        link = 'https://www.stantec.com' + item['link']
        inner_html = getHtml(link).text
        inner_result = getInfo(inner_html)
        hbc = [headline, subhead, lede, link]
        hbc.extend(inner_result)
        finalResult.append(hbc)
    return finalResult


baseUrl = 'https://www.stantec.com/content/stantec/en/services/architecture-interior-design/projects/_jcr_content.more.json'
param = {'currPage': 1}
Original = getHtml(baseUrl, params=param).json()
total = Original['totalResults']
numbers = total // 42 + 1
Result = []
for ii in range(1, numbers + 1):
    param = {'currPage': ii}
    ii_html = getHtml(baseUrl, params=param).json()
    joke = getLinks(ii_html)

    Result.extend(joke)
    

dataSave = pd.DataFrame(Result, columns=[
                        'Headline', 'Subhead', 'Lede', 'Link', 'Stats', 'Title', 'Content', 'Item'])
dataSave.to_csv('../Stantec.csv', index=False)

