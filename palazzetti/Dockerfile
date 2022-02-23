FROM python:3-alpine

ENV HTTP_PORT 8080
ENV MQTT_PORT 1883
ENV MQTT_HOST mqtt
ENV MQTT_TOPIC palazzetti
ENV PALAZZETTI_HOST 192.168.1.1
ENV PALAZZETTI_PULL_STATUS 5
WORKDIR /usr/src/palazzetti

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "-u", "server.py"]