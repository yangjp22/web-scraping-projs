#!/usr/bin/env python
# coding: utf-8

import requests
import re
import json
from urllib import parse
import time
from matplotlib import pyplot as plt
import pymongo
from multiprocessing import Queue, Process


class Producer(Process):
    
    def __init__(self, url, queue):
        super(Producer, self).__init__()
        self.queue = queue
        self.url = url
    
    def getHtml(self, url):
        headers = {
            'Cookie': 'pgv_pvid=3918504627; pac_uid=0_fa38b19827a7c; tvfe_boss_uuid=322f64b84f1316ee; AMCV_248F210755B762187F000101%40AdobeOrg=-1891778711%7CMCIDTS%7C18008%7CMCMID%7C73888650160712395190870001653859710530%7CMCAAMLH-1556491252%7C7%7CMCAAMB-1556491252%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1555893652s%7CNONE%7CMCAID%7CNONE%7CvVersion%7C2.4.0; eas_sid=J195E5F6S3d9I7o8e0x0u8e6C1; pgv_pvi=6811439104; LW_uid=R1N5A586H6b6N312d2C6K8S2y7; LW_sid=x1i5J6k1z423d7U8K0x088K5Y5; pgv_pvid_new=10001_a15a30a72e; pgv_info=ssid=s2570261392; g_tk=9903965324cc4e41cbc68072c05317837a28fcf2; __guid=2209186.3545395084861666300.1564272793405.6245; monitor_count=3; ad_play_index=12; ts_last=coral.qq.com/4031994449; ts_uid=3381523565',
            'Host': 'coral.qq.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.encoding = response.apparent_encoding
        return response
    
    def getPage(self):
        url = 'http://coral.qq.com/article/4031994449/commentnum?'
        params = {
                'callback':'_article4031994449commentnum',
                '_':int(time.time() * 1000)
        }
        Url = url + parse.urlencode(params)
        response = self.getHtml(Url).text
        inner = response.split('(')[-1].split(')')[0]
        number = int(json.loads(inner)['data']['commentnum'])
        pages = number // 10 + 1
        return pages 
    
    def createUrl(self, cursor = 0):
        
        params = {
                'callback':'_article4031994449commentv2',
                'orinum':10,
                'oriorder':'o',
                'pageflag':1,
                'cursor':cursor,
                'scorecursor':0,
                'orirepnum':2,
                'reporder':'o',
                'reppageflag':1,
                'source':1,
                '_':int(time.time() * 1000)
        }
        Url = self.url + parse.urlencode(params)
        return Url

    def run(self):
        maxPage = self.getPage()
        cursor = 0
        n = 1
        for i in range(maxPage):
            try:
                Url = self.createUrl(cursor=cursor)
                respo = self.getHtml(Url).text
                respos = re.sub(u"\t|\n|\.|-|;|\)|\(|\?|'|", '', ''.join(''.join(respo.split('(')[1:]).split(')')[:-1]))
                json_data = json.loads(respos)['data']
                cursor = json_data['oriCommList'][-1]['id']
                print(n)
                n += 1
                self.queue.put(json_data)
                print('-----*****-----')

            except:
                self.queue.put(None)
                break
            
        self.queue.put(None)


class Consumer(Process):
    
    def __init__(self, queue):
        super(Consumer, self).__init__()
        self.queue = queue
        self.result = []
    
    def amend(self, string):
        return re.sub('<.*?>', '', string)

    def dataSaveMongoDB(self, data, databaseName, collectionName, allIn = True):
        '''
        data: [{}, {}, {}]
        '''
        client = pymongo.MongoClient('mongodb://localhost:27017/')
        db = client[databaseName]
        collection = db[collectionName]
        
        if allIn:
            collection.insert_many(data)
        else:
            for each in data:
                collection.insert_one(each)

        print('Save successfully!')


    def run(self):
        
        while True:
            take = self.queue.get()

            if take is None:
                break

            Comments = [self.amend(each['content']) for each in take['oriCommList']]
            Times = [time.strftime("%Y/%m/%d %H:%M", time.localtime(int(each['time'])))  for each in take['oriCommList']]
            Approves = [int(each['up'])  for each in take['oriCommList']]
            Replys = [int(each['orireplynum'])  for each in take['oriCommList']]
            UserIds = [int(each['userid'])  for each in take['oriCommList']]

            for comm, tim, appro, reply, user in zip(Comments, Times, Approves, Replys, UserIds):
                self.result.append({"Time":tim, "Comment":comm, "Reply":reply, "Approval":appro, "UserId": user})
            
            print('*****-----*****')

        self.dataSaveMongoDB(self.result, "TencentComment", "ShaoNianPai")


def main():
    queue = Queue()
    baseUrl = 'http://coral.qq.com/article/3937239663/comment/v2?'
    producer = Producer(baseUrl, queue)
    consumer = Consumer(queue)
    producer.start()
    consumer.start()
    producer.join()
    consumer.join()
    
if __name__ == '__main__':
    main()

