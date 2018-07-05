
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
from . import schedule
from . import searchBusStation
from operator import eq

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

    intent_name = str(data['result']['metadata']['intentName'])
    incom = str(data['result']['actionIncomplete'])
    res = str(data['result']['fulfillment']['speech'])

    if incom == "False":
        text = incomFalse(intent_name, data)

        return JsonResponse({
         'message': {'text': text},
       })

    elif incom == "True":
        incomTrue(intent_name,data)
        return JsonResponse({
            'message': {'text': "!!!\n"+ str(session_id) + "\n"+ res + "\n\n!!!"},
        })

def incomTrue(intent_name,data):
    if eq(intent_name,"Bus_Info"):
        bus_station = str(data['result']['parameters']['bus_station'])
        bus_direction = str(data['result']['parameters']['bus_direction'])
        bus_number = str(data['result']['parameters']['bus_number'])

        if eq(bus_direction,""):
            print("방향비어있음 " + "\n")

        print(bus_station + " " + bus_direction + " " + bus_number + "\n")



def incomFalse(intent_name, data):

    if(intent_name == "PathFind"):
        start = str(data['result']['parameters']['from'])
        end = str(data['result']['parameters']['to'])

        if eq(start,'') and eq(end,''):
            start = str(data['result']['parameters']['fromAny'])
            end = str(data['result']['parameters']['toAny'])
        elif not eq(start,'') and eq(end,''):
            end = str(data['result']['parameters']['toAny'])
        elif eq(start,'') and not eq(end,''):
            start = str(data['result']['parameters']['fromAny'])

        tsType = str(data['result']['parameters']['transportation'])
        print("start==>"+start)
        print("end==>"+end)
        print("tsType==>"+tsType)

        if eq(tsType,''):
            text = pathPrint.resultPrint(start, end, '')
        elif eq(tsType,"지하철") or eq(tsType,"버스"):
            text = pathPrint.resultPrint(start, end, tsType)
        elif eq(tsType,"고속버스") or eq(tsType,"시외버스"):
            text = anotherPathPrint.resultPrint(start, end, tsType)
            print("text==>"+text)
            text += "\n\n다른 결과"
    elif intent_name == "TimeSchedule":
        transportation = str(data['result']['parameters']['transportation'])
        if transportation == "지하철":
            #비슷한 역이름 처리
            SNList = [["반포역", "신반포역", "구반포역"], ["논현역", "신논현역"]]
            ###비슷한 역이름 처리하기 위해 임시로!!!
            #SNList = [["테스트","테스트1","테스트2","테스트3"], ["반포역", "신반포역", "구반포역"]]
            #stationName = str(data['result']['parameters']['from'])
            line_number = str(data['result']['parameters']['line_number'])
            direction = str(data['result']['parameters']['subway_direction'])

            #if stationName=='' or stationName=='[]':
                #stationName = str(data['result']['parameters']['any'])
            stationName = "반포역"
            #print("지하철역 명"+stationName)
            print("stationName="+stationName+" line_number="+line_number+" direction="+direction)
            #print("stationName : "+stationName)
            print("SNList : "+str(SNList))
            for e in SNList:
                print("e = "+str(e))
                print("stationName="+stationName+" line_number="+line_number+" direction="+direction)
                if stationName in e:
                    print("리스트에 있음")
                    print("리스트 길이 : "+str(len(SNList)))
                    for i in range(0, len(SNList)):
                        print(str(i)+"번째 리스트 내용 :"+str(SNList[i]))
                        if stationName in SNList[i]:
                            option = SNList[i]
                            print("option = "+str(option))
            print("선택사항 : "+str(option))

            data = schedule.getStationInfo(stationName)
            station_info = data['result']['station']
            current_stationID = 0
            for idx, info in enumerate(station_info):
                if line_number in info['laneName']:
                    current_stationID = int(data['result']['station'][idx]['stationID'])
                    current_laneName = data['result']['station'][idx]['laneName'] #예:수도권 1호선
            if eq(direction,"상행") or eq(direction,"내선"):
                stationID = [current_stationID+4,current_stationID+2, current_stationID]
            if eq(direction,"하행") or eq(direction,"외선"):
                stationID = [current_stationID,current_stationID-2, current_stationID-4]
            text=""
            canUse = True
            StationExistList=[]
            for idx, get_stationID in enumerate(stationID):
                #print("@@@==>"+str(get_stationID))
                new_stationName = schedule.getStationName(get_stationID)
                if new_stationName == "none":
                    continue
                num = schedule.getStationResult(current_stationID,get_stationID,new_stationName, idx*2,current_laneName,direction,line_number)

                if num == "error":
                    text="현재 이용 불가 10초 뒤에 다시 이용해주세요"
                    canUse = False
                    break
                elif num == "none":
                    continue
                else:
                    StationExistList.append(num)
            if canUse:
                StationExistNameList = []
                if eq(direction,"상행") or eq(direction,"내선"):
                    StationIDList = [current_stationID+6,current_stationID+5,current_stationID+4,current_stationID+3,current_stationID+2, current_stationID+1,current_stationID]
                if eq(direction,"하행") or eq(direction,"외선"):
                    StationIDList = [current_stationID-6,current_stationID-5,current_stationID-4,current_stationID-3,current_stationID-2, current_stationID-1,current_stationID]
                StationNameList = []
                for id in StationIDList:
                    StationNameList.append(schedule.getStationName(id))#뒤로 -5정거장까지 전체 노선 정보
                for n in StationExistList:
                    if eq(direction,"상행") or eq(direction,"내선"):
                        StationExistNameList.append(schedule.getStationName(current_stationID-n+6))
                    if eq(direction,"하행") or eq(direction,"외선"):
                        StationExistNameList.append(schedule.getStationName(current_stationID-n))

                count_end = 0#종점인지 체크하는 변수
                text +="💌["+stationName+" "+line_number+"정보입니다]💌\n"
                for total in StationNameList:
                    exist = False
                    #text+=str(StationExistNameList)
                    for element in StationExistNameList:
                        #print("element="+element)
                        #print("total = "+total)
                        if eq(element,total):
                            if eq(total,StationNameList[6]):
                                text+=total+"🚋\n"
                            else:
                                text+=total+"🚋\n   ↓↓↓   \n"
                            exist = True
                    if exist==False:
                        if eq(total,"none"):
                            count_end = count_end+1
                            continue
                        #print(total)
                        if eq(total,StationNameList[6]):
                            text +=total+"\n"
                        else:
                            text+=total+"\n   ↓↓↓   \n"
                if count_end ==6:
                    #print("종점입니다")
                    text +="종점인데 어딜가시려구요?👀\n"
        elif transportation == "고속버스":
            Exstart = str(data['result']['parameters']['any'][0])
            Exend = str(data['result']['parameters']['any'][1])
            schedule1 = schedule.getExpressInfo(Exstart,Exend)
            text = "💌["+Exstart+"터미널에서 "+Exend+"까지 시간표 정보입니다💌\n"
            text+=schedule1
    elif intent_name == "Bus_Info":
        print("AAAAAAAAA")
        searchList = data['result']['parameters']['bus_info']
        print(type(searchList))

        text = searchBusStation.search(searchList)
    elif intent_name == "Default Fallback Intent":
        text = str(data['result']['fulfillment']['messages'][0]['speech'])

    return text
