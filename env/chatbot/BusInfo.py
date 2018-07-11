import urllib.request
import urllib.parse
import json
import xml.etree.ElementTree as ET
from operator import eq

bus_station_id = {}

def get_bus_station(data):
    #오디세이에서 버스 리스트 반환
    global bus_station_id

    action = 1
    searchST = str(data['result']['parameters']['bus_station'])
    res = ""
    ACCESS = "rxJqZMHh6oQDUSfc7Kh42uCXZuHEhmj7dY7VWber2ryr9L5t2CFRy3z834JMR7RygMzaVby7ZQ3sW%2ByCZZn0Ig%3D%3D"
    my = "f/WM8od4VAXdGg4Q5ZaWSlJ8tIbSpw+nJ4WQ4AFRpsM"
    encMy = urllib.parse.quote_plus(my)
    encST = urllib.parse.quote_plus(searchST)

    odUrl = "https://api.odsay.com/v1/api/searchStation?lang=&stationName="+encST+"&CID=1000&stationClass=1&apiKey="+encMy

    request = urllib.request.Request(odUrl)
    response = urllib.request.urlopen(request)

    json_rt = response.read().decode('utf-8')
    data = json.loads(json_rt)

    bus_station_list = []
    stInfo = data['result']['station']

    for i in stInfo:
        if i['stationName']in bus_station_id:
            bus_station_id[i['stationName']].append(i['stationID'])
        else :
            bus_station_id[i['stationName']] = [i['stationID']]


        if i['stationName'] not in bus_station_list:
            bus_station_list.append(i['stationName'])
            

    if len(bus_station_list) == 1:
        action = 1
        return [bus_station_list[0],action,bus_station_list]
    else :
        action = 2
        res += "정류장을 선택해 주세요." + "\n"
        for i in range(0,len(bus_station_list)):
            res += str(i+1) +". " + bus_station_list[i] + "\n"


    for i in range(len(bus_station_list['숭실대입구역'])):
        print(i)

    return [res,action,bus_station_list]


def get_bus_direction(data):

        bus_station = str(data['result']['parameters']['bus_station'])
        bus_direction = str(data['result']['parameters']['bus_direction'])
        bus_number = str(data['result']['parameters']['bus_number'])

def get_result(data):
    bus_station = searchList[0]
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

    print("bcnt " + str(bcnt))
    text = "💌[ "+st_name+" ]💌\n"
    for i in range(0, bcnt):
        bus_msg1 = "msg1_c"+str(i)
        bus_msg2 = "msg2_c"+str(i)
        bus_adr = "adr_c"+str(i)
        bus_No = "busNo_c"+str(i)
        text += "🚌" + busList[bus_No] + "\n 👉🏿"+busList[bus_msg1]+"\n"

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

        arrival_busstation = []
        kk = ""
        for i in range(0, bcnt):
            bus_key = "busNo_c"+str(i)
            if(busList[bus_key] == bus_number):
                arrival_first = busList["msg1_c"+str(i)]
                arrival_second = busList["msg2_c"+str(i)]


        print(arrival_first)

        if eq(arrival_first,"곧 도착") != True:
            for i in range(0,len(arrival_first)):
                if eq(arrival_first[i],"["):
                    arrival_busstation.append(arrival_first[i+1])
        else :
            print("00000")
            arrival_busstation.append("0")

#        print(arrival_second)
#        if eq(arrival_second,"곧 도착") != True:
#            for i in range(0,len(arrival_second)):
#                if eq(arrival_second[i],"["):
#                    arrival_busstation.append(arrival_second[i+1])
#                    if(int(arrival_busstation[i+2]))

        print(arrival_busstation)
        counter = 0
        current = 0
        for i in res:
            if i  == bus_station :
                current = counter
                break
            else :
                counter += 1

        print("current : " + res[current])

        path_res = []
        for i in range(0,len(arrival_busstation)):
            path_res.append(res[current+int(arrival_busstation[i])])

        for i in range(0,len(path_res)):
            print("path_res " + path_res[i])

        text += "💌["+bus_number+"번 버스에 대한 정보]💌\n"
        if direction == "+":
            for i in range(5,-1,-1):
                checked = False
                for j in range(0,len(path_res)):
                    if eq(path_res[j],res[current+i]) :
                        text += "💛"+res[current+i]+" 🚌\n"
                        print(res[current+i] + "***")
                        checked = True
                        break
                if checked == False:
                    text += "💛"+res[current+i]+"\n"
                    print(res[current+i])
                if i != 0 :
                    text += "       ↓↓↓   \n"

        text += "\n"
        text+= "👉🏿 " + arrival_first + "\n"
        text+= "👉🏿 " + arrival_second

    return text
