#!/usr/bin/env python3

# Script que envia uma notificação via OneSignal ou Telegram, mediante a uma determinada temperatura atingida do Raspberry.

import sys
import time
import os
import logging
import json

from firebase_admin import initialize_app
from firebase_admin import credentials
from firebase_admin import db

from gpiozero import CPUTemperature
from notification_helper import send_notification

firebase_app_name = 'home-automation-fd418-default-rtdb'
firebase_admin_sdk_json_path = '/home/pi/Scripts/python/config/home-automation-fd418-firebase-adminsdk-6552s-037f34a75e.json'

firebase_obj = ""

firebase_local_json_path = "/home/pi/Scripts/python/config/homeAutomationConfig.json"

notification_method = ""
notification_method_path = "/CONFIGURATION/SCRIPTS/AlertRaspberryTemperature/NotificationMethod/"

max_temperature_alert = 0
max_temperature_alert_path = "/CONFIGURATION/SCRIPTS/AlertRaspberryTemperature/MaxTemperatureAlert/"

logging.basicConfig(filename='/home/pi/Scripts/python/logs/alertRaspberryTemperature.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(funcName)s => %(message)s')


def initialize_firebase():
    try:
        
        global firebase_obj
        
        options = {'databaseURL': 'https://{}.firebaseio.com'
               .format(firebase_app_name),'storageBucket': '{}.appspot.com'
               .format(firebase_app_name)}

        credential = credentials.Certificate(firebase_admin_sdk_json_path)        
        firebase_obj = initialize_app(credential, options, name = firebase_app_name)
        
    except Exception as e:
        logging.exception("Ocorreu um erro no Metodo initialize_firebase() {}".format(e)) 


def load_config():
    try:
        
        global notification_method, max_temperature_alert
    
        ref = db.reference(notification_method_path, app= firebase_obj)
        notification_method = ref.get().replace("\"", "")
    
        ref = db.reference(max_temperature_alert_path, app= firebase_obj)
        max_temperature_alert = float(ref.get().replace("\"", ""))
    
    except Exception as e:
        logging.exception("Ocorreu um erro no Metodo load_config() {}".format(e))
        
        # caso nao consiga conexao com Firebase
        load_config_local()
    
    
def load_config_local():
    try:
        
        print("Erro ao baixar definições do Firebase. Usando o ultimo arquivo de configuração local...")
        logging.debug("Erro ao baixar definições do Firebase. Usando o ultimo arquivo de configuração local...")
        
        global notification_method, max_temperature_alert
    
        with open(firebase_local_json_path) as json_data_file:
            data = json.load(json_data_file)
       
        notification_method = data["CONFIGURATION"]["SCRIPTS"]["AlertRaspberryTemperature"]["NotificationMethod"]
        max_temperature_alert = int(data["CONFIGURATION"]["SCRIPTS"]["AlertRaspberryTemperature"]["MaxTemperatureAlert"])
        
    except Exception as e:
        logging.exception("Ocorreu um erro no Metodo load_config_local() {}".format(e))

  
def get_temperature():
    while True:
        try:

            temp = CPUTemperature().temperature
            
            print("Verificando temperatura... {}".format(temp))

            if(temp >= max_temperature_alert):
                enviar_notificacao("Temperatura do Raspberry está elevada! {}".format(int(temp)))
                
            time.sleep(10)
        
        except Exception as e:
            logging.exception("Ocorreu um erro no Metodo get_temperature() {}".format(e))            


def enviar_notificacao(mensagem):
    try:
        
        os.system("notify-send 'Home Automation' '{}'".format(mensagem))
        logging.debug(mensagem);
        
        response = send_notification(mensagem, notification_method, firebase_obj)
                
        logging.debug("StatusCode: {}, Reason: {}".format(response.status_code, response.reason))
             
    except Exception as e:
        logging.exception("Ocorreu um erro no Metodo enviar_notificacao() {}".format(e))


try:
    print("Iniciando script alertRaspberryTemperature.py")
    logging.debug("Iniciando script alertRaspberryTemperature.py")
    
    os.system("notify-send 'Home Automation' 'Iniciando script alertRaspberryTemperature.py'")
    
    initialize_firebase()
    load_config()
    get_temperature()
                      
except KeyboardInterrupt:
    
    print ("\nCtrl+C pressionado, encerrando a aplicacao...")
    logging.debug("\nCtrl+C pressionado, encerrando a aplicacao...")
    sys.exit(0)

