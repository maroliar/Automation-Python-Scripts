#!/usr/bin/env python3

# Script que envia uma notificação via OneSignal ou Telegram, mediante um evento de callback mqtt.

import paho.mqtt.client as mqtt
import sys
import time
import os
import logging
import requests
import json

from firebase_admin import initialize_app
from firebase_admin import credentials
from firebase_admin import db

from notification_helper import send_notification

firebase_app_name = 'home-automation-fd418-default-rtdb'
firebase_admin_sdk_json_path = '/home/pi/Scripts/python/config/home-automation-fd418-firebase-adminsdk-6552s-037f34a75e.json'

firebase_obj = ""

firebase_local_json_path = "/home/pi/Scripts/python/config/homeAutomationConfig.json"

notification_method = ""
notification_method_path = "/CONFIGURATION/SCRIPTS/AlertRingInterfone/NotificationMethod/"

# definicoes MQTT: 
Broker = "raspberrypi"
PortaBroker = 1883
KeepAliveBroker = 60
Topico = "HOME/INTERFONE"

logging.basicConfig(filename='/home/pi/Scripts/python/logs/alertRingInterfone.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(funcName)s => %(message)s')


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
            
        global notification_method
    
        ref = db.reference(notification_method_path, app= firebase_obj)
        notification_method = ref.get().replace("\"", "")
            
    except Exception as e:
        logging.exception("Ocorreu um erro no Metodo load_config() {}".format(e))
        
        # caso nao consiga conexao com Firebase
        load_config_local()
        

def load_config_local():
    try:
        
        print("Erro ao baixar definições do Firebase. Usando o ultimo arquivo de configuração local...")
        logging.debug("Erro ao baixar definições do Firebase. Usando o ultimo arquivo de configuração local...")
    
        global notification_method
    
        with open(firebase_local_json_path) as json_data_file:
            data = json.load(json_data_file)
       
        notification_method = data["CONFIGURATION"]["SCRIPTS"]["AlertRingInterfone"]["NotificationMethod"]
    
    except Exception as e:
        logging.exception("Ocorreu um erro no Metodo load_config_local() {}".format(e))
    

def on_connect(client, userdata, flags, rc):    
    client.subscribe(Topico)

def on_message(client, userdata, msg):
    try:
        
        mensagemRecebida = str(msg.payload.decode("utf-8"))
    
        print("Nova mensagem recebida: {}".format(mensagemRecebida))
    
        if (str(mensagemRecebida).find("RING") >= 0): 
            enviar_notificacao("Parece que tem alguém tocando o Interfone!")

    except ReadTimeoutError as t:
        logging.exception("Timeout Error Exception: {}".format(t))
        
    except Exception as e:
        logging.exception("Ocorreu um erro no Metodo on_message() {}".format(e))


def enviar_notificacao(mensagem):
    try:
        
        os.system("notify-send 'Home Automation' '{}'".format(mensagem))
        logging.debug(mensagem);
        
        response = send_notification(mensagem, notification_method, firebase_obj)
                
        logging.debug("StatusCode: {}, Reason: {}".format(response.status_code, response.reason))
             
    except Exception as e:
        logging.exception("Ocorreu um erro no Metodo enviar_notificacao() {}".format(e))

try:
    print("Iniciando script alertRingInterfone.py")
    logging.debug("Iniciando script alertRingInterfone.py")
    
    os.system("notify-send 'Home Automation' 'Iniciando script alertRingInterfone.py'")
    
    initialize_firebase()
    load_config()
    
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
        
    client.connect(Broker, PortaBroker, KeepAliveBroker)
    client.loop_forever()
        
except KeyboardInterrupt:
    
    print ("\nCtrl+C pressionado, encerrando a aplicacao...")
    logging.debug("\nCtrl+C pressionado, encerrando a aplicacao...")
    sys.exit(0)
