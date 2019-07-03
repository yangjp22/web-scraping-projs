import requests
import base64
from lxml import etree

def getHex(param1):
    return {
        'str': param1[4:],
        'hex': ''.join(list(param1[:4])[::-1]),
    }

def getDecimal(param1):
    loc2 = str(int(param1, 16))
    print(loc2)#
    return {
        'pre': list(loc2[:2]),
        'tail': list(loc2[2:]),
    }

def substr(param1, param2):
    loc3 = param1[0: int(param2[0])]
    loc4 = param1[int(param2[0]): int(param2[0]) + int(param2[1])]
    print("loc4",loc4)
    return loc3 + param1[int(param2[0]):].replace(loc4, "")

def getPosition(param1, param2):
    param2[0] = len(param1) - int(param2[0]) - int(param2[1])
    return param2

def decode (code):
    dict2 = getHex(code)
    dict3 = getDecimal(dict2['hex'])
    print("dict3", dict3['pre'])  #
    str4 = substr(dict2['str'], dict3['pre'])
    return base64.b64decode(substr(str4,getPosition(str4, dict3['tail'])))

def crawl_video_url (url):
    response = requests.get(url).text
    obj = etree.HTML(response).xpath('//meta[@property="og:video:url"]/@content')[0]
    result = decode(code)
    print(result)

if __name__ == '__main__':
    url = "http://www.meipai.com/media/816057957"
    crawl_video_url(url)