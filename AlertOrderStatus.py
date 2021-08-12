#!/usr/bin/env python3

# Script que obtem o codigo e informações de rastreio de um objeto cadastrado no firebase, e compara com o ultimo status disponivel nos correios (via API pyrastreio).
# Caso tenha alguma mudança, o status do objeto é atualizado no firebase, e uma notificação via OneSignal ou Telegram é enviada aos usuarios.

# NAO TEM SENTIDO EXECUTAR OFFLINE, LOGO NAO PRECISA LER CONFIGURAÇÕES DE JSON LOCALMENTE EM CASO DE FALHA DE COMUNICAÇÃO COM FIREBASE

import sys
import os
import logging
import time
import json

from firebase_admin import initialize_app
from firebase_admin import credentials
from firebase_admin import db

from retry import retry
from pyrastreio import correios
from notification_helper import send_notification

firebase_app_name = 'home-automation-fd418-default-rtdb'
firebase_admin_sdk_json_path = '/home/pi/Scripts/python/config/home-automation-fd418-firebase-adminsdk-6552s-037f34a75e.json'

firebase_obj = ""

notification_method = ""
notification_method_path = "/CONFIGURATION/SCRIPTS/AlertOrderStatus/NotificationMethod/"
order_list_path = "/CONFIGURATION/SCRIPTS/AlertOrderStatus/OrderList/"
 
logging.basicConfig(filename='/home/pi/Scripts/python/logs/alertOrderStatus.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(funcName)s => %(message)s')

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
        notification_method = ref.get()
    
    except Exception as e:
        logging.exception("Ocorreu um erro no Metodo load_config() {}".format(e))
        sys.exit(0)
        

@retry(Exception, delay=10*60, tries=-1)
def get_order_info():
    while True:        
        try:
            
            print("Realizando a consulta dos codigos de rastreio cadastrados no firebase...")
            logging.debug("Realizando a consulta dos codigos de rastreio cadastrados no firebase...");
             
            ref = db.reference('/CONFIGURATION/SCRIPTS/AlertOrderStatus/OrderList/', app= firebase_obj) 
            firebaseResponse = ref.get()
            
            if isinstance(firebaseResponse, dict):
    
                obj_list = list(firebaseResponse.items())
                    
                for item in obj_list:
                
                    codigoObjeto = item[0]
                    statusObjeto = item[1]
                
                    correiosResponse = correios(codigoObjeto)
                                 
                    print(correiosResponse)        
                                 
                    #if correiosResponse == []:
                    #    break
                    
                    if not len(correiosResponse):
                        continue
                    
                    statusObjetoCorreios = correiosResponse[0]

                    #DEBUG
                    #print("Debug: firebase: {}".format(statusObjeto))
                    #print("Debug: correios: {}".format(statusObjetoCorreios))

                    if statusObjeto != statusObjetoCorreios:
                    
                        print("O objeto {} teve atualização de status: \n{}".format(codigoObjeto, statusObjetoCorreios["mensagem"]))
                        logging.debug("O objeto {} teve atualização de status: \n{}".format(codigoObjeto, statusObjetoCorreios["mensagem"]))
                                         
                        enviar_notificacao("O objeto {} teve atualização de status: \n{}".format(codigoObjeto, statusObjetoCorreios["mensagem"]))
                        
                        update_order_status(codigoObjeto, correiosResponse[0])                  
                    
                    else:
                        print("Sem mudança de status para o objeto {}".format(codigoObjeto))
                        logging.debug("Sem mudança de status para o objeto {}".format(codigoObjeto))
                
                    time.sleep(5)    
            
            print("Aguardando proxima consulta...")
            logging.debug("Aguardando proxima consulta...")
            
            time.sleep(1800) # 30 minutos
            
        except Exception as e: 
            logging.exception("Ocorreu um erro no Metodo get_order_info() {}".format(e))


def enviar_notificacao(mensagem):
    try:
        
        os.system("notify-send 'Home Automation' '{}'".format(mensagem))
        logging.debug(mensagem);
        
        response = send_notification(mensagem, notification_method, firebase_obj)
                
        logging.debug("StatusCode: {}, Reason: {}".format(response.status_code, response.reason))
             
    except Exception as e:
        logging.exception("Ocorreu um erro no Metodo enviar_notificacao() {}".format(e))


@retry(Exception, delay=10*60, tries=-1)
def update_order_status(codigoObjeto, statusObjetoCorreios):  
    try:

        logging.debug("Atualizando Status da Encomenda no Firebase");
        
        ref = db.reference('{}{}'.format(order_list_path, codigoObjeto), app= firebase_obj)
        ref.set(statusObjetoCorreios)
             
    except Exception as e: 
        logging.exception("Ocorreu um erro no Metodo update_order_status() {}".format(e))

try:
    print("Iniciando script alertOrderStatus.py")
    logging.debug("Iniciando script alertOrderStatus.py")
    
    os.system("notify-send 'Home Automation' 'Iniciando script alertOrderStatus.py'")
          
    initialize_firebase()
    
    load_config()
    get_order_info()
                   
except KeyboardInterrupt:
    
    print ("\nCtrl+C pressionado, encerrando a aplicacao...")
    logging.debug("\nCtrl+C pressionado, encerrando a aplicacao...")
    sys.exit(0)


