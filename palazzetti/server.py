#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Jérémy BRAUD

from const import Constantes
from mqtt2palazzetti import Mqtt2Palazzetti
from palazzetti2mqtt import Palazzetti2Mqtt
from time import sleep

# Envoie des ordres à Palazzetti
mqtt2palazzetti = Mqtt2Palazzetti()
mqtt2palazzetti.start()

# Temps entre chaque pull >= 2
pullTime = Constantes.palazzettiPullStatus
if pullTime < 2:
    pullTime = 2

Palazzetti2Mqtt.init()
# Boucle infinie pour récupérer les différentes valeurs
while True:
    palazzetti2mqtt = Palazzetti2Mqtt()
    palazzetti2mqtt.start()

    # On met en pause le traitement
    sleep(pullTime)