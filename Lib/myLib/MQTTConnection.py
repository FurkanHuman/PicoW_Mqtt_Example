import ubinascii
import machine
import ssl
from Lib.myLib.CertLoader import CertLoader
from Lib.simple import MQTTClient

CONFIG_FILE = "/Secrets/MQTTServer.conf"


class MQTTConnection:
    def __init__(self):
        self.certloader = CertLoader()
        self.certloader.find_pem_files()
        self.config = self.read_connection_config()

        self.mqtt_client = MQTTClient(
            client_id=self.config["MQTT_CLIENT_ID"], # + str(f"-{ubinascii.hexlify(machine.unique_id()).decode()}"),             
            server=self.config["MQTT_BROKER"],
            keepalive=60,
            ssl=True,
            ssl_params={
                "key": self.certloader.get_key(),
                "cert": self.certloader.get_cert(),
                "server_hostname": self.config["MQTT_BROKER"],
                "cert_reqs": ssl.CERT_REQUIRED,
                "cadata": self.certloader.get_ca(),
            },
        )

    def send_mqtt_ping(self, t):
        print("TX: ping")
        self.mqtt_client.ping()

    def read_connection_config(self):
        config = {}
        with open(CONFIG_FILE, "r") as file:
            for line in file:
                key, value = line.strip().split("=")
                config[key.strip()] = value.strip()
        return config
