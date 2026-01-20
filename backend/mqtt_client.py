# backend/mqtt_client.py
import os
import paho.mqtt.client as mqtt
from dotenv import load_dotenv

load_dotenv()

BROKER = os.getenv("MQTT_BROKER", "localhost")
PORT = int(os.getenv("MQTT_PORT", 1883))
USER = os.getenv("MQTT_USER")
PASS = os.getenv("MQTT_PASS")

TOPIC_NAME = "dnd/encounter/active/name"
TOPIC_HP   = "dnd/encounter/active/hp"

mqttc = mqtt.Client(client_id="dnd_backend")
mqttc.username_pw_set(USER, PASS)

def on_connect(client, userdata, flags, rc):
    print(f"MQTT connected ({rc})")

mqttc.on_connect = on_connect
mqttc.connect(BROKER, PORT, 60)
mqttc.loop_start()

def publish_active(name: str, hp: int):
    mqttc.publish(TOPIC_NAME, name, retain=True)
    mqttc.publish(TOPIC_HP, str(hp), retain=True)
