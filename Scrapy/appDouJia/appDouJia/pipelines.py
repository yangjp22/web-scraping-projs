# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
import scrapy
from scrapy.pipelines.images import ImagesPipeline

class AppdoujiaPipeline(object):
    def process_item(self, item, spider):
        return item

# 存储到MongoDB
class mongodbPipeline(object):
    def __init__(self, mongoUrl, host, mongoDB):
        self.mongoUrl = mongoUrl  
        self.mongoDB = mongoDB
        self.host = host

    @classmethod
    def from_crawler(cls, crawler):
        return cls(mongoUrl = crawler.settings.get('MONGO_URL'),
                    host = crawler.settings.get('MONGO_HOST'),
                    mongoDB = crawler.settings.get('MONGO_DB'))

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongoUrl, self.host)
        self.db = self.client[self.mongoDB]

    def process_item(self, item, spider):
        name = item.__class__.__name__
        # upsert = True表示没有时，添加
        self.db[name].update_one(item, {'$set':item}, upsert = True)  
        return item

    def close_spider(self, spider):
        self.client.close()

# 图片下载类
# class imageDownloadPipeline(ImagesPipeline):
#     def get_media_requests(self, item, info):
#         if item['iconUrl']:
#             yield scrapy.Request(item['iconUrl'], meta = {'item':item})

#     def file_path(self, request, response = None, info = None):
#         name = request.meta['item']['appName']
#         cateName = request.meta['item']['cateName']
#         childCateName = request.meta['item']['childCateName']

#         path1 = r'/'


