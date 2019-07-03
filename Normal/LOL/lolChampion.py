#!/usr/bin/env python
# coding: utf-8

import requests
import lxml
import pandas as pd
from collections import defaultdict

baseUrl = 'https://ddragon.leagueoflegends.com/cdn/9.11.1/data/en_US/champion.json'
response = requests.get(baseUrl).json()
originalDatas = response['data']
datas = pd.DataFrame(originalDatas)


def Info(x):
    return pd.Series({'attack': x['attack'],'defense': x['defense'],'magic': x['magic'],'difficulty': x['difficulty']})

def Tags(x):
    return pd.Series({'Tags':'/'.join(x)})

def classTags(x):
    allItem = x['Tags'].to_list()
    allTypes = []
    [allTypes.extend(each.split('/')) for each in allItem]
    allSet = list(set(allTypes))
    allDict = dict.fromkeys(allSet)
    finalDict = defaultdict(dict)
    for index, each in enumerate(allItem):
        inner = each.split('/')
        for i in inner:
            finalDict[i][x.index[index]] = 1
    finalDict = pd.DataFrame(finalDict).fillna(0)
    return finalDict

def Stats(x):
    innerDict = {}
    for each in x.items():
        innerDict[each[0]] = each[1]
    return pd.Series(innerDict)

zeta = datas['info'].apply(Info)
beta = datas['tags'].apply(Tags)
finalTag = classTags(final)
gamma = datas['stats'].apply(Stats)


final = datas.merge(zeta, right_index=True, left_index=True)
final = final.merge(beta, right_index = True, left_index = True)
final = final.merge(finalTag, right_index=True, left_index=True)
final = final.merge(gamma, right_index=True, left_index=True)
final = final.drop(['blurb','id','image','key','title','stats','Tags','partype','info','tags', 'version'], axis = 1)

final.to_csv(r'C:\Users\fred\desktop\lol.csv', index = False)





