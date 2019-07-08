#!/usr/bin/env python
# coding: utf-8

import requests
from lxml import etree
import pandas as pd
import re


def getHtml(url, method='get'):
    if method == 'post':
        data_ = {"keyword": "", 'location': 'Dallas'}
        header_ = {
            'Origin': 'https://www.hksinc.com',
            'Referer': 'https://www.hksinc.com/search/?locations=Dallas&services=Architecture&contentTypes=Case%20Studies',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'}
        response = requests.post(url, headers=header_, data=data_)

    else:
        header_ = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'cookie': '_ga=GA1.2.802953523.1559879715; _gid=GA1.2.2065957837.1559879715; consentCookie=true; _hjIncludedInSample=1',
            'referer': 'https//www.hksinc.com/what-we-do/case-studies/the-farm-at-crossroad-commons/',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36'}
        response = requests.get(url, headers=header_)
    response.encoding = response.apparent_encoding
    return response


baseUrl = 'https://hksproduction.wpengine.com/wp-json/v2/elastic-search'
baseData = getHtml(baseUrl, method='post').json()
OrigInfo = baseData['hits']['hits']


def getJs(url):
    One = getHtml(url).text
    link_reg = re.compile('/path---what-we-do-case-studies-(.*?).js')
    links = re.findall(link_reg, One)
    if len(links) == 0:
        return None
    else:
        jsLink = ' https://www.hksinc.com/path---what-we-do-case-studies-' +             re.findall(link_reg, One)[0] + '.js'
        return jsLink


def getInfos(url):
    html = getHtml(url).text
    feature_reg = re.compile('project_features:\[\{(.*?)\}\]')
    awards_reg = re.compile('awards:\[\{(.*?)\}\]')
    featureItem = re.findall(feature_reg, html)
    awardItem = re.findall(awards_reg, html)
    if len(featureItem) != 0:
        feature = '\n'.join([item.split(':')[-1].strip('"').strip()
                             for item in re.findall(feature_reg, html)[0].split('},{')])
    else:
        feature = None

    if len(awardItem) != 0:
        award = '\n'.join([item.split(':')[-1].strip('"').strip()
                           for item in re.findall(awards_reg, html)[0].split('},{')])
    else:
        award = None

    return feature, award


zeta = []
for each in OrigInfo:
    if each['_source']['post_type'] != None and 'case_study' in each['_source']['post_type']:
        if each['_source']['locations'] != None and 'Dallas' in each['_source']['locations']:
            if each['_source']['services'] != None and 'Architecture' in each['_source']['services']:
                title = each['_source'].get('title', None)
                service = '/'.join([single.strip()
                                    for single in each['_source'].get('services', None)])
                locations = '/'.join([single.strip()
                                      for single in each['_source'].get('locations', None)])
                people = each['_source'].get('people', None)
                if people != None:
                    people = '/'.join([single.strip() for single in people])
                    
                project_types = each['_source'].get('project_types', None)
                if project_types != None:
                    project_types = '/'.join([single.strip()
                                              for single in project_types])
                body = each['_source'].get('body', None)
                if body != None:
                    body = '\n'.join([list(single.values())[0].replace('<p>', '').replace(
                        '</p>', '').replace("’s", "'s").strip() for single in body])

                inner = title.replace(' ', '-')
                inner = ''.join(
                    [single if (single.isalnum() or single == '-') else '' for single in inner])

                url = 'https://www.hksinc.com/what-we-do/case-studies/' + inner + '/'
                jsUrl = getJs(url)

                if jsUrl != None:
                    features, awards = getInfos(jsUrl)
                else:
                    features, awards = None, None
                zeta.append([title, service, locations,
                             body, features, awards])


zetaToSave = pd.DataFrame(zeta, columns = ['Title', 'Service', 'Locations', 'Description', 'Features', 'Awards'])
zetaToSave.to_csv('C:/Users/fred/desktop/HKS.csv', index = False)

