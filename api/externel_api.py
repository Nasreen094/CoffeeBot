import os.path
import sys
import yaml
import pprint
from config import *
import pymysql
import pandas as pd
from django.contrib.admin.templatetags.admin_list import results
import requests
import json
#from __main__ import name
#from nltk.sem.chat80 import items



try:
    import apiai
except ImportError:
    sys.path.append(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
    )
    import apiai



global CART
CART={}
global data
data=[]
global NAME
NAME=None
global DOB
DOB=None



def call_api(dict_input):
    global out_dict
    out_dict = {}
    out_dict['messageText'] = []
    out_dict['messageSource'] = 'messageFromBot'
    ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN)
    request = ai.text_request()
    request.lang = 'de'
    request.resetContexts = False
    request.session_id = dict_input['user_id']
    request.query = dict_input['messageText']
    print(request.query)
    global item       
    response = yaml.load(request.getresponse())
    pp = pprint.PrettyPrinter(indent=4)
    json_data = response['result']['parameters']
    pp.pprint(response)
    if response['result']['metadata']=={}:
        out_dict['messageText'].append(response['result']['fulfillment']['messages'][0]['speech'])
        return out_dict
    elif response['result']['metadata']['intentName'] == 'Default Fallback Intent':
        out_dict['messageText'].append(response['result']['fulfillment']['messages'][0]['speech'])
        return out_dict
    elif response['result']['metadata']['intentName'] == 'offer':
        out_dict['messageText'].append('Here are the hot offers we provide')
        out_dict["plugin"] = {'name': 'empyee_signin', 'type': 'link to signin', 'data': {'text': "Offers", 'link': "http://bewley.sysgsoft.com/#portfolios"}}
        return out_dict
    elif response['result']['metadata']['intentName'] == 'products':
        out_dict['messageText'].append('Please tap below to see our featured products')
        out_dict["plugin"] = {'name': 'empyee_signin', 'type': 'link to signin', 'data': {'text': "Products", 'link': "http://bewley.sysgsoft.com/#services"}}
        return out_dict
    elif response['result']['metadata']['intentName'] == 'menu':
        out_dict['messageText'].append(' Just click here to see our core menu')
        #out_dict["plugin"] = {'name': 'card', 'type': 'text', 'data': menu_items}
        out_dict["plugin"] = {'name': 'empyee_signin', 'type': 'link to signin', 'data': {'text': "Menu", 'link': "https://www.bewleys.com/ie/wp-content/uploads/sites/2/2018/04/Bewleys-Grafton-Street-Core-Menu.pdf"}}
        return out_dict
    elif response['result']['metadata']['intentName'] == 'outlets':
        out_dict['messageText'].append(response['result']['fulfillment']['messages'][0]['speech'])
        #out_dict["plugin"] = {'name': 'card', 'type': 'text', 'data': 'outlets'}
        out_dict["plugin"] = {'name': 'outlet', 'type': 'job lists', 'data': outlets}
        return out_dict
    elif response['result']['metadata']['intentName'] == 'order coffee':
        print json_data
        if json_data['Espresso']==[]:
            if json_data['Filter']==[]:
                out_dict['messageText']=['what kind?']
                #out_dict["plugin"] = {'name': 'suggestion', 'type': 'text', 'data': list}
                out_dict["plugin"] = {'name': 'autofill', 'type': 'items', 'data': list}
                return out_dict
            elif json_data['Filter']==["Filter"]:
                out_dict['messageText']=['Good! Here are the varieties of Filter we offer. Take a look below']
                out_dict["plugin"] = {'name': 'autofill', 'type': 'items', 'data': Fil_items}
                return out_dict
            else:
                global CART
                global item
                global number
                item=json_data['Filter'][0]
                CART['item']=item
                print CART
                number=json_data['number']
                out_dict['messageText']=['Do you wanna add it to your cart?']
                out_dict["plugin"] = {'name': 'autofill', 'type': 'items', 'data': ['yes','no']}
                return out_dict
        elif json_data['Espresso']==['Espresso']:
                out_dict['messageText']=['Excellent choice! Here are the varieties of Espresso we offer. Take a look below']
                out_dict["plugin"] = {'name': 'autofill', 'type': 'items', 'data': Esp_items}
                return out_dict
        else:
            global CART
            global item
            global number
            item=json_data['Espresso'][0]
            CART['item']=item
            print CART
            number=json_data['number']
            print str(number)
            out_dict['messageText']=['Do you wanna add it to your cart?']
            out_dict["plugin"] = {'name': 'autofill', 'type': 'items', 'data': ['yes','no']}
            return out_dict
    
    elif response['result']['metadata']['intentName'] == 'order coffee - yes':
        if number==[]:
                    out_dict['messageText']=['How many cups of '+item+' do you need?']
                    return out_dict
        else:
                    global CART
                    CART['quantity']=number
                    print CART
                    out_dict['messageText']=['Great! '+str(number[0])+' cups of '+item+' has been added to your cart']
                    return out_dict
    elif response['result']['metadata']['intentName'] == 'order coffee - no':
        global DOB
        global NAME
        if (DOB==None)&(NAME!=None):
            out_dict['messageText']=['Alright! Would you love to get a free cake at your birthday '+NAME+'?']
        else:
            out_dict['messageText'].append(response['result']['fulfillment']['messages'][0]['speech'])
        return out_dict
    elif response['result']['metadata']['intentName'] == 'order coffee - no - yes':
        out_dict['messageText'].append(response['result']['fulfillment']['messages'][0]['speech'])
        return out_dict
    elif response['result']['metadata']['intentName'] == 'order coffee - no - no':
        if NAME==None:
            out_dict['messageText']=['Ok.']
        else:
            out_dict['messageText']=['Alright '+NAME+' ! What else do you want?']
        return out_dict
    elif response['result']['metadata']['intentName'] == 'order coffee - no - yes - dob':
        global DOB
        global NAME
        DOB=json_data['date']
        out_dict['messageText']=['Your birthday date is saved '+NAME+'!','BE READY. When your birthday come, we\'ll invite u to celebrate it around your FREE delicious cake in Bewley\'s!' ]
        return out_dict
    elif response['result']['metadata']['intentName'] == 'order coffee - yes - select.number':  
            global CART
            num=str(json_data['number'][0])
            CART['quantity']=num
            print CART
            print data
            out_dict['messageText']=['Great! '+num+' cups of '+item+' has been added to your cart','Would you like to continue shoping?']
            out_dict["plugin"] = {'name': 'autofill', 'type': 'items', 'data': ['yes, continue','Show cart'],'link':'yes','value':'https://www.bewleys.com/ie/checkout/'}
            return out_dict  
    elif response['result']['metadata']['intentName'] == 'order coffee - yes - select.number - yes':
            out_dict['messageText']=['Great, What else would you like to have?']
            out_dict["plugin"] = {'name': 'autofill', 'type': 'items', 'data': menu_items}
            return out_dict
    elif response['result']['metadata']['intentName'] == 'show cart':
        global data
        global CART
        out_dict['messageText']=['Here is your current cart.']
        CART['Link']='https://www.bewleys.com/ie/checkout/'
        print CART
        data.append(CART)
        CART={}
        print data
        out_dict["plugin"] = {'name': 'link', 'type': 'job lists', 'data': data, 'buttons':['Shop more']}
        return out_dict
    elif response['result']['metadata']['intentName'] == 'order tea':
        if json_data['Black']==[]:
            if json_data['HerbalTisanes']==[]:
                if json_data['Green']==[]:
                    out_dict['messageText']=['what kind?']
                #out_dict["plugin"] = {'name': 'suggestion', 'type': 'text', 'data': listeat}
                    out_dict["plugin"] = {'name': 'autofill', 'type': 'items', 'data': list_tea}
                    return out_dict
                elif json_data['Green']==['Green']:
                    out_dict['messageText']=['Good! Green leaves are naturally high in antioxidants.',' Here are the varieties we offer. Take a look below']
                    out_dict["plugin"] = {'name': 'autofill', 'type': 'items', 'data': green_items}
                    return out_dict
                else:
                    global CART
                    global item
                    global number
                    item=json_data['Green'][0]
                    CART['item']=item
                    print CART
                    number=json_data['number']
                    out_dict['messageText']=['Do you wanna add it to your cart?']
                    out_dict["plugin"] = {'name': 'autofill', 'type': 'items', 'data': ['yes','no']}
                    return out_dict
            elif json_data['HerbalTisanes']==['Herbal Tisanes']:
                    out_dict['messageText']=['Great! Have a calming & caffeine free tisane from Bewley\'s.','Which is your favourite?']
                    out_dict["plugin"] = {'name': 'autofill', 'type': 'items', 'data': herbal_items}
                    return out_dict
            else:
                    global CART
                    global item
                    global number
                    item=json_data['HerbalTisanes'][0]
                    CART['item']=item
                    print CART
                    number=json_data['number']
                    out_dict['messageText']=['Do you wanna add it to your cart?']
                    out_dict["plugin"] = {'name': 'autofill', 'type': 'items', 'data': ['yes','no']}
                    return out_dict
        elif json_data['Black']==['Black']:
                    out_dict['messageText']=['Great! Have a wonderful tea experience with your favourite black tea from Bewley\'s']
                    out_dict["plugin"] = {'name': 'autofill', 'type': 'items', 'data': black_items}
                    return out_dict 
        else:
            global CART
            global item
            global number
            item=json_data['Black'][0]
            CART['item']=item
            print CART
            number=json_data['number']
            print str(number)
            out_dict['messageText']=['Do you wanna add it to your cart?']
            out_dict["plugin"] = {'name': 'autofill', 'type': 'items', 'data': ['yes','no']}
            return out_dict     
    elif response['result']['metadata']['intentName'] == 'order tea - yes':
        if number==[]:
                    out_dict['messageText']=['How many cups of '+item+' do you need?']
                    return out_dict
        else:
                    global CART
                    CART['quantity']=number
                    print CART
                    out_dict['messageText']=['Great! '+str(number[0])+' cups of '+item+' has been added to your cart']
                    return out_dict
    elif response['result']['metadata']['intentName'] == 'order tea - no':
        global DOB
        global NAME
        if (DOB==None)&(NAME!=None):
            out_dict['messageText']=['Alright! Would you love to get a free cake at your birthday '+NAME+'?']
        else:
            out_dict['messageText'].append(response['result']['fulfillment']['messages'][0]['speech'])
        return out_dict
    elif response['result']['metadata']['intentName'] == 'order tea - no - no':
        if NAME==None:
            out_dict['messageText']=['Ok.']
        else:
            out_dict['messageText']=['Alright '+NAME+' ! What else do you want?']
        return out_dict
    elif response['result']['metadata']['intentName'] == 'order tea - no - yes':
        out_dict['messageText'].append(response['result']['fulfillment']['messages'][0]['speech'])
        return out_dict
    elif response['result']['metadata']['intentName'] == 'order tea - no - yes - dob':
        global DOB
        global NAME
        DOB=json_data['date']
        out_dict['messageText']=['Your birthday date is saved '+NAME+'!','BE READY. When your birthday come, we\'ll invite u to celebrate it around your FREE delicious cake in Bewley\'s!' ]
        return out_dict
    
    elif response['result']['metadata']['intentName'] == 'order tea - yes - select.number':  
            num=str(json_data['number'][0])
            global CART
            CART['quantity']=num
            print CART
            print data
            out_dict['messageText']=['Great! '+num+' cups of '+item+' has been added to your cart','Would you like to continue shoping?']
            out_dict["plugin"] = {'name': 'autofill', 'type': 'items', 'data': ['yes, continue','Show cart'],'link':'yes','value':'https://www.bewleys.com/ie/checkout/'}
            return out_dict    
    elif response['result']['metadata']['intentName'] == 'order tea - yes - select.number - yes':
            out_dict['messageText']=['Great, What else would you like to have?']
            out_dict["plugin"] = {'name': 'autofill', 'type': 'items', 'data': menu_items}
            return out_dict
    elif response['result']['metadata']['intentName'] == 'follow':
        out_dict['messageText'].append('You can follow us by clicking here:')
        out_dict["plugin"] = {'name': 'follow', 'type': 'lists', 'data': fol}
        return out_dict  
    elif response['result']['metadata']['intentName'] == 'place order':  
        out_dict['messageText'].append('Here are the items we offer. What would you like to have?')
        out_dict["plugin"] = {'name': 'autofill', 'type': 'text', 'data': menu_items}
        return out_dict           

       
           
          
                