#!/usr/bin/env python
# coding: utf-8

import requests
import pandas as pd
import re
from lxml import etree


def getHtml(url):
    header = {
        'Referer': 'https://www.ibigroup.com/services/architecture/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36'
    }
    response = requests.get(url, headers=header)
    response.encoding = response.apparent_encoding
    return response


def getInfo(html):
    reg_client = re.compile('<h6>Client</h6>(.*?)<div')
    if len(re.findall(reg_client, html)) != 0:
        clients = re.findall(reg_client, html)[0]
    else:
        clients = None

    reg_types = re.compile(
        '<h3>Services and Project Types</h3>.*?<li>(.*?)</ul>')
    if len(re.findall(reg_types, html)) != 0:
        types = re.findall(reg_types, html)[0].split('</li></a>')[:-1]
        types = '\n'.join([single.split('<li>')[-1] for single in types])
    else:
        types = None

    reg_leaders = re.compile('Project Leaders<(.*?)</div></div></div></div>')
    if len(re.findall(reg_leaders, html)) != 0:
        leaders = re.findall(reg_leaders, html)[0].split('<h3>')[1:]
        comBins = []
        for i_leader in leaders:
            name = i_leader.split('</h3><p>')[0]
            position = i_leader.split('</h3><p>')[1].split('<br>')[0]
            combine = name + ': ' + position
            comBins.append(combine)
        leaders = '\n'.join(comBins)
    else:
        leaders = None

    lxml_obj = etree.HTML(html)
    reg_title = '//ul[@id="breadcrumbs"]/following-sibling::p[1]//text()'
    introduction = lxml_obj.xpath(reg_title)
    introduction = ''.join(introduction).replace(
        '’', "'").replace(' “', ' "').replace('” ', '" ')
    reg_info = '//div[@class="fast-fact__item"]/span/text()'
    inner_infos = lxml_obj.xpath(reg_info)
    infos = []
    length = int(len(inner_infos) / 2)
    for ij in range(length):
        key = inner_infos[2 * ij + 1]
        value = inner_infos[2 * ij]
        infos.append(key + ': ' + value)
    infos = '\n'.join(infos)

    return [clients, types, infos, leaders, introduction]


def getLinks(html):
    obj = etree.HTML(html)
    reg_links = '//div[@class="filter-item__inner__title"]/a/@href'
    reg_titles = '//div[@class="filter-item__inner__title"]/a/h3/text()'
    reg_locations = '//div[@class="filter-item__inner__title"]/span/text()'
    
    links = obj.xpath(reg_links)
    titles = obj.xpath(reg_titles)
    locations = obj.xpath(reg_locations)
    
    finalResult = []
    for i, each in enumerate(links):
        each_html = getHtml(each).text
        zeta = [titles[i], locations[i]]
        zeta.extend(getInfo(each_html))
        finalResult.append(zeta)
        
    return finalResult


baseUrl = 'https://www.ibigroup.com/projects/?&tags=architecture,&regions=north%20america,'
orig = getHtml(baseUrl).text
result = getLinks(orig)

resultSave = pd.DataFrame(result, columns=[
                          'Titles', 'Location', 'Client', 'Type', 'Info', 'Leader', 'Introduction'])
resultSave.to_csv('C:/Users/fred/desktop/IBI.csv', index=False)

