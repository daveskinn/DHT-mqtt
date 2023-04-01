import network
import time
import dht
import machine
import ujson
import usys
import config
from time import sleep
from machine import Pin
from umqtt.robust import MQTTClient
from picozero import RGBLED, PWMLED

rgb = RGBLED(red = 1, green = 3, blue = 4, pwm = True)
rgb.color = (50, 0, 0) #red until network connection

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(config.ssid, config.net_pass)
time.sleep(10)
rgb.color = (50, 25, 0) #orange on network connection
print(wlan.isconnected())

sensor = dht.DHT22(machine.Pin(2))

mqtt_server = config.mqtt_server
client_id = config.client_id
user = config.user
password = config.mqtt_pass
topic_pub = config.topic_pub

def mqtt_connect():
    client = MQTTClient(client_id, mqtt_server, 1883, user, password, keepalive=3600)
    client.connect()
    print('Connected to %s MQTT Broker'%(mqtt_server))
    return client

def reconnect():
    print('Failed to connect to the MQTT Broker. Reconnecting...')
    time.sleep(5)
    client.reconnect()

try:
    client = mqtt_connect()
except OSError as e:
    reconnect()
while True:
    try:
        sensor.measure()
        payload = ujson.dumps({
            "temp": sensor.temperature(),
            "humidity": sensor.humidity(),
        })
        print(payload)
        rgb.color = (0, 0, 50) #blue when publishing
        client.publish(topic_pub, payload)
        rgb.color = (0, 50, 0) #green after published
        sleep(360)
    except KeyboardInterrupt:
        client.disconnect()
        rgb.off()
        usys.exit()
    except:
        rgb.color = (50, 25, 0) #orange on mqtt connection failure
        sleep(360) #wait before reconnecting
        reconnect()
        

