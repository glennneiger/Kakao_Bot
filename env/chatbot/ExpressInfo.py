def get_result(my_Exstart, my_Exend):
    myKey = "f/WM8od4VAXdGg4Q5ZaWSlJ8tIbSpw+nJ4WQ4AFRpsM"
    encKey = urllib.parse.quote_plus(myKey)
    encExstart = urllib.parse.quote_plus(my_Exstart)
    encExend = urllib.parse.quote_plus(my_Exend)
    odSUrl = "https://api.odsay.com/v1/api/expressBusTerminals?&terminalName="+encExstart+"&apiKey="+encKey
    odEUrl = "https://api.odsay.com/v1/api/expressBusTerminals?&terminalName="+encExend+"&apiKey="+encKey

    s_request = urllib.request.Request(odSUrl)
    s_response = urllib.request.urlopen(s_request)
    json_rt_s = s_response.read().decode('utf-8')
    data_s = json.loads(json_rt_s)
    sID = str(data_s['result'][0]['stationID'])

    e_request = urllib.request.Request(odEUrl)
    e_response = urllib.request.urlopen(e_request)
    json_rt_e = e_response.read().decode('utf-8')
    data_e = json.loads(json_rt_e)
    eID = str(data_e['result'][0]['stationID'])

    tUrl = "https://api.odsay.com/v1/api/expressServiceTime?&startStationID="+sID+"&endStationID="+eID+"&apiKey="+myKey

    request = urllib.request.Request(tUrl)
    response = urllib.request.urlopen(request)
    json_rt = response.read().decode('utf-8')
    data = json.loads(json_rt)

    schedule = data['result']['station'][0]['schedule']

    text = "💌["+Exstart+"터미널에서 "+Exend+"까지 시간표 정보입니다💌\n"
    text += schedule

    return text
