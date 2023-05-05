import machine
import ntptime
import uasyncio
import gc
import time
from Lib.myLib.MQTTMessageHandler import MQTTMessageHandler
from Lib.myLib.OnBoardLed import OnBoardLed
from Lib.myLib.WConnection import WConnection
from Lib.myLib.MQTTConnection import MQTTConnection
from Lib.simple import MQTTException

led = OnBoardLed()

led.first_up()

wifi = WConnection()

wifi.first_connection()


ntptime.settime()

MQTT_TOPIC = "sdk/test/python"
MQTT_TIME_TOPIC = "sdk/test/python"

mqtt_connection = MQTTConnection()
mqtt_client = mqtt_connection.mqtt_client

print(f"Device Id: {mqtt_client.client_id}")


print(f"Connecting to MQTT broker: {mqtt_client.server}")

msg_handler = MQTTMessageHandler()

mqtt_client.set_callback(msg_handler.handler)

while True:
    try:
        mqtt_client.connect()
        break
    except MQTTException as e:
        print("MQTT Connection Error. Retrying...", e)
        time.sleep(1)


while True:
    try:
        mqtt_client.subscribe(MQTT_TOPIC)
        break
    except MQTTException as e:
        print("Subscribe error:", e)
        time.sleep(1)

print(f"Connected to MQTT broker: {mqtt_client.server}")
print(f"Connected to MQTT topic: {MQTT_TOPIC}")

mqtt_client.set_last_will(
    MQTT_TOPIC, f"Connection Terminated. Client Id={mqtt_client.client_id}", retain=True, qos=1)


def publish_mqtt_msg():
    topic_str = MQTT_TIME_TOPIC

    current_time = time.localtime()

    formatted_time = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
        current_time[0], current_time[1], current_time[2], current_time[3], current_time[4], current_time[5])

    msg_str = '{"UTC Time": "'+formatted_time+'"}'

    uasyncio.run(led.long_down(50))

    print(f"TX: {topic_str}\n\t{msg_str}")
    mqtt_client.publish(topic_str, str(msg_str))


def publish_topic(t):
    publish_mqtt_msg()
    uasyncio.run(led.short_up(75))


machine.Timer(mode=machine.Timer.PERIODIC, period=mqtt_client.keepalive *
              1000, callback=mqtt_connection.send_mqtt_ping)

machine.Timer(mode=machine.Timer.PERIODIC,
              period=mqtt_client.keepalive * 125, callback=publish_topic)


async def mqtt_subscriber(c_alive):
    while c_alive:
        mqtt_client.check_msg()

        uasyncio.sleep_ms(15)


loop = uasyncio.get_event_loop()
loop.create_task(mqtt_subscriber(wifi._connection_alive))
loop.create_task(wifi.connection_control())
loop.run_forever()
