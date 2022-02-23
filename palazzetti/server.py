#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Jérémy BRAUD

from const import Constantes
from mqtt import Mqtt

# Lancement des threads
Mqtt.mqtt2palazzetti()
Mqtt.palazzetti2mqtt()

