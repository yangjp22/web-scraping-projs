import requests
from lxml import etree
import faker
import time
import json
from collections import defaultdict
import pandas as pd
import numpy as np
from collections import Counter

def getHtml(url, header = None ,param = None):
	response = requests.get(url,headers = header,params = param )
	response.encoding = response.apparent_encoding
	return response.text

def processHtmlSellRang(html):
	content = html.split(',[')
	inner = [each.strip(']') for each in content[1:]]
	final = [each.split(',') for each in inner]
	return final

def processOriginChange(ID,timeID):
    originUrl = 'http://ftapi.jczj123.com/home/service.json?service=HUNDRED_EUR_ODDS_QUERY&raceId={}&_={}'.format(ID,timeID)
    header = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36',
    'Host':'ftapi.jczj123.com',
    'Origin':'http://www.jczj123.com'}
	   # 'Referer':'http://www.jczj123.com/lottery/eurOdds.htm?raceId={}'.format(ID)}
    html = getHtml(originUrl,header = header)
    oJson = json.loads(html)
    innerData = oJson['response']['eurList']
    Origin = []
    Delta = []
    for i in innerData:
    	if i['cn'] == 'bet 365':
    		Origin.append(i['fho']) 
    		Origin.append(i['fd'])
    		Origin.append(i['fgo'])
    		Delta.append(i['ho'])
    		Delta.append(i['d'])
    		Delta.append(i['go'])
    		break    	
    return Origin,Delta

def Judge(A,B):
	if A in B:
		return 1
	elif B in A:
		return 1
	else:
		for jkl in A:
			if jkl in B:
				return 1
		return 0

def innerInfos(timeId,groupId):
	innerUrl = 'http://ft.jczj123.com/season/seasonRaceRank.json?groupId={}&rankType=SR_HAR&_={}'.format(groupId,timeId)
	head = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36',
	'Cookie':'_tracker_global_id=20180827174618g104dd61141fa420d96400c80d23dacb8; jczjsid=2018082809ccbec125ba8141d4a9a6d835d75e16bc80e43f3d; jczjsid_sn=2c626e1acd84a811536fc958a524b2ae; loginInfo=7Ervqy3oAMfrVYYGkin4xklmfpyScdXqdp2Hoc3hRmgcTqrtV9qMsn1wK4Hh2k8h4kX5r7RRwOiORtWAeD+srg==; buriedData=screen%3A1280X720%7CuserId%3A8201708111815462; Hm_lvt_100743a90fea504059524b1e12c43dc0=1535377477,1535418676,1535437712,1535437755; Hm_lpvt_100743a90fea504059524b1e12c43dc0=1535438113; JSESSIONID=BB84678EE39EDCFA46C095F10EA0C85E.jchweb-1-1; cookie=1.1.6.f4977bf8'
	}
	innerHtml = getHtml(innerUrl,header = head)
	print(innerHtml)
	innerObj = json.loads(innerHtml)
	innerHomeData = innerObj['rankResult']['seasonRaceRankViewDataList']
	homeMatch = sum([int(each['mc']) for each in innerHomeData])
	homeGain = sum([int(each['ig']) for each in innerHomeData])
	homeLoss = sum([int(each['lg']) for each in innerHomeData])

	innerGuestUrl = innerUrl.replace('HAR','GAR')
	innerGuestHtml = getHtml(innerGuestUrl,header = head)
	innerGuestObj = json.loads(innerGuestHtml)
	innerGuestData = innerGuestObj['rankResult']['seasonRaceRankViewDataList']
	GuestMatch = sum([int(each['mc']) for each in innerGuestData])
	GuestGain = sum([int(each['ig']) for each in innerGuestData])
	GuestLoss = sum([int(each['lg']) for each in innerGuestData])

	return [homeMatch,homeGain,homeLoss],[GuestMatch,GuestGain,GuestLoss]


def DetailInfos(Id,timeID):
	head = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36',
	'Cookie':'_tracker_global_id=20180827174618g104dd61141fa420d96400c80d23dacb8; jczjsid=2018082809ccbec125ba8141d4a9a6d835d75e16bc80e43f3d; jczjsid_sn=2c626e1acd84a811536fc958a524b2ae; loginInfo=7Ervqy3oAMfrVYYGkin4xklmfpyScdXqdp2Hoc3hRmgcTqrtV9qMsn1wK4Hh2k8h4kX5r7RRwOiORtWAeD+srg==; buriedData=screen%3A1280X720%7CuserId%3A8201708111815462; Hm_lvt_100743a90fea504059524b1e12c43dc0=1535377477,1535418676,1535437712,1535437755; Hm_lpvt_100743a90fea504059524b1e12c43dc0=1535438113; JSESSIONID=BB84678EE39EDCFA46C095F10EA0C85E.jchweb-1-1; cookie=1.1.6.f4977bf8'
	}
	detailUrl = 'http://ft.jczj123.com/race/jump/{}.htm'.format(Id)
	detailHtml = getHtml(detailUrl,header = head)
	detailObj = etree.HTML(detailHtml)
	Text = detailObj.xpath('//li[@class="active first-nav"]/text()')
	
	if len(Text) > 0 and Text[0] == '积分榜':
		groupId = detailObj.xpath('//select[@id="scsele"]/option/@value')
		if len(groupId) > 0:
			groupId = groupId[0]
			HomeInfo,GuestInfo = innerInfos(timeID,groupId)
			print(HomeInfo,GuestInfo)
			return HomeInfo,GuestInfo
	else:
		return [None,None,None],[None,None,None]

def processLatestInfos(ID,timeID,HomeName,GuestName):
	initUrl = 'http://ftapi.jczj123.com/home/service.json?service=TEAM_LATEST_RACES_QUERY&raceId={}&_={}'.format(ID,timeID)
	header = {
	'Cookie':'_tracker_global_id=20180827174618g104dd61141fa420d96400c80d23dacb8; jczjsid=2018082809ccbec125ba8141d4a9a6d835d75e16bc80e43f3d; jczjsid_sn=2c626e1acd84a811536fc958a524b2ae; loginInfo=7Ervqy3oAMfrVYYGkin4xklmfpyScdXqdp2Hoc3hRmgcTqrtV9qMsn1wK4Hh2k8h4kX5r7RRwOiORtWAeD+srg==; Hm_lvt_100743a90fea504059524b1e12c43dc0=1535377477,1535418676,1535437712,1535437755; Hm_lpvt_100743a90fea504059524b1e12c43dc0=1535460981; JSESSIONID=BD939D37AC0AF9A68B12B7A9264D853A; cookie=1.1.6.f4977bf8',
	'Host':'ftapi.jczj123.com',
	'Referer':'http://www.jczj123.com/lottery/3841362.htm',
	'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36'
	}
	initHtml = getHtml(initUrl,header = header)
	oJson = json.loads(initHtml)
	initData = oJson['response']

	Hhome = [each for each in initData['homeViewDataList'] if Judge(HomeName,each['htn'])]
	HSample = Counter([each['htn'] for each in Hhome]).most_common(1)[0][0]
	Hhome = [each for each in initData['homeViewDataList'] if HSample == each['htn']]

	HhomeScore = [int(each['hs']) for each in Hhome]
	HguestScore = [int(each['gs']) for each in Hhome]

	Hdiff = []
	for i,j in zip(HhomeScore,HguestScore):
		if i > j:
			Hdiff.append(1)
		elif i == j:
			Hdiff.append(0)
		else:
			Hdiff.append(-1)

	Gguest = [each for each in initData['guestViewDataList'] if Judge(GuestName,each['gtm'])]
	GSample = Counter([each['gtm'] for each in Gguest]).most_common(1)[0][0]
	Gguest = [each for each in initData['guestViewDataList'] if GSample == each['gtm']]

	GhomeScore = [int(each['hs']) for each in Gguest]
	GguestScore = [int(each['gs']) for each in Gguest]
	Gdiff = []

	for i,j in zip(GhomeScore,GguestScore):
		if i < j:
			Gdiff.append(1)
		elif i == j:
			Gdiff.append(0)
		else:
			Gdiff.append(-1)
	# print([HomeName,Hdiff.count(1),Hdiff.count(0),Hdiff.count(-1),sum(HhomeScore),sum(HguestScore),len(Hhome)],[GuestName,Gdiff.count(1),Gdiff.count(0),Gdiff.count(-1),sum(GguestScore),sum(GhomeScore),len(Gguest)])
	return [Hdiff.count(1),Hdiff.count(0),Hdiff.count(-1),sum(HhomeScore),sum(HguestScore),len(Hhome)],[Gdiff.count(1),Gdiff.count(0),Gdiff.count(-1),sum(GguestScore),sum(GhomeScore),len(Gguest)]

def Operate(timeId):
	head = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36',
	'Cookie':'_tracker_global_id=20180827174618g104dd61141fa420d96400c80d23dacb8; jczjsid=2018082809ccbec125ba8141d4a9a6d835d75e16bc80e43f3d; jczjsid_sn=2c626e1acd84a811536fc958a524b2ae; loginInfo=7Ervqy3oAMfrVYYGkin4xklmfpyScdXqdp2Hoc3hRmgcTqrtV9qMsn1wK4Hh2k8h4kX5r7RRwOiORtWAeD+srg==; buriedData=screen%3A1280X720%7CuserId%3A8201708111815462; Hm_lvt_100743a90fea504059524b1e12c43dc0=1535377477,1535418676,1535437712,1535437755; Hm_lpvt_100743a90fea504059524b1e12c43dc0=1535438113; JSESSIONID=BB84678EE39EDCFA46C095F10EA0C85E.jchweb-1-1; cookie=1.1.6.f4977bf8'
	}
	baseUrl = 'http://www.jczj123.com/lottery/jczq/jczqSpfHhgg.htm'
	baseHtml = getHtml(baseUrl,header = head)

	# allObj = etree.HTML(baseHtml).xpath('//tr[@data-status="WAIT"]/@data-inid')
	baseObj = etree.HTML(baseHtml).xpath('//tr[@data-status="WAIT"]/@data-inid')
	baseId = etree.HTML(baseHtml).xpath('//tr[@data-status="WAIT"]/@id')
	baseId = [each.split('_')[-1] for each in baseId]
	HomeNames = etree.HTML(baseHtml).xpath('//tr[@data-status="WAIT"]//td[@class="text-right"]/span/text()')
	GuestNames = etree.HTML(baseHtml).xpath('//tr[@data-status="WAIT"]//td[@class="text-left"]/span/text()')
	ChampionNames = etree.HTML(baseHtml).xpath('//tr[@data-status="WAIT"]//td[2]/div/a/text()')

	HomeNames = [each.strip() for each in HomeNames]
	GuestNames = [each.strip() for each in GuestNames]
	ChampionNames = [each.strip() for each in ChampionNames]

	OriginsDict = {}
	DeltasDict = {}
	HomeDict = {}
	GuestDict = {}
	HomeChampaion = {}
	GuestChampaion = {}


	for each_x,each_y,each_home,each_guest,each_champion in zip(baseObj,baseId,HomeNames,GuestNames,ChampionNames):

		Origin,Delta = processOriginChange(each_x,timeId)
		OriginsDict[each_y] = Origin

		OriginsDict[each_y].insert(0,each_home)
		OriginsDict[each_y].insert(1,each_guest)

		DeltasDict[each_y] = Delta
		Home,Guest = processLatestInfos(each_x,timeId,each_home,each_guest)
		HomeDict[each_y] = Home
		GuestDict[each_y] = Guest
		# print()
		
		homeChampion,guestChampion = DetailInfos(each_x,timeId)
		HomeChampaion[each_y] = homeChampion
		HomeChampaion[each_y].insert(0,each_champion)
		GuestChampaion[each_y] = guestChampion
		
		# except:
		# 	continue

	sellUrl = 'http://img-dynamic.jczj123.com/script/lotterycore/jczq/jczq_rqspf_sp.js?_={}'.format(timeId)
	rangUrl = 'http://img-dynamic.jczj123.com/script/lotterycore/jczq/jczq_spf_sp.js?_={}'.format(timeId)
	sellHtml = getHtml(sellUrl)
	rangHtml = getHtml(rangUrl)
	Sell = processHtmlSellRang(sellHtml)
	Rang = processHtmlSellRang(rangHtml)
	SellDict = { each[0]:each[-3:] for each in Sell }
	RangDict = { each[0]:each[-3:] for each in Rang }

	FinalDict = defaultdict(list)

	for each in OriginsDict:
		FinalDict[each].extend(OriginsDict[each])

		if each in DeltasDict:
			FinalDict[each].extend(DeltasDict[each])
		else:
			FinalDict[each].extend([None,None,None])

		if each in SellDict:
			FinalDict[each].extend(SellDict[each])
		else:
			FinalDict[each].extend([None,None,None])	

		if each in RangDict:
			FinalDict[each].extend(RangDict[each])
		else:
			FinalDict[each].extend([None,None,None])

		if each in HomeDict:
			FinalDict[each].extend(HomeDict[each])
		else:
			FinalDict[each].extend([None,None,None,None,None,None])

		if each in GuestDict:
			FinalDict[each].extend(GuestDict[each])
		else:
			FinalDict[each].extend([None,None,None,None,None,None])

		if each in HomeChampaion:
			FinalDict[each].extend(HomeChampaion[each])
		else:
			FinalDict[each].extend([None,None,None,None])

		if each in GuestChampaion:
			FinalDict[each].extend(GuestChampaion[each])
		else:
			FinalDict[each].extend([None,None,None])

	return FinalDict
# return Deltas,Origins

def wirte_to_csv(filename,datas):
	names = ['主队','客队','初始赔率_胜','初始赔率_平','初始赔率_负','赔率变化_胜','赔率变化_平','赔率变化_负',
	'售卖赔率_胜','售卖赔率_平','售卖赔率_负','让球赔率_胜','让球赔率_平','让球赔率_负',
	'主队近况_胜','主队近况_平','主队近况_负','主队_进球数','主队_失球数','主队_总场数',
	'客队近况_胜','客队近况_平','客队近况_负','客队_进球数','客队_失球数','客队_总场数',
	'联赛名','主场_赛数目','主场_得分','主场_失分','客场_赛数目','客场_得分','客场_失分']
	Dataframe = pd.DataFrame(datas, dtype = np.float32,index = names)
	Dataframe = Dataframe.T

	# Dataframe['主队近况_平均进球'] = Dataframe['主队近况_进球']/Dataframe['主队近况_总场数']
	# Dataframe['客队近况_平均进球'] = Dataframe['客队近况_进球']/Dataframe['客队近况_总场数']

	# Dataframe['主队近况_胜率'] = Dataframe['主队近况_胜']/np.sum(Dataframe[['主队近况_胜','主队近况_平','主队近况_负']],axis = 1)
	# Dataframe['客队近况_胜率'] = Dataframe['客队近况_胜']/np.sum(Dataframe[['客队近况_胜','客队近况_平','客队近况_负']],axis = 1)
	dropcols = ['主队近况_胜','主队近况_平','主队近况_负','客队近况_胜','客队近况_平',
	            '客队近况_负']
	            
	Dataframe.drop(dropcols,axis=1, inplace=True)
	Dataframe["Name"] = Dataframe['主队'] + 'VS' + Dataframe['客队']
	Dataframe = Dataframe.set_index("Name")
	del Dataframe['主队']
	del Dataframe['客队']
	Dataframe.to_csv(filename,encoding = 'gbk')

def main():
	timeId = int(time.time()*1000)
	Data = Operate(timeId)
	filename = 'C:/Users/dell/Desktop/my_6.csv'
	wirte_to_csv(filename,Data)

if __name__ == '__main__':
	main()
