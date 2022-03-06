#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Jérémy BRAUD

import json
import requests
import paho.mqtt.client as mqtt
from const import Constantes
from threading import Thread

class Palazzetti2Mqtt(Thread):

    @staticmethod
    def publish(topic, playload, retain=True):
        """ Publication des messages MQTT """
        client = mqtt.Client()
        client.connect(Constantes.mqttHost, Constantes.mqttPort, 60)
        client.publish(topic, playload, retain=retain)
        client.disconnect()

    @staticmethod
    def init():
        """ Publication de la config pour discovery """
        topic = Constantes.mqttTopic + "/climate/palazzetti/config"
        payload = '{'
        payload += '"name":"Palazzetti",'
        payload += '"mode_command_topic":"' + Constantes.mqttTopic + '/climate/palazzetti/modeCmd",'
        payload += '"mode_state_topic":"' + Constantes.mqttTopic + '/climate/palazzetti/state",'
        payload += '"mode_state_template":"{{ value_json.mode}}",'
        payload += '"preset_mode_command_topic":"' + Constantes.mqttTopic + '/climate/palazzetti/presetCmd",'
        payload += '"preset_mode_state_topic":"' + Constantes.mqttTopic + '/climate/palazzetti/state",'
        payload += '"preset_mode_value_template":"{{ value_json.preset}}",'
        payload += '"temperature_command_topic":"' + Constantes.mqttTopic + '/climate/palazzetti/tempCmd",'
        payload += '"temperature_state_topic":"' + Constantes.mqttTopic + '/climate/palazzetti/state",'
        payload += '"temperature_state_template":"{{ value_json.target_temp}}",'
        payload += '"current_temperature_topic":"' + Constantes.mqttTopic + '/climate/palazzetti/state",'
        payload += '"current_temperature_template":"{{ value_json.current_temp}}",'
        payload += '"fan_mode_command_topic":"' + Constantes.mqttTopic + '/climate/palazzetti/fanCmd",'
        payload += '"fan_mode_state_topic":"' + Constantes.mqttTopic + '/climate/palazzetti/state",'
        payload += '"fan_mode_state_template":"{{ value_json.fan_mode}}",'
        payload += '"action_topic":"' + Constantes.mqttTopic + '/climate/palazzetti/state",'
        payload += '"action_template":"{{ value_json.action}}",'
        payload += '"min_temp":"18",'
        payload += '"max_temp":"28",'
        payload += '"modes":["off", "heat"],'
        payload += '"preset_modes":["1", "2", "3", "4", "5"],'
        payload += '"fan_modes":["Off", "1", "2", "3", "4", "5", "High", "Auto"]'
        payload += '}'
        Palazzetti2Mqtt.publish(topic, payload)

    def __init__(self):
        Thread.__init__(self)

    def run(self):

        url = "http://" + Constantes.palazzettiHost + "/cgi-bin/sendmsg.lua?cmd=GET+ALLS"
        req = requests.get(url)
        jsonStatus = json.loads(req.text)

        topic = Constantes.mqttTopic + '/climate/palazzetti/state'
        payload = '{'

        # Room temp
        payload += '"current_temp":"' + str(jsonStatus['DATA']['T1']) + '",'
        # Temp set
        payload += '"target_temp":"' + str(jsonStatus['DATA']['SETP']) + '.0",'
        # Power
        payload += '"preset":"' + str(jsonStatus['DATA']['PWR']) + '",'

        # Fan
        fanState = str(jsonStatus['DATA']['F2L'])
        if "0" == fanState:
            fanState = "Off"
        elif "6" == fanState:
            fanState = "High"
        elif "7" == fanState:
            fanState = "Auto"
        payload += '"fan_mode":"' + fanState + '",'

        # Mode
        status = str(jsonStatus['DATA']['STATUS'])
        if "0" == status :
            mode = "off"
        else:
            mode = "heat"
        payload += '"mode":"' + mode + '",'
        if "0" == status :
            action = "off"
        elif "6" == status :
            action = "cooling"
        else:
            action = "heating"
        payload += '"action":"' + action + '"'
        payload += '}'

        Palazzetti2Mqtt.publish(topic, payload)
