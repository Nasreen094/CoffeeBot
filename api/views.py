from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.gis.geoip import GeoIP
from rest_framework import status
from django.contrib.sessions.models import Session
from django.conf import settings
from django.db import models

from rest_framework import viewsets
from config import *
from api.externel_api import call_api
import requests
from rest_framework.decorators import permission_classes
from rest_framework import permissions
import apiai
import yaml
import datetime
#from django.contrib.auth.signals import user_logged_in

currentTime = datetime.datetime.utcnow()
print currentTime




    
def page_reload_operation(question):
    question['messageSource'] = 'messageFromBot'
    
    if currentTime.hour < 12:
        wish='Good morning! '
    elif 12 <= currentTime.hour < 18:
        wish='Good afternoon! '
    else:
        wish='Good evening! '
    #print type(wish)
    question['messageText'] = [ wish+ 'Welcome to Bewley\'s! ']
    #question["plugin"] = {'name': 'textbox', 'type': 'text', 'data': 'Type your name'}
    question["plugin"] = {'name': 'autofill', 'type': 'items', 'data': show}
    
    return question
def message_something_else(question):
    question['messageSource'] = 'messageFromBot'
    question['messageText'] = reply_something_else 
    return question

def clear_context(user_id):
    ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN)
    request = ai.text_request()
    request.lang = 'de'
    request.resetContexts = True
    request.session_id = user_id
    request.query = 'hi'
    response = yaml.load(request.getresponse())
    print (response)
    
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

# Create your views here.
@permission_classes((permissions.AllowAny,))
class TestAPI(viewsets.ViewSet):
    def create(self, request):
        question = request.data
        print question
        '''
        ip=get_client_ip(request)
        print ip
        g = GeoIP()
        print g
        '''
        #print g.city(ip)
        CACHE_ID = 'Constant'
        if 'user_id' in question:
            CACHE_ID = question['user_id']
#
        user_input = question['messageText']
        if question['messageSource'] == 'userInitiatedReset':
            clear_context(CACHE_ID)
            question = page_reload_operation(question)
            return Response(question)
        
        if 'something else' in question['messageText'].lower():
            question = message_something_else(question)
            return Response(question)
       
        
        question = call_api(question)
        print (question)

        return Response(question)
