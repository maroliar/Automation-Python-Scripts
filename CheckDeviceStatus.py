#!/usr/bin/env python3

# Script que monitora o status atual dos devices mqtt, e posta o resultado continuamente no firebase.

import paho.mqtt.client as mqtt
import sys
import time
import os
import logging
import json

from firebase_admin import initialize_app
from firebase_admin import credentials
from firebase_admin import db

from retry import retry
#from notification_helper import send_notification

firebase_app_name = 'home-automation-fd418-default-rtdb'
firebase_admin_sdk_json_path = '/home/pi/Scripts/python/config/home-automation-fd418-firebase-adminsdk-6552s-037f34a75e.json'

firebase_obj = ""

#firebase_local_json_path = "/home/pi/Scripts/python/config/homeAutomationConfig.json"
#notification_method = ""
#notification_method_path = "/CONFIGURATION/SCRIPTS/CheckDeviceStatus/NotificationMethod"

# Definições MQTT: 
Broker = "raspberrypi"
PortaBroker = 1883
KeepAliveBroker = 60

TopicsList = [("HOME/PETS",0), ("HOME/INTERFONE",0), ("HOME/DESODORIZACAO",0), ("HOME/GATEWAY/SMS",0)]
#TopicsList = [("HOME/PETS",0), ("HOME/INTERFONE",0), ("HOME/DESODORIZACAO",0), ("HOME/GATEWAY/SMS",0), ("HOME/SWITCH",0)]

Esp32_Pets_MQTT_Topic = ""
Esp32_Pets_MQTT_Topic_Path = "/DEVICES/ESP32_PETS/MQTT_TOPIC"

NodeMCU_Interfone_MQTT_Topic = ""
NodeMCU_Interfone_MQTT_Topic_Path = "/DEVICES/NODEMCU_INTERFONE/MQTT_TOPIC"

Esp8266_Desodorizacao_MQTT_Topic = ""
Esp8266_Desodorizacao_MQTT_Topic_Path = "/DEVICES/ESP8266_DESODORIZACAO/MQTT_TOPIC"

Esp32_Gateway_SMS_MQTT_Topic = ""
Esp32_Gateway_SMS_MQTT_Topic_Path = "/DEVICES/ESP32_GATEWAY_SMS/MQTT_TOPIC"

#Esp32_Switch_MQTT_Topic = ""
#Esp32_Switch_MQTT_Topic_Path = "/DEVICES/ESP32_SWITCH/MQTT_TOPIC"


# Valores abaixo nao necessitam serem armazenados como referencia, logo apenas o Path é necessário
Esp32_Pets_Status_Path = "/DEVICES/ESP32_PETS/STATUS"
NodeMCU_Interfone_Status_Path = "/DEVICES/NODEMCU_INTERFONE/STATUS"
Esp8266_Desodorizacao_Status_Path = "/DEVICES/ESP8266_DESODORIZACAO/STATUS"
Esp32_Gateway_SMS_Status_Path = "/DEVICES/ESP32_GATEWAY_SMS/STATUS"
#Esp32_Switch_Status_Path = "/DEVICES/ESP32_SWITCH/STATUS" 


checkCountPets = 0
checkCountInterfone = 0
checkCountDesodorizacao = 0
checkCountGatewaySMS = 0
#checkCountSwitch = 0

logging.basicConfig(filename='/home/pi/Scripts/python/logs/checkDeviceStatus.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(funcName)s => %(message)s')


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
    
        global Esp32_Pets_MQTT_Topic
        global NodeMCU_Interfone_MQTT_Topic
        global Esp8266_Desodorizacao_MQTT_Topic  
        global Esp32_Gateway_SMS_MQTT_Topic
        #global Esp32_Switch_MQTT_Topic 

        ref = db.reference(Esp32_Pets_MQTT_Topic_Path, app= firebase_obj)
        Esp32_Pets_MQTT_Topic = ref.get().replace("\"", "")
         
        ref = db.reference(NodeMCU_Interfone_MQTT_Topic_Path, app= firebase_obj)
        NodeMCU_Interfone_MQTT_Topic = ref.get().replace("\"", "")
         
        ref = db.reference(Esp8266_Desodorizacao_MQTT_Topic_Path, app= firebase_obj)
        Esp8266_Desodorizacao_MQTT_Topic = ref.get().replace("\"", "")
         
        ref = db.reference(Esp32_Gateway_SMS_MQTT_Topic_Path, app= firebase_obj)
        Esp32_Gateway_SMS_MQTT_Topic = ref.get().replace("\"", "")
         
        #ref = db.reference(Esp32_Switch_MQTT_Topic_Path, app= firebase_obj)
        #Esp32_Switch_MQTT_Topic = ref.get().replace("\"", "")
        
    except Exception as e:
        logging.exception("Ocorreu um erro no Metodo load_config() {}".format(e))
        

@retry(Exception, delay=10*60, tries=-1)
def on_connect(client, userdata, flags, rc):    
    client.subscribe(TopicsList)

@retry(Exception, delay=10*60, tries=-1)
def on_message(client, userdata, msg):
    try:
        
        global checkCountPets
        global checkCountInterfone
        global checkCountDesodorizacao
        global checkCountGatewaySMS
        #global checkCountSwitch
        
        mensagemRecebida = str(msg.payload.decode("utf-8"))
        topico = str(msg.topic)
    
        print("Nova mensagem recebida: {}, no topico: {}".format(mensagemRecebida, topico))
        #logging.debug("Nova mensagem recebida: {}, no topico: {}".format(mensagemRecebida, topico))
    
        if(str(topico.upper()).find("PETS") >= 0):
            
            ref = db.reference(Esp32_Pets_Status_Path, app= firebase_obj)
            
            if (str(mensagemRecebida.upper()).find("CHECK") >= 0):
                checkCountPets += 1
                
                if(checkCountPets >= 2):
                    ref.set("OFFLINE")
                    checkCountPets = 0
                               
            if (str(mensagemRecebida.upper()).find("ONLINE") >= 0):
                ref.set("ONLINE")
                checkCountPets = 0

        
        if(str(topico.upper()).find("INTERFONE") >= 0):
            
            ref = db.reference(NodeMCU_Interfone_Status_Path, app= firebase_obj)
            
            if (str(mensagemRecebida.upper()).find("CHECK") >= 0):
                checkCountInterfone += 1
                
                if(checkCountInterfone >= 2):
                    ref.set("OFFLINE")
                    checkCountInterfone = 0
                               
            if (str(mensagemRecebida.upper()).find("ONLINE") >= 0):
                ref.set("ONLINE")
                checkCountInterfone = 0

        
        if(str(topico.upper()).find("DESODORIZACAO") >= 0):
            
            ref = db.reference(Esp8266_Desodorizacao_Status_Path, app= firebase_obj)
            
            if (str(mensagemRecebida.upper()).find("CHECK") >= 0):
                checkCountDesodorizacao += 1
                
                if(checkCountDesodorizacao >= 2):
                    ref.set("OFFLINE")
                    checkCountDesodorizacao = 0
                               
            if (str(mensagemRecebida.upper()).find("ONLINE") >= 0):
                ref.set("ONLINE")
                checkCountDesodorizacao = 0

        
        if(str(topico.upper()).find("SMS") >= 0):
            
            ref = db.reference(Esp32_Gateway_SMS_Status_Path, app= firebase_obj)
            
            if (str(mensagemRecebida.upper()).find("CHECK") >= 0):
                checkCountGatewaySMS += 1
                
                if(checkCountGatewaySMS >= 2):
                    ref.set("OFFLINE")
                    checkCountGatewaySMS = 0
                               
            if (str(mensagemRecebida.upper()).find("ONLINE") >= 0):
                ref.set("ONLINE")
                checkCountGatewaySMS = 0
                
                
        #if(str(topico.upper()).find("SWITCH") >= 0):
        #    
        #    ref = db.reference(Esp32_Switch_Status_Path, app= firebase_obj)
        #    
        #    if (str(mensagemRecebida.upper()).find("CHECK") >= 0):
        #        checkCountPets += 1
        #        
        #        if(checkCountPets >= 2):
        #            ref.set("OFFLINE")
        #            checkCountPets = 0
        #                       
        #    if (str(mensagemRecebida.upper()).find("ONLINE") >= 0):
        #        ref.set("ONLINE")
        #        checkCountPets = 0
          
    except Exception as e:
        logging.exception("Ocorreu um erro no Metodo on_message() {}".format(e))

@retry(Exception, delay=10*60, tries=-1)
def checkDeviceStatus():
    while True:
        try:
        
            print("Checkando status dos devices MQTT...")
    
            client.publish(Esp32_Pets_MQTT_Topic, "{\"device\":\"SCRIPT\",\"message\":\"CHECK\"}")
            time.sleep(1)
    
            client.publish(NodeMCU_Interfone_MQTT_Topic, "{\"device\":\"SCRIPT\",\"message\":\"CHECK\"}")
            time.sleep(1)
    
            client.publish(Esp8266_Desodorizacao_MQTT_Topic, "{\"device\":\"SCRIPT\",\"message\":\"CHECK\"}")
            time.sleep(1)
            
            client.publish(Esp32_Gateway_SMS_MQTT_Topic, "{\"device\":\"SCRIPT\",\"message\":\"CHECK\"}")
            time.sleep(10)
            
            #client.publish(Esp32_Switch_MQTT_Topic, "{\"device\":\"SCRIPT\",\"message\":\"CHECK\"}")
            #time.sleep(10)
        
        except Exception as e:
            logging.exception("Ocorreu um erro no Metodo checkDeviceStatus() {}".format(e))
      
try:
    print("Iniciando script checkDeviceStatus.py")
    logging.debug("Iniciando script checkDeviceStatus.py")
     
    os.system("notify-send 'Home Automation' 'Iniciando script checkDeviceStatus.py'")
 
    # Aguarda 1 min na inicialização para evitar que o programa se encerre prematuramente, devido a rede não estar pronta ainda
    time.sleep(60) 
    
    initialize_firebase()
    load_config()
    
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
                
    client.connect(Broker, PortaBroker, KeepAliveBroker)
    
    client.loop_start()
        
    checkDeviceStatus()
    
    client.disconnect()
    client.loop_stop()
    
except KeyboardInterrupt:
    
    print ("\nCtrl+C pressionado, encerrando a aplicacao...")
    logging.debug("\nCtrl+C pressionado, encerrando a aplicacao...")
    sys.exit(0)
