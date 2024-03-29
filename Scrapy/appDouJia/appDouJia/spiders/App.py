# -*- coding: utf-8 -*-
import scrapy
from appDouJia.items import AppdoujiaItem
import re
from urllib.parse import urlencode
import json


class AppSpider(scrapy.Spider):
    name = 'App'
    allowed_domains = ['www.wandoujia.com']
    # start_urls = ['http://www.wandoujia.com/']
    
    def __init__(self):
        self.cateUrl = 'https://www.wandoujia.com/category/app'
        # 子分类首页Url
        self.url = 'https://www.wandoujia.com/category/'
        # 子分类 ajax请求也url
        self.ajaxUrl = 'https://www.wandoujia.com/wdjweb/api/category/more?'
        # 实例化分类标签
        self.wanDouCategory = GetCategory()

    def start_requests(self):
        yield scrapy.Request(self.cateUrl, callback = self.getCategory)

    def getCategory(self, response):
        cateContent = self.wanDouCategory.parseCategory(response)
        for item in cateContent:
            child_cate = item['child_cate_codes']
            for cate in child_cate:
                cate_code = item['cate_code']
                cate_name = item['cate_name']
                child_cate_code = cate['child_cate_code']
                child_cate_name = cate['child_cate_name']
        
                page = 1 # 设置爬取起始页数
                if page == 1:
                   # 构造首页url
                    category_url = '{}{}_{}' .format(self.url, cate_code, child_cate_code)
                else:
                    params = {
                       'catId': cate_code,  # 类别
                       'subCatId': child_cate_code,  # 子类别
                       'page': page,
                       }
                    category_url = self.ajax_url + urlencode(params)
                dict = {'page':page,'cate_name':cate_name,'cate_code':cate_code,'child_cate_name':child_cate_name,'child_cate_code':child_cate_code}
                yield scrapy.Request(category_url,callback=self.parse,meta=dict)

    def clean_name(self, name):
        return name.strip()

    def parse(self, response):
        if len(response.body) >= 100:  # 判断该页是否爬完，数值定为100是因为无内容时长度是87
            page = response.meta['page']
            cate_name = response.meta['cate_name']
            cate_code = response.meta['cate_code']
            child_cate_name = response.meta['child_cate_name']
            child_cate_code = response.meta['child_cate_code']

            if page == 1:
                contents = response
            else:
                jsonresponse = json.loads(response.body_as_unicode())
                contents = jsonresponse['data']['content']
                # response 是json,json内容是html，html 为文本不能直接使用.css 提取，要先转换
                contents = scrapy.Selector(text=contents, type="html")

            contents = contents.css('.card')
            for content in contents:
                # num += 1
                item = AppdoujiaItem()
                item['cateName'] = cate_name
                item['childCateName'] = child_cate_name
                item['appName'] = self.clean_name(content.css('.name::text').extract_first())  
                item['install'] = content.css('.install-count::text').extract_first()
                item['volume'] = content.css('.meta span:last-child::text').extract_first()
                item['comment'] = content.css('.comment::text').extract_first().strip()
                # item['iconUrl'] = self.get_icon_url(content.css('.icon-wrap a img'),page)
                item['iconUrl'] = None
                yield item

            # 递归爬下一页
            page += 1
            params = {
                    'catId': cate_code,  # 大类别
                    'subCatId': child_cate_code,  # 小类别
                    'page': page,
                    }
            ajax_url = self.ajaxUrl + urlencode(params)
            dict = {'page':page,'cate_name':cate_name,'cate_code':cate_code,'child_cate_name':child_cate_name,'child_cate_code':child_cate_code}
            yield scrapy.Request(ajax_url,callback=self.parse,meta=dict)  

# 定义了一个类 Get_category() 专门用于提取全部的子分类 URL
class GetCategory():
    def parseCategory(self, response):
        category = response.css('.parent-cate')
        data = [{
            'cate_name': item.css('.cate-link::text').extract_first(),
            'cate_code': self.get_category_code(item),
            'child_cate_codes': self.get_child_category(item),
        } for item in category]
        return data

    # 获取所有主分类标签数值代码
    def get_category_code(self, item):
        cate_url = item.css('.cate-link::attr("href")').extract_first()
        pattern = re.compile(r'.*/(\d+)')  # 提取主类标签代码
        cate_code = re.search(pattern, cate_url)
        return cate_code.group(1)

    # 获取所有子分类名称和编码
    def get_child_category(self, item):
        child_cate = item.css('.child-cate a')
        child_cate_url = [{
            'child_cate_name': child.css('::text').extract_first(),
            'child_cate_code': self.get_child_category_code(child)
        } for child in child_cate]
        return child_cate_url

    # 正则提取子分类编码
    def get_child_category_code(self, child):
        child_cate_url = child.css('::attr("href")').extract_first()
        pattern = re.compile(r'.*_(\d+)')  # 提取小类标签编号
        child_cate_code = re.search(pattern, child_cate_url)
        return child_cate_code.group(1)