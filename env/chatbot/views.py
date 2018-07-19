
# Create your views here.
from django.http import JsonResponse
import json
import os.path
import sys
import random
import urllib.request
import urllib.parse
import re
import time
from operator import eq

from . import pathPrint
from . import anotherPathPrint
# from . import schedule
from . import SubwayInfo
from . import BusInfo
from . import ExpressInfo


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
data = []
check = False

p_cnt = 0
diff_path_action = 0
limit_time = 0

dialogflow_action = 0

station_list = []
bus_direction_ars = []
bus_station_list_action = 0
bus_direction_action = 0
selected_bus_station = ""
selected_bus_direction = 0

sub_line_list = []
sub_line_action = 0
sub_direction_action = 0
selected_sub_line = 0


def dialogflow(msg_str):
    ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN)
    dialogflow_request = ai.text_request()

    dialogflow_request.lang = 'ko'
    dialogflow_request.session_id = session_id
    dialogflow_request.query = msg_str
    response = dialogflow_request.getresponse()

    data = json.loads(response.read().decode('utf-8'))
    return data

def keyboard(request):

    return JsonResponse({
        'type' : 'text',
    })


@csrf_exempt
def message(request):
    message = ((request.body).decode('utf-8'))

    msg = json.loads(message)
    msg_str = msg['content']

    global data

    global p_cnt
    global diff_path_action
    global limit_time

    global dialogflow_action
    global bus_station_list_action
    global station_list
    global selected_bus_station
    global selected_bus_direction
    global bus_direction_action

    global sub_line_list
    global sub_line_action
    global sub_direction_action
    global selected_sub_line


    text = ""
    incom = ""

    if diff_path_action == 1:
        cur_time = time.time()
        print("diff_path_action 은 1")
        if eq(msg_str,"Y") or eq(msg_str,"y") or eq(msg_str,"ㅇ") or eq(msg_str,"응") or eq(msg_str,"어"):
            if cur_time <= limit_time:
                p_cnt = p_cnt + 1
            else:
                p_cnt = 0
                diff_path_action = 3
                text = "시간이 지났어요!!\n다시 경로를 찾아주세요"
                incom = "False"
        else:
            p_cnt = 0
            diff_path_action = 0

    if diff_path_action == 0:
        if dialogflow_action == 0:
            print("Diaglogflow start")
            data = dialogflow(msg_str)
            if bus_direction_action == 1:
                print(bus_direction_ars)
                bus_direction = str(data['result']['parameters']['bus_direction'])
                selected_bus_direction = bus_direction_ars[int(bus_direction)-1]
                print("user direction : " + selected_bus_direction)



        ###정확한 버스 정류장 선택하기
        if bus_station_list_action == 2:
            print("user : " + msg_str)
            selected_bus_station = station_list[int(msg_str)-1]
            bus_station_list_action = 4

        if sub_line_action == 1:
            selected_sub_line = sub_line_list[int(msg_str)-1]
            sub_line_action = 4
            data = dialogflow(selected_sub_line)


    if diff_path_action != 3:
        intent_name = str(data['result']['metadata']['intentName'])
        incom = str(data['result']['actionIncomplete'])
        res = str(data['result']['fulfillment']['speech'])

    if eq(incom,"False"):
        if diff_path_action != 3:
            text = incomFalse(intent_name, data)
        else:
            diff_path_action = 0

        return JsonResponse({
         'message': {'text': text},
       })

    elif eq(incom,"True"):
        result = incomTrue(intent_name,data)

        if bus_station_list_action == 2:
            dialogflow_action = 1
            return JsonResponse({
            'message': {'text': "!!!\n"+ result + "\n\n!!!"},
            })

        if bus_direction_action == 1:
            return JsonResponse({
                'message': {'text': "!!!\n"+ str(session_id) + "\n"+ result + "\n\n!!!"},
            })

        if sub_line_action == 1:
            return JsonResponse({
                'message': {'text': "!!!\n지하철 호선 선택\n\n\n"+  result + "\n\n!!!"},
            })


def incomTrue(intent_name,data):
    global station_list
    global bus_station_list_action
    global bus_direction_action
    global dialogflow_action
    global selected_bus_station
    global bus_direction_ars

    global sub_line_action
    global sub_direction_action

    if eq(intent_name,"Bus_Info"):
        bus_station = str(data['result']['parameters']['bus_station'])
        bus_direction = str(data['result']['parameters']['bus_direction'])
        bus_number = str(data['result']['parameters']['bus_number'])

        print("come here")
        print("global bus station" + selected_bus_station)
        if bus_station_list_action == 0:
            dialogflow_action = 1
            res_bus_station = BusInfo.get_bus_station(data)
            bus_station_list_action = res_bus_station[1]
            for i in res_bus_station[2]:
                station_list.append(i)
            return res_bus_station[0]

        if bus_direction_action == 0:
            dialogflow_action = 0
            res_bus_direction = BusInfo.get_bus_direction(selected_bus_station)
            for i in res_bus_direction[0]:
                bus_direction_ars.append(i)
            bus_direction_action = 1
            return res_bus_direction[1]
    elif eq(intent_name, "Subway"):
        sb_res = str(data['result']['fulfillment']['speech'])
        if eq(sb_res[0],"호"):
            #호선 입력
            res_sub_line = SubwayInfo.get_subway_line(data['result']['parameters']['subway_station'])
            sub_line_action = res_sub_line[1]
            for i in res_sub_line[2]:
                sub_line_list.append(i)
            return res_sub_line[0]
        elif eq(sb_res[0],"어"):
            #방향 입력
            print("AAAAAAAAAA")
            print(data)
            return "BBBB"




def incomFalse(intent_name, data):
    global p_cnt
    global diff_path_action
    global limit_time

    global dialogflow_action
    global bus_direction_action
    global bus_station_list_action
    global bus_direction_ars
    global station_list
    global selected_bus_direction
    global selected_bus_station

    ##########
    if eq(intent_name,"PathFind"):
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
            text = pathPrint.get_result(start, end, '', p_cnt)
        elif eq(tsType,"지하철") or eq(tsType,"버스"):
            text = pathPrint.get_result(start, end, tsType, p_cnt)
        elif eq(tsType,"고속버스") or eq(tsType,"시외버스"):
            text = anotherPathPrint.get_result(start, end, tsType)
            print("text==>"+text)

        if not eq(text[0],"더"):
            diff_path_action = 1
            limit_time = time.time() + 10
    elif eq(intent_name,"Subway"):
        stationName = str(data['result']['parameters']['from'])
        line_number = str(data['result']['parameters']['line_number'])
        direction = str(data['result']['parameters']['subway_direction'])

        text = SubwayInfo.get_result(stationName, line_number, direction)
    elif eq(intent_name,"Bus_Info"):
        data['result']['parameters']['bus_station'] = selected_bus_station
        data['result']['parameters']['bus_direction'] = selected_bus_direction
        print(data)
        text = BusInfo.get_bus_station_information(data)

        #초기화
        diff_path_action = 0
        dialogflow_action = 0
        station_list = []
        bus_direction_ars = []
        bus_station_list_action = 0
        bus_direction_action = 0
        selected_bus_station = ""
        selected_bus_direction = 0

    elif eq(intent_name,"Express_Info"):
        Exstart = str(data['result']['parameters']['any'][0])
        Exend = str(data['result']['parameters']['any'][1])
        text = ExpressInfo.get_result(Exstart,Exend)
    # elif eq(intent_name,"Default Fallback Intent"):
    #     text = str(data['result']['fulfillment']['messages'][0]['speech'])
    else:
        text = str(data['result']['fulfillment']['speech'])

    return text
