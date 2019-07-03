from base.DataOutput import DataOutput
from base.HTMLParser import HTMLParser
from base.HTMLDownload import HTMLDownload
from base.URLManager import URLManager


class SpiderMan(object):
    def __init__(self):
        self.manager = URLManager()
        self.downloader = HTMLDownload()
        self.parser = HTMLParser()
        self.output = DataOutput()


    def crawl(self, root_url):
        # 添加入口 URL
        self.manager.addNewUrl(root_url)
        # 判断 url 管理器中是否有新的 url，同时判断抓取多少个 url
        while( not self.manager.newUrlEmpty() and self.manager.oldUrlSize()<100):
            try:
                # 从 URL 管理器获取新的 URL
                new_url = self.manager.getNewUrl()
                print(new_url)
                # HTML 下载器下载网页
                html = self.downloader.download(new_url)
                # HTML 解析器抽取网页数据
                new_urls, data = self.parser.parser(new_url, html)
                print(new_urls)
                # 将抽取的 url 添加到 URL 管理器中
                self.manager.addNewUrls(new_urls)
                # 数据存储器存储文件
                self.output.storeData(data)
                print("已经抓取%s 个链接" % self.manager.oldUrlSize())
            except Exception as e:
                print("failed")
                print(e)
            # 数据存储器将文件输出成指定的格式
            self.output.outputHtml()


if __name__ == '__main__':
    spider_man = SpiderMan()
    spider_man.crawl("http://www.runoob.com/w3cnote/page/1")