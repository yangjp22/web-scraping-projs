import requests
import time
import json
import pymongo
import pandas as pd

def crawler(url, data):
    header = {
    'Referer':'https://www.renrendai.com/loan.html',
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
    }
    response = requests.get(url, headers = header, params = data)
    # response.raise_statues()
    response.encoding = response.apparent_encoding
    return response.json()

def parse(text):
    dataList = text['data']['list']
    for each in dataList:
        eachDict = {}
        eachDict['loanId'] = each['loanId']
        eachDict['interest'] = float(each['interest'])
        eachDict['status'] = each['status']
        eachDict['title'] = each['title']
        eachDict['loanType'] = each['loanType']
        eachDict['borrowerId'] = each['borrowerId']
        eachDict['productId'] = each['productId']
        eachDict['amount'] = int(each['amount'])
        eachDict['leftMonths'] = int(each['leftMonths'])
        save(eachDict)

    print('Successfully!')

def save(data):
    client = pymongo.MongoClient('mongodb://localhost:27017/')
    db = client['Loan']
    collection = db['renRenDai']
    collection.insert_one(data)

def main():
    url = 'https://www.renrendai.com/loan/list/loanList'
    Time = int(time.time() * 1000)
    parameters = {
          'startNum':0,
          'limit':1000,
          '_':Time
    }

    content = crawler(url, parameters)
    parse(content)
    client = pymongo.MongoClient('localhost', 27017)
    db = client['Loan']
    collection = db['renRenDai']
    data = pd.DataFrame(list(collection.find()))
    data.drop('_id', axis = 1, inplace = True)
    data.to_csv('C:/Users/fredy/Desktop/loan.csv',encoding = 'gbk')

if __name__ == '__main__':
    main()



