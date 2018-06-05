import os.path
import sys
import dialogflow
import urllib.request
import json
import re
import random
from django.shortcuts import render
from django.http import JsonResponse

try:
    import apiai
except ImportError:
    sys.path.append(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
    )
    import apiai

def keyboard(request):
    return JsonResponse({
        'type':'text'
    })

CLIENT_ACCESS_TOKEN = '72906773549e43b2b2fe92dcdd24abe7'

def dialogflow():

    ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN)
    request = ai.text_request()

    request.lang = 'ko'
    session_id = random.randint(100000,999999)
    request.session_id = session_id


    request.query = input()
    response = request.getresponse()

    data = json.loads(response.read().decode('utf-8'))


    start = str(data['result']['parameters']['from'])
    end = str(data['result']['parameters']['to'])
    intent_name = str(data['result']['metadata']['intentName'])
    incom = str(data['result']['actionIncomplete'])
    res = str(data['result']['fulfillment']['speech'])

    print(res)

    while incom == "True":
        request = ai.text_request()
        request.lang = 'ko'
        request.session_id = session_id
        request.query = input()
        response = request.getresponse()

        data = json.loads(response.read().decode('utf-8'))
        res = str(data['result']['fulfillment']['speech'])
        incom = str(data['result']['actionIncomplete'])
        print(res)



if __name__ == "__main__":

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mytest.settings")
    print("serverworks!")
    dialogflow()




