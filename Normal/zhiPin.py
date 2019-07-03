import pickle
import csv
from lxml import etree

def get_infos(html):
    obj_2 = etree.HTML(html)
    all_infos_1 = obj_2.xpath('//div[@class="info-primary"][1]')
    if len(all_infos_1) == 0:
        Name = None
        Raise = None
        Number = None
    else:
        all_infos_1 = all_infos_1[0]
        Name = all_infos_1.xpath('h1/text()')[0].strip().replace('\u2122','').replace('\u2022','')
        Raise = all_infos_1.xpath('p/text()')[0].strip().replace('\u2122','').replace('\u2022','')
        Number = all_infos_1.xpath('p/text()')[1].strip().replace('\u2122','').replace('\u2022','')
    
    Company = obj_2.xpath('//div[@class="job-sec"][1]/div/text()')
    Company = '\n'.join([each_comp.strip() for each_comp in Company]).replace('\u2122','').replace('\u2022','')
    Product = obj_2.xpath('//div[@class="job-sec company-products"]')
    
    if len(Product) == 0:
        Product = None
    else:
        final_text = []
        text = Product[0].xpath('//div[@class="job-sec company-products"]/ul/li/div[2]/div/a')
        for each_text in text:
            each_text = each_text.xpath('text()')
            inner_text = ''.join([i.strip() for i in each_text])
            final_text.append(inner_text) 
        Product = '\n'.join([each_text.strip() for each_text in final_text]).replace('\u2122','').replace('\u2022','')
    return [Name,Raise,Number,Company,Product]

def write_file(file_name,data):
    with open(file_name,'a',encoding = 'gbk',errors = 'ignore') as fp:
        writer = csv.writer(fp)
        writer.writerow(data)
    
def main():
    file = 'C:/Users/dell/desktop/ZhiPin2.csv'
#    origi = 'C:/Users/dell/desktop/ZhiPin///%d.pkl'
    with open(file,'a',encoding = 'gbk',errors = 'ignore') as fp:
        writer = csv.writer(fp)
        writer.writerow(['名字','融资情况','人数','公司简介','产品简介'])
    
    data = []
    for i in range(97):
        with open('C:/Users/dell/desktop/ZhiPin/%d.pkl' % i,'rb') as fp:
            data.append(pickle.load(fp))

#    print(data)
            
    for Inn_html in data:
        result = get_infos(Inn_html)
        print(result)
        write_file(file,result)
        
if __name__ == '__main__':
	 main()


      
    