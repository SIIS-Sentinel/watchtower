import config_hub as cfg
import json
from typing import Dict

import paho.mqtt.client as mqtt

from bookkeeper.sql import create_sessions, Node, Measurement, Event, Sensor


class SensorJSON():
    """Define a class for entry files"""

    def __init__(self, entry: dict):
        self.name = ""
        self.unit = entry["unit"]
        # self.previous_raw = 0
        self.average = entry["average"]
        self.std = entry["std"]
        self.ts = entry["ts"]


class WatchtowerHub():
    def __init__(self):
        self.nodes: Dict[str, Dict[str, SensorJSON]] = {}
        self.node_ids: Dict[str, int] = {}
        self.sensor_ids: Dict[str] = {}

        # MQTT client
        self.client: mqtt.Client = mqtt.Client(cfg.client_name)
        self.client.tls_set(ca_certs=cfg.ca_cert,
                            certfile=cfg.certfile,
                            keyfile=cfg.keyfile)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_log = self.on_log

        # SQL session
        self.session = create_sessions(cfg.db_path)
        self.transactions_counter: int = 0
        self.max_transaction_counter: int = 50

    def on_connect(self, client: mqtt.Client, userdata, flags, rc):
        print("Watchtower: Connected to broker at %s" % cfg.broker_addr)
        client.subscribe("/nodes")
        for node in self.nodes.keys():
            topic = f"/sentinel/{node}/#"
            client.subscribe(topic)

    def on_message(self, client: mqtt.Client, userdata, message: mqtt.MQTTMessage):
        node_name: str
        if (message.topic == "/nodes"):
            # Message announcing a node
            node_topic: str = message.payload.decode()
            node_name = node_topic.split("/")[2]
            if (node_name not in self.nodes):
                print(f"Watchtower: New node detected, subscribing to it with topic {node_topic}")
                client.subscribe(node_topic + "/#")
                self.nodes[node_name] = {}
                self.add_node(node_name)
        else:
            # Message announcing a sensor measurement
            topic_split: list = message.topic.split("/")
            node_name = topic_split[2]
            sensor_name: str = topic_split[3]
            message_json = json.loads(message.payload.decode("utf-8"))
            node_id = self.get_node_id(node_name)
            sensor: SensorJSON
            if (sensor_name not in self.nodes[node_name]):
                print(f"Watchtower: Found new sensor {sensor_name} for the node {node_name}")
                sensor = SensorJSON(message_json)
                sensor.name = sensor_name
                self.nodes[node_name][sensor_name] = sensor
                self.add_sensor(sensor_name, sensor.unit,
                                sensor.average, sensor.std, node_id)
            sensor_id: int = self.get_sensor_id(sensor_name, node_name)
            sensor = self.nodes[node_name][sensor_name]
            ts: float = float(message_json["ts"])
            value = float(message_json["value"])
            self.add_measurement(ts, value, sensor_id, node_id)

    def on_log(sefl, client, userdata, level, buf):
        if level == mqtt.MQTT_LOG_WARNING:
            print("Warning: %s" % (buf))
        elif level == mqtt.MQTT_LOG_ERR:
            print("Error: %s" % (buf))

    def add_node(self, name: str):
        oldNode = self.session.query(Node.name).filter_by(name=name).all()
        if len(oldNode) == 0:
            newNode = Node(name=name)
            self.session.add(newNode)
            self.session.commit()

    def add_measurement(self, ts: float, value: float, sensor: int, node: int):
        newMeasurement = Measurement(
            timestamp=ts, value=value, sensor_id=sensor, node_id=node)
        self.session.add(newMeasurement)
        self.transactions_counter += 1
        if self.transactions_counter >= self.max_transaction_counter:
            self.session.commit()
            self.transactions_counter = 0

    def add_sensor(self, name: str, unit: str, avg: float, std: float, node: int):
        oldSensor = self.session.query(Sensor).filter_by(node_id=node, name=name).all()
        if len(oldSensor) == 0:
            newSensor = Sensor(name=name, unit=unit, average=avg,
                               std=std, node_id=node)
            self.session.add(newSensor)
            self.session.commit()

    def get_node_id(self, name: str):
        if name in self.node_ids:
            return self.node_ids[name]
        node = self.session.query(Node.id).filter_by(name=name).all()
        if len(node) == 0:
            return 0
        self.node_ids[name] = node[0].id
        return node[0].id

    def get_sensor_id(self, name: str, node: str):
        tag: str = f"{node}/{name}"
        if tag in self.sensor_ids:
            return self.sensor_ids[tag]
        node_id = self.get_node_id(node)
        sensor = self.session.query(Sensor.id).filter_by(
            name=name, node_id=node_id).all()
        if len(sensor) == 0:
            return 0
        self.sensor_ids[tag] = sensor[0].id
        return sensor[0].id

    def connect(self):
        self.client.connect(cfg.broker_addr, cfg.broker_port)

    def start(self):
        self.connect()
        self.client.loop_forever()


if __name__ == "__main__":
    wt = WatchtowerHub()
    wt.start()
