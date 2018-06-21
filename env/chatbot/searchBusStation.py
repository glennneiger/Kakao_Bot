import urllib.request
import urllib.parse
import json
import xml.etree.ElementTree as ET

def search(searchList):
	searchST = searchList[0]
	searchBus = ""
	if len(searchList) != 1:
		searchBus = searchList[1]

	text = ""

	ACCESS = "rxJqZMHh6oQDUSfc7Kh42uCXZuHEhmj7dY7VWber2ryr9L5t2CFRy3z834JMR7RygMzaVby7ZQ3sW%2ByCZZn0Ig%3D%3D"

	my = "f/WM8od4VAXdGg4Q5ZaWSlJ8tIbSpw+nJ4WQ4AFRpsM"
	encMy = urllib.parse.quote_plus(my)
	encST = urllib.parse.quote_plus(searchST)

	odUrl = "https://api.odsay.com/v1/api/searchStation?lang=&stationName="+encST+"&apiKey="+encMy

	request = urllib.request.Request(odUrl)
	response = urllib.request.urlopen(request)

	json_rt = response.read().decode('utf-8')
	data = json.loads(json_rt)

	stInfo = data['result']['station'][0]

	st_name = stInfo['stationName']
	st_ars = str(stInfo['arsID'])

	st_ars = st_ars.replace("-","")
	enArs = urllib.parse.quote_plus(st_ars)

	ACCESS = "rxJqZMHh6oQDUSfc7Kh42uCXZuHEhmj7dY7VWber2ryr9L5t2CFRy3z834JMR7RygMzaVby7ZQ3sW%2ByCZZn0Ig%3D%3D"

	oAPI = "http://ws.bus.go.kr/api/rest/stationinfo/getStationByUid?ServiceKey="+ACCESS+"&arsId="+encArs

	tree = ET.parse(urllib.request.urlopen(oAPI))

	root = tree.getroot()
	mbody = root.find("msgBody")

	busList = {}
	cnt = 0
	for bus in mbody.iter("itemList"):
		text = "######"+ bus.find("arrmsg1").text+"\n"+bus.find("arrmsg1").text+"\n"+bus.find("adirection").text+"\n"+bus.find("rtNm").text+"######"
        # msg1 = "msg1_c"+str(cnt)
        # msg2 = "msg2_c"+str(cnt)
        # adr = "adr_c"+str(cnt)
        # busNo = "busNo_c"+str(cnt)
        # busList[msg1] =  bus.find("arrmsg1").text
        # busList[msg2] =  bus.find("arrmsg1").text
        # busList[adr] =  bus.find("adirection").text
        # busList[busNo] =  bus.find("rtNm").text
		cnt = cnt+1




	return text
