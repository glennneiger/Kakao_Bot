
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

                data = schedule.getStationInfo(stationName)
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
                    new_stationName = schedule.getStationName(get_stationID)
                    num = schedule.getStationResult(current_stationID,get_stationID,new_stationName, idx*2,current_laneName,direction,line_number)

                    if num == "error":
                        txt="현재 이용 불가 10초 뒤에 다시 이용해주세요"
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
                        StationNameList.append(schedule.getStationName(id))#뒤로 -5정거장까지 전체 노선 정보
                    #print(StationNameList)
                    for n in StationExistList:
                        if direction == "하행":
                            StationExistNameList.append(schedule.getStationName(current_stationID-n))
                        elif direction == "상행":
                            StationExistNameList.append(schedule.getStationName(current_stationID-n+6))
                    #print(StationExistNameList)
                    txt="==="+stationName+" 시간표 정보\n"
                    for total in StationNameList:
                        exist = False
                        for element in StationExistNameList:
                            #print("element="+element)
                            #print("total = "+total)
                            if element == total:
                                txt=txt+total+"(별)\n"
                                exist = True
                        if exist==False:
                            txt=txt+total+"\n"
            #print(getStationExistNameList)
            elif transportation == "고속버스":
                Exstart = str(data['result']['parameters']['any'][0])
                Exend = str(data['result']['parameters']['any'][1])
                schedule = schedule.getExpressInfo(Exstart,Exend)
                txt = "==="+Exstart+"터미널에서 "+Exend+"까지 시간표 정보\n"
                txt+=schedule
        elif intent_name == "Default Fallback Intent":
            txt = str(data['result']['fulfillment']['messages'][0]['speech'])
        return JsonResponse({
         'message': {'text': "!!!\n"+txt+"\n\n!!!"},
       })

    elif incom == "True":
        return JsonResponse({
            'message': {'text': "!!!\n"+incom+"\n" +start+"\n"+end+"\n"+ str(session_id) + "\n"+ res + "\n\n!!!"},
        })
