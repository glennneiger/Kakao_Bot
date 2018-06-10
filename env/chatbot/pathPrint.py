import json
import urllib.request
import urllib.parse

def subway(swPath):
	sText = ""
	
	sText += swPath['startName']+"역에서\n"
	sText += swPath['passStopList']['stations'][1]['stationName']+"방면으로 "
	sText += swPath['lane'][0]['name']+"탑승\n"
	sText += str(swPath['stationCount'])+"개 정류장 이동\n"
	sText += swPath['endName']+"역에서 하차\n"

	return sText


def bus(busPath):
	bText = ""

	bText += busPath['startName']+"정류장에서\n"
	bText += busPath['lane'][0]['busNo']+"번 버스 탑승\n"
	bText += str(busPath['stationCount'])+"개 정류장 이동\n"
	bText += busPath['endName']+"정류장에서 하차\n"

	return bText


def resultPrint(start, end):

	geoUrl = "https://maps.googleapis.com/maps/api/geocode/json?&sensor=false&language=ko&address="

	sUrl = geoUrl+urllib.parse.quote_plus(start)
	eUrl = geoUrl+urllib.parse.quote_plus(end)

	s_request = urllib.request.Request(sUrl+'&key=AIzaSyBZNZ54ytcVVd6JZMCsEJ55pasegJRAIt8')
	e_request = urllib.request.Request(eUrl+'&key=AIzaSyBZNZ54ytcVVd6JZMCsEJ55pasegJRAIt8')

	s_response = urllib.request.urlopen(s_request)
	e_response = urllib.request.urlopen(e_request)

	s_json = json.loads(s_response.read().decode('utf-8'))
	e_json = json.loads(e_response.read().decode('utf-8'))

	s_status = str(s_json['status'])
	if s_status == "OK" :
		#(x, 경도, longtitude) , (y, 위도, latitude)
		sx = str(s_json['results'][0]['geometry']['location']['lng'])
		sy = str(s_json['results'][0]['geometry']['location']['lat'])
		ex = str(e_json['results'][0]['geometry']['location']['lng'])
		ey = str(e_json['results'][0]['geometry']['location']['lat'])

		SPT = "&SearchPathType=0"

		my = "f/WM8od4VAXdGg4Q5ZaWSlJ8tIbSpw+nJ4WQ4AFRpsM"
		encMy = urllib.parse.quote_plus(my)

		odUrl = "https://api.odsay.com/v1/api/searchPubTransPath?SX="+sx+"&SY="+sy+"&EX="+ex+"&EY="+ey+SPT+"&apiKey="+encMy

		request = urllib.request.Request(odUrl)
		response = urllib.request.urlopen(request)

		json_rt = response.read().decode('utf-8')
		data = json.loads(json_rt)

		pType = data['result']['path'][0]['pathType']
		subPath = data['result']['path'][0]['subPath']

		count = len(subPath)

		if pType == 1:
			txt = "[지하철로 이동]\n"
			for i in range(0, count):
				tType = subPath[i]['trafficType']
				if tType == 1:
					txt += subway(subPath[i])
		elif pType == 2:
			txt = "[버스로 이동]\n"
			for i in range(0, count):
				tType = subPath[i]['trafficType']
				if tType == 2:
					txt += bus(subPath[i])
		else:
			txt = "[지하철+버스로 이동]\n"
			for i in range(0, count):
				tType = subPath[i]['trafficType']
				if tType == 1 :
					txt += "\n[지하철로 이동]\n"
					txt += subway(subPath[i])
				elif tType == 2:
					txt += "\n[버스로 이동]\n"
					txt += bus(subPath[i])

	elif s_status == "ZERO_RESULTS" :
		txt = "존재하지 않는 주소입니다"
	elif s_status == "OVER_QUERY_LIMIT" :
		txt = "할당량 초과"
	elif s_status == "REQUEST_DENIED":
		txt = "요청거부"
	elif s_status == "INVALID_REQUEST":
		txt = "출발지 정보 누락"
	elif s_status =="UNKNOWN_ERROR":
		txt = "서버오류"

	return txt
