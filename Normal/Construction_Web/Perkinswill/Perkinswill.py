#!/usr/bin/env python
# coding: utf-8

import requests
import re
from lxml import etree

def getHtml(url):
    response = requests.get(url)
    response.encoding = response.apparent_encoding
    return response.text

baseUrl = 'https://perkinswill.com/work/Architecture?'
baseHtml = getHtml(baseUrl)
baseOri = etree.HTML(baseHtml )
resultInnerURL = baseOri.xpath('//span[@class="field-content"]/a/@href')
resultTitle = baseOri.xpath('//span[@class="field-content"]/a/text()')
resultURL = ['https://perkinswill.com' + each for each in resultInnerURL]
# print(resultURL)
# print(resultTitle)

def processItem(html):
    Title = html.xpath('//div[@class="project-description__title"]/text()')
    if len(Title) == 0:
        Title = None
    else:
        Title = Title[0]
    
    subTitle = html.xpath('//div[@class="field-subtitle"]/text()') 
    if len(subTitle) == 0:
        subTitle = None
    else:
        subTitle = subTitle[0].strip()
    
    Location = html.xpath('//div[@class="project-description__location"]/text()')
    if len(Location) == 0:
        Location = None
    else:
        Location = Location[0].strip()

    Stats = html.xpath('//div[@class="project-description__statistics"]/text()')
    if len(Stats) == 0:
        Stats = None
    else:
        Stats = '\n'.join([each.strip() for each in Stats])
    
    Descr = html.xpath('//div[@class="project-description__body"]/p/text()')
    if len(Descr) == 0:
        Descr = None
    else:
        Descr = '\n'.join([each.strip() for each in Descr])
    
    types = html.xpath('//h2[text()="Type"]/text()')
    if len(types) == 0:
        typeItem = None
    else:
        typeItem = html.xpath('//div[contains(@class, "views-field-is-")]//a/text()')
        typeItem = '\n'.join([each.strip() for each in typeItem])
    
    services = html.xpath('//h2[text()="Service"]/text()')
    if len(services) == 0:
        serviceItem = None
    else:
        serviceItem = html.xpath('//div[@class="views-field views-field-name"]//a/text()')
        serviceItem = '\n'.join([each.strip() for each in serviceItem])
    
    peoples = html.xpath('//h2[text()="People"]/text()')
    if len(peoples) == 0:
        peopleItem = None
    else:
        peopleItem = html.xpath('//div[@class="views-field views-field-title"]//a/text()')
        peopleItem = '\n'.join([each.strip() for each in peopleItem])
    
    newItem = html.xpath('//span[@class="news--title"]/text()')
    if len(newItem) == 0:
        newItem = None
    else:
        newItem = '\n'.join([each.strip() for each in newItem])
    
    finalItem = [Title, subTitle,Location, Stats, Descr,typeItem, serviceItem, peopleItem, newItem]
    finalNames = ['Title','SubTitle','Location','Statistics','Description','Type','Service','People','News']
    return finalItem, finalNames

Results = []
Names = []
for url in resultURL:
    innerHtml = etree.HTML(getHtml(url))
    innerResult, innerName = processItem(innerHtml)
    Results.append(innerResult)
    Names.append(innerName)
# print(Results)

import pandas as pd
data = pd.DataFrame(Results, columns = Names[0])
data.to_csv(r'../Perkinswill.csv', index = False)

