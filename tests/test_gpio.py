from pidevices.hardware_interfaces.gpio_implementations import RPiGPIO


if __name__ == "__main__":
    gpio = RPiGPIO(shutdown=4)
    gpio.set_pin_function('shutdown', 'output')
    gpio.write('shutdown', 1)