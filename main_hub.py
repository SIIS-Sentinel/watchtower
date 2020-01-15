from config_hub import *
import csv
import paho.mqtt.client as mqtt
import json
import ssl
from sqlalchemy import create_engine, Column, Integer, Float, String, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Global variables
nodes: dict = {}
Base = declarative_base()


class SensorJSON():
    """Define a class for entry files"""

    def __init__(self, entry: dict):
        self.name = ""
        self.unit = entry["unit"]
        # self.previous_raw = 0
        self.average = entry["average"]
        self.std = entry["std"]
        self.ts = entry["ts"]


class Node(Base):
    __tablename__ = "nodes"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)

    def __repr__(self):
        return "Node(%s)" % (self.name)


class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True)
    event_type = Column(String)
    timestamp = Column(Float)
    node_id = Column(Integer, ForeignKey('nodes.id'))
    node = relationship("Node", back_populates="events")

    def __repr__(self):
        return "Event(%s, %s, %0.1f)" % (self.node, self.event_type, self.timestamp)


Node.events = relationship("Event", order_by=Event.id, back_populates="node")


class Sensor(Base):
    __tablename__ = "sensors"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    unit = Column(String)
    average = Column(Float)
    std = Column(Float)
    node_id = Column(Integer, ForeignKey('nodes.id'))
    node = relationship("Node", back_populates="sensors")

    def __repr__(self):
        return "Sensor(%s, %s, %s, %0.2f, %0.2f)" % (self.node, self.name, self.unit, self.average, self.std)


Node.sensors = relationship(
    "Sensor", order_by=Sensor.id, back_populates="node")


class Measurement(Base):
    __tablename__ = "measurements"
    id = Column(Integer, primary_key=True)
    sensor_id = Column(Integer, ForeignKey("sensors.id"))
    sensor = relationship("Sensor", back_populates="measurements")
    timestamp = Column(Float)
    value = Column(Float)
    node_id = Column(Integer, ForeignKey('nodes.id'))
    node = relationship("Node", back_populates="measurements")

    def __repr__(self):
        return "Measurement(%s, %s, %0.1f, %f)" % (self.node, self.sensor, self.timestamp, self.value)


Node.measurements = relationship(
    "Measurement", order_by=Measurement.id, back_populates="node")
Sensor.measurements = relationship(
    "Measurement", order_by=Measurement.id, back_populates="sensor")


# Create and connect to the database
engine = create_engine('sqlite:///data.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()


def is_outlier(sensor: Sensor, value: float):
    if (sensor.average is None or sensor.std is None):
        print("Data missing for an outlier detection")
        return False
    return (value > sensor.average + nb_std * sensor.std) or (value < sensor.average - nb_std * sensor.std)


def update_sample_period(client: mqtt.Client, node_name: str, new_period: float):
    print("Changing the sample period of node %s to %0.1f" %
          (node_name, new_period))
    client.publish(node_name + "/sample_period", str(new_period))


def add_node(name: str):
    oldNode = session.query(Node.name.label('name')).all()
    if len(oldNode) == 0:
        newNode = Node(name=name)
        session.add(newNode)
        session.commit()


def add_event(ts: float, ev_type: str, node: int):
    newEvent = Event(timestamp=ts, event_type=ev_type, node_id=node)
    session.add(newEvent)
    session.commit()


def add_measurement(ts: float, value: float, sensor: int, node: int):
    newMeasurement = Measurement(
        timestamp=ts, value=value, sensor_id=sensor, node_id=node)
    session.add(newMeasurement)
    session.commit()


def add_sensor(name: str, unit: str, avg: float, std: float, node: int):
    oldSensor = session.query(Sensor).filter_by(node_id=node, name=name).all()
    if len(oldSensor) == 0:
        newSensor = Sensor(name=name, unit=unit, average=avg,
                           std=std, node_id=node)
        session.add(newSensor)
        session.commit()


def get_node_id(name: str):
    node = session.query(Node.id).filter_by(name=name)
    return node[0].id


def get_sensor_id(name: str, node: str):
    node_id = session.query(Node.id).filter_by(name=node)
    sensor = session.query(Sensor.id).filter_by(name=name)
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
        node_id = get_node_id(node_name)
        sensor_id = get_sensor_id(sensor_name, node_name)
        if (sensor_name not in nodes[node_name]):
            print("Found new sensor (%s) for the node" % sensor_name)
            sensor: Sensor = SensorJSON(message_json)
            sensor.name = sensor_name
            nodes[node_name][sensor_name] = sensor
            add_sensor(sensor_name, sensor.unit,
                       sensor.average, sensor.std, node_id)
        sensor: Sensor = nodes[node_name][sensor_name]
        value = float(message_json["value"])
        add_measurement(sensor.ts, value, sensor_id, node_id)
        if (is_outlier(sensor, value=value)):
            print("Outlier detected: %s (value: %.02f, average: %.02f, std: %.02f)" %
                  (sensor.name, value, sensor.average, sensor.std))


def on_log(client, userdata, level, buf):
    # print("Log: %s" % buf)
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
