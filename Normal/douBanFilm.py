#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-12-20 23:44:23
# @Author  : Your Name (you@example.org)
# @Link    : http://example.org
# @Version : $Id$

from crawler import getHtml
from lxml import etree
import csv
import pickle
import pymongo
import saveFile

def getInfo(html):
    obj = etree.HTML(html)
    inner = obj.xpath('//ul[@class="lists"]')[0].xpath('./li')
    final = []
    finalDict = []
    for each in inner:
        eId = int(each.xpath('@id')[0]) if each.xpath('@id') else 0
        eTitle = each.xpath('@data-title')[0] if each.xpath('@data-title') else ''
        eScore = float(each.xpath('@data-score')[0]) if each.xpath('@data-score') else 0.0
        eStars = int(each.xpath('@data-star')[0]) if each.xpath('@data-star') else 0
        eDuration = int(each.xpath('@data-duration')[0].strip().split('分钟')[0].strip()) if (each.xpath('@data-duration') and len(each.xpath('@data-duration')[0]) > 0) else 0
        eDirector = each.xpath('@data-director')[0] if each.xpath('@data-director') else ''
        eActors = each.xpath('@data-actors')[0] if each.xpath('@data-actors') else ''
        eCategory = each.xpath('@data-category')[0] if each.xpath('@data-category') else ''
        eVoteCount = int(each.xpath('@data-votecount')[0]) if each.xpath('@data-votecount') else 0
        final.append((eId, eTitle, eScore, eStars, eDuration, eDirector, eActors, eCategory, \
            eVoteCount))
        innerdict = {'ID':eId, 'Title':eTitle, 'Score': eScore, 'Stars': eStars, 'Duration':eDuration, 
                     'Director':eDirector, 'Actors': eActors, 'Category':eCategory, 'VoteCount': eVoteCount
                    }
        finalDict.append(innerdict)

    return final, finalDict

url = 'https://movie.douban.com/cinema/nowplaying/beijing/'
html = getHtml(url)

# # with open('csv.pickle', 'wb') as fp:
# #     pickle.dump(html, fp)

# with open('csv.pickle', 'rb+') as fp:
#     html = pickle.loads(fp)

final, Dict = getInfo(html)

headers = ['ID', 'Title', 'Score', 'Stars', 'Duration', 'Director', 'Actors', 'Category', 'VoteCount']
saveFile.saveCsv('5.csv', final, headers, encode = 'gbk')
saveFile.saveMongoDB(Dict, 'try','second')

# with open('1.csv', 'w', newline = '', encoding = 'gbk', errors  ='ignore') as fp:
#     writer = csv.writer(fp)
#     writer.writerow(headers)
#     for zeta in final:
#         writer.writerow(zeta)

# with open('2.csv', 'w', newline = '', encoding = 'gbk', errors  ='ignore') as fp:
#     writer = csv.writer(fp)
#     writer.writerow(headers)
#     writer.writerows(final)

# with open('3.csv', 'w', newline = '', encoding = 'gbk', errors  ='ignore') as fp:
#     writer = csv.DictWriter(fp, headers)
#     writer.writeheader()
#     for zeta in Dict:
#         writer.writerow(zeta)

# with open('4.csv', 'w', newline = '', encoding = 'gbk', errors  ='ignore') as fp:
#     writer = csv.DictWriter(fp, headers)
#     writer.writeheader()
#     writer.writerows(Dict)


# client = pymongo.MongoClient('mongodb://localhost:27017/')
# db = client['spyder']
# collection = db['Douban']
# for i in Dict:
#     collection.insert(i)

# collection = db['Douban2']
# collection.insert_many(Dict)

