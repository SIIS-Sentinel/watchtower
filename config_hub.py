# Watchtower sample period(in s)
sample_period: float = 1

# Output CSV file path (relative to the executable, or absolute)
csv_path = "out.csv"

# Path to a reference output, considered safe
csv_safe = "safe.csv"

# Number of STD of deviation allowed
nb_std = 4

# MQTT client name
client_name = "watchtower_hub"

# MQTT broker address
# Make sure that this address is the one in the broker certificate
broker_addr = "localhost"
broker_port: int = 8883

# Root CA path
ca_cert = "/certs/CA.pem"

# Client certificate and key paths
certfile = "/certs/hub.crt"
keyfile = "/certs/hub.key"

# DB path
db_path = "postgresql://pi:password@localhost/sentinel"

# Info about all files to sample
files: list = [
    {"path": "/sys/kernel/sentinel/nb_cpus",
        "name": "Number of CPUs cores",
        "unit": "N/A",
        "differential": 0},

    {"path": "/sys/kernel/sentinel/CPU_0",
        "name": "CPU 0 freq",
        "unit": "kHz",
        "differential": 0},

    {"path": "/sys/kernel/sentinel/CPU_1",
        "name": "CPU 1 freq",
        "unit": "kHz",
        "differential": 0},

    {"path": "/sys/kernel/sentinel/CPU_2",
        "name": "CPU 2 freq",
        "unit": "kHz",
        "differential": 0},

    {"path": "/sys/kernel/sentinel/CPU_3",
        "name": "CPU 3 freq",
        "unit": "kHz",
        "differential": 0},

    {"path": "/sys/kernel/sentinel/free_ram",
        "name": "Free RAM",
        "unit": "kB",
        "differential": 0},

    {"path": "/sys/kernel/sentinel/used_ram",
        "name": "Used RAM",
        "unit": "kB",
        "differential": 0},

    {"path": "/sys/kernel/sentinel/total_ram",
        "name": "Total RAM",
        "unit": "kB",
        "differential": 0},

    {"path": "/sys/kernel/sentinel/free_swap",
        "name": "Free Swap",
        "unit": "kB",
        "differential": 0},

    {"path": "/sys/kernel/sentinel/used_swap",
        "name": "Used Swap",
        "unit": "kB",
        "differential": 0},

    {"path": "/sys/kernel/sentinel/total_swap",
        "name": "Total Swap",
        "unit": "kB",
        "differential": 0},

    {"path": "/sys/kernel/sentinel/load_1m",
        "name": "CPU load (1m)",
        "unit": "%",
        "differential": 0},

    {"path": "/sys/kernel/sentinel/load_5m",
        "name": "CPU load (5m)",
        "unit": "%",
        "differential": 0},

    {"path": "/sys/kernel/sentinel/load_15m",
        "name": "CPU load (15m)",
        "unit": "%",
        "differential": 0},

    {"path": "/sys/kernel/sentinel/nb_processes",
        "name": "Number of processes",
        "unit": "N/A",
        "differential": 0},

    {"path": "/sys/class/net/ens33/statistics/rx_bytes",
        "name": "Number of bytes received",
        "unit": "bytes",
        "differential": 1},

    {"path": "/sys/class/net/ens33/statistics/tx_bytes",
        "name": "Number of bytes sent",
        "unit": "bytes",
        "differential": 1},

    {"path": "/sys/class/net/ens33/statistics/rx_packets",
        "name": "Number of packets received",
        "unit": "N/A",
        "differential": 1},

    {"path": "/sys/class/net/ens33/statistics/tx_packets",
        "name": "Number of packets sent",
        "unit": "N/A",
        "differential": 1},

]
