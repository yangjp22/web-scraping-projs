# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo

class KuanPipeline(object):
    def process_item(self, item, spider):
        return item

class mongodbPipeline(object):
    def __init__(self, mongoUrl, mongoHost, mongoDB):
        self.mongoUrl = mongoUrl
        self.mongoHost = mongoHost
        self.mongoDB = mongoDB

    @classmethod
    def from_crawler(cls, crawler):
        return cls(mongoUrl = crawler.settings.get('MONGO_URL'),
                    mongoHost = crawler.settings.get('MONGO_HOST'),
                    mongoDB = crawler.settings.get('MONGO_DB'))

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongoUrl, self.mongoHost)
        self.database = self.client[self.mongoDB]

    def process_item(self, item, spider):
        name = item.__class__.__name__
        self.database[name].update(item, {'$set':item}, upsert = True)
        return item

    def close_spider(self, spider):
        self.client.close()