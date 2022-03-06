#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Jérémy BRAUD

import paho.mqtt.client as mqtt
import requests
from const import Constantes
from threading import Thread

class Mqtt2Palazzetti(Thread):
    """ Thread chargé de la connexion au broker MQTT """

    def __init__(self):
        Thread.__init__(self)

    def on_connect(self, client, userdata, flags, rc):
        """ 
        Abonnement aux topics souhaités :
        - Mode
        - Preset (puissance)
        - Temperature
        - Fan
        """
        affichage = "Connected to MQTT with result code " + str(rc)
        print(affichage)
        topic = Constantes.mqttTopic + '/climate/palazzetti/modeCmd'
        client.subscribe(topic)
        topic = Constantes.mqttTopic + '/climate/palazzetti/presetCmd'
        client.subscribe(topic)
        topic = Constantes.mqttTopic + '/climate/palazzetti/tempCmd'
        client.subscribe(topic)
        topic = Constantes.mqttTopic + '/climate/palazzetti/fanCmd'
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
        elif topic.find("preset") != -1 :
            # Gestion de la puissance
            if "none" == payload.lower():
                payload = "1"
            urlPalazzetti += "SET+POWR+" + payload
        elif topic.find("temp") != -1 :
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


