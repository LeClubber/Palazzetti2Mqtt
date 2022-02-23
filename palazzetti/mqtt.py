#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Jérémy BRAUD

import json
import paho.mqtt.client as mqtt
import requests
from const import Constantes
from time import sleep
from threading import Thread

# MQTT
class Mqtt2Palazzetti(Thread):
    """ Thread chargé de la connexion au broker MQTT """

    def __init__(self):
        Thread.__init__(self)

    def on_connect(self, client, userdata, flags, rc):
        """ 
        Abonnement aux topics souhaités :
        - Mode
        - Hold (puissance)
        - Temperature
        - Fan
        """
        affichage = "Connected to MQTT with result code " + str(rc)
        print(affichage)
        topic = Constantes.mqttTopic + "/mode/set"
        client.subscribe(topic)
        topic = Constantes.mqttTopic + "/hold/set"
        client.subscribe(topic)
        topic = Constantes.mqttTopic + "/temperature/set"
        client.subscribe(topic)
        topic = Constantes.mqttTopic + "/fan/set"
        client.subscribe(topic)

    def on_message(self, client, userdata, msg):
        """ Traitement du message recu """
        urlPalazzetti = 'http://' + Constantes.palazzettiHost + "/cgi-bin/sendmsg.lua?cmd="
        topic = str(msg.topic)
        payload = str(msg.payload, encoding="utf-8")

        if topic.find("mode") != -1 :
            # Gestion de l'allumage
            if "heat" == payload.lower():
                urlPalazzetti += "CMD+ON"
            else:
                urlPalazzetti += "CMD+OFF"
        elif topic.find("hold") != -1 :
            # Gestion de la puissance
            urlPalazzetti += "SET+POWR+" + payload
        elif topic.find("temperature") != -1 :
            # Gestion de la température de consigne
            urlPalazzetti += "SET+SETP+" + payload.replace(".0", "")
        elif topic.find("fan") != -1 :
            # Gestion du ventilateur
            urlPalazzetti += "SET+RFAN+"
            if "auto" == payload.lower():
                urlPalazzetti += "7"
            elif "high" == payload.lower():
                urlPalazzetti += "6"
            elif "off" == payload.lower():
                urlPalazzetti += "0"
            else:
                urlPalazzetti += payload

        # Appel de l'API
        requests.get(urlPalazzetti)

    def run(self):
        """ Démarrage du service MQTT """
        client = mqtt.Client()
        client.on_connect = self.on_connect
        client.on_message = self.on_message
        client.connect(Constantes.mqttHost, Constantes.mqttPort, 60)
        client.loop_forever()

class Mqtt():
    
    @staticmethod
    def publish(topic, playload, retain=True):
        """ Publication des messages MQTT """
        client = mqtt.Client()
        client.connect(Constantes.mqttHost, Constantes.mqttPort, 60)
        client.publish(topic, playload, retain=retain)
        client.disconnect()

    @staticmethod
    def mqtt2palazzetti():
        mqtt2palazzetti = Mqtt2Palazzetti()
        mqtt2palazzetti.start()

    @staticmethod
    def palazzetti2mqtt():

        # Trmps entre chaque pull >= 2
        pullTime = Constantes.palazzettiPullStatus
        if pullTime < 2:
            pullTime = 2

        # Boucle infinie pour récupérer les différentes valeurs
        while True:
            palazzetti2mqtt = Palazzetti2Mqtt()
            palazzetti2mqtt.start()

            # On met en pause le traitement
            sleep(pullTime)

class Palazzetti2Mqtt(Thread):

    def __init__(self):
        Thread.__init__(self)

    def getTopic(self, typeInfo, mode='state'):
        """ Construit le topic """
        return Constantes.mqttTopic + "/" + typeInfo + "/" + mode

    def run(self):

        url = "http://" + Constantes.palazzettiHost + "/cgi-bin/sendmsg.lua?cmd=GET+ALLS"
        req = requests.get(url)
        jsonStatus = json.loads(req.text)

        # Room temp
        topic = self.getTopic('temperature', "current")
        payload = str(jsonStatus['DATA']['T1'])
        Mqtt.publish(topic, payload)

        # Temp set
        topic = self.getTopic('temperature')
        payload = str(jsonStatus['DATA']['SETP']) + ".0"
        Mqtt.publish(topic, payload)

        # Power
        topic = self.getTopic('hold')
        payload = str(jsonStatus['DATA']['PWR'])
        Mqtt.publish(topic, payload)

        # Fan
        topic = self.getTopic('fan')
        payload = str(jsonStatus['DATA']['F2L'])
        if "0" == payload:
            payload = "Off"
        elif "6" == payload:
            payload = "High"
        elif "7" == payload:
            payload = "Auto"
        Mqtt.publish(topic, payload)

        # Mode
        topic = self.getTopic('mode')
        status = str(jsonStatus['DATA']['STATUS'])
        if "0" == status :
            payload = "off"
        else:
            payload = "heat"
        Mqtt.publish(topic, payload)
        topic = self.getTopic('action')
        if "0" == status :
            payload = "off"
        elif "6" == status :
            payload = "cooling"
        else:
            payload = "heating"
        Mqtt.publish(topic, payload)
        
        
