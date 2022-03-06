# Palazzetti2Mqtt

Outil de conversion de l'API du Palazzetti (Connection Box) vers MQTT et inversement pour Home Assistant.

## Déploiement

Il vous faut :

- Home-Assistant (en même temps, vous êtes surtout là pour lui non?)
- Un brocker (serveur) MQTT (non sécurisé, sans login/mot de passe pour l'instant)
- Le service Palazzetti2Mqtt

Il y a deux solutions pour déployer ce service :

- Docker (recommandé)
- Exécuter le script python directement

### Docker

Je préfère cette solution car elle encapsule le processus, contient toutes les dépendances  et facilite le déploiement.

Le service peut être démarré grâce à la commande suivante :

``` sh
docker run -d --name palzzzetti \
    -e PALAZZETTI_HOST=192.168.1.1 \
    -e PALAZZETTI_PULL_STATUS=5 \
    leclubber/palazzetti2mqtt
```

Ou en docker-compose (recommandé) :

``` yaml
version: '3'
services:
  palazzetti:
    container_name: palazzetti
    image: leclubber/palazzetti2mqtt
    privileged: true
    restart: always
    environment:
      - MQTT_PORT=1883
      - MQTT_HOST=mqtt
      - MQTT_TOPIC=homeassistant
      - PALAZZETTI_HOST=192.168.1.21
      - PALAZZETTI_PULL_STATUS=5
```

Les variables d'environnement sont optionnelles, elles possèdent une valeur par défaut. Ces variables d'environnement sont les suivantes :

- MQTT_PORT (1883 par défaut)
- MQTT_HOST (mqtt par défaut)
- MQTT_TOPIC (homeassistant par défaut)
- PALAZZETTI_HOST (192.168.1.1 par défaut)
- PALAZZETTI_PULL_STATUS (5s par défaut)

Un fichier [docker-compose.yml](docker-compose.yml) est disponible pour exemple, avec toutes les variables d'environnement ainsi que les services homeassistant et mqtt.

Une fois votre fichier docker-compose.yml réalisé, il faut lancer la commande suivante pour démarrer le ou les services configurés :

``` sh
docker-compose up -d
```

### Python

Il faut récupérer le contenu du dossier [palazzetti](palazzetti) et le mettre sur votre futur serveur.

Les variables d'environnement sont optionnelles, elles possèdent une valeur par défaut (voir section Docker).
Chaque variable sera définie de cette manière :

``` sh
export ENV_VAR=valeur
```

Exécuter ensuite les lignes suivantes :

``` sh
pip install -r requirements.txt
chmod +x *.py
./server.py
```

## Configuration de Home-Assistant

Le poêle dans Home-Assistant fonctionne avec le discovery de MQTT. Il suffit de s'abonner dans Home-Assistant au canal souhaité ("homeassistant" par défaut).

**Optionnel :** On peut également le déclarer via le fichier de configuration [configuration.yaml](configuration.yaml). Il faut ajouter un module "climate" de cette fçon :
``` yaml
climate:
  - platform: mqtt
    name: Palazzetti
    unique_id: palazzetti
    modes:
      - "off"
      - "heat"
    hold_modes:
      - "1"
      - "2"
      - "3"
      - "4"
      - "5"
    fan_modes:
      - "Off"
      - "1"
      - "2"
      - "3"
      - "4"
      - "5"
      - "High"
      - "Auto"
    mode_command_topic: "homeassistant/climate/palazzetti/modeCmd"
    mode_state_topic: "homeassistant/climate/palazzetti/state"
    mode_state_template: "{{ value_json.mode}}"
    hold_command_topic: "homeassistant/hold/set"
    hold_state_topic: "homeassistant/climate/palazzetti/state"
    hold_state_topic: "{{ value_json.hold}}"
    temperature_command_topic: "homeassistant/temperature/set"
    temperature_state_topic: "homeassistant/climate/palazzetti/state"
    temperature_state_template: "{{ value_json.target_temp}}"
    current_temperature_topic: "homeassistant/climate/palazzetti/state"
    current_temperature_template: "{{ value_json.current_temp}}"
    fan_mode_command_topic: "homeassistant/fan/set"
    fan_mode_state_topic: "homeassistant/climate/palazzetti/state"
    fan_mode_state_template: "{{ value_json.fan_mode}}"
    action_topic: "homeassistant/climate/palazzetti/state"
    action_template: "{{ value_json.action}}"
    max_temp: 28
    min_temp: 18
```

Vous pourrez alors :
- Allumer et éteindre le poêle
- Modifier la puissance du feu (Préréglage dans HA)
- Modifier le niveau de ventilation
- Avoir la température actuelle
- Modifie la température cible

## Bug connus
- Le préréglage "Aucun" met la puissance à 1 (il n'existe pas de puissance 0 sur le Palazzetti)
- La gestion des codes status de Palazzetti n'est pas assez fine, et il est impossible d'afficher une erreur en particulier dans Home-Assistant

## Todo list

- [x] Refactoring en classe Python
- [x] Initialisation des config dans MQTT
- [x] Documentation
- [x] Publier image Docker en multiple arch
- [x] Discovery MQTT
- [x] Changer la commande "hold" qui est dépréciée
- [x] Utilisation d'un login/mot de passe pour le broker MQTT
- [ ] Attente du serveur MQTT si non disponible
- [ ] Tester les paramètres et gestion d'erreur
