# Watchtower sample period (in s)
sample_period: float = 1

# Output CSV file path (relative to the executable, or absolute)
csv_path = "out.csv"

# Path to a reference output, considered safe
csv_safe = "safe.csv"

# Number of STD of deviation allowed
nb_std = 4

# MQTT client name
client_name = "/sentinel/node_1"

# MQTT broker address
broker_addr = "hub"
# broker_addr = "hub.local"

# Root CA path
ca_cert = "certs/yubikey.crt"

# Client certificate and key paths
certfile = "certs/watchtower_node.crt"
keyfile = "certs/watchtower_node.key"


# Info about all files to sample
files: list = [
    {"path": "/sys/kernel/sentinel/nb_cpus",
        "name": "Number of CPUs cores",
        "unit": "N/A",
        "topic": "/nb_cpus",
        "differential": 0},

    {"path": "/sys/kernel/sentinel/CPU_0",
        "name": "CPU 0 freq",
        "unit": "kHz",
        "topic": "/CPU_0",
        "differential": 0},

    {"path": "/sys/kernel/sentinel/CPU_1",
        "name": "CPU 1 freq",
        "unit": "kHz",
        "topic": "/CPU_1",
        "differential": 0},

    {"path": "/sys/kernel/sentinel/CPU_2",
        "name": "CPU 2 freq",
        "unit": "kHz",
        "topic": "/CPU_2",
        "differential": 0},

    {"path": "/sys/kernel/sentinel/CPU_3",
        "name": "CPU 3 freq",
        "unit": "kHz",
        "topic": "/CPU_3",
        "differential": 0},

    {"path": "/sys/kernel/sentinel/free_ram",
        "name": "Free RAM",
        "unit": "kB",
        "topic": "/free_ram",
        "differential": 0},

    {"path": "/sys/kernel/sentinel/used_ram",
        "name": "Used RAM",
        "unit": "kB",
        "topic": "/used_ram",
        "differential": 0},

    {"path": "/sys/kernel/sentinel/total_ram",
        "name": "Total RAM",
        "unit": "kB",
        "topic": "/total_ram",
        "differential": 0},

    {"path": "/sys/kernel/sentinel/free_swap",
        "name": "Free Swap",
        "unit": "kB",
        "topic": "/free_swap",
        "differential": 0},

    {"path": "/sys/kernel/sentinel/used_swap",
        "name": "Used Swap",
        "unit": "kB",
        "topic": "/used_swap",
        "differential": 0},

    {"path": "/sys/kernel/sentinel/total_swap",
        "name": "Total Swap",
        "unit": "kB",
        "topic": "/total_swap",
        "differential": 0},

    {"path": "/sys/kernel/sentinel/load_1m",
        "name": "CPU load (1m)",
        "unit": "%",
        "topic": "/load_1m",
        "differential": 0},

    {"path": "/sys/kernel/sentinel/load_5m",
        "name": "CPU load (5m)",
        "unit": "%",
        "topic": "/load_5m",
        "differential": 0},

    {"path": "/sys/kernel/sentinel/load_15m",
        "name": "CPU load (15m)",
        "unit": "%",
        "topic": "/load_15m",
        "differential": 0},

    {"path": "/sys/kernel/sentinel/nb_processes",
        "name": "Number of processes",
        "unit": "N/A",
        "topic": "/nb_processes",
        "differential": 0},

    {"path": "/sys/class/net/wlan0/statistics/rx_bytes",
        "name": "Number of bytes received",
        "unit": "bytes",
        "topic": "/rx_bytes",
        "differential": 1},

    {"path": "/sys/class/net/wlan0/statistics/tx_bytes",
        "name": "Number of bytes sent",
        "unit": "bytes",
        "topic": "/tx_bytes",
        "differential": 1},

    {"path": "/sys/class/net/wlan0/statistics/rx_packets",
        "name": "Number of packets received",
        "unit": "N/A",
        "topic": "/rx_packets",
        "differential": 1},

    {"path": "/sys/class/net/wlan0/statistics/tx_packets",
        "name": "Number of packets sent",
        "unit": "N/A",
        "topic": "/tx_packets",
        "differential": 1},

    {"path": "/sys/kernel/sentinel/hiwater_rss",
        "name": "RSS high watermark",
        "unit": "Bytes",
        "topic": "/hiwater_rss",
        "differential": 0},

    {"path": "/sys/kernel/sentinel/hiwater_vm",
        "name": "VM high watermark",
        "unit": "Bytes",
        "topic": "/hiwater_vm",
        "differential": 0},

    {"path": "/sys/kernel/sentinel/nb_fds",
        "name": "Number of file decriptors",
        "unit": "N/A",
        "topic": "/nb_fds",
        "differential": 0},

    {"path": "/sys/kernel/sentinel/task_size",
        "name": "Tracked task current size",
        "unit": "Bytes",
        "topic": "/task_size",
        "differential": 0},

    {"path": "/sys/kernel/sentinel/tracked_pid",
        "name": "Tracked PID",
        "unit": "N/A",
        "topic": "/tracked_pid",
        "differential": 0},
]
