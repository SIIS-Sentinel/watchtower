from config_hub import broker_addr, client_name, ca_cert, certfile, keyfile
import argparse
import paho.mqtt.client as mqtt


def on_log(client: mqtt.Client, userdata, flags, rc):
    pass


def on_connect(client: mqtt.Client, userdata, flags, rc):
    print("Connected to broker at %s" % broker_addr)


def update_delay(client: mqtt.Client, node_name: str, delay: float) -> None:
    topic: str = "/%s/sample_period" % node_name
    client.publish(topic, delay)


client = mqtt.Client(client_name)
client.tls_set(ca_certs=ca_cert,
               certfile=certfile,
               keyfile=keyfile)
client.on_connect = on_connect
client.on_log = on_log
client.connect(broker_addr, port=8883)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Send a backoff message to the given node, with the new given sample delay.')
    parser.add_argument("node", metavar="node", type=str,
                        help="Node you wish to examine")
    parser.add_argument("delay", metavar="sensor", type=float,
                        help="New sample delay")
    args = parser.parse_args()
    print("Sending setting the sample delay of %s to %0.1fs..." %
          (args.node, args.delay))
    update_delay(client, args.node, args.delay)
    print("Done")
