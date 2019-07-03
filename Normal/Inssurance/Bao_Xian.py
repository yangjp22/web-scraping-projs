import requests
import urllib


##
##def get_html(url):
##    headers = {
         


    
url = 'http://bxjg.circ.gov.cn/tabid/5253/ctl/ViewOrgList/mid/16658/OrgTypeID/1/Default.aspx?ctlmode=none'

response = requests.get(url)


file = 'C:/Users/dell/desktop/data3.html'

urllib.request.urlretrieve(url,file)

print(response.text)
