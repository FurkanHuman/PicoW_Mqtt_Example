import json
import uasyncio
from Lib.myLib.WOLan import WakeOnLan
from Lib.myLib.OnBoardLed import OnBoardLed


class MQTTMessageHandler:

    def __init__(self):

        self.FUNCTION_MAP = {
            'led_state': OnBoardLed.process_led_state,
            'mac_address': WakeOnLan.process_mac_address
        }
        self.led = OnBoardLed()

    def handler(self, topic, msg):
        topic_str = topic.decode()
        msg_str = msg.decode()
        print(f"RX: {topic_str}\n\t{msg_str}")
        try:
            json_obj = json.loads(msg_str)
            uasyncio.run(self.led.long_up(85))

            self.process_json_object(json_obj)

            del json_obj

        except ValueError:
            print(f"Invalid JSON: {msg_str}")

    def process_json_object(self, json_obj):
        for key, value in json_obj.items():
            if key in self.FUNCTION_MAP:
                self.FUNCTION_MAP[key](value)

    def on_mqtt_msg(self, topic, msg):
        topic_str = topic.decode()
        msg_str = msg.decode()
        print(f"RX: {topic_str}\n\t{msg_str}")
