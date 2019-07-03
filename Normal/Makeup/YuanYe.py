import requests
import re
from faker import Factory
import time
fake = Factory().create()

s = []
for i in range(1,2):
    base_url = 'http://125.35.6.80:8080/ftba/itownet/fwAction.do?method=getBaNewInfoPage'
    data = {
                        'on':'true',
                        'page':i,
                        'pageSize':15,
                        'productName':'原液',
                        'conditionType':1,
                        'applyname':'',
                        'applysn':''}
    reg_Number = re.compile('"applySn":"(.*?)"')

    headers = {
    'Host':'125.35.6.80:8080',
    'Origin':'http://125.35.6.80:8080',
    'Referer':'http://125.35.6.80:8080/ftba/fw.jsp',
    'User-Agent':fake.user_agent()
    }

    html = requests.post(base_url,data = data,headers = headers)
    print(html.url)
##    if len(html.text) == 0:
##        print(html.status_code)
##        print('****')
##    t = re.findall(reg_Number,str(html.text))
##    if len(t) != 0:
##        s.append(t)
##    time.sleep(1)
##print(len(s))
