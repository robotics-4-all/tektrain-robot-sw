# from pidevices.hardware_interfaces.gpio_implementations import PiGPIO
# import pigpio
# import time

# def cbf(gpio, level, tick, *args):
#    print(gpio, level, tick)

# gpio = PiGPIO()
# gpio.add_pins(pin=24)
# gpio.set_pin_function('pin', 'input')
# gpio.set_pin_bounce('pin', 2000)
# gpio.set_pin_edge('pin', 'rising')
# gpio.set_pin_event('pin', cbf)

# time.sleep(10)

from pidevices import DfrobotMotorControllerPiGPIO
from pidevices.sensors import DfRobotWheelEncoderPiGPIO
import time

motor_driver = DfrobotMotorControllerPiGPIO(E1=20, E2=21, M1=19, M2=26, range=1000, frequency=200)
encoder_l = DfRobotWheelEncoderPiGPIO(pin=23)
encoder_r = DfRobotWheelEncoderPiGPIO(pin=24)

motor_driver.start()
encoder_l.start()
encoder_r.start()

motor_driver.write(0.3, 0.3)

sum = 0

for i in range(50):
   val_l = encoder_l.read()["rps"]
   val_r = encoder_r.read()["rps"]
   sum = sum + (val_l + val_r)/2 * 0.1

   print(val_l, val_r)

   time.sleep(0.1)

print("total_distance: ", sum * 0.0325)


motor_driver.terminate()