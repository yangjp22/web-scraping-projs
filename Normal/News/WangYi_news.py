# -*- coding: utf-8 -*-
"""
Created on Tue Jul 17 20:56:40 2018

@author: dell
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Jul 16 21:36:49 2018

@author: dell
"""

import requests
from lxml import etree
import re

#   获取网页源码
def get_html(url,param = None, headers = None):
    # 模拟浏览器的头部信息访问
    if headers == None:
        headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'}
    
    response = requests.get(url,headers = headers ,params = param)
    response.encoding = response.apparent_encoding
    return response.text  #返回网页返回值

# 在首页中获取各个子网页的链接
def get_next_html(html):
    #解析源码
    inner = etree.HTML(html)
    next_data = inner.xpath('//*[@id="js_index2017_wrap"]/div/div/div/div/div/div/div/div/div/div/ul/li/a/@href')
    next_urls =[]     #存储内容链接
    comment_urls = []  #存储评论页的链接
    
    # 筛选符合条件的子网页链接
    for each_x in next_data:
        if '.html' in each_x and 'photoview' not in each_x and 'product.auto.' not in each_x and 'live.' not in each_x and 'v.163.com' not in each_x:
            next_urls.append(each_x)   #加入列表中
            comment_url = 'http://comment.tie.163.com/' + each_x.split('/')[-1]  #构造评论页的链接
            comment_urls.append(comment_url)  
    return next_urls,comment_urls      #返回两个列表
  
# 对评论页的链接单独进行解析
def get_number(url):
    # 头部信息
    header = {
            'Cookie':'mail_psc_fingerprint=0bed4b9ba8967a14f1d478356d09bfc7; NTES_CMT_USER_INFO=116257010%7C%E6%9C%89%E6%80%81%E5%BA%A6%E7%BD%91%E5%8F%8B06Xv3O%7Chttps%3A%2F%2Fsimg.ws.126.net%2Fe%2Fimg5.cache.netease.com%2Ftie%2Fimages%2Fyun%2Fphoto_default_62.png.39x39.100.jpg%7Cfalse%7CbTE1NjI0OTUyNzExQDE2My5jb20%3D; _qddaz=QD.n1ayxp.i0o6se.j6qijwrv; vjuids=c6df96352.15f10b1e0a7.0.a6aa51a8; __gads=ID=74eb58738effe4d6:T=1507813617:S=ALNI_MblRY5w-mbzr0KVq_8g3rY95BTWEQ; P_INFO=m15624952711@163.com|1518320131|0|mail163|00&99|yun&1517495715&mail163#hun&431200#10#0#0|156711&1||15624952711@163.com; nts_mail_user=15624952711@163.com:-1:1; _ntes_nnid=d275eb6942af5fed0cafa615eac0917d,1525586852324; _ntes_nuid=d275eb6942af5fed0cafa615eac0917d; __e_=1526355691756; usertrack=ezq0plshPfCkG/iKHjROAg==; _ga=GA1.2.1780550983.1493294252; __f_=1531116203155; Province=010; City=010; NNSSPID=e42f816830ec4d87884d27341f2c5c9d; NTES_hp_textlink1=old; UM_distinctid=164a62f39b19ac-0aa47882d0fb26-5d4e211f-e1000-164a62f39b24ec; __guid=167472044.1048577775480694800.1531796769648.631; _antanalysis_s_id=1531796772610; _antanalysis_s_id=1531832243538; __utma=187553192.1780550983.1493294252.1526994531.1531833293.7; __utmb=187553192.1.10.1531833293; __utmc=187553192; __utmz=187553192.1526994531.6.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __oc_uuid=d5563f60-67cf-11e7-80ec-2bdac8e17837; ne_analysis_trace_id=1531833327896; pgr_n_f_l_n3=5d348f2a94c224ae15318340244565012; vinfo_n_f_l_n3=5d348f2a94c224ae.1.10.1507813613753.1531833144034.1531834108850; s_n_f_l_n3=5d348f2a94c224ae1531833145029; vjlast=1507813614.1531758378.12; monitor_count=17',
           'Host':'comment.tie.163.com',
             'Referer':url,
             'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'}
    num_html = get_html(url,headers = header)
    
    #采用 正则表达式解析
    reg_1  = re.compile('"cmtAgainst":(\d+)')
    reg_2  = re.compile('"cmtVote":(\d+)')
    reg_3  = re.compile('"rcount":(\d+)')
    reg_4  = re.compile('"tcount":(\d+)')
    
    #count为评论人数
    count = re.findall(reg_4,num_html)[0]
    c1 = int(re.findall(reg_1,num_html)[0])
    c2 = int(re.findall(reg_2,num_html)[0])
    c3 = int(re.findall(reg_3,num_html)[0])
    
    #join为参与人数
    join_count = str(c1+c2+c3)
    return count,join_count  #返回两个人数
   
# 对子网页进行内容提取
def get_Infos(html):
    inter = etree.HTML(html)
    
    #最后将结果放入 列表中
    final_list = []
    
    #  获取时间，没有的话就不用添加到列表中
    Time = inter.xpath('//*[@id="epContentLeft"]/div[1]/text()')
    if len(Time) != 0:
        # 有结果的话就加入列表中，方便写入文件
        final_list.append(('时间：',Time[0].strip().split('来源:')[0].strip()))
    
    # 获取来源，没有的话就不用添加到列表中
    Origin = inter.xpath('//*[@id="ne_article_source"]/text()')
    if len(Origin) != 0:
        # 有结果的话就加入列表中，方便写入文件
        final_list.append(('来源：',Origin[0].strip()))
        
     # 获取新闻正文，没有的话就不用添加到列表中
    Content = inter.xpath('//*[@id="endText"]/p/text()')
    if len(Content) != 0:
        # 对内容格式进行处理
        Content = ''.join([i.strip() for i in Content])
        # 有结果的话就加入列表中，方便写入文件
        final_list.append(('内容：',Content))
    
    # 获取编辑人员，没有的话就不用添加到列表中
    Author = inter.xpath('//span[@class="ep-editor"]/text()')
    if len(Author) != 0:
        #进行格式处理
        Author = Author[0].split('编辑：')[1].split('_N')[0]
        # 有结果的话就加入列表中，方便写入文件
        final_list.append(('编辑；',Author))
    return final_list   #返回内容列表
    
# 将得到的列表写入文件中
def write_file(filename,data):
    #打开文件
    with open(filename,'a',errors='ignore') as fp:
        #对列表元素进行迭代，全写入文件中
        for each_x in data:
            fp.write("{key}{value}  \n".format(key = each_x[0],value = each_x[1]))
   
def main():
    # 最初的首页
    base_url = 'http://www.163.com/'
    #文件名
    file = 'C:/Users/dell/desktop/new2/News%s.txt'
    #获取初始的网页源码
    html = get_html(base_url)
    #调用函数获取 子网页和评论页链接
    next_urls,Com_urls = get_next_html(html)
    i = 1
    #迭代元素
    for each,other in zip(next_urls,Com_urls):
        #获取子网页
        next_html  = get_html(each)
        #获取子网页的内容
        result = get_Infos(next_html)
        # 如果没有结果就重新放入列表中，再试一次
        if len(result) == 0:
            next_urls.append(each)
            continue
        # 返回参与人数和评论人数
        num_result, num_join = get_number(other)
        # 将两个人数放入列表中
        result.append(('评论人数：',num_result))
        result.append(('参与人数：',num_join))
        file = 'C:/Users/dell/desktop/new4/News%s.txt' % str(i)
        #写入文件中
        write_file(file,result)
        i += 1
        
if __name__ == '__main__':
    main()
      
        
        
        
