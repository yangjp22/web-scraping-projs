import requests
import tkinter
from lxml import etree
import re
import os

class FindURL(object):

    def __init__(self):
        # 创建主窗口
        self.root = tkinter.Tk()
        # 主窗口大小
        self.root.minsize = (600, 400)
        # 生成框架
        self.frame = tkinter.Frame(self.root)
        # 框架的位置布局
        self.frame.pack()
        # 设置标题
        self.root.title("Download Picture")
        # 创建一个输入框
        self.url_input = tkinter.Entry(self.frame, width=30)
        self.display_info = tkinter.Listbox(self.root, width=50)

        # 创建一个查询按钮
        self.result_button = tkinter.Button(self.frame, command=self.find_URL_a, text="查询")
        self.url_input.focus()

    def gui_arrange(self):
        self.url_input.pack(side=tkinter.LEFT)
        self.display_info.pack()
        self.result_button.pack(side=tkinter.RIGHT)


    def get_html(self,url):
        self.headers = {
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36',
        'Referer':url,
         }
        self.response = requests.get(url,headers = self.headers,verify = True)
        # 对返回的信息的编码进行处理
        self.response.encoding = self.response.apparent_encoding
        # 返回相应的文本
        return self.response       
        
    def find_URL_a(self):
        self.url = self.url_input.get()
        self.url_input.delete(0, tkinter.END)
        self.display_info.delete(0, tkinter.END)

        self.html = self.get_html(self.url).text
        self.inner = etree.HTML(self.html)
        self.title = self.inner.xpath('//li[contains(text(),"书名")]/text()')[0].split('书名:')[1].strip().split(' ')
        self.title = ''.join([each.strip() for each in self.title])
        self.main_pic_urls = self.inner.xpath('//ul[@class="tb-thumb tm-clear"]/li/a/img/@src')
        
        self.reg1 = re.compile('"httpsDescUrl":"(.*?)"')
        self.inter = "http:" + re.findall(self.reg1,self.html)[0]
        self.next_html = self.get_html(self.inter).text
        self.vise_pic_urls = etree.HTML(self.next_html).xpath('//img[@align="absmiddle"]/@src')
       
        self.write_file1()
        print("===============下载完毕================")
        
    def write_file1(self):
        self.folder = os.getcwd() + '\\' + self.title
        print(self.folder)
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)
        self.folder_2 = self.folder + r'\详情页'
        if not os.path.exists(self.folder_2):
            os.makedirs(self.folder_2)
        self.folder_1 = self.folder + r'\主图'
        if not os.path.exists(self.folder_1):
            os.makedirs(self.folder_1)
        
        self.length_1 = len(self.main_pic_urls)
        for i in range(self.length_1):
            self.file_1_i = self.folder_1 + '\\' + str(i+1) +'.jpg'
            each_x = 'http:' + self.main_pic_urls[i].split('q90')[0][:-5] + 'q90.jpg'
            with open(self.file_1_i,'wb') as fp:
                u = self.get_html(each_x)
                fp.write(u.content)
                
        self.length_2 = len(self.vise_pic_urls)
        for i in range(self.length_2):
            self.file_2_i = self.folder_2 + '\\' + str(i+1) +'.jpg'
            each_x =  self.vise_pic_urls[i]
            with open(self.file_2_i,'wb') as fp:
                u = self.get_html(each_x)
                fp.write(u.content) 
       
def main():
    FL = FindURL()
    FL.gui_arrange()
    tkinter.mainloop()
    

if __name__ == "__main__":
    main()
