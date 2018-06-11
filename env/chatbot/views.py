
# Create your views here.
from django.http import JsonResponse
import json
import os.path
import sys
import random
import urllib.request
import urllib.parse
import re
from . import pathPrint
from . import anotherPathPrint

from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt


try:
    import apiai
except ImportError:
    sys.path.append(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
    )
    import apiai

CLIENT_ACCESS_TOKEN = '72906773549e43b2b2fe92dcdd24abe7'
session_id = random.randint(100000,999999)
check = False

subwayID = [[1001, "수도권 1호선"],[1002, "수도권 2호선"],[1003, "수도권 3호선"],[1004, "수도권 4호선"],[1005, "수도권 5호선"]
,[1006, "수도권 6호선"],[1007, "수도권 7호선"],[1008, "수도권 8호선"],[1009, "수도권 9호선"],[1065,"수도권 공항철도"],[1071,"수도권 수인선"],[1075,"수도권 분당선"]
,[1075,"수도권 분당선"],[1063,"경의중앙선"],[1067,"수도권 경춘선"],[1077,"수도권 신분당선"],[1077,"수도권 신분당선"]]

def getStationInfo(myStationName):
    myKey = "f/WM8od4VAXdGg4Q5ZaWSlJ8tIbSpw+nJ4WQ4AFRpsM"
    encKey = urllib.parse.quote_plus(myKey)
    encStationname = urllib.parse.quote_plus(myStationName)
    odUrl = "https://api.odsay.com/v1/api/searchStation?lang=0&stationName="+encStationname+"&stationClass=2&apiKey="+encKey
    request = urllib.request.Request(odUrl)
    response = urllib.request.urlopen(request)

    json_rt = response.read().decode('utf-8')
    data = json.loads(json_rt)
    return data

def getStationName(stationID):
    myKey = "f/WM8od4VAXdGg4Q5ZaWSlJ8tIbSpw+nJ4WQ4AFRpsM"
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
    #print("==="+stationName)
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
                    #print("전역도착")
                    return idx+1
                elif "(" in list['arvlMsg2']:
                    #print("시간정보")
                    my_str = list['arvlMsg2'].split()
                    for i in my_str:
                        print("my_str = "+i)
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
                    if direction == "상행":
                        return 6-(new_stationID-cID)
                    elif direction == "하행":
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
    return schedule

def keyboard(request):

    return JsonResponse({
        'type' : 'text',
    })

@csrf_exempt
def message(request):
    message = ((request.body).decode('utf-8'))

    msg = json.loads(message)
    msg_str = msg['content']

    ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN)
    dialogflow_request = ai.text_request()

    dialogflow_request.lang = 'ko'
    dialogflow_request.session_id = session_id
    dialogflow_request.query = msg_str
    response = dialogflow_request.getresponse()

    data = json.loads(response.read().decode('utf-8'))


    #start = str(data['result']['parameters']['from'])
    #end = str(data['result']['parameters']['to'])
    intent_name = str(data['result']['metadata']['intentName'])
    incom = str(data['result']['actionIncomplete'])
    res = str(data['result']['fulfillment']['speech'])

    if incom == "False":

        txt = ""

        if(intent_name == "PathFind"):#지하철,버스
            start = str(data['result']['parameters']['from'])
            end = str(data['result']['parameters']['to'])

            if(start== '' and end==''):
                start = str(data['result']['parameters']['any'][0])
                end = str(data['result']['parameters']['any'][1])
            elif(start!='' and end==''):
                end = str(data['result']['parameters']['any'][0])
            elif(start=='' and end!=''):
                start = str(data['result']['parameters']['any'][0])

            tsType = str(data['result']['parameters']['transportation'])

            if(tsType == ''):
                txt = pathPrint.resultPrint(start, end)
                txt += "\n\n결과"
            elif(tsType != null):
                end_length = len(end)
                end = end[2:end_length-2]
                txt = anotherPathPrint.resultPrint(start, end, tsType)
                txt += "\n\n다른 결과"
        elif intent_name == "TimeSchedule":
            transportation = str(data['result']['parameters']['transportation'])
            if transportation == "지하철":
                stationName = str(data['result']['parameters']['from'])
                line_number = str(data['result']['parameters']['line_number'])
                direction = str(data['result']['parameters']['subway_direction'])
                #print("호선 명 : "+line_number)
                if stationName=='' or stationName=='[]':
                    stationName = str(data['result']['parameters']['any'])

                #print("지하철역 명"+stationName)
                #print("stationName="+stationName+" line_number="+line_number+" direction="+direction)

                data = getStationInfo(stationName)
                station_info = data['result']['station']
                #print("station Info : "+str(station_info))
                #print("사용자가 입력한 호선 명 : "+line_number)
                for idx, info in enumerate(station_info):
                    #print("호선 명"+info['laneName'])
                    if line_number in info['laneName']:
                        #print("일치, "+info['laneName'])
                        current_stationID = int(data['result']['station'][idx]['stationID'])
                        current_laneName = data['result']['station'][idx]['laneName'] #예:수도권 1호선
                #print(current_stationID)
                #print(current_laneName)
                if direction =="하행":
                    stationID = [current_stationID,current_stationID-2, current_stationID-4]
                elif direction == "상행":
                    stationID = [current_stationID+4,current_stationID+2, current_stationID]
                #subwayID = [[1063,"경의중앙선"], [1004, "수도권 4호선"]]
                #i=0
                canUse = True
                StationExistList=[]
                for idx, get_stationID in enumerate(stationID):
                    new_stationName = getStationName(get_stationID)
                    num = getStationResult(current_stationID,get_stationID,new_stationName, idx*2,current_laneName,direction,line_number)

                    if num == "error":
                        chat_message="현재 이용 불가 10초 뒤에 다시 이용해주세요"
                        canUse = False
                        break
                    elif num == "none":
                        continue
                    else:
                        #print("num = "+str(num))
                        #print("i="+str(i))
                        #예:-3정거장 전에 있으면 -1, -1정거장 전에있으면 1
                        StationExistList.append(num)
                        #i+=1
                if canUse:
                    #print(StationExistList)
                    StationExistNameList = []
                    if direction == "하행":
                        StationIDList = [current_stationID-6,current_stationID-5,current_stationID-4,current_stationID-3,current_stationID-2, current_stationID-1,current_stationID]
                    elif direction == "상행":
                        StationIDList = [current_stationID+6,current_stationID+5,current_stationID+4,current_stationID+3,current_stationID+2, current_stationID+1,current_stationID]
                    StationNameList = []
                    for id in StationIDList:
                        StationNameList.append(getStationName(id))#뒤로 -5정거장까지 전체 노선 정보
                    #print(StationNameList)
                    for n in StationExistList:
                        if direction == "하행":
                            StationExistNameList.append(getStationName(current_stationID-n))
                        elif direction == "상행":
                            StationExistNameList.append(getStationName(current_stationID-n+6))
                    #print(StationExistNameList)
                    chat_message="==="+stationName+" 시간표 정보\n"
                    for total in StationNameList:
                        exist = False
                        for element in StationExistNameList:
                            #print("element="+element)
                            #print("total = "+total)
                            if element == total:
                                chat_message=chat_message+total+"(별)\n"
                                exist = True
                        if exist==False:
                            chat_message=chat_message+total+"\n"
            #print(getStationExistNameList)
            elif transportation == "고속버스":
                Exstart = str(data['result']['parameters']['any'][0])
                Exend = str(data['result']['parameters']['any'][1])
                schedule = getExpressInfo(Exstart,Exend)
                chat_message = "==="+Exstart+"터미널에서 "+Exend+"까지 시간표 정보\n"
                chat_message+=schedule
        elif intent_name == "Default Fallback Intent":
            chat_message = str(data['result']['fulfillment']['messages'][0]['speech'])
        return JsonResponse({
         'message': {'text': "!!!\n"+txt+"\n\n!!!"},
       })

    elif incom == "True":
        return JsonResponse({
            'message': {'text': "!!!\n"+incom+"\n" +start+"\n"+end+"\n"+ str(session_id) + "\n"+ res + "\n\n!!!"},
        })
