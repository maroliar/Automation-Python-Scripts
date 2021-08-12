#!/usr/bin/env python3

# Script que envia uma push notification via OneSignal ou Telegram, mediante a variação de valor do Bitcoin obtido da api MercadoBitcoin.

# NAO TEM SENTIDO EXECUTAR OFFLINE, LOGO NAO PRECISA LER CONFIGURAÇÕES DE JSON LOCALMENTE EM CASO DE FALHA DE COMUNICAÇÃO COM FIREBASE

import sys
import time
import os
import json
import logging
import requests

from firebase_admin import initialize_app
from firebase_admin import credentials
from firebase_admin import db

from mercado_bitcoin import DataAPI
from retry import retry
from notification_helper import send_notification

firebase_app_name = 'home-automation-fd418-default-rtdb'
firebase_admin_sdk_json_path = '/home/pi/Scripts/python/config/home-automation-fd418-firebase-adminsdk-6552s-037f34a75e.json'

firebase_obj = ""

notification_method = ""
notification_method_path = "/CONFIGURATION/SCRIPTS/AlertMercadoBitcoinPrice/NotificationMethod/"

initial_min_price_alert = 0.
initial_min_price_alert_path = "/CONFIGURATION/SCRIPTS/AlertMercadoBitcoinPrice/InitialMinPriceAlert/"

initial_max_price_alert = 0.
initial_max_price_alert_path = "/CONFIGURATION/SCRIPTS/AlertMercadoBitcoinPrice/InitialMaxPriceAlert/"

round_alert_time = 0
round_alert_time_path = "/CONFIGURATION/SCRIPTS/AlertMercadoBitcoinPrice/AlertTimeInMinutes/"

current_round = 1

logging.basicConfig(filename='/home/pi/Scripts/python/logs/alertMercadoBitcoinPrice.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(funcName)s => %(message)s')


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
    
        global notification_method, initial_min_price_alert, initial_max_price_alert, round_alert_time
    
        ref = db.reference(notification_method_path, app= firebase_obj)
        notification_method = ref.get().replace("\"", "")
                        
        ref = db.reference(initial_min_price_alert_path, app= firebase_obj)
        initial_min_price_alert = float(ref.get().replace("\"", ""))
    
        ref = db.reference(initial_max_price_alert_path, app= firebase_obj)
        initial_max_price_alert = float(ref.get().replace("\"", ""))
    
        ref = db.reference(round_alert_time_path, app= firebase_obj)
        round_alert_time = int(ref.get().replace("\"", ""))
    
    except Exception as e:
        logging.exception("Ocorreu um erro no Metodo load_config() {}".format(e))
        sys.exit(0)
    
@retry(Exception, delay=10*60, tries=-1)
def get_bitcoin_price():
    while True:
        try:
            time.sleep(60)
                     
            global initial_min_price_alert
            global initial_max_price_alert
            global round_alert_time
            global current_round    
        
            responseMercadoBitcoin = DataAPI.ticker("BTC")

            jsonPrice = json.loads(responseMercadoBitcoin.content)
            lastPrice = float(jsonPrice["ticker"]["last"])

            print("Rodada {} de {}".format(current_round, round_alert_time))
            logging.debug("Rodada {} de {}".format(current_round, round_alert_time))

            print("Verificando preço do bitcoin... R${:.2f}".format(lastPrice))
            logging.debug("Verificando preço do bitcoin... R${:.2f}".format(lastPrice))

            if(lastPrice < initial_min_price_alert):
                initial_min_price_alert = lastPrice
                enviar_notificacao("Preço do bitcoin atingiu o menor valor pre definido! R${:.2f}".format(lastPrice))
                        
            if(lastPrice > initial_max_price_alert):
                initial_max_price_alert = lastPrice
                enviar_notificacao("Preço do bitcoin atingiu o maior valor pre definido! R${:.2f}".format(lastPrice))        
                        
            # cada rodada tem duração de 1 min, conforme time.sleep(60)

            if(current_round == round_alert_time):
                enviar_notificacao("Preço atual do bitcoin: R${:.2f}".format(lastPrice))
                current_round = 1
            else:
                current_round += 1                
                        
        except Exception as e: 
            logging.exception("Ocorreu um erro no Metodo get_bitcoin_price() {}".format(e))
  
def enviar_notificacao(mensagem):
    try:
        
        os.system("notify-send 'Home Automation' '{}'".format(mensagem))
        logging.debug(mensagem)
        
        response = send_notification(mensagem, notification_method, firebase_obj)
                
        logging.debug("StatusCode: {}, Reason: {}".format(response.status_code, response.reason))
             
    except Exception as e:
        logging.exception("Ocorreu um erro no Metodo enviar_notificacao() {}".format(e))
  
try:
    print("Iniciando script alertMercadoBitcoinPrice.py")
    logging.debug("Iniciando script alertMercadoBitcoinPrice.py")
    
    os.system("notify-send 'Home Automation' 'Iniciando script alertMercadoBitcoinPrice.py'")
     
    initialize_firebase()
    load_config()  
    get_bitcoin_price()
                   
except KeyboardInterrupt:
    
    print ("\nCtrl+C pressionado, encerrando a aplicacao...")
    logging.debug("\nCtrl+C pressionado, encerrando a aplicacao...")
    sys.exit(0)
