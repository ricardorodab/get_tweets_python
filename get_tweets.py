## @package twitter
# 
#  Biblioteca para poder observar continuamente modificacions
#  de un usuario de twitter.
#
#  Se genera cada vez que se modifique un timeline de twitter un archivo
#  de texto para dar seguimiento en tiempo real a los updates de un
#  usuario.

## @name Luis Edgar Rodriguez Abreu
## @date Nov 15, 2017
##
import os
import sys
import time
import twitter
import threading
from threading import Thread
import ConfigParser
import datetime

tweet_saved = None
tweet_new = None
perfil_nombre = None
contador_peticiones = 0

## Funcion que crea la conexion con el servidor de twitter..
def get_conexion():
    global perfil_nombre
    # ConfigParser nos sirve para parsear archivos tipo cfg.
    config_parser = ConfigParser.RawConfigParser()
    # Obtenemos el nombre del directorio actual.
    cur_path = os.path.dirname(__file__)
    config_file_path = 'keys_file.cfg'
    abs_file_path = os.path.join(cur_path, config_file_path)
    # Leemos el archivo 'directorio_actual+archivo.cfg'
    config_parser.read(abs_file_path)

    # Buscamos los valores de las instancias de categoria KEY:
    cons_key = config_parser.get('KEYS', 'consumer_key')
    cons_secret = config_parser.get('KEYS', 'consumer_secret')
    access_key = config_parser.get('KEYS', 'access_token_key')
    access_secret = config_parser.get('KEYS', 'access_token_secret')

    # Buscamos el valor de las instancias de la categoria USUARIO:

    perfil_nombre = config_parser.get('USUARIO', 'nombre')
    
    # Se instancia el objeto Api:
    api = twitter.Api(consumer_key=cons_key,
                      consumer_secret=cons_secret,
                      access_token_key=access_key,
                      access_token_secret=access_secret)
    return api

 ## Imprime y almacen los cambios de un tweet y una fecha.
 #  @tweet - Es el tweet a imprimir/guardar.
 #  @fecha - Es la fecha en la que se imprime el cambio.
def imprime_cambios(tweet, fecha):
    salida = open(fecha, 'w')
    tweet_str = u' '.join(tweet).encode('utf-8')
    salida.write(tweet_str)
    salida.close()
    print "Se envio el tweet: "+ tweet_str + " - El dia: " + fecha
    

## Funcion que hace la chamba:
#  Obtiene el valor del timeline y lo compara con un estado anterior:
#  Si el estado muta, entonces significa que existe un nuevo tweet.
#  
#  @conexion - Es el enlace a el servidor de twitter.
#  @nombre - Es el nombre del usuario que se desea monitorear.
def monitorea_perfil(conexion, nombre):
    global contador_peticiones
    contador_peticiones = contador_peticiones + 1
    if contador_peticiones == 15:
        contador_peticiones = 0
        monitorea_perfil(get_conexion(),nombre)
    global tweet_new
    global tweet_saved
    tweet_new = api.GetUserTimeline(screen_name=nombre)
    if tweet_saved == None:
        tweet_saved = tweet_new 
    if not (tweet_new == tweet_saved):
        fecha_actual = str(datetime.datetime.now())
        imprime_cambios(tweet_new[0].text, fecha_actual)
        tweet_saved = tweet_new
    # Esperamos 5 segundos:
    time.sleep(61)
    # Volvemos a llamar a la funcion "while(true)"
    monitorea_perfil(conexion, nombre)
    


 ## Crea e inicia un Thread que empiece el monitoreo del perfil.
 #  @conexion - Es el enlace a el servidor de twitter.
 #  @nombre - Es el nombre del usuario que se desea monitorear.
def inicia_monitoreo(conexion, nombre):
     hilo = threading.Thread(target=monitorea_perfil(conexion,nombre))
     hilo.setDeamon(True)
     hilo.start()


if __name__ == "__main__":
    try:
        api = get_conexion()
        inicia_monitoreo(api, perfil_nombre)
    except (KeyboardInterrupt, SystemExit):
        print "El programa es interrumpido por el usuario"
        #monitorea_perfil(api, perfil_nombre)
