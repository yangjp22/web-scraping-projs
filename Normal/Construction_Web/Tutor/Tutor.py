import requests
import pandas as pd
from lxml import etree
import re
from multiprocessing import Process,Queue
from urllib import parse
import time

class Producer(Process):
    
    def __init__(self, url, queue):
        super(Producer, self).__init__()
        self.queue = queue
        self.url = url
    
    def gethtml(self, url):
        headers = {
            'Cookie': '_ga=GA1.2.1599477005.1562532451; _gid=GA1.2.1004816103.1562532451',
            'authority': 'www.tutorperini.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36'
         }
        response = requests.get(url, headers = headers)
        response.encoding = response.apparent_encoding
        return response
    
    def get_max_page(self):
        data = {
            'c': 'Commercial|Education|Government & Military|Healthcare|Mixed Use & Retail|Residential',
            'p': 1
        }
        
        self.new_url = self.url + parse.urlencode(data)
        
        response = self.gethtml(self.new_url).text
        
        max_reg = '//ul[@class="pager"]/li[last()]/a/text()'
        
        max_page = int(etree.HTML(response).xpath(max_reg)[0].strip())
        
        return max_page
    
    def run(self):
        maxPage = self.get_max_page()
        print(maxPage)
        for i in range(1, maxPage + 1):
            data = {
            'c': 'Commercial|Education|Government & Military|Healthcare|Mixed Use & Retail|Residential',
            'p':i
            }
            self.new_url = self.url + parse.urlencode(data)
            
            html = self.gethtml(self.new_url).text
            
            item_reg = '//div[@class="col"]/a/@href'
            
            items = etree.HTML(html).xpath(item_reg)
            
            for single in items:
                single_url = 'https://www.tutorperini.com' + single
                single_html = self.gethtml(single_url).text
                self.queue.put(single_html)
                print('-----*****-------')
        self.queue.put(None)

class Consumer(Process):
    
    def __init__(self, queue):
        super(Consumer, self).__init__()
        self.queue = queue
        self.result = []
    
    def parse_title(self, obj):
        title_reg = '//div[@class="project-header"]//strong'
        
        self.title = obj.xpath(title_reg)
        if len(self.title) == 0:
            self.title = None
        else:
            self.title = self.title[0].xpath('string(.)').strip()
        
    def parse_description(self, obj):
        description_reg = '//div[@class="left-col"]/p/text()'

        self.description = obj.xpath(description_reg)
        if len(self.description ) == 0:
            self.description = None
        else:
            self.description = '\n'.join([single_.strip() for single_ in self.description])
            
    def parse_awards(self, obj):
        award_reg = '/html/body/div/main/div/div[3]/div[4]/div[2]/p/text()'

        self.award = obj.xpath(award_reg)
        if len(self.award ) == 0:
            self.award = None
        else: 
            self.award = '\n'.join([single_.strip() for single_ in self.award])

    def parse_content(self, obj):
        content_reg = '//div[@class="col left"]'
        self.content = obj.xpath(content_reg)
        if len(self.content) == 0:
            self.content = None
        else: 
            self.content = self.content[0].xpath('string(.)')

    def parse_size(self, obj):
        size_reg = '/html/body/div/main/div/div[3]/div[2]/div[3]/p[1]/br/text()'
        self.size = obj.xpath(size_reg)
        if len(self.size) == 0:
            self.size = None
        else: 
            self.size = '\n'.join([single_.strip() for single_ in self.size])

    def parse_completion(self, obj):
        completion_reg = '/html/body/div/main/div/div[3]/div[2]/div[3]/p[2]/br/text()'
        self.completion = obj.xpath(completion_reg)
        if len(self.completion) == 0:
            self.completion = None
        else: 
            self.completion = '\n'.join([single_.strip() for single_ in self.completion])

    def parse_owner(self, obj):
        owner_reg = '/html/body/div/main/div/div[3]/div[2]/div[2]/p[2]/br/text()'
        self.owner = obj.xpath(owner_reg)
        if len(self.owner) == 0:
            self.owner = None
        else: 
            self.owner = '\n'.join([single_.strip() for single_ in self.owner]) 

    def parse_location(self, obj):
        location_reg = '/html/body/div/main/div/div[3]/div[2]/div[2]/p[2]/br/text()'
        self.location = obj.xpath(location_reg)
        if len(self.location) == 0:
            self.location = None
        else: 
            self.location = '\n'.join([single_.strip() for single_ in self.location])


    def run(self):
        
        while True:
            take = self.queue.get()

            if take is None:
                break

            print('******----------******')
            html = etree.HTML(take)
            self.dict = {}
            self.parse_title(html)
            self.parse_description(html)
            self.parse_awards(html)
            self.parse_size(html)
            self.parse_completion(html)
            self.parse_location(html)
            self.parse_owner(html)
            self.parse_content(html)
            self.dict['title'] = self.title
            self.dict['description'] = self.description
            self.dict['awards'] = self.award
            self.dict['size'] = self.size
            self.dict['completion'] = self.completion
            self.dict['location'] = self.location
            self.dict['owner'] = self.owner
            self.dict['content'] = self.content
        
            self.result.append(self.dict)

        df = pd.DataFrame(self.result)
        df.to_csv('./tutor.csv', index = False)
        
def main():
    queue = Queue()
    baseUrl = 'https://www.tutorperini.com/projects/?'
    producer = Producer(baseUrl, queue)
    consumer = Consumer(queue)
    producer.start()
    consumer.start()
    producer.join()
    consumer.join()
    
if __name__ == '__main__':
    main()