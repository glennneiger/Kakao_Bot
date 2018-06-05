
# Create your views here.
from django.http import JsonResponse

from django.shortcuts import render
from django.http import HttpResponse



def keyboard(request):

    return JsonResponse({
        'type' : 'text',
    })


