from config_hub import *
import csv
import paho.mqtt.client as mqtt
import json
import ssl
from sql import session, Node, Measurement, Event, Sensor

# Global variables
nodes: dict = {}


class SensorJSON():
    """Define a class for entry files"""

    def __init__(self, entry: dict):
        self.name = ""
        self.unit = entry["unit"]
        # self.previous_raw = 0
        self.average = entry["average"]
        self.std = entry["std"]
        self.ts = entry["ts"]


def is_outlier(sensor: SensorJSON, value: float):
    if (sensor.average is None or sensor.std is None):
        # print("Data missing for an outlier detection")
        return False
    return (value > sensor.average + nb_std * sensor.std) or (value < sensor.average - nb_std * sensor.std)


def update_sample_period(client: mqtt.Client, node_name: str, new_period: float):
    print("Changing the sample period of node %s to %0.1f" %
          (node_name, new_period))
    client.publish(node_name + "/sample_period", str(new_period))


def add_node(name: str):
    oldNode = session.query(Node.name).filter_by(name=name).all()
    if len(oldNode) == 0:
        newNode = Node(name=name)
        session.add(newNode)
        session.commit()
        # session.flush()


def add_event(ts: float, ev_type: str, node: int):
    newEvent = Event(timestamp=ts, event_type=ev_type, node_id=node)
    session.add(newEvent)
    session.commit()
    # session.flush()


def add_measurement(ts: float, value: float, sensor: int, node: int):
    newMeasurement = Measurement(
        timestamp=ts, value=value, sensor_id=sensor, node_id=node)
    session.add(newMeasurement)
    session.commit()
    # session.flush()


def add_sensor(name: str, unit: str, avg: float, std: float, node: int):
    oldSensor = session.query(Sensor).filter_by(node_id=node, name=name).all()
    if len(oldSensor) == 0:
        newSensor = Sensor(name=name, unit=unit, average=avg,
                           std=std, node_id=node)
        session.add(newSensor)
        session.commit()
        # session.flush()


def get_node_id(name: str):
    node = session.query(Node.id).filter_by(name=name).all()
    if len(node) == 0:
        return 0
    return node[0].id


def get_sensor_id(name: str, node: str):
    node_id = session.query(Node.id).filter_by(name=node).all()[0].id
    sensor = session.query(Sensor.id).filter_by(
        name=name, node_id=node_id).all()
    if len(sensor) == 0:
        return 0
    return sensor[0].id


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
            add_node(node_name)
    else:
        # Message announcing a sensor measurement
        node_name: str = message.topic.split("/")[2]
        sensor_name: str = message.topic.split("/")[3]
        message_json = json.loads(message.payload.decode("utf-8"))
        # try:
        node_id = get_node_id(node_name)
        # except:
        #     pass
        if (sensor_name not in nodes[node_name]):
            print("Found new sensor (%s) for the node" % sensor_name)
            sensor: SensorJSON = SensorJSON(message_json)
            sensor.name = sensor_name
            nodes[node_name][sensor_name] = sensor
            add_sensor(sensor_name, sensor.unit,
                       sensor.average, sensor.std, node_id)
        sensor_id: int = get_sensor_id(sensor_name, node_name)
        sensor: SensorJSON = nodes[node_name][sensor_name]
        ts: float = float(message_json["ts"])
        value = float(message_json["value"])
        add_measurement(ts, value, sensor_id, node_id)
        if (is_outlier(sensor, value=value)):
            print("Outlier detected: %s (value: %.02f, average: %.02f, std: %.02f)" %
                  (sensor.name, value, sensor.average, sensor.std))


def on_log(client, userdata, level, buf):
    print("Log: %s" % (buf))
    pass


# Create and connect the MQTT client
client = mqtt.Client(client_name)
client.tls_set(ca_certs=ca_cert,
               certfile=certfile,
               keyfile=keyfile)
client.on_connect = on_connect
client.on_log = on_log
client.on_message = on_message
client.connect(broker_addr, port=8883)
client.loop_forever()
