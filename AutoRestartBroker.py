#!/usr/bin/env python3

# Script que reinicia o broker em um dia da semana e horário determinado, e envia uma notificação via OneSignal ou Telegram. 
# O comando de acionamento é feito por S.O.
# Nao tem registros de log deste script, uma vez que o mesmo limpará todos ao reiniciar

import sys
import time
import os
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
notification_method_path = "/CONFIGURATION/SCRIPTS/AutoRestartBroker/NotificationMethod"

time_to_act = []
time_to_act_path = "/CONFIGURATION/SCRIPTS/AutoRestartBroker/TimeToAct"

minutes_waiting_to_restart = 0
minutes_waiting_to_restart_path = "/CONFIGURATION/SCRIPTS/AutoRestartBroker/MinutesWaitingToRestart"

day_of_week_to_restart = ""
day_of_week_to_restart_path = "/CONFIGURATION/SCRIPTS/AutoRestartBroker/DayOfWeekToRestart"

log_path_to_delete = "/home/pi/Scripts/python/logs/"


def initialize_firebase():
    try:
        
        global firebase_obj
        
        options = {'databaseURL': 'https://{}.firebaseio.com'
               .format(firebase_app_name),'storageBucket': '{}.appspot.com'
               .format(firebase_app_name)}

        credential = credentials.Certificate(firebase_admin_sdk_json_path)        
        firebase_obj = initialize_app(credential, options, name = firebase_app_name)
        
    except Exception as e:
        print("Ocorreu um erro no Metodo initialize_firebase() {}".format(e)) 

def load_config():
    try:
    
        global notification_method, time_to_act, minutes_waiting_to_restart, day_of_week_to_restart
    
        ref = db.reference(notification_method_path, app= firebase_obj)
        notification_method = ref.get().replace("\"", "")
    
        ref = db.reference(time_to_act_path, app= firebase_obj)
        time_to_act = ref.get().replace("\"", "")
    
        ref = db.reference(minutes_waiting_to_restart_path, app= firebase_obj)
        minutes_waiting_to_restart = int(ref.get().replace("\"", ""))
    
        ref = db.reference(day_of_week_to_restart_path, app= firebase_obj)
        day_of_week_to_restart = ref.get().replace("\"", "")
            
    except Exception as e:
        print("Ocorreu um erro no Metodo load_config() {}".format(e))
        
        # caso nao consiga conexao com Firebase
        load_config_local()


def load_config_local():
    try:
        
        print("Erro ao baixar definições do Firebase. Usando o ultimo arquivo de configuração local...")
        
        global notification_method, time_to_act, minutes_waiting_to_restart, day_of_week_to_restart 
    
        with open(firebase_local_json_path) as json_data_file:
            data = json.load(json_data_file)
       
        notification_method = data["CONFIGURATION"]["SCRIPTS"]["AutoRestartBroker"]["NotificationMethod"]
        time_to_act = str(data["CONFIGURATION"]["SCRIPTS"]["AutoRestartBroker"]["TimeToAct"]).split(",")
        minutes_waiting_to_restart = int(data["CONFIGURATION"]["SCRIPTS"]["AutoRestartBroker"]["MinutesWaitingToRestart"])
        day_of_week_to_restart = data["CONFIGURATION"]["SCRIPTS"]["AutoRestartBroker"]["DayOfWeekToRestart"]

    except Exception as e:
        print("Ocorreu um erro no Metodo load_config_local() {}".format(e))


def check_time():
    while True:
        try:
        
            now = datetime.now()
            
            current_time = now.strftime("%H:%M:%S")
            current_weekday = now.strftime("%A")
        
            print("Checking current day and time: {} of {}".format(current_time, current_weekday))
            
            if current_time in time_to_act and current_weekday.upper() == day_of_week_to_restart.upper():
                              
                mensagem = "Raspberry será reiniciado em {} minutos, e todos os logs serão deletados. \nAguardando {} minuto(s) para reiniciar.".format(minutes_waiting_to_restart, minutes_waiting_to_restart)
                
                os.system("notify-send 'Home Automation' '{}'".format(mensagem))
                enviar_notificacao(mensagem)
                
                time.sleep(minutes_waiting_to_restart * 60)
                
                delete_old_logs()
                restart()
                
            time.sleep(1)
        
        except Exception as e:
            print("Ocorreu um erro no Metodo check_time() {}".format(e))


def enviar_notificacao(mensagem):
    try:
          
        response = send_notification(mensagem, notification_method, firebase_obj)
             
        print("StatusCode: {}, Reason: {}".format(response.status_code, response.reason))
             
    except Exception as e:
        print("Ocorreu um erro no Metodo enviar_notificacao() {}".format(e))


def delete_old_logs():
    try:
        
        print("Deletando logs antigos antes do Reboot...")
        os.system("notify-send 'Home Automation' 'Deletando logs antigos antes do Reboot...'")
        
        os.system("sudo rm -rf {}*".format(log_path_to_delete))
        
        print("Logs antigos deletados!")
        os.system("notify-send 'Home Automation' 'Logs antigos deletados!'")
        
    except Exception as e:
        print("Ocorreu um erro no Metodo delete_old_logs() {}".format(e))


def restart():
    try:

        os.system("notify-send 'Home Automation' 'Reiniciando Raspberry'")
        os.system("sudo shutdown -r now")
        
    except Exception as e:
        print("Ocorreu um erro no Metodo restart() {}".format(e))
       
try:
    
    print("Iniciando script autoRestartBroker.py")   
    os.system("notify-send 'Home Automation' 'Iniciando script autoRestartBroker.py'")
    
    initialize_firebase()    
    load_config()       
    check_time()
               
except KeyboardInterrupt:
    
    print ("\nCtrl+C pressionado, encerrando a aplicacao...")
    sys.exit(0)
