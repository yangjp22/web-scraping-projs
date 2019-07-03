# -*- coding: utf-8 -*-
"""
Created on Tue Jul 17 00:41:15 2018

@author: dell
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Jul 16 21:36:49 2018

@author: dell
"""

import requests
from lxml import etree
import json
import re

#   获取网页源码
def get_html(url):
    # 模拟浏览器的头部信息访问
    header = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'}
    response = requests.get(url,headers = header)
    response.encoding = response.apparent_encoding
    return response.text #返回网页返回值

# 在首页中获取各个子网页的链接
def get_next_html(html):
    #解析源码
    inner = etree.HTML(html)
    inter_urls = inner.xpath('//section[contains(@class,"cont_")]/div/ul[@class="list14"]/li/a/@href')
    next_urls =[]  #存储内容链接
    # 筛选符合条件的子网页链接
    for each in inter_urls:
        next_urls.append(each)   #加入列表中
    return next_urls

# 对子网页进行内容提取
def get_Infos(html):
    inter = etree.HTML(html)
     #最后将结果放入 列表中
    final_list = []
    
     #  获取时间，没有的话就不用添加到列表中
    Time = inter.xpath('//div[@class="box01"]/div[@class="fl"]/text()')
    if len(Time) != 0:
        # 有结果的话就加入列表中，方便写入文件
        final_list.append(('时间：',Time[0].split('来源：')[0].strip()))
    
    # 获取来源，没有的话就不用添加到列表中
    Origin = inter.xpath('//div[@class="box01"]/div[@class="fl"]/a/text()')
    if len(Origin) != 0:
        # 有结果的话就加入列表中，方便写入文件
        final_list.append(('来源：',Origin[0]))
    
    # 获取新闻正文，没有的话就不用添加到列表中
    Content = inter.xpath('//*[@id="rwb_zw"]/p/text()')
    if len(Content) != 0:
         # 对内容格式进行处理
        Content = ''.join([i.strip() for i in Content])
        # 有结果的话就加入列表中，方便写入文件
        final_list.append(('内容：',Content))
      
        # 获取编辑人员，没有的话就不用添加到列表中
    Author = inter.xpath('//*[@id="rwb_zw"]/div[4]/text()')
    if len(Author) != 0:
        #进行格式处理
        Author = Author[0].split('责编：')[1].split(')')[0]
        # 有结果的话就加入列表中，方便写入文件
        final_list.append(('编辑；',Author))
    return final_list

# 将得到的列表写入文件中 
def write_file(filename,data):
    #打开文件
    with open(filename,'a',errors='ignore') as fp:
        #对列表元素进行迭代，全写入文件中
        for each_x in data:
            fp.write("{key}{value}  \n".format(key = each_x[0],value = each_x[1]))
   
def main():
     # 最初的首页
    base_url = 'http://www.people.com.cn/'
    #获取初始的网页源码
    html = get_html(base_url)
    #调用函数获取 子网页链接
    next_urls = get_next_html(html)
    i = 1
    #迭代元素
    for each in next_urls:
        #获取子网页
        next_html  = get_html(each)
        #获取子网页的内容
        result = get_Infos(next_html)
        if len(result) == 0:
            continue
        #写入文件中
        file = 'C:/Users/dell/desktop/new1/News%s.txt' % str(i)
        write_file(file,result)
        i += 1
        
if __name__ == '__main__':
    main()
      
        
        
        

