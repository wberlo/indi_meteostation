try:
  import usocket as socket

except:
  import socket

from machine import Pin
import network
import time

import esp
esp.osdebug(None)

import gc
gc.collect()

ssid = '<your wifi network name>'
password = '<your passphrase>'

station = network.WLAN(network.STA_IF)
station.active(True)
station.connect(ssid, password)

while station.isconnected() == False:
    print(".", end="")
    time.sleep(1)
    
print('Connection successful')
print(station.ifconfig())




