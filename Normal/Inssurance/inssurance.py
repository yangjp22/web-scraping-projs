# -*- coding: utf-8 -*-
"""
Created on Wed Jul 18 19:28:49 2018

@author: dell
"""

# 导入相关的库，requests库时下载网页源码，lxml是用于对源码进行解析，提取元素
import requests
from lxml import etree
import csv
import time

# 定义下载源码的函数
def get_html(url):
    # 定义头部信息，模拟浏览器访问服务器
    headers = {
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36',
        'Host':'bxjg.circ.gov.cn',
        'Referer':'http://bxjg.circ.gov.cn/tabid/6757/Default.aspx'
    }
    # 采用get方法获取网页源码
    response = requests.get(url,headers = headers)
    # 对返回的信息的编码进行处理
    response.encoding = response.apparent_encoding
    # 返回相应的文本
    return response.text

# 定义新的函数，在网页源码中获取下一级别网页的url链接和保险公司名字
def get_info(htmls):
    # 对得到的html进行解析
    Obj = etree.HTML(htmls)
    # 采用xapth方法提取元素，返回一个列表
    next_urls = Obj.xpath('//td[@class="orglist_td"]/a/@href')
    Names = Obj.xpath('//td[@class="orglist_td"]/a/text()')
    # 得到的url链接是一个相对url，补全得到完整的url
    Entire_urls = []
    for each in next_urls:
        Entire_urls.append('http://bxjg.circ.gov.cn'+each )
    # 返回完整的url和对应的保险公司名字
    return Entire_urls,Names

# 对新网页的内容进行提取，得到各保险产品名称，备案时间和种类
def get_Info(htmls):
    # 先解析
    inner = etree.HTML(htmls)
    # 后提取元素内容，返回值均为列表
    Product_names = inner.xpath('//table[@class="tableRecordProduct"]/tr/td[1]/text()')
    Dates = inner.xpath('//table[@class="tableRecordProduct"]/tr/td[2]/text()')
    Kinds = inner.xpath('//table[@class="tableRecordProduct"]/tr/td[3]/text()')
    # 将获取到的所有信息汇集成一个总列表，列表每一个元素包含每一个产品名称和备案时间，种类
    final_list = []
    for j,k,l in zip(Product_names,Dates,Kinds):
        final_list.append([j,k,l])
    # 返回总的列表
    return final_list

# 写入csv文件

def write_file(filename,datas):
    # 打开文件
    with open(filename,'a+',encoding='gbk',errors='ignore') as fp:
        # 写入文件
        writer = csv.writer(fp)
        writer.writerows(datas)
        
def main():
    # 最开始的url链接，即首页
    base_url = 'http://bxjg.circ.gov.cn/tabid/5253/ctl/ViewOrgList/mid/16658/OrgTypeID/1/Default.aspx?ctlmode=none'
    # 调用上述函数获取网页源码，保存到html中
    html = get_html(base_url)
    # 调用上述函数获取链接和名字
    Next_urls,Next_Names = get_info(html)
    # 对已有的链接列表和名字列表进行迭代，获取信息
    for each_url,each_name in zip(Next_urls,Next_Names):
    #     对次级的url获取源码
        inter_html = get_html(each_url)
        # 在次级url的源码中获取信息，并得到列表
        results  = get_Info(inter_html)
        
        # 如果返回的信息为空，就将连接再次放入列表中，重新再解析
        if len(results) == 0:
            Next_urls.append(each_url)
            Next_Names.append(each_name)
            continue
        # 根据保险公司的名字来创建文件名
        file = 'C:/Users/dell/desktop/Data1/%s.csv' % each_name
        #　调用函数，将所得的列表写入文件中
        write_file(file,results)
        time.sleep(1)
        
    
if __name__ == "__main__":
    main()