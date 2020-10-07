from pidevices import DfrobotMotorControllerPiGPIO
from time import sleep

motor_driver = DfrobotMotorControllerPiGPIO(E1=20, E2=12, M1=21, M2=16, range=1.0)

motor_driver.start()

# motor_driver.move_linear(0.5)
# sleep(5)
motor_driver.move_angular(1.0)
sleep(4)
# motor_driver.move_linear(0.0)
motor_driver.move_linear(0.0)

motor_driver.stop()