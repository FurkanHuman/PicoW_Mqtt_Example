import uasyncio
import urequests
import machine
import os
import time
import ubinascii

CERT_PATH = "/Secrets/Certs/"
MQTT_CLIENT_KEY_POSTFIX = "private.pem.key"
MQTT_CLIENT_CERT_POSTFIX = "certificate.pem.crt"
MQTT_BROKER_CA_POSTFIX = "AmazonRootCA3.pem"


class CertLoader:
    def __init__(self):
        self._key = None
        self._cert = None
        self._ca = None

    def read_pem(self, file):
        with open(file, "r") as input:
            text = input.read().strip()
            split_text = text.split("\n")
            base64_text = "".join(split_text[1:-1])
            return ubinascii.a2b_base64(base64_text)

    def find_pem_files(self):
        self.check_ca_file()
        for filename in os.listdir(CERT_PATH):
            if filename.endswith(MQTT_CLIENT_KEY_POSTFIX):
                key_data = self.read_pem(file=CERT_PATH + filename)
                if key_data:
                    self._key = key_data

            elif filename.endswith(MQTT_CLIENT_CERT_POSTFIX):
                cert_data = self.read_pem(file=CERT_PATH + filename)
                if cert_data:
                    self._cert = cert_data

            elif filename.endswith(MQTT_BROKER_CA_POSTFIX):
                ca_data = self.read_pem(file=CERT_PATH + filename)
                if ca_data:
                    self._ca = ca_data

    def check_ca_file(self):

        ca_file_found = False
        for file in os.listdir(CERT_PATH):
            if MQTT_BROKER_CA_POSTFIX in file:
                print("CA file already exists.")
                ca_file_found = True
                break
        if not ca_file_found:
            print("CA file not exists. started downloading")
            from Lib.myLib.OnBoardLed import OnBoardLed
            led = OnBoardLed()
            uasyncio.run(led.long_up(500))
            self.download_ca()

    def download_ca(self):
        try:
            ca = urequests.get(
                f"https://www.amazontrust.com/repository/{MQTT_BROKER_CA_POSTFIX}")

            with open(CERT_PATH + MQTT_BROKER_CA_POSTFIX, 'w') as ca_file:
                ca_file.write(ca.text)

            ca.close()
            print("CA file downloaded and saved successfully.")
            time.sleep(3)
            machine.soft_reset()

        except Exception:
            print("An error occurred while downloading the CA file.")

    def get_key(self):
        return self._key

    def get_cert(self):
        return self._cert

    def get_ca(self):
        return self._ca
