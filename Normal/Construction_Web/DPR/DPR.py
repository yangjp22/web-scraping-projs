import requests
import pandas as pd
from lxml import etree
from multiprocessing import Process, Queue
import time

class Producer(Process):
    def __init__(self, url, queue):
        super(Producer, self).__init__()
        self.url = url
        self.queue = queue

    def get_html(self, url):
        headers = {
            'Cookie': '__cfduid=dd8bf4a15f8aef3ad51ee4ae251f737661562531642; hubspotutk=516caff5df2b7d915b0974636bcfab99; cookiePU=yes; __atuvc=1%7C28; __utma=182893811.1527619433.1562531645.1562531645.1562629349.2; __utmc=182893811; __utmz=182893811.1562629349.2.2.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); __utmt=1; __hstc=163232931.516caff5df2b7d915b0974636bcfab99.1562531645496.1562531645496.1562629349218.2; __hssrc=1; __hssc=163232931.3.1562629349218; __utmb=182893811.13.9.1562629729389',
            'Host': 'www.dpr.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.encoding = response.apparent_encoding
        return response

    def run(self):
        self.parse()

    def parse(self):
        html = self.get_html(self.url).json()
        for i, each in enumerate(html):
            if 'coreMarket' not in each:
                core_market_ = None
            else:
                core_market_ = ', '.join(each['coreMarket'])

            if 'client' not in each:
                client_ = None
            else:
                client_ = each['client']

            if 'title' not in each:
                title_ = None
            else:  
                title_ = each['title']

            url_ = each['url']
            html_ = self.get_html(url_).text
            print(url_)
            self.queue.put([core_market_, client_, title_, url_, html_])
            print('-----Put---%s--' % str(i))

        self.queue.put(None)


class Consumer(Process):
    def __init__(self, queue):
        super(Consumer, self).__init__()
        self.queue = queue
        self.finals = []


    def run(self):

        while True:
            single = self.queue.get()

            if single == None:
                break

            print('-----Get-----')
            self.parse(single[-1])

            self.dict = {}
            self.dict['Market'] = single[0]
            self.dict['Client'] = single[1]
            self.dict['Title'] = single[2]
            self.dict['Link'] = single[3]
            self.dict['Article'] = self.article
            self.dict['Fact'] = self.fact
            self.finals.append(self.dict)

        self.save()


    def parse(self, html):
        obj = etree.HTML(html)

        article_reg = '//div[@class="article project-article"]/p/text()'
        articles = obj.xpath(article_reg)
        if len(articles) == 0:
            self.article = None
        else:
            self.article = '\n'.join([single_.strip()
                                       for single_ in articles])

        fact_reg = '//ul[@id="nav-sub"]/li'
        facts = obj.xpath(fact_reg)
        if len(facts) == 0:
            self.fact = None
        else:
            self.fact = ''
            for fact_ in facts[:-1]:
                self.fact_ = fact_.xpath('string(.)').strip().split('\n')
                if len(self.fact_) != 1:
                    self.fact_ = self.fact_[0] + ': ' + ', '.join(self.fact_[1: ])
                else:
                    self.fact_ = self.fact_[0]
                self.fact += self.fact_ + '\n'
            self.fact.strip('\n')


    def save(self):
        self.data = pd.DataFrame(self.finals)
        self.data.to_csv('./Dpr.csv', index = False)

def main():
    queue = Queue()
    url = 'https://www.dpr.com/api/project-list.json'
    producer = Producer(url, queue)
    consumer = Consumer(queue)
    producer.start()
    consumer.start()
    producer.join()
    consumer.join()


if __name__ == '__main__':
    main()