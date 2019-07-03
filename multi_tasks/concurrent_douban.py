
import gevent
from gevent import monkey
import requests
from bs4 import BeautifulSoup
import multiprocessing
import time
import os


    
def create_url(base_url):
    count = 0
    urls = []
    while count >= 0 and count <= 250:
        page_url = base_url + '?start=' + str(count) + '&filter='
        count += 25
        urls.append(page_url)

    return urls
    
def run(url):
    header = {'Referer': 'https://www.douban.com/',
              'User-Agent':
                  'ozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
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


def main():

    # st = time.time()
    monkey.patch_all()

    base = 'https://movie.douban.com/top250'
    urls = create_url(base)
    gens = []
    for each in urls:
        g = gevent.spawn(run, each)
        gens.append(g)

    gevent.joinall(gens)

    # end = time.time()

    # print(end - st)

if __name__ == '__main__':
    main()