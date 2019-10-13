from config_hub import *
import csv
import paho.mqtt.client as mqtt
import json

# Global variables
nodes: dict = {}


class Sensor():
    """Define a class for entry files"""

    def __init__(self, entry: dict):
        self.name = ""
        self.unit = entry["unit"]
        self.previous_raw = 0
        self.average = entry["average"]
        self.std = entry["std"]


def is_outlier(sensor: Sensor, value: float):
    if (sensor.average is None or sensor.std is None):
        print("Data missing for an outlier detection")
        return False
    return (value > sensor.average + nb_std * sensor.std) or (value < sensor.average - nb_std * sensor.std)


def on_connect(client: mqtt.Client, userdata, flags, rc):
    print("Connected to broker at %s" % broker_addr)
    client.subscribe("/nodes")


def on_message(client: mqtt.Client, userdata, message: mqtt.MQTTMessage):
    global nodes
    if (message.topic == "/nodes"):
        # Message announcing a node
        node_topic: str = message.payload.decode()
        node_name = node_topic.split("/")[2]
        if (node_name not in nodes):
            print("New node detected, subscribing to it with topic %s" %
                  node_topic)
            client.subscribe(node_topic + "/#")
            nodes[node_name] = {}
    else:
        # Message announcing a sensor measurement
        node_name: str = message.topic.split("/")[2]
        sensor_name: str = message.topic.split("/")[3]
        message_json = json.loads(message.payload.decode("utf-8"))
        if (sensor_name not in nodes[node_name]):
            print("Found new sensor (%s) for the node" % sensor_name)
            sensor: Sensor = Sensor(message_json)
            sensor.name = sensor_name
            nodes[node_name][sensor_name] = sensor
        sensor: Sensor = nodes[node_name][sensor_name]
        value = float(message_json["value"])
        if (is_outlier(sensor, value=value)):
            print("Outlier detected: %s (value: %.02f, average: %.02f, std: %.02f)" %
                  (sensor.name, value, sensor.average, sensor.std))


def on_log(client, userdata, level, buf):
    # print("Log: %s" % buf)
    pass


client = mqtt.Client(client_name)
client.on_connect = on_connect
client.on_log = on_log
client.on_message = on_message
client.connect(broker_addr)
client.loop_forever()
