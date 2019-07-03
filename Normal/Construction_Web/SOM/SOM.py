#!/usr/bin/env python
# coding: utf-8

# In[66]:


import requests
import pandas as pd
import re
from lxml import etree


def getHtml(url):
    headers = {
        'cookie': '_ga=GA1.2.1515719766.1560197289; _gid=GA1.2.2031311116.1560197289; _fbp=fb.1.1560197288983.707655106; ci_website=a%3A4%3A%7Bs%3A10%3A%22session_id%22%3Bs%3A32%3A%2282cba1c62789d6078d4cef8f5fd6c028%22%3Bs%3A10%3A%22ip_address%22%3Bs%3A14%3A%2210.189.246.102%22%3Bs%3A10%3A%22user_agent%22%3Bs%3A50%3A%22Mozilla%2F5.0+%28Windows+NT+10.0%3B+Win64%3B+x64%29+AppleWeb%22%3Bs%3A13%3A%22last_activity%22%3Bs%3A10%3A%221560197292%22%3B%7Da492637c8ce16364b453d5ecd48a0bdc; MPEL=EL',        'referer': 'https://www.som.com/',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36'
    }
    response = requests.get(url, headers = headers)
    response.encoding = response.apparent_encoding
    return response


baseUrl = 'https://www.som.com/projects#mode=grid&sort=date&region=north_america&service=architecture'
Original = getHtml(baseUrl)


def getInfo(html):
    info_obj = etree.HTML(html)
    
    reg_content = '//div[@class="container"]/p/text()'
    reg_news = '//span[@class="title"]/text()'
    
    reg_orgnization = '//span[@class="organization"]/text()'
    reg_name = '//span[@class="name"]/text()'
    reg_time = '//p[@class="secondary"]/text()'
    
    content = info_obj.xpath(reg_content)
    if len(content) != 0:
        content = '\n'.join([each.strip() for each in content])
    else:
        content = None
        
    news = info_obj.xpath(reg_news)
    if len(news) == 1:
        news = None
    else:
        news = '\n'.join([zeta.strip() for zeta in news[1:]])
    
    orgnization = info_obj.xpath(reg_orgnization) 
    if len(orgnization) == 0:
        awards = None
    else:
        names = info_obj.xpath(reg_name)
        time = info_obj.xpath(reg_time)[0:len(names)]
        singleOne = ''
        for innerOr, innerTime, innerName in zip(orgnization, time, names):
            singleOne += innerTime + '\n' + innerName + '\n' + innerOr + '\n\n'
            
    reg_facts = re.compile('>Project Facts<(.*?)</div></div></div>')
    facts = re.findall(reg_facts, html)
    finalfacts = ''
    if len(facts) == 0:
        finalfacts = None
    else:
        innerfact = facts[0].split('class="key">')[1:]
        for singlefact in innerfact:
            keyIndex = singlefact.index(':')
            key = singlefact[:keyIndex].strip()
            reg_value = re.compile('">(.*?)</')
            value = re.findall(reg_value, singlefact)
            if len(value) == 0:
                value = ""
            else:
                value = [eachii[eachii.index('>')+1:] if '>' in eachii else eachii for eachii in value]
                value = ', '.join([eachii.strip() for eachii in value])
            finalfacts += key + ': ' + value + '\n'
    finalfacts.strip('\n')
    return [content, news,singleOne, finalfacts]   

def getLinks(html):
    obj = etree.HTML(html)

    reg_titles = '//div[@class="project_item grid"]//span[@class="heading"]/text()'
    reg_links = '//div[@class="project_item grid"]/a/@href'
    reg_locations = '//div[@class="project_item grid"]//span[@class="subhead"]/text()'
    
    titles = obj.xpath(reg_titles)
    links = obj.xpath(reg_links)
    links = ['https://www.som.com/' + each for each in links]
    locations = obj.xpath(reg_locations)
    
    finalData = []
    for jj, link in enumerate(links):
        link = 'https://www.som.com/projects/india_basin'
        innerHtml = getHtml(link).text
        infos = getInfo(innerHtml)
        zeta = [titles[jj], locations[jj]]
        zeta.extend(infos)
        finalData.append(zeta)
        
    return finalData

result = getLinks(Original.text)

dataSave =  pd.DataFrame(result, columns = ['Title', 'Location','Content','News','Awards','Facts'])
dataSave.to_csv('../SOM.csv', index  = False)




