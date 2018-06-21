import urllib.request
import urllib.parse
import json
import xml.etree.ElementTree as ET

def search(searchList):
    print(searchList)
    searchST = searchList[0]
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
    encArs = urllib.parse.quote_plus(st_ars)

    ACCESS = "rxJqZMHh6oQDUSfc7Kh42uCXZuHEhmj7dY7VWber2ryr9L5t2CFRy3z834JMR7RygMzaVby7ZQ3sW%2ByCZZn0Ig%3D%3D"

    oAPI = "http://ws.bus.go.kr/api/rest/stationinfo/getStationByUid?ServiceKey="+ACCESS+"&arsId="+encArs

    tree = ET.parse(urllib.request.urlopen(oAPI))

    root = tree.getroot()
    mbody = root.find("msgBody")

    busList = {}
    bcnt = 0
    for bus in mbody.iter("itemList"):
        msg1 = "msg1_c"+str(bcnt)
        msg2 = "msg2_c"+str(bcnt)
        adr = "adr_c"+str(bcnt)
        busNo = "busNo_c"+str(bcnt)
        busList[msg1] =  bus.find("arrmsg1").text
        busList[msg2] =  bus.find("arrmsg2").text
        busList[adr] =  bus.find("adirection").text
        busList[busNo] =  bus.find("rtNm").text
        bcnt = bcnt+1

    

    ###버스 정보
    if len(searchList) != 1:
        text = ""
        bus_number = searchList[1]
        bus_station = st_name
        Bus_Info_URL = "https://api.odsay.com/v1/api/searchBusLane?lang=0&busNo="+bus_number+"&apiKey="+encMy+"&CID=1000"

        bus_info_request = urllib.request.Request(Bus_Info_URL)
        bus_info_res = urllib.request.urlopen(bus_info_request)

        json_data = json.loads(bus_info_res.read().decode('utf-8'))

        busID = json_data['result']['lane'][0]['busID']
        direction = "+"
        Line_URL = "https://api.odsay.com/v1/api/busLaneDetail?lang=0&busID="+str(busID)+"&apiKey="+encMy

        request = urllib.request.Request(Line_URL)
        response = urllib.request.urlopen(request)

        json_rt = response.read().decode('utf-8')
        data = json.loads(json_rt)

        startStation = data['result']['busStartPoint']
        endStation = data['result']['busEndPoint']

        station_idx_res = {}
        idx_station_res = {}
        res = []

        for i in data['result']['station']:
            idx_station_res[i['idx']] = i['stationName']
            res.append(i['stationName'])

        arr = []
        kk = ""
        for i in range(0, bcnt):
            bus_key = "busNo_c"+str(i)
            if(busList[bus_key] == bus_number):
                print(busList[bus_key])
                kk = "msg1_c"+str(i)

        counter = 0
        current = 0
        for i in res:
            if i  == bus_station :
                current = counter
                break
            else :
                counter += 1

        print("currnet : " + res[current])

        if direction == "+":
            for i in range(5,0,-1):
                print(res[current+i])


    return text
