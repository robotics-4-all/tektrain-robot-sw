from pidevices.hardware_interfaces.gpio_implementations import Mcp23017GPIO
import time

def cbf(pin, level, *args):
    global i
    i = i + 1
    print("Called!", i) 
    print(level ,pin)
    print("Given: ", args[0])


i = 0
obj = Mcp23017GPIO(bus=1, address=0x20)
obj.add_pins(button="B_0")
obj.set_pin_function('button', 'input')
obj.set_pin_bounce('button', 50)
obj.set_pin_edge('button', 'both')
obj.set_pin_event('button', cbf, "giorgos")

obj.start_polling('button')

time.sleep(5)