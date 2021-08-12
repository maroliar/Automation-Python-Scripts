#!/usr/bin/env python3

import paho.mqtt.client as mqtt
import sys
import time
import os
import logging

from firebase_admin import initialize_app
from firebase_admin import credentials
from firebase_admin import db

firebase_app_name = 'home-automation-fd418-default-rtdb'
firebase_admin_sdk_json_path = '/home/pi/Scripts/python/config/home-automation-fd418-firebase-adminsdk-6552s-037f34a75e.json'

firebase_obj = ""

# Valores abaixo nao necessitam serem armazenados como referencia, logo apenas o Path é necessário
Esp32_Pets_Command_Path = "/DEVICES/ESP32_PETS/COMMAND"
NodeMCU_Interfone_Command_Path = "/DEVICES/NODEMCU_INTERFONE/COMMAND"
Esp8266_Desodorizacao_Command_Path = "/DEVICES/ESP8266_DESODORIZACAO/COMMAND"
Esp32_Gateway_SMS_Command_Path = "/DEVICES/ESP32_GATEWAY_SMS/COMMAND"
#Esp32_Switch_Command_Path = "/DEVICES/ESP32_SWITCH/COMMAND" 

# Definições MQTT: 
Broker = "raspberrypi"
PortaBroker = 1883
KeepAliveBroker = 60

TopicsList = [("HOME/PETS",0), ("HOME/INTERFONE",0), ("HOME/DESODORIZACAO",0), ("HOME/GATEWAY/SMS",0)]
#TopicsList = [("HOME/PETS",0), ("HOME/INTERFONE",0), ("HOME/DESODORIZACAO",0), ("HOME/GATEWAY/SMS",0), ("HOME/SWITCH",0)]

logging.basicConfig(filename='/home/pi/Scripts/python/logs/gatewayMQTT2Firebase.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(funcName)s => %(message)s')


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
        print("Sem parametro de inicialização para load_config()")
        
    except Exception as e:
        logging.exception("Ocorreu um erro no Metodo load_config() {}".format(e))




def on_connect(client, userdata, flags, rc):    
    client.subscribe(TopicsList)

def on_message(client, userdata, msg):
    
    try:
    
        mensagemRecebida = str(msg.payload.decode("utf-8"))
        topico = str(msg.topic)
    
        print("Nova mensagem recebida: {}, no topico: {}".format(mensagemRecebida, topico))
        
        if(str(topico.upper()).find("PETS") >= 0):
            
            ref = db.reference(Esp32_Pets_Command_Path, app=firebase_obj)
            
            if (str(mensagemRecebida.upper()).find("OK ACT") >= 0):
                
                print("COMANDO 'OK ACT' Recebido. Voltando status padrão no Firebase");
                logging.debug("COMANDO 'OK ACT' Recebido. Voltando status padrão no Firebase");
                ref.set("")
                
            if (str(mensagemRecebida.upper()).find("OK RST") >= 0):

                print("COMANDO 'OK RST' Recebido. Voltando status padrão no Firebase");
                logging.debug("COMANDO 'OK RST' Recebido. Voltando status padrão no Firebase");
                ref.set("")                
        
        
        if(str(topico.upper()).find("INTERFONE") >= 0):
            
            ref = db.reference(NodeMCU_Interfone_Command_Path, app= firebase_obj)
            
            if (str(mensagemRecebida.upper()).find("OK ACT") >= 0):
                
                print("COMANDO 'OK ACT' Recebido. Voltando status padrão no Firebase");
                logging.debug("COMANDO 'OK ACT' Recebido. Voltando status padrão no Firebase");
                ref.set("")
                
            if (str(mensagemRecebida.upper()).find("OK RST") >= 0):

                print("COMANDO 'OK RST' Recebido. Voltando status padrão no Firebase");
                logging.debug("COMANDO 'OK RST' Recebido. Voltando status padrão no Firebase");
                ref.set("")
         
        
        if(str(topico.upper()).find("DESODORIZACAO") >= 0):
            
            ref = db.reference(Esp8266_Desodorizacao_Command_Path, app= firebase_obj)
            
            if (str(mensagemRecebida.upper()).find("OK ACT") >= 0):
                
                print("COMANDO 'OK ACT' Recebido. Voltando status padrão no Firebase");
                logging.debug("COMANDO 'OK ACT' Recebido. Voltando status padrão no Firebase");
                ref.set("")
                
            if (str(mensagemRecebida.upper()).find("OK RST") >= 0):

                print("COMANDO 'OK RST' Recebido. Voltando status padrão no Firebase");
                logging.debug("COMANDO 'OK RST' Recebido. Voltando status padrão no Firebase");
                ref.set("")
                
        
        if(str(topico.upper()).find("SMS") >= 0):
            
            ref = db.reference(Esp32_Gateway_SMS_Command_Path, app= firebase_obj)
            
            if (str(mensagemRecebida.upper()).find("OK ACT1") >= 0):
                
                print("COMANDO 'OK ACT1' Recebido. Voltando status padrão no Firebase");
                logging.debug("COMANDO 'OK ACT1' Recebido. Voltando status padrão no Firebase");
                ref.set("")
                
            if (str(mensagemRecebida.upper()).find("OK ACT2") >= 0):
                
                print("COMANDO 'OK ACT2' Recebido. Voltando status padrão no Firebase");
                logging.debug("COMANDO 'OK ACT2' Recebido. Voltando status padrão no Firebase");
                ref.set("")
                
            if (str(mensagemRecebida.upper()).find("OK RST") >= 0):

                print("COMANDO 'OK RST' Recebido. Voltando status padrão no Firebase");
                logging.debug("COMANDO 'OK RST' Recebido. Voltando status padrão no Firebase");
                ref.set("")

    except TypeError as e:
        logging.debug(f"Argument Error: {e}")

try:
    print("Iniciando script gatewayMQTT2Firebase.py")
    logging.debug("Iniciando script gatewayMQTT2Firebase.py")
     
    os.system("notify-send 'Home Automation' 'Iniciando script gatewayMQTT2Firebase.py'")
     
    # Aguarda 1 min na inicialização para evitar que o programa se encerre prematuramente, devido a rede não estar pronta ainda
    time.sleep(60) 
     
    initialize_firebase()
    #load_config()
   
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
        
    client.connect(Broker, PortaBroker, KeepAliveBroker)
    client.loop_forever()
        
except KeyboardInterrupt:
    
    print ("\nCtrl+C pressionado, encerrando a aplicacao...")
    logging.debug("\nCtrl+C pressionado, encerrando a aplicacao...")
    sys.exit(0)
    
