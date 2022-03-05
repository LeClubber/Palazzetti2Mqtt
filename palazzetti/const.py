#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Jérémy BRAUD

import os

class Constantes():
    
    # Recuperation des variables d'environnement
    mqttPort = int(os.getenv('MQTT_PORT', 1883))
    mqttHost = os.getenv('MQTT_HOST', "localhost")
    mqttTopic = os.getenv('MQTT_TOPIC', "homeassistant")
    mqttUser = os.getenv('MQTT_USER')
    mqttPassword = os.getenv('MQTT_PASSWORD')
    palazzettiHost = os.getenv("PALAZZETTI_HOST", "192.168.1.1")
    palazzettiPullStatus = int(os.getenv("PALAZZETTI_PULL_STATUS", 5))
