import json
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import re
import os


url='http://api.roll.news.sina.com.cn/zt_list?channel=news&cat_1=gnxw&cat_2==gdxw1||=gatxw||=zs-pl||=mtjj&level==1||=2&show_ext=1&show_all=1&show_num=22&tag=1&format=json&page={}&callback=newsloadercallback&_=1528548757769'
commenturl='http://comment5.news.sina.com.cn/page/info?version=1&format=json&channel=gn&newsid=comos-{}&group=undefined&compress=0&ie=utf-8&oe=utf-8&page=1&page_size=3&t_size=3&h_size=3&thread=1'

def mkdir(path):
    folder = os.path.exists(path)
    if not folder:  # 判断是否存在文件夹如果不存在则创建为文件夹
        os.makedirs(path)  # makedirs 创建文件时如果路径不存在会创建这个路径
        print("---  new folder...  ---")
    else:
        print("---  There is this folder!  ---")

def parseListLinks(url):
    i=1
    newsdetail=[]
    res=requests.get(url)
    jd=json.loads(res.text.lstrip('  newsloadercallback(').rstrip(');'))
    for ent in jd['result']['data']:
        newsdetail.append(getnewsdetail(ent['url'],i))
        i+=1
    return newsdetail

def get_comment_people(newsurl):  # 获取参与人数
    m = re.compile('doc-i(.*?).shtml').findall(newsurl)
    newsid = m[0]
    comments = requests.get(commenturl.format(newsid))
    jd = json.loads(comments.text)
    return jd['result']['count']['total']

def get_comment_num(newsurl):  # 获取新闻评论数
    m = re.compile('doc-i(.*?).shtml').findall(newsurl)
    newsid = m[0]
    comments = requests.get(commenturl.format(newsid))
    jd = json.loads(comments.text)
    return jd['result']['count']['show']

def getnewsdetail(newsurl,i):  # 获得单页的新闻内容
   # sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf8')
    f1=open("sina\\%d.txt"%i,'w',errors='ignore')
    #f1 = open("sina\\%d.txt" % i, 'w',encoding='UTF-8')
    result = {}   #用一个字典存放各种信息
    res = requests.get(newsurl)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'html.parser')
    result['title'] = soup.select('.main-title')[0].text  # 标题
    timesource = soup.select('.date-source span')[0].text
    #result["time"] = datetime.strptime(timesource, '%Y年%m月%d日 %H:%M').strftime('%Y-%m-%d')  # 时间

    result['时间']=timesource
    result['编辑'] = soup.select('#article p')[-1].text.strip('责任编辑：')  # 获取作者姓名
    result['评论数'] = get_comment_num(newsurl)
    result['参与人数'] = get_comment_people(newsurl)

    articleall = []  # 获取文章内容
    for p in soup.select('#article p')[:-1]:
        articleall.append(p.text.strip())
    article=' '.join(articleall)
    result['主体'] = article
    result['来源'] = soup.select('.source')[0].text  # 来源

    f1.write("时间：%s  \n"%timesource)
    f1.write("编辑：%s  \n"%result['编辑'] )
    f1.write("评论数：%d  \n"%result['评论数'])
    f1.write("参与人数：%d  \n"%result['参与人数'])
    f1.write("来源%s \n" %result['来源'])
    #articleall.append("item")
    #for i in articleall:
        #f1.write(i)
        #f1.write("\n")
    f1.write(article)

    f1.close()

    return result

def main():
    news_total=[]
    mkdir('sina')

    for i in range(1,10):
        newsurl=url.format(i)
        newsary=parseListLinks(newsurl)
        news_total.extend(newsary)
    print(news_total)

if __name__=="__main__":
    main()




