#!/usr/bin/env python
# coding: utf-8

import time
import requests
import pandas as pd
import datetime


def getHtml(url,params = None):
    headers = {
        'Cookie': '_ga=GA1.2.802091817.1560273719; vxv=2015041001; vxu=k4uqq-pdp4IOsVorKqHDng; __cfduid=d1693755abeeb2d0848fe807e37550fed1560273765; vxl=1560273768; _gid=GA1.2.743034161.1560688898',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36'     
    }
    response = requests.post(url, headers = headers, params = params)
    response.encoding = response.apparent_encoding
    return response

dataReader = pd.read_csv('c:/Users/fred/desktop/DC1.csv', encoding = 'gbk')
newTime = dataReader['IssuedDate'][0]
init = datetime.datetime.strptime(newTime, '%Y/%m/%d')
end = init - datetime.timedelta(days = 1)
endDate = end.strftime('%Y/%m/%d')


base_url = 'https://eservices.dcra.dc.gov/dcradataconnect/Home/getPermitData'
finalData = []

init_month = init.month
end_month = time.localtime().tm_mon


for month in range(init_month, end_month + 1):
    for i in range(1,9):
        paramss = {
            'year': time.localtime().tm_year,
            'month': month,
            'ward': i
        }
        original = getHtml(base_url, params = paramss).json()['permitData']
        finalData.append(original)


def Date(date):
    date = int(date.split('(')[1].split(')')[0])
    sec = int(date / 1000)
    timeA = time.localtime(sec)
    timeStr = time.strftime('%Y/%m/%d', timeA)
    return timeStr


dataSave = pd.DataFrame(columns = ['ANC', 'Address', 'Applicant', 'DescriptionOfWork', 'FeeType', 'Green',
       'IssuedDate', 'Latitude', 'Longitude', 'OwnerName', 'PermitCategory',
       'PermitGroup', 'PermitNumber', 'PermitSubType', 'PermitType', 'SSL',
       'Status', 'TotalPaid', 'Ward', 'Zoning'])

for each in finalData:
    innerEach = []
    for j in each:
        innerDate = Date(j['IssuedDate'])
        if innerDate > endDate:
            innerEach.append(j)
    if len(innerEach) > 0:
        zeta = pd.DataFrame(innerEach)
        zeta['IssuedDate'] = zeta['IssuedDate'].apply(Date)
        dataSave = pd.concat([dataSave, zeta])

dataSave = dataSave.sort_values(by = 'IssuedDate',ascending=False )
dataSave.to_csv('c:/Users/fred/desktop/DC2.csv',index = False)


# In[ ]:




