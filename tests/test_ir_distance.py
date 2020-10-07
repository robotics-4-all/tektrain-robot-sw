from pidevices import ADS1X15
from pidevices import GP2Y0A41SK0F
import time

adc = ADS1X15()
        
sensor = GP2Y0A41SK0F(adc)
sensor._channel = 0

for i in range(100):
    print("Distance {} cm".format(sensor.read()))
    time.sleep(0.2)

print("setting units to cm")
sensor.set_units("cm")

for i in range(100):
    print("Distance {} cm".format(sensor.read()))
    time.sleep(0.2)