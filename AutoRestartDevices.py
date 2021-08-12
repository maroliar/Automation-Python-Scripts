#!/usr/bin/env python3

# Script que reinicia todos os devices MQTT mediante um horário determinado, e envia uma notificacao por OneSignal ou Telegram. 
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
notification_method_path = "/CONFIGURATION/SCRIPTS/AutoRestartDevices/NotificationMethod"

time_to_act = []
time_to_act_path = "/CONFIGURATION/SCRIPTS/AutoRestartDevices/TimeToAct"

logging.basicConfig(filename='/home/pi/Scripts/python/logs/autoRestartDevices.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(funcName)s => %(message)s')


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
    
        global notification_method, time_to_act
    
        ref = db.reference(notification_method_path, app= firebase_obj)
        notification_method = ref.get().replace("\"", "")
    
        ref = db.reference(time_to_act_path, app= firebase_obj)
        time_to_act = ref.get().replace("\"", "")
               
    except Exception as e:
        logging.exception("Ocorreu um erro no Metodo load_config() {}".format(e))
        
        # caso nao consiga conexao com Firebase
        load_config_local()


def load_config_local():
    try:
        
        print("Erro ao baixar definições do Firebase. Usando o ultimo arquivo de configuração local...")
        logging.debug("Erro ao baixar definições do Firebase. Usando o ultimo arquivo de configuração local...")
    
        global notification_method, time_to_act, day_of_week_to_restart 
    
        with open(firebase_local_json_path) as json_data_file:
            data = json.load(json_data_file)
       
        notification_method = data["CONFIGURATION"]["SCRIPTS"]["AutoRestartDevices"]["NotificationMethod"]
        time_to_act = str(data["CONFIGURATION"]["SCRIPTS"]["AutoRestartDevices"]["TimeToAct"]).split(",")

    except Exception as e:
        logging.exception("Ocorreu um erro no Metodo load_config_local() {}".format(e))


def check_time():
    while True:
        try:
        
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
        
            print("Verificando horário: {}".format(current_time))
            
            if current_time in time_to_act:
                enviar_notificacao("Dispositivos reiniciados conforme schedule de horário.")
                restart_devices()
                
            time.sleep(1)
            
        
        except Exception as e: 
            logging.exception("Ocorreu um erro no Metodo check_time() {}".format(e))


def enviar_notificacao(mensagem):
    try:
        
        print(mensagem)
        os.system("notify-send 'Home Automation' '{}'".format(mensagem))
        
        response = send_notification(mensagem, notification_method, firebase_obj)
               
        print("StatusCode: {}, Reason: {}".format(response.status_code, response.reason))
             
    except Exception as e:
        print("Ocorreu um erro no Metodo enviar_notificacao() {}".format(e))
            
        
def restart_devices():
    try:
        
        print("Horário atingido!")
        logging.debug("Horário atingido!")

        os.system("mosquitto_pub -h 'raspberrypi' -t 'HOME/PETS' -m '{\"device\": \"SCRIPT\",\"message\": \"RST\"}'")
        logging.debug("Executou: mosquitto_pub 'Json Message' no topico: HOME/PETS");
        time.sleep(2)

        os.system("mosquitto_pub -h 'raspberrypi' -t 'HOME/INTERFONE' -m '{\"device\": \"SCRIPT\",\"message\": \"RST\"}'")
        logging.debug("Executou: mosquitto_pub 'Json Message' no topico: HOME/INTERFONE");
        time.sleep(2)

        os.system("mosquitto_pub -h 'raspberrypi' -t 'HOME/DESODORIZACAO' -m '{\"device\": \"SCRIPT\",\"message\": \"RST\"}'")
        logging.debug("Executou: mosquitto_pub 'Json Message' no topico: HOME/DESODORIZACAO");
        time.sleep(2)
        
        os.system("mosquitto_pub -h 'raspberrypi' -t 'HOME/GATEWAY/SMS' -m '{\"device\": \"SCRIPT\",\"message\": \"RST\"}'")
        logging.debug("Executou: mosquitto_pub 'Json Message' no topico: HOME/GATEWAY/SMS");
        time.sleep(2)        
    
        #os.system("mosquitto_pub -h 'raspberrypi' -t 'HOME/SWITCH' -m '{\"device\": \"SCRIPT\",\"message\": \"RST\"}'")
        #logging.debug("Executou: mosquitto_pub 'Json Message' no topico: HOME/SWITCH");
        #time.sleep(2)     
        
    except Exception as e:
        logging.exception("Ocorreu um erro no Metodo restart_devices() {}".format(e))
       
try:
    print("Iniciando script autoRestartDevices.py")
    logging.debug("Iniciando script autoRestartDevices.py")
    
    os.system("notify-send 'Home Automation' 'Iniciando script autoRestartDevices.py'")
    
    initialize_firebase() 
    load_config()
    check_time()
               
except KeyboardInterrupt:
    
    print ("\nCtrl+C pressionado, encerrando a aplicacao...")
    logging.debug("\nCtrl+C pressionado, encerrando a aplicacao...")
    sys.exit(0)

