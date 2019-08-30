from config import *
import csv
import time
import threading
import os.path

# Global variables
next_call: float = time.time()
start_time: float = 0


class Entry():
    """Define a class for entry files"""

    def __init__(self, entry: dict):
        self.name = entry["name"]
        self.unit = entry["unit"]
        self.path = entry["path"]


def load_entries(files: list = files) -> list:
    entries: list = []
    for file in files:
        entry: Entry = Entry(file)
        entries += [entry]
    return entries


def sample(entries: list, delta_t: float) -> None:
    """Run one sampling iteration, and creates/runs a timer for the next one"""
    global next_call
    next_call += sample_period
    print("Taking a sample at time %0.1fs" % (time.time() - start_time))
    samples: list = [time.time()]
    for entry in entries:
        with open(entry.path, "r") as file:
            samples += [file.readline().split()[0]]
    with open(csv_path, "a") as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(samples)
    threading.Timer(next_call - time.time(), sample,
                    args=[entries, sample_period]).start()


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
    print("Starting the sampling with a period of %.0fs" % sample_period)
    start_time = time.time()
    sample(entries, delta_t)


# Start polling the files
if __name__ == "__main__":
    start_sampling(files, sample_period)
