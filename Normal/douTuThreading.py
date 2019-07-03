#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-12-21 14:51:23
# @Author  : Your Name (you@example.org)
# @Link    : http://example.org
# @Version : $Id$

from crawler import getHtml
from lxml import etree
import re
import os
from urllib import request
import queue
import threading

class Producer(threading.Thread):
    def __init__(self, pageQueue, imgUrlQueue, *args, **kwargs):
        self.pageQueue = pageQueue
        self.imgUrlQueue = imgUrlQueue
        super(Producer, self).__init__(*args, **kwargs)

    def run(self):
        while not self.pageQueue.empty() :
            trainUrl = self.pageQueue.get()
            trainHtml = getHtml(trainUrl)
            html = etree.HTML(trainHtml)
            imgs = html.xpath('//div[@class="page-content text-center"]//img[@class!="gif"]')
            for img in imgs:
                imgUrl = img.get('data-original')
                alt = img.get('alt')
                alt = re.sub(r'[\?？，。\.!！\*/]', '', alt)
                suffix = os.path.splitext(imgUrl)[1]
                filename = alt + suffix
                self.imgUrlQueue.put((imgUrl, filename))

class Consumer(threading.Thread):
    def __init__(self, pageQueue, imgUrlQueue, *args, **kwargs):
        self.pageQueue = pageQueue
        self.imgUrlQueue = imgUrlQueue
        super(Consumer, self).__init__(*args, **kwargs)

    def run(self):
        while not self.imgUrlQueue.empty() or not self.pageQueue.empty():
            imgUrl, fileName = self.imgUrlQueue.get()
            request.urlretrieve(imgUrl, 'images/' + fileName)
            print(fileName + '   下载完成！   ')

def parse_page(html):
    html = etree.HTML(html)
    imgs = html.xpath('//div[@class="page-content text-center"]//img[@class!="gif"]')
    for img in imgs:
        imgUrl = img.get('data-original')
        alt = img.get('alt')
        alt = re.sub(r'[\?？，。\.!！\*]', '', alt)
        suffix = os.path.splitext(imgUrl)[1]
        filename = alt + suffix
        request.urlretrieve(imgUrl, 'images/' + filename)

def Yibu():
    pageQueue = queue.Queue(100)
    imgQueue = queue.Queue(500)
    baseUrl = 'https://www.doutula.com/photo/list/?page='
    for i in range(1, 101):
        pageQueue.put(baseUrl + str(i))

    for each in range(5):
        t = Producer(pageQueue, imgQueue)
        t.start()

    for each in range(5):
        t = Consumer(pageQueue, imgQueue)
        t.start()

def TongBu():
    baseUrl = 'https://www.doutula.com/photo/list/?page='
    for i in range(1,101):
        url = baseUrl + str(i)
        html = getHtml(url)
        parse_page(html)

def main():
    # TongBu()
    Yibu()


if __name__ == '__main__':
    main()