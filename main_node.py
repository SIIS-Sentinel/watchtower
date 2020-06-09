import config_node as cfg
import csv
import time
import threading
import os.path
import statistics as st
import pandas as pd
import paho.mqtt.client as mqtt
import json
from typing import Optional

# Global variables
next_call: float = time.time()
start_time: float = 0
client: mqtt.Client = None


class Entry():
    """Define a class for entry files"""

    def __init__(self, entry: dict):
        self.name: str = entry["name"]
        self.unit: str = entry["unit"]
        self.path: str = entry["path"]
        self.topic: str = entry["topic"]
        self.differential: bool = entry["differential"]
        self.previous_raw: float = 0
        self.average: Optional[float] = None
        self.std: Optional[float] = None


def on_connect(client: mqtt.Client, userdata, flags, rc):
    print("Connected to MQTT server at %s" % (cfg.broker_addr))
    client.subscribe(cfg.client_name + "/sample_period")


def on_message(client: mqtt.Client, userdata, message: mqtt.MQTTMessage):
    global sample_period
    # Check if this is a message that changes the sample period
    if message.topic == cfg.client_name + "/sample_period":
        message_data: str = message.payload.decode()
        message_float: float = float(message_data)
        cfg.sample_period = message_float
    else:
        # This should not happen, we are not subscribed to anything else
        print("Unexpected message received, channel: %s" % message.topic)


def load_entries(files: list = cfg.files) -> list:
    entries: list = []
    for file in files:
        entry: Entry = Entry(file)
        entries += [entry]
    return entries


def is_outlier(entry: Entry, value: float) -> bool:
    if entry.average is None or entry.std is None:
        return False
    return (value > entry.average + cfg.nb_std * entry.std) or (value < entry.average - cfg.nb_std * entry.std)


def sample(entries: list, delta_t: float, client: mqtt.Client = client, initial_call: int = 0) -> None:
    """Run one sampling iteration, and creates/runs a timer for the next one"""
    global next_call
    next_call += cfg.sample_period
    print("Taking a sample at time %0.1fs" % (time.time() - start_time))
    client.publish("/nodes", cfg.client_name)
    samples: list = [time.time()]
    # Add all the values to the samples list
    for entry in entries:
        with open(entry.path, "r") as file:
            # Take care of the differential variables
            if entry.differential == 1:
                raw = float(file.readline().split()[0])
                if initial_call:
                    val_buf: float = 0
                else:
                    val_buf = raw - entry.previous_raw
                entry.previous_raw = raw
            else:
                val_buf = float(file.readline().split()[0])
            message = json.dumps(
                {"value": val_buf, "unit": entry.unit, "ts": samples[0], "std": entry.std, "average": entry.average})
            client.publish(cfg.client_name + entry.topic, message)
            samples += [val_buf]
    # Write the samples to the CSV file
    with open(cfg.csv_path, "a") as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(samples)
    threading.Timer(next_call - time.time(), sample,
                    args=[entries, cfg.sample_period, client]).start()


def start_sampling(files: list = cfg.files, delta_t: float = cfg.sample_period) -> None:
    """Creates a CSV file if required, and starts the sampling with the given config"""
    global start_time
    print("Loading the entries to read from config.py")
    entries: list = load_entries(files)
    if not os.path.isfile(cfg.csv_path):
        print("CSV file does not exists, creating it")
        with open(cfg.csv_path, "w") as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(["Measurement time"] +
                                [entry.name for entry in entries])
            csv_writer.writerow(["s"] + [entry.unit for entry in entries])
    if os.path.isfile(cfg.csv_safe):
        print("Baseline CSV file found, extracting its contents")
        csv_safe: pd.DataFrame = pd.read_csv(cfg.csv_safe, skiprows=[1])
        for entry in entries:
            entry.average = st.mean(csv_safe[entry.name].astype(float))
            entry.std = st.stdev(csv_safe[entry.name].astype(float))
    print("Connecting to MQTT broker")
    client = mqtt.Client(cfg.client_name)
    client.on_connect = on_connect
    client.on_message = on_message
    client.tls_set(ca_certs=cfg.ca_cert,
                   certfile=cfg.certfile,
                   keyfile=cfg.keyfile)
    client.connect(cfg.broker_addr, port=cfg.broker_port)
    print("Starting the sampling with a period of %.0fs" % cfg.sample_period)
    start_time = time.time()
    sample(entries, delta_t, client, 1)


# Start polling the files
if __name__ == "__main__":
    start_sampling(cfg.files, cfg.sample_period)
