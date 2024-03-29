#from pidevices.hardware_interfaces.gpio_implementations import Mcp23017GPIO
from time import sleep
from pidevices import Mcp23017GPIO

motor = Mcp23017GPIO(bus=1, address=0x22, M2="B_0", E2="B_1",M1="B_3", E1="B_2")

motor.initialize()

motor.set_pin_function('M1', 'output')
motor.set_pin_function('M2', 'output')

motor.set_pin_function('E2', 'output')
motor.set_pin_function('E1', 'output')
motor.set_pin_pwm('E2', True)
motor.set_pin_pwm('E1', True)
motor.set_pin_frequency('E2', 200)
motor.set_pin_frequency('E1', 200)


motor.write("M1",1)
motor.write('E1', 0.01)
motor.write('E2', 0.01)
sleep(10)

#motor.write("M1",0)
#motor.write('E1', 0.1)
#motor.write('E2', 0.2)
#sleep(2)


motor.write("E1", 0)
motor.write("E2", 0)


motor.set_pin_pwm('E2', False)
motor.set_pin_pwm('E1', False)
sleep(1)

motor.close()
