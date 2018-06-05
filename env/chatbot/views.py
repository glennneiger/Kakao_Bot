
# Create your views here.
from django.http import JsonResponse
import json
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt



def keyboard(request):

    return JsonResponse({
        'type' : 'text',
    })

@csrf_exempt
def message(request):
    message = ((request.body).decode('utf-8'))

    msg = json.loads(message)
    msg_str = msg['content']

    return JsonResponse({
        'message': {'text': "!!!\n\n" + "fkfkfkfkkfkf" + "\n\n!!!"},
        'keyboard': {'type': 'text'}
    })






