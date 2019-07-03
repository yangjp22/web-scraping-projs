# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class AppdoujiaItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    cateName = scrapy.Field()   #分类名
    childCateName = scrapy.Field() #分类编号
    appName = scrapy.Field() # 子分类名
    install = scrapy.Field() # 子分类编号
    volume = scrapy.Field() # 体积
    comment = scrapy.Field() # 评论
    iconUrl = scrapy.Field() # 图标url
    
 
