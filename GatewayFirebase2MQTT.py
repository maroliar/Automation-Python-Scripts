#!/usr/bin/env python3

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
Esp32_Pets_Command_Path = "/DEVICES/ESP32_PETS/COMMAND"
NodeMCU_Interfone_Command_Path = "/DEVICES/NODEMCU_INTERFONE/COMMAND"
Esp8266_Desodorizacao_Command_Path = "/DEVICES/ESP8266_DESODORIZACAO/COMMAND"
Esp32_Gateway_SMS_Command_Path = "/DEVICES/ESP32_GATEWAY_SMS/COMMAND"
#Esp32_Switch_Command_Path = "/DEVICES/ESP32_SWITCH/COMMAND" 

scripts_path_in_firebase = "/CONFIGURATION/SCRIPTS"
scripts_path_in_linux = "/home/pi/Scripts/python/"

logging.basicConfig(filename='/home/pi/Scripts/python/logs/gatewayFirebase2MQTT.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(funcName)s => %(message)s')


def initialize_firebase():
    try:
        
        global firebase_obj
        
        options = {'databaseURL': 'https://{}.firebaseio.com'
               .format(firebase_app_name),'storageBucket': '{}.appspot.com'
               .format(firebase_app_name)}

        credential = credentials.Certificate(firebase_admin_sdk_json_path)        
        firebase_obj = initialize_app(credential, options, name = firebase_app_name)
        
        db.reference('/', app= firebase_obj).listen(listener)
        
    except Exception as e:
        logging.exception("Ocorreu um erro no Metodo initialize_firebase() {}".format(e))


def load_config():
    try:
    
        global Esp32_Pets_MQTT_Topic
        global NodeMCU_Interfone_MQTT_Topic
        global Esp8266_Desodorizacao_MQTT_Topic  
        global Esp32_Gateway_SMS_MQTT_Topic
        #global Esp32_Switch_MQTT_Topic 

        ref = db.reference(Esp32_Pets_MQTT_Topic_Path, app=firebase_obj)
        Esp32_Pets_MQTT_Topic = ref.get().replace("\"", "")
         
        ref = db.reference(NodeMCU_Interfone_MQTT_Topic_Path, app=firebase_obj)
        NodeMCU_Interfone_MQTT_Topic = ref.get().replace("\"", "")
         
        ref = db.reference(Esp8266_Desodorizacao_MQTT_Topic_Path, app=firebase_obj)
        Esp8266_Desodorizacao_MQTT_Topic = ref.get().replace("\"", "")
         
        ref = db.reference(Esp32_Gateway_SMS_MQTT_Topic_Path, app=firebase_obj)
        Esp32_Gateway_SMS_MQTT_Topic = ref.get().replace("\"", "")
         
        #ref = db.reference(Esp32_Switch_MQTT_Topic_Path, app=firebase_obj)
        #Esp32_Switch_MQTT_Topic = ref.get().replace("\"", "")
        
    except Exception as e:
        logging.exception("Ocorreu um erro no Metodo load_config() {}".format(e))


def listener(event):
            
    try:
        print("Evento Recebido: {}, Path: {}, Data: {}".format(event.event_type, event.path, event.data))
        logging.debug("Evento Recebido: {}, Path: {}, Data: {}".format(event.event_type, event.path, event.data))

        if(event.path.upper() == Esp32_Pets_Command_Path):
                 
            if(event.data == "2"): # RESET
                              
                os.system("mosquitto_pub -h 'raspberrypi' -t 'HOME/PETS' -m '{\"device\": \"SCRIPT\",\"message\": \"RST\"}'")
                logging.debug("Executou: mosquitto_pub 'Json Message' no topico: HOME/PETS");
                
            if(event.data == "3"): # ACTION
                
                os.system("mosquitto_pub -h 'raspberrypi' -t 'HOME/PETS' -m '{\"device\": \"SCRIPT\",\"message\": \"ACT\"}'")
                logging.debug("Executou: mosquitto_pub 'Json Message' no topico: HOME/PETS");
                       
            
        if(event.path.upper() == NodeMCU_Interfone_Command_Path):
            
            if(event.data == "2"): # RESET
                
                os.system("mosquitto_pub -h 'raspberrypi' -t 'HOME/INTERFONE' -m '{\"device\": \"SCRIPT\",\"message\": \"RST\"}'")
                logging.debug("Executou: mosquitto_pub 'Json Message' no topico: HOME/INTERFONE");
                
            if(event.data == "3"): # ACTION
                
                os.system("mosquitto_pub -h 'raspberrypi' -t 'HOME/INTERFONE' -m '{\"device\": \"SCRIPT\",\"message\": \"ACT\"}'")
                logging.debug("Executou: mosquitto_pub 'Json Message' no topico: HOME/INTERFONE");
            
                    
        if(event.path.upper() == Esp8266_Desodorizacao_Command_Path):
            
            if(event.data == "2"): # RESET
                
                os.system("mosquitto_pub -h 'raspberrypi' -t 'HOME/DESODORIZACAO' -m '{\"device\": \"SCRIPT\",\"message\": \"RST\"}'")
                logging.debug("Executou: mosquitto_pub 'Json Message' no topico: HOME/DESODORIZACAO");
                
            if(event.data == "3"): # ACTION
                
                os.system("mosquitto_pub -h 'raspberrypi' -t 'HOME/DESODORIZACAO' -m '{\"device\": \"SCRIPT\",\"message\": \"ACT\"}'")
                logging.debug("Executou: mosquitto_pub 'Json Message' no topico: HOME/DESODORIZACAO");
                
        
        if(event.path.upper() == Esp32_Gateway_SMS_Command_Path):
            
            if(event.data == "2"): # RESET
                
                os.system("mosquitto_pub -h 'raspberrypi' -t 'HOME/GATEWAY/SMS' -m '{\"device\": \"SCRIPT\",\"message\": \"RST\"}'")
                logging.debug("Executou: mosquitto_pub 'Json Message' no topico: HOME/GATEWAY/SMS");
                
            if(event.data == "31"): # ACTION RELAY 1
                
                os.system("mosquitto_pub -h 'raspberrypi' -t 'HOME/SWITCH' -m '{\"device\": \"SCRIPT\",\"message\": \"ACT1\"}'")
                logging.debug("Executou: mosquitto_pub 'Json Message' no topico: HOME/SWITCH");
        
            if(event.data == "32"): # ACTION RELAY 2
                
                os.system("mosquitto_pub -h 'raspberrypi' -t 'HOME/SWITCH' -m '{\"device\": \"SCRIPT\",\"message\": \"ACT1\"}'")
                logging.debug("Executou: mosquitto_pub 'Json Message' no topico: HOME/SWITCH");
     
             
             
        # Evento de atualização de instruções dos Scripts no Firebase
        if(scripts_path_in_firebase in event.path):
            
            ref = db.reference(event.path, app=firebase_obj)
                    
            if(event.data.replace("\"", "") == "1"): # RESTART SCRIPT
                                  
                # obtem o nome do script pela posicao da string path recebida
                script_name = event.path.split("/")[3] 
            
                print("Reiniciando {}.py para atualização de instruções".format(script_name))
                logging.debug("Reiniciando {}.py para atualização de instruções".format(script_name))
            
                # mata o processo do script (o mesmo sera startado posteriormente pelo script_monitor.sh)
                os.system("ps -ef |grep {}{}.py ".format(scripts_path_in_linux, script_name) + "|grep -v -E 'grep|scriptMonitor' |awk '{print $2}' |xargs kill")
     
                # Retornando Status padrão ao Firebase (seguindo o padrão salvo, por conta do kodular)
                # ref.set("0")
                ref.set("\"0\"") 
         
    except Exception as e:
        logging.exception("Ocorreu um erro no Metodo listener() {}".format(e))


try:

    print("Iniciando script gatewayFirebase2MQTT.py")
    logging.debug("Iniciando script gatewayFirebase2MQTT.py")
    
    os.system("notify-send 'Home Automation' 'Iniciando script gatewayFirebase2MQTT.py'")
    
    # Aguarda 1 min na inicialização para evitar que o programa se encerre prematuramente, devido a rede não estar pronta ainda
    time.sleep(60)
    
    initialize_firebase() 
    load_config()

except KeyboardInterrupt:
    
    print ("\nCtrl+C pressionado, encerrando a aplicacao...")
    logging.debug("\nCtrl+C pressionado, encerrando a aplicacao...")           
    sys.exit(0)
