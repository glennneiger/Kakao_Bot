import json
import os.path
import sys
import random
import urllib.request
import urllib.parse
import re
from . import pathPrint
from . import anotherPathPrint
from . import schedule

CLIENT_ACCESS_TOKEN = '72906773549e43b2b2fe92dcdd24abe7'
session_id = random.randint(100000,999999)
check = False

subwayID = [[1001, "수도권 1호선"],[1002, "수도권 2호선"],[1003, "수도권 3호선"],[1004, "수도권 4호선"],[1005, "수도권 5호선"]
,[1006, "수도권 6호선"],[1007, "수도권 7호선"],[1008, "수도권 8호선"],[1009, "수도권 9호선"],[1065,"수도권 공항철도"],[1071,"수도권 수인선"],[1075,"수도권 분당선"]
,[1075,"수도권 분당선"],[1063,"경의중앙선"],[1067,"수도권 경춘선"],[1077,"수도권 신분당선"],[1077,"수도권 신분당선"]]

def getStationInfo(myStationName):
    myKey = "sfUWUSpyZPCTdcli/St2gPbb1Se3TCP2dL6LZQzhsEE"
    encKey = urllib.parse.quote_plus(myKey)
    encStationname = urllib.parse.quote_plus(myStationName)
    odUrl = "https://api.odsay.com/v1/api/searchStation?lang=0&stationName="+encStationname+"&stationClass=2&apiKey="+encKey
    request = urllib.request.Request(odUrl)
    response = urllib.request.urlopen(request)

    json_rt = response.read().decode('utf-8')
    data = json.loads(json_rt)
    return data

def getStationName(stationID):
    myKey = "sfUWUSpyZPCTdcli/St2gPbb1Se3TCP2dL6LZQzhsEE"
    encKey = urllib.parse.quote_plus(myKey)
    encStationID = urllib.parse.quote_plus(str(stationID))
    odUrl = "https://api.odsay.com/v1/api/subwayStationInfo?lang=0&stationID="+encStationID+"&apiKey="+encKey
    request = urllib.request.Request(odUrl)
    response = urllib.request.urlopen(request)

    od_json = response.read().decode('utf-8')
    od_data = json.loads(od_json)
    #print(od_data)
    stationName = od_data['result']['stationName']
    return stationName

def getStationResult(cID, stationID, stationName, idx, current_laneName,direction,line_number): #예:서울역 수도권 4호선 426
    for (first, last) in subwayID:
        #print("first = "+str(first))
        #print("last = "+last)
        if current_laneName == last:
            open_data_subwayID = first #예:수도권 4호선인 경우 open_data_subwayID = 1004
    #print("subwayID = "+str(open_data_subwayID))
    open_data_key = "714d78526b7369683130356e4d455357"
    enckey = urllib.parse.quote_plus(open_data_key)
    #'역'글자 빼기
    #stationName = stationName.replace("(역)$","")
    stationName = re.sub("[역]$","", stationName)
    print("==="+stationName)
    encStationname = urllib.parse.quote_plus(stationName)
    open_data_url = "http://swopenapi.seoul.go.kr/api/subway/"+enckey+"/json/realtimeStationArrival/0/5/"+encStationname
    try:
        request = urllib.request.Request(open_data_url)
        response = urllib.request.urlopen(request)

        real_json = response.read().decode('utf-8')
        real_data = json.loads(real_json)
        #print(real_data)
        realtimeList = real_data['realtimeArrivalList']
        #realtimeList_length = realtimeList.length

        #print(realtimeList[0])
        for list in realtimeList:
            if list['subwayId'] == str(open_data_subwayID) and list['updnLine']==direction:
                #print("list['updnLine']="+list['updnLine'])
                #print("direction="+direction)
                #print("메시지 : "+list['arvlMsg2'])
                #if list['arvlMsg2'].find("도착"):
                    #print(stationName+"역 정보 : "+list['arvlMsg2'])
                if list['arvlMsg2'] == "전역 도착" or list['arvlMsg2'] == "전역 출발":
                    #print("$$$$$$$$$$$$$$$전역도착")
                    return idx+1
                elif "[" in list['arvlMsg2']:#[5]번째 전역 (화전)
                    #print("$$$$$$$$$몇정거장 전")
                    info_str = list['arvlMsg2'].split()
                    #for i in info_str:
                        #print("info_str = "+i)
                    info_str2 = info_str[2]
                    info_str2 = info_str2[1:len(info_str2)-1]
                    #print("**info_str = "+info_str2)
                    new_data = getStationInfo(info_str2)
                    new_station_info = new_data['result']['station']
                    for idx, info in enumerate(new_station_info):
                        if line_number in info['laneName']:
                            new_stationID = int(new_data['result']['station'][idx]['stationID'])
                    #print("new_stationID = " +str(new_stationID))
                    if direction == "상행" or "외선":
                        return 6-(new_stationID-cID)
                    elif direction == "하행" or "내선":
                        return cID-new_stationID
                elif "(" in list['arvlMsg2']:#3분 58초 후 (삼각지)
                    #print("$$$$$$$$$$시간정보")
                    my_str = list['arvlMsg2'].split()
                    #for i in my_str:
                    #    print("my_str = "+i)
                    my_str2 = my_str[3]
                    my_str2 = my_str2[1:len(my_str2)-1]
                    #my_str = my_str[3].replace(' ','')
                    #print("**my_str = "+my_str2)
                    new_data = getStationInfo(my_str2)
                    new_station_info = new_data['result']['station']
                    for idx, info in enumerate(new_station_info):
                        if line_number in info['laneName']:
                            new_stationID = int(new_data['result']['station'][idx]['stationID'])
                    #print("new_stationID = " +str(new_stationID))
                    if direction == "상행" or "외선":
                        return 6-(new_stationID-cID)
                    elif direction == "하행" or "내선":
                        return cID-new_stationID
                else:
                    #print("해당역 도착")
                    return idx
                #elif list['arvlMsg2'].find("\d+(분)\s\d+(초)\s(후)"):
                    #print("***"+stationName+"역 정보 : "+list['arvlMsg2'])
                    #print("현재 이용 불가 10초 뒤에 다시 이용해주세요")
                    #return "error"
        return "none"
    except urllib.error.HTTPError:
        return "error"

def getExpressInfo(my_Exstart, my_Exend):
    myKey = "sfUWUSpyZPCTdcli/St2gPbb1Se3TCP2dL6LZQzhsEE"
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
    return schedule
