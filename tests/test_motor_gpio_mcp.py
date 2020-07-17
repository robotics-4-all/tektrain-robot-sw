#from pidevices.hardware_interfaces.gpio_implementations import Mcp23017GPIO
from time import sleep
from pidevices.mcp23017 import MCP23017
from pidevices import Mcp23017GPIO

motor = Mcp23017GPIO(bus=1, address=0x22, M2="B_0", E2="B_1",M1="B_3", E1="B_2")

motor.initialize()

motor.set_pin_function('M1', 'output')
motor.set_pin_function('M2', 'output')


motor.set_pin_function('E2', 'output')
motor.set_pin_function('E1', 'output')

motor.write("M1",1)

sleep(1)

for i in range(500):
    motor.write("E1", 1)
    motor.write("E2", 1)
    sleep(0.002)
    motor.write("E1", 0)
    motor.write("E2", 0)
    sleep(0.006)


motor.close()