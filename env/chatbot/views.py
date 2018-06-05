
# Create your views here.
from django.http import JsonResponse
import json
import os.path
import sys
import random
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
    dialogflow_request.query = msg_str
    response = dialogflow_request.getresponse()

    data = json.loads(response.read().decode('utf-8'))


    start = str(data['result']['parameters']['from'])
    end = str(data['result']['parameters']['to'])
    intent_name = str(data['result']['metadata']['intentName'])
    incom = str(data['result']['actionIncomplete'])
    res = str(data['result']['fulfillment']['speech'])

    if incom == "True":
        return JsonResponse({
            'message': {'text': "!!!\n\n" + "잘못된접근" + "\n\n!!!"},
            'keyboard': {'type': 'text'}
        })


    return JsonResponse({
        'message': {'text': "!!!\n\n" + res + "\n\n!!!"},
        'keyboard': {'type': 'text'}
    })






