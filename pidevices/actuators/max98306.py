from pidevices.devices import Actuator
from pidevices.hardware_interfaces.gpio_implementations import RPiGPIO

import atexit
import time


class Max98306Error(Exception):
    pass

class InvalidPinError(Exception):
    pass


class Max98306(Actuator):
    def __init__(self, shutdown_pin=4, name="", max_data_length=0):
        super(Max98306, self).__init__(name, max_data_length)

        try:
            self.shutdown_pin = shutdown_pin
        
            self._amp_interface = self.init_interface(
                interface='gpio',                                       
                impl="RPiGPIO",
                shutdown=self.shutdown_pin
            )

            self.start()

            atexit.register(self.stop)
        except Exception as e:
            raise Max98306Error(
                "Error occured when setting MAX98306 shutdown pin"
            )

    @property
    def shutdown_pin(self):
        return self._shutdown_pin

    @shutdown_pin.setter
    def shutdown_pin(self, pin):
        if isinstance(pin, int):
            self._shutdown_pin = pin
        else:
            raise InvalidPinError

    def start(self):
        # set shutdown pin as output
        self.hardware_interfaces[self._amp_interface].set_pin_function(
            'shutdown', 
            'output'
        )

        self.hardware_interfaces[self._amp_interface].write('shutdown', 0)

    def enable(self):
        self.hardware_interfaces[self._amp_interface].write('shutdown', 1)
        time.sleep(0.05)

    def disable(self):
        time.sleep(0.05)
        self.hardware_interfaces[self._amp_interface].write('shutdown', 0)
    
    def stop(self):
        self.hardware_interfaces[self._amp_interface].close()
