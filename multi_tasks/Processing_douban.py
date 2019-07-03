#!/usr/bin/env python
# coding: utf-8


import requests
from bs4 import BeautifulSoup
import multiprocessing
import time
import os

class geturl(multiprocessing.Process):
    def __init__(self, urlqueue, count, url):
        super(geturl, self).__init__()
        self.urlqueue = urlqueue
        self.url = url
        self.count = count
    
    def run(self):
        while self.count >= 0 and self.count <= 250:
            page_url = self.url + '?start=' + str(self.count) + '&filter='
            self.urlqueue.put(page_url)
            self.count += 25


class getcontent(multiprocessing.Process):
    def __init__(self, urlqueue):
        super(getcontent,self).__init__()
        self.urlqueue = urlqueue
    
    def run(self):
        while True:
            header = {'Referer': 'https://www.douban.com/',
                      'User-Agent':
                          'ozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
            url = self.urlqueue.get()
            res = requests.get(url, headers=header)
            soup = BeautifulSoup(res.text, 'html.parser')
            for contents in soup.select('.info'):
                if contents.select('.hd') != []:
                    titles = ''.join(contents.select('.hd')[0].text.split())
                    # print(titles)
                if contents.select('.bd p') != []:
                    peoples = contents.select('.bd p')[0]
                    name = peoples.contents[0].strip()
                    addrs = peoples.contents[2].strip()
                    # print(name)
                    # print(addrs)
                score = contents.select('.bd .star .rating_num')[0].text
                numbers = contents.select('.bd .star span')[3].text  # .contents[6]
                # print (score)
                # print(numbers)
                if contents.select('.bd .quote .inq') != []:
                    message = contents.select('.bd .quote .inq')[0].text
                    # print(message)
 
                content = [titles, name, addrs,
                           score, numbers, message]
 
                # with open('C:\\Users\\fred\\Desktop\\douban.txt', 'a', encoding='utf-8') as file:
                #     for each in content:
                #         file.write(each)
 
                #         file.write('\n')
                #     file.write('\n')
                #     file.write('\n')
                # print()
                for each in content:
                    print(each)
                    print('\n')
                print('-------------------------')
                print('\n\n')



            
            if self.urlqueue.empty():
                # with open('C:\\Users\\fred\\Desktop\\star.txt', 'a', encoding='utf-8') as file:
                #     file.write('*')
                break
            # time.sleep(1)

def main():
    # st = time.time()
    q = multiprocessing.Queue()
    get = geturl(q,0,'https://movie.douban.com/top250' )
    content =getcontent(q)
    get.start()
    content.start()
    get.join()
    content.join()
    # ed = time.time()
    # print(st - ed)

if __name__ == '__main__':
    main()




