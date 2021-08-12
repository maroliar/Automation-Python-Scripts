#!/usr/bin/env python3

# Script que aciona o ESP32_PETS mediante um horário determinado, e envia uma notificação via OneSignal ou Telegram. 
# O comando de acionamento é feito por S.O.

import sys
import time
import os
import logging
import json

from firebase_admin import initialize_app
from firebase_admin import credentials
from firebase_admin import db

from datetime import datetime
from notification_helper import send_notification

firebase_app_name = 'home-automation-fd418-default-rtdb'
firebase_admin_sdk_json_path = '/home/pi/Scripts/python/config/home-automation-fd418-firebase-adminsdk-6552s-037f34a75e.json'

firebase_obj = ""

firebase_local_json_path = "/home/pi/Scripts/python/config/homeAutomationConfig.json"

notification_method = ""
notification_method_path = "/CONFIGURATION/SCRIPTS/AutoFeedPets/NotificationMethod/"

act_time_list = []
act_time_list_path = "/CONFIGURATION/SCRIPTS/AutoFeedPets/TimeToAct/"

logging.basicConfig(filename='/home/pi/Scripts/python/logs/autoFeedPets.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(funcName)s => %(message)s')


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
    
        global notification_method, act_time_list
    
        ref = db.reference(notification_method_path, app= firebase_obj)
        notification_method = ref.get().replace("\"", "")
    
        ref = db.reference(act_time_list_path, app= firebase_obj)
        act_time_list = str(ref.get()).replace("\"", "").split(",")
            
    except Exception as e:
        logging.exception("Ocorreu um erro no Metodo load_config() {}".format(e))
        
        # caso nao consiga conexao com Firebase
        load_config_local()


def load_config_local():
    try:
        
        print("Erro ao baixar definições do Firebase. Usando o ultimo arquivo de configuração local...")
        logging.debug("Erro ao baixar definições do Firebase. Usando o ultimo arquivo de configuração local...")
        
        global notification_method, act_time_list
    
        with open(firebase_local_json_path) as json_data_file:
            data = json.load(json_data_file)
       
        notification_method = data["CONFIGURATION"]["SCRIPTS"]["AutoFeedPets"]["NotificationMethod"]
        act_time_list = str(data["CONFIGURATION"]["SCRIPTS"]["AutoFeedPets"]["TimeToAct"]).split(",") 

    except Exception as e:
        logging.exception("Ocorreu um erro no Metodo load_config_local() {}".format(e))

def check_time():  
    while True:      
        try:
                                 
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            
            print("Verificando horário: {}".format(current_time))
        
            if(current_time in act_time_list):
                alimentar_pets()
                enviar_notificacao("Pets alimentados conforme schedule de horário.")
            
            time.sleep(1)
        
        except Exception as e:
            logging.exception("Ocorreu um erro no Metodo check_time() {}".format(e))
            

#TODO: Estudar uma forma de inserir os parametros de MQTT abaixo no arquivo de configuracao
def alimentar_pets():
    
    try:
        print("Horário atingido!")
        logging.debug("Horário atingido!")

        os.system("mosquitto_pub -h 'raspberrypi' -t 'HOME/PETS' -m '{\"device\": \"Script\",\"message\": \"ACT\"}'")
        logging.debug("Executou: mosquitto_pub 'Json Message' no topico: HOME/PETS")
        
    except Exception as e:
        logging.exception("Ocorreu um erro no Metodo alimentar_pets() {}".format(e))

def enviar_notificacao(mensagem):
    try:
        
        os.system("notify-send 'Home Automation' '{}'".format(mensagem))
        logging.debug(mensagem)
               
        response = send_notification(mensagem, notification_method, firebase_obj)
               
        logging.debug("StatusCode: {}, Reason: {}".format(response.status_code, response.reason))
             
    except Exception as e:
        logging.exception("Ocorreu um erro no Metodo enviar_notificacao() {}".format(e))

try:
    print("Iniciando script autoFeedPets.py")
    logging.debug("Iniciando script autoFeedPets.py")           
               
    os.system("notify-send 'Home Automation' 'Iniciando script autoFeedPets.py'")
    
    initialize_firebase()
    load_config()
    check_time()
                     
except KeyboardInterrupt:
    
    print ("\nCtrl+C pressionado, encerrando a aplicacao...")
    logging.debug("\nCtrl+C pressionado, encerrando a aplicacao...")           
    sys.exit(0)    
