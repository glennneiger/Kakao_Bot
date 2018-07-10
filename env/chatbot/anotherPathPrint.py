import json
import urllib.request
import urllib.parse
from operator import eq

def subway(swPath):
	sText = ""
	sText += "💜"+swPath['startName']+"역에서\n"
	sText += swPath['passStopList']['stations'][1]['stationName']+"방면으로 "
	sText += swPath['lane'][0]['name']+"을 탑승합니다\n"
	sText += "💜"+str(swPath['stationCount'])+"개 정류장을 이동합니다\n"
	sText += "💜"+swPath['endName']+"역에서 하차합니다\n"
	sText += "💜"+"지하철로 이동 끝!\n"

	return sText


def bus(busPath):
	bText = ""
	bText += "💛"+busPath['startName']+"정류장에서\n"
	bText += busPath['lane'][0]['busNo']+"번 버스를 탑승합니다\n"
	bText += "💛"+str(busPath['stationCount'])+"개 정류장을 이동합니다\n"
	bText += "💛"+busPath['endName']+"정류장에서 하차합니다\n"
	bText += "💛"+"버스로 이동 끝!\n"

	return bText

def getNormalPath(sx, sy, ex, ey):

	myKey = "f/WM8od4VAXdGg4Q5ZaWSlJ8tIbSpw+nJ4WQ4AFRpsM"
	encKey = urllib.parse.quote_plus(myKey)

	odUrl = "https://api.odsay.com/v1/api/searchPubTransPath?SX="+sx+"&SY="+sy+"&EX="+ex+"&EY="+ey+"&apiKey="+encKey

	request = urllib.request.Request(odUrl)
	response = urllib.request.urlopen(request)

	json_rt = response.read().decode('utf-8')
	data = json.loads(json_rt)

	pType = data['result']['path'][0]['pathType']
	subPath = data['result']['path'][0]['subPath']

	count = len(subPath)

	if pType == 1:
		txt = "[지하철로 이동 🚋🚋]\n"
		for i in range(0, count):
			tType = subPath[i]['trafficType']
			if tType == 1:
				txt +=subway(subPath[i])
	elif pType == 2:
		txt = "[버스로 이동 🚌🚌]\n"
		for i in range(0, count):
			tType = subPath[i]['trafficType']
			if tType == 2:
				txt += bus(subPath[i])
	else:
		txt = "\n[지하철+버스로 이동하세요🚋🚌]\n\n"
		for i in range(0, count):
			tType = subPath[i]['trafficType']
			if tType == 1:
				txt+="\n[지하철로 이동 🚋🚋]\n"
				txt+=subway(subPath[i])
			elif tType == 2:
				txt+="\n[버스로 이동 🚌🚌]\n"
				txt+=bus(subPath[i])

	return txt

def resultPrint(start, end, tsType):

	geoUrl = "https://maps.googleapis.com/maps/api/geocode/json?&sensor=false&language=ko&address="
	sUrl = geoUrl+urllib.parse.quote_plus(start)
	eUrl = geoUrl+urllib.parse.quote_plus(end)

	s_request = urllib.request.Request(sUrl+'&key=AIzaSyBIzgEJhBW4nWqhRhooD2dx_kPFZuCgNSA')
	e_request = urllib.request.Request(eUrl+'&key=AIzaSyBIzgEJhBW4nWqhRhooD2dx_kPFZuCgNSA')

	s_response = urllib.request.urlopen(s_request)
	e_response = urllib.request.urlopen(e_request)

	s_json = json.loads(s_response.read().decode('utf-8'))
	e_json = json.loads(e_response.read().decode('utf-8'))

	s_status = str(s_json['status'])

	if eq(s_status,"OK") :
		#(x, 경도, longtitude) , (y, 위도, latitude)
		sx = str(s_json['results'][0]['geometry']['location']['lng'])
		sy = str(s_json['results'][0]['geometry']['location']['lat'])
		ex = str(e_json['results'][0]['geometry']['location']['lng'])
		ey = str(e_json['results'][0]['geometry']['location']['lat'])

		myKey = "f/WM8od4VAXdGg4Q5ZaWSlJ8tIbSpw+nJ4WQ4AFRpsM"
		encKey = urllib.parse.quote_plus(myKey)

		odUrl = "https://api.odsay.com/v1/api/searchPubTransPath?SX="+sx+"&SY="+sy+"&EX="+ex+"&EY="+ey+"&apiKey="+encKey

		request = urllib.request.Request(odUrl)
		response = urllib.request.urlopen(request)

		json_rt = response.read().decode('utf-8')
		data = json.loads(json_rt)
		searchType = data['result']['searchType']

		#도시간 이동
		if searchType == 1:
			#print(transportationType)
			if eq(tsType,"고속버스"):
				startSTN = str(data['result']['exBusRequest']['OBJ'][0]['startSTN'])
				startSTN_sx = str(data['result']['exBusRequest']['OBJ'][0]['SX'])
				startSTN_sy = str(data['result']['exBusRequest']['OBJ'][0]['SY'])

				endSTN = str(data['result']['exBusRequest']['OBJ'][0]['endSTN'])
				endSTN_ex = str(data['result']['exBusRequest']['OBJ'][0]['EX'])
				endSTN_ey = str(data['result']['exBusRequest']['OBJ'][0]['EY'])

				time = data['result']['exBusRequest']['OBJ'][0]['time']
				payment = data['result']['exBusRequest']['OBJ'][0]['payment']

				txt = getNormalPath(sx, sy, startSTN_sx, startSTN_sy)
				txt += "\n[고속버스로 이동🚎🚎]\n"
				txt += startSTN+"에서 "+endSTN+"까지 \n소요시간 : "+str(int(time)//60)+"시간 "+str(int(time)%60)+"분\n"
				txt += "비용 : "+str(payment)+"원\n"
				txt += getNormalPath(endSTN_ex, endSTN_ey, ex, ey)

			elif eq(tsType,"시외버스"):
				startSTN = str(data['result']['outBusRequest']['OBJ'][0]['startSTN'])
				startSTN_sx = str(data['result']['outBusRequest']['OBJ'][0]['SX'])
				startSTN_sy = str(data['result']['outBusRequest']['OBJ'][0]['SY'])

				endSTN = str(data['result']['outBusRequest']['OBJ'][0]['endSTN'])
				endSTN_ex = str(data['result']['outBusRequest']['OBJ'][0]['EX'])
				endSTN_ey = str(data['result']['outBusRequest']['OBJ'][0]['EY'])

				time = data['result']['outBusRequest']['OBJ'][0]['time']
				payment = data['result']['outBusRequest']['OBJ'][0]['payment']

				txt = getNormalPath(sx, sy, startSTN_sx, startSTN_sy)
				txt += "\n[시외버스로 이동🚎🚎]\n"
				txt += startSTN+"에서 "+endSTN+"까지 \n소요시간 : "+str(int(time)//60)+"시간 "+str(int(time)%60)+"분\n"
				txt += "비용 : "+str(payment)+"원\n\n"
				txt += getNormalPath(endSTN_ex, endSTN_ey, ex, ey)

		elif searchType == 0:
			pType = data['result']['path'][0]['pathType']
			subPath = data['result']['path'][0]['subPath']
			count = len(subPath)
			txt = getNormalPath(sx, sy, ex, ey)

		txt ="💌["+start+"에서 "+end+"까지 고속버스 경로 정보 입니다]💌\n\n"+txt
	elif eq(s_status,"ZERO_RESULTS"):
		txt = "존재하지 않는 주소입니다"
	elif eq(s_status,"OVER_QUERY_LIMIT"):
		txt = "할당량 초과"
	elif eq(s_status,"REQUEST_DENIED"):
		txt = "요청거부"
	elif eq(s_status,"INVALID_REQUEST"):
		txt = "출발지 정보 누락"
	elif eq(s_status,"UNKNOWN_ERROR"):
		txt = "서버오류"

	return txt