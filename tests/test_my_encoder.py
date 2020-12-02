from pidevices.hardware_interfaces.gpio_implementations import PiGPIO
import pigpio
import time

def cbf(gpio, level, tick, *args):
   print(gpio, level, tick)

gpio = PiGPIO()
gpio.add_pins(pin=23)
gpio.set_pin_function('pin', 'input')
gpio.set_pin_bounce('pin', 2000)
gpio.set_pin_edge('pin', 'rising')
gpio.set_pin_event('pin', cbf)

time.sleep(10)
