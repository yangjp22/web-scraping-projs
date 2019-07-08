#!/usr/bin/env python
# coding: utf-8

import requests
import pandas as pd
from lxml import etree
import re


def getHtml(url):
    header = {
        'authority': 'www.hdrinc.com',
        'cookie': '_ga=GA1.2.1294019488.1560113939; _gid=GA1.2.582636237.1560113939; _hjIncludedInSample=1; cookie-agreed=2; _gat_UA-12552034-1=1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36'
    }
    response = requests.get(url, headers=header)
    response.encoding = response.status_code
    return response


def processItem(stuff):
    if len(stuff) == 0:
        return None
    else:
        return '\n'.join([each.strip() for each in stuff]).replace('m²', 'm2')


def getInfo(html):
    info_obj = etree.HTML(html)
    reg_content = '//div[1][@class="field field--name-body field--type-text-with-summary field--label-hidden field__item"]'
    reg_size = '//div[@class="field field--name-field-project-size field--type-string field--label-above"]//div[@class="field__item"]/text()'
    reg_certification = '//div[@class="field field--name-field-project-certifications field--type-string field--label-above"]//div[@class="field__item"]//text()'
    reg_markets = '//div[@class="field field--name-field-markets field--type-entity-reference field--label-above"]//div[@class="field__item"]//text()'
    reg_services = '//div[@class="field field--name-field-services field--type-entity-reference field--label-above"]//div[@class="field__item"]//text()'
    reg_subservices = '//div[@class="field field--name-field-subservices field--type-entity-reference field--label-above"]//div[@class="field__item"]//text()'

    content_tag = info_obj.xpath(reg_content)[0]
    content = content_tag.xpath('//p//text()')
    content = processItem(content[:-7])

    sizes = info_obj.xpath(reg_size)
    sizes = processItem(sizes)

    certifications = info_obj.xpath(reg_certification)
    certifications = processItem(certifications)

    markets = info_obj.xpath(reg_markets)
    markets = processItem(markets)

    services = info_obj.xpath(reg_services)
    services = processItem(services)

    subservices = info_obj.xpath(reg_subservices)
    subservices = processItem(subservices)

    return [sizes, markets, services, subservices, certifications, content]


def getLinks(html):
    obj = etree.HTML(html)
    reg_link = '//td[@headers="view-title-table-column"]/a/@href'
    reg_title = '//td[@headers="view-title-table-column"]/a/text()'
    reg_location = '//td[@headers="view-field-location-table-column"]//span/text()'
    reg_client = '//td[@headers="view-field-project-client-table-column"]//text()'

    titles = obj.xpath(reg_title)

    locations = obj.xpath(reg_location)
    length = int(len(locations) / 3)
    location = []
    for i in range(length):
        location.append(locations[3*i].strip() + ', ' + locations[3 *
                                                                  i + 1].strip() + ' ' + locations[3*i + 2].strip())
    locations = location

    clients = obj.xpath(reg_client)
    clients = [each.strip() for each in clients]

    links = obj.xpath(reg_link)
    base_link = 'https://www.hdrinc.com'
    next_links = [base_link + each for each in links]

    finalResult = []

    for order, single in enumerate(next_links):
        single_html = getHtml(single).text
        result = getInfo(single_html)
        single_result = [titles[order], locations[order], clients[order]]
        single_result.extend(result)
        finalResult.append(single_result)
    return finalResult


url = 'https://www.hdrinc.com/portfolio-list?market=&service=97&location=US'
original = getHtml(url).text
results = getLinks(original)


dataSave = pd.DataFrame(results, columns=[
                        'Title', 'Location', 'Client', 'Size', 'Market', 'Service', 'Subservice', 'Certification', 'Description'])
dataSave.to_csv('C:/Users/fred/desktop/HDR.csv', index=False)




