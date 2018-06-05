import os.path
import sys
import random
import json

try:
    import apiai
except ImportError:
    sys.path.append(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
    )
    import apiai

CLIENT_ACCESS_TOKEN = '72906773549e43b2b2fe92dcdd24abe7'

def dialogflow(text):

    ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN)
    dialogflow_request = ai.text_request()

    dialogflow_request.lang = 'ko'
    session_id = random.randint(100000,999999)
    dialogflow_request.session_id = session_id

    dialogflow_request.query = text
    response = dialogflow_request.getresponse()

    data = json.loads(response.read().decode('utf-8'))


    start = str(data['result']['parameters']['from'])
    end = str(data['result']['parameters']['to'])
    intent_name = str(data['result']['metadata']['intentName'])
    incom = str(data['result']['actionIncomplete'])
    res = str(data['result']['fulfillment']['speech'])

    print(res)

    while incom == "True":
        dialogflow_request = ai.text_request()
        dialogflow_request.lang = 'ko'
        dialogflow_request.session_id = session_id
        dialogflow_request.query = input()
        response = dialogflow_request.getresponse()

        data = json.loads(response.read().decode('utf-8'))
        res = str(data['result']['fulfillment']['speech'])
        incom = str(data['result']['actionIncomplete'])
        print(res)

    return data