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
def get_html(url,param = None):
    # 模拟浏览器的头部信息访问
    header = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'}
    response = requests.get(url,headers = header,params = param)
    response.encoding = response.apparent_encoding
    return response.text  #返回网页返回值

# 在首页中获取各个子网页的链接
def get_next_html(html):
    #解析源码
    inner = etree.HTML(html)
    json_urls = inner.xpath('//script[contains(text(),"dataList")]/text()')[1].split('dataList=[')[1].split('];')[0]
    reg = re.compile('"url":"(.*?)"')
    next_data = re.findall(reg,json_urls)
    next_urls =[]   #存储内容链接
    for each in next_data:
        # 筛选符合条件的子网页链接
        if 'news.ifeng' in each:
            next_urls.append(each)   #加入列表中
    return next_urls

# 对评论页的链接单独进行解析
def get_number(url):
    #评论页的原始网页
    ori_url = 'http://comment.ifeng.com/get.php?'
    #待提交的表单元素
    data = {
            'callback':'hotCommentListCallBack',
           'orderby':'uptimes',
          'docUrl':url,
         'format':'js',
         'job':'1',
        'p':'1',
        'pageSize':10,
        'callback':'hotCommentListCallBack',
        'skey':'a1d22a'
        }
    num_html = get_html(ori_url,param = data)
    #采用 正则表达式解析
    reg_1  = re.compile('"count":(.*?),')
    reg_2  = re.compile('"join_count":(.*?),')
     #count为评论人数
    count = re.findall(reg_1,num_html)[0]
    #join为参与人数
    join_count = re.findall(reg_2,num_html)[0]
    return count,join_count  #返回两个人数

# 对子网页进行内容提取
def get_Infos(html):
    inter = etree.HTML(html)
     #最后将结果放入 列表中
    final_list = []
    
     #  获取时间，没有的话就不用添加到列表中
    Time = inter.xpath('//*[@id="artical_sth"]/p/span[1]/text()')
    if len(Time) != 0:
        # 有结果的话就加入列表中，方便写入文件
        final_list.append(('时间：',Time[0]))
     
        # 获取来源，没有的话就不用添加到列表中
    Origin = inter.xpath('//*[@id="artical_sth"]/p/span[3]/span/a/text()')
    if len(Origin) != 0:
        # 有结果的话就加入列表中，方便写入文件
        final_list.append(('来源：',Origin[0]))
    
    # 获取新闻正文，没有的话就不用添加到列表中
    Content = inter.xpath('//*[@id="main_content"]/p/text()')
    if len(Content) != 0:
         # 对内容格式进行处理
        Content = ''.join([i.strip() for i in Content]).replace('\u200b','').replace('\u2022','').replace('\u2219','').replace('\xa0','').replace('\u2027','').replace('\xbd','')
       # 有结果的话就加入列表中，方便写入文件
        final_list.append(('内容：',Content))
     
        # 获取编辑人员，没有的话就不用添加到列表中
    Author = inter.xpath('//*[@id="artical_sth2"]/p[1]/text()')
    if len(Author) != 0:
        #进行格式处理
        Author = Author[0].split('责任编辑：')[1].split('P')[0]
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
    base_url = 'http://news.ifeng.com/'
     #文件名
    file = 'C:/Users/dell/desktop/new/News%s.txt'
    #获取初始的网页源码
    html = get_html(base_url)
    #调用函数获取 子网页和评论页链接
    next_urls = get_next_html(html)
    i = 1
    #迭代元素
    for each in next_urls:
        #获取子网页
        next_html  = get_html(each)
        #获取子网页的内容
        result = get_Infos(next_html)
         # 如果没有结果就重新放入列表中，再试一次
        if len(result) == 0:
            next_urls.append(each)
            continue
        # 返回参与人数和评论人数
        num_result, num_join = get_number(each)
        # 将两个人数放入列表中
        result.append(('评论人数：',num_result))
        result.append(('参与人数：',num_join))
        #写入文件中
        file = 'C:/Users/dell/desktop/new/News%s.txt' % str(i)
        write_file(file,result)
        i += 1
        
if __name__ == '__main__':
    main()
      
        
        
        
