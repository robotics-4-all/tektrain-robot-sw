from pidevices import ADS1X15
from pidevices import GP2Y0A41SK0F
import time

adc = ADS1X15()
        
sensor = GP2Y0A41SK0F(adc)
sensor._channel = 0
while True:
    print("Distance {} cm".format(sensor.read()))
    time.sleep(0.1)