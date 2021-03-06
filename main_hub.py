import config_hub as cfg
import paho.mqtt.client as mqtt
import json
# from sql import session, Node, Measurement, Event, Sensor
from bookkeeper.sql import create_sessions, Node, Measurement, Event, Sensor
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


def update_sample_period(client: mqtt.Client, node_name: str, new_period: float):
    print("Watchtower: Changing the sample period of node %s to %0.1f" %
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
    print("Watchtower: Connected to broker at %s" % cfg.broker_addr)
    client.subscribe("/nodes")
    for node in nodes.keys():
        topic = f"/sentinel/{node}/#"
        client.subscribe(topic)


def on_message(client: mqtt.Client, userdata, message: mqtt.MQTTMessage):
    global nodes
    node_name: str
    if (message.topic == "/nodes"):
        # Message announcing a node
        node_topic: str = message.payload.decode()
        node_name = node_topic.split("/")[2]
        if (node_name not in nodes):
            print(f"Watchtower: New node detected, subscribing to it with topic {node_topic}")
            client.subscribe(node_topic + "/#")
            nodes[node_name] = {}
            add_node(node_name)
    else:
        # Message announcing a sensor measurement
        topic_split: list = message.topic.split("/")
        node_name = topic_split[2]
        sensor_name: str = topic_split[3]
        message_json = json.loads(message.payload.decode("utf-8"))
        node_id = get_node_id(node_name)
        sensor: SensorJSON
        if (sensor_name not in nodes[node_name]):
            print(f"Watchtower: Found new sensor {sensor_name} for the node {node_name}")
            sensor = SensorJSON(message_json)
            sensor.name = sensor_name
            nodes[node_name][sensor_name] = sensor
            add_sensor(sensor_name, sensor.unit,
                       sensor.average, sensor.std, node_id)
        sensor_id: int = get_sensor_id(sensor_name, node_name)
        sensor = nodes[node_name][sensor_name]
        ts: float = float(message_json["ts"])
        value = float(message_json["value"])
        add_measurement(ts, value, sensor_id, node_id)


def on_log(client, userdata, level, buf):
    if level == mqtt.MQTT_LOG_WARNING:
        print("Warning: %s" % (buf))
    elif level == mqtt.MQTT_LOG_ERR:
        print("Error: %s" % (buf))


# Create the SQL session
session = create_sessions(cfg.db_path)

# Create and connect the MQTT client
client = mqtt.Client(cfg.client_name)
client.tls_set(ca_certs=cfg.ca_cert,
               certfile=cfg.certfile,
               keyfile=cfg.keyfile)
client.on_connect = on_connect
client.on_log = on_log
client.on_message = on_message
client.connect(cfg.broker_addr, port=8883)
client.loop_forever()
