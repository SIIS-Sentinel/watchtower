from config_node import *
import csv
import time
import threading
import os.path
import statistics as st
import pandas as pd
import paho.mqtt.client as mqtt
import json

# Global variables
next_call: float = time.time()
start_time: float = 0
client: mqtt.Client = None


class Entry():
    """Define a class for entry files"""

    def __init__(self, entry: dict):
        self.name = entry["name"]
        self.unit = entry["unit"]
        self.path = entry["path"]
        self.topic = entry["topic"]
        self.differential = entry["differential"]
        self.previous_raw = 0
        self.average = None
        self.std = None


def on_connect(client: mqtt.Client, userdata, flags, rc):
    print("Connected to MQTT server at %s" % (broker_addr))


def load_entries(files: list = files) -> list:
    entries: list = []
    for file in files:
        entry: Entry = Entry(file)
        entries += [entry]
    return entries


def is_outlier(entry: Entry, value: float):
    return (value > entry.average + nb_std * entry.std) or (value < entry.average - nb_std * entry.std)


def sample(entries: list, delta_t: float, client: mqtt.Client = client, initial_call: int = 0) -> None:
    """Run one sampling iteration, and creates/runs a timer for the next one"""
    global next_call
    next_call += sample_period
    print("Taking a sample at time %0.1fs" % (time.time() - start_time))
    client.publish("/nodes", client_name)
    samples: list = [time.time()]
    # Add all the values to the samples list
    for entry in entries:
        with open(entry.path, "r") as file:
            # Take care of the differential variables
            if entry.differential == 1:
                raw = float(file.readline().split()[0])
                if initial_call:
                    val_buf = 0
                else:
                    val_buf = raw - entry.previous_raw
                entry.previous_raw = raw
            else:
                val_buf = float(file.readline().split()[0])
            # if is_outlier(entry, val_buf):
            #     print("Outlier detected for metric %s (avg: %.02f, std: %.02f, value: %.02f)" % (
            #         entry.name, entry.average, entry.std, val_buf))
            message = json.dumps(
                {"value": val_buf, "unit": entry.unit, "ts": samples[0], "std": entry.std, "average": entry.average})
            client.publish(client_name + entry.topic, message)
            samples += [val_buf]
    # Write the samples to the CSV file
    with open(csv_path, "a") as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(samples)
    threading.Timer(next_call - time.time(), sample,
                    args=[entries, sample_period, client]).start()


def start_sampling(files: list = files, delta_t: float = sample_period) -> None:
    """Creates a CSV file if required, and starts the sampling with the given config"""
    global start_time
    print("Loading the entries to read from config.py")
    entries: list = load_entries(files)
    if not os.path.isfile(csv_path):
        print("CSV file does not exists, creating it")
        with open(csv_path, "w") as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(["Measurement time"] +
                                [entry.name for entry in entries])
            csv_writer.writerow(["s"] + [entry.unit for entry in entries])
    if os.path.isfile(csv_safe):
        print("Baseline CSV file found, extracting its contents")
        csv_file = pd.read_csv(csv_safe, skiprows=[1])
        for entry in entries:
            entry.average = st.mean(csv_file[entry.name].astype(float))
            entry.std = st.stdev(csv_file[entry.name].astype(float))
    print("Connecting to MQTT broker")
    client = mqtt.Client(client_name)
    client.on_connect = on_connect
    client.tls_set(ca_certs=ca_cert,
                   certfile=certfile,
                   keyfile=keyfile)
    client.connect(broker_addr, port=8883)
    print("Starting the sampling with a period of %.0fs" % sample_period)
    start_time = time.time()
    sample(entries, delta_t, client, 1)


# Start polling the files
if __name__ == "__main__":
    start_sampling(files, sample_period)
