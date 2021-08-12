#!/usr/bin/env python3

import requests
import os
import urllib
import json

from firebase_admin import db

one_signal_config_path = "/CONFIGURATION/GATEWAYS/OneSignal/"
telegram_config_path = "/CONFIGURATION/GATEWAYS/Telegram/"


def load_config(firebase_obj):
    try:
                
        ref = db.reference(one_signal_config_path, app= firebase_obj)
        one_signal_config = ref.get()
        
        ref = db.reference(telegram_config_path, app= firebase_obj)
        telegram_config = ref.get()
              
        config = {
            "OneSignal" : one_signal_config,
            "Telegram" : telegram_config
        }
                
        return config
    
    except Exception as e:
        print("Ocorreu um erro no Metodo load_config() em notification_helper: {}".format(e))
        return ""

def send_notification(message, platform, firebase_obj):
        
    config = load_config(firebase_obj)
        
    response = requests
    
    if platform.upper() == "TELEGRAM":          
        response = send_notification_telegram(config, message)
                
    if platform.upper() == "ONESIGNAL":            
        response = send_notification_onesignal(config, message)

    if platform.upper() == "ALL":            
        response = send_notification_all(config, message)
    
    return response


def send_notification_telegram(config, message):
    try:
        
        token = config["Telegram"]["Token"]
        chatIDs = config["Telegram"]["NotificationNumbers"]
       
        for key, chatID in chatIDs.items():
            send_text = 'https://api.telegram.org/bot' + token + '/sendMessage?chat_id=' + chatID + '&parse_mode=Markdown&text=' + message
            response_telegram = requests.get(send_text)
  
        response = requests
        response.status_code = 200
        response.reason = "OK"
             
    except Exception as e: 
        
        response = requests
        response.status_code = 500
        response.reason = "Internal Server Error: {}".format(e)
        
    finally:
        
        return response
    
    
def send_notification_onesignal(config, message):
    try:
        
        header = {"Content-Type": "application/json; charset=utf-8",
          "Authorization": "Basic {}".format(config["OneSignal"]["RestAPIKey"])}

        payload = {"app_id": "16f4bf3a-8542-43be-b92d-5c1b2f142d9b",
           "included_segments": ["{}".format(config["OneSignal"]["Segment"])],
           "contents": {"en": "{}".format(message)}}
        
        response = requests.post("https://onesignal.com/api/v1/notifications", headers=header, data=json.dumps(payload))
        
        return response
        
    except Exception as e: 
        
        return response
        

def send_notification_all(config, message):
    try:
        
        result_telegram = send_notification_telegram(config, message)
        result_onesignal = send_notification_onesignal(config, message)
                     
        if result_telegram.status_code == 200 and result_onesignal.status_code == 200:             
                     
            response = requests
            response.status_code = 200
            response.reason = "OK"
        
        else:
            raise Exception
        
    except Exception as e:
        
        response = requests
        response.status_code = 500
        response.reason = "Internal Server Error: {}".format(e)
        
    finally:
        return response
