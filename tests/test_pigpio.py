from pidevices import DfrobotMotorControllerPiGPIO
from time import sleep

motor_driver = DfrobotMotorControllerPiGPIO(E1=20, E2=12, M1=21, M2=16, range=1.0)

motor_driver.start()

motor_driver.move_linear(0.5)
sleep(2)
motor_driver.move_angular(0.5)
sleep(2)
motor_driver.move_linear(0.0)


motor_driver.stop()