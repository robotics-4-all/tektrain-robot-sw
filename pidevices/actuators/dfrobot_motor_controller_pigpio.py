from .motor_controller import MotorController
from pidevices.hardware_interfaces.gpio_implementations import PiGPIO
from enum import Enum


class Side(Enum):
    LEFT = 0
    RIGHT = 1
    BOTH = 2
    NONE = 3
    


class DfrobotMotorControllerPiGPIO(MotorController):
    """Dfrobot motor controller implementation using hwpm pins. Extends 
    :class:`MotorController`.
    
    Args:
        E1 (int): The pwm pin number of the first pwm channel.
        M1 (int): Pin number of first direction pin.
        E2 (int): The pwm pin number of the second pwm channel.
        M2 (int): Pin number of second direction pin.
    """

    def __init__(self,
                 E1, M1,
                 E2, M2,
                 range,
                 name="", max_data_length=0):
        super(DfrobotMotorControllerPiGPIO, self).__init__(name, max_data_length)

        self._E1 = E1
        self._M1 = M1
        self._E2 = E2
        self._M2 = M2

        self._range = range

        self._gpio = PiGPIO()

    @property
    def E1(self):
        """Pin number of first pwm channel."""
        return self._E1

    @E1.setter
    def E1(self, E1):
        self._E1 = E1

    @property
    def E2(self):
        """Pin number of second pwm channel."""
        return self._E2

    @E2.setter
    def E2(self, E2):
        self._E2 = E2

    @property
    def M1(self):
        """Pin number of first direction pin."""
        return self._M1

    @M1.setter
    def M1(self, M1):
        self._M1 = M1

    @property
    def M2(self):
        """Pin number of second direction pin."""
        return self._M2

    @M2.setter
    def M2(self, M2):
        self._M2 = M2

    def _map(self, value, leftMin, leftMax, rightMin, rightMax):
        # Figure out how 'wide' each range is
        leftSpan = leftMax - leftMin
        rightSpan = rightMax - rightMin

        # Convert the left range into a 0-1 range (float)
        valueScaled = float(value - leftMin) / float(leftSpan)

        # Convert the 0-1 range into a value in the right range.
        return rightMin + (valueScaled * rightSpan)
    
    def start(self):
        self._gpio.add_pins(E1=self._E1)
        self._gpio.add_pins(E2=self._E2)
        self._gpio.add_pins(M1=self._M1)
        self._gpio.add_pins(M2=self._M2)

        self._gpio.set_pin_function('E1', 'output')
        self._gpio.set_pin_function('E2', 'output')
        self._gpio.set_pin_function('M1', 'output')
        self._gpio.set_pin_function('M2', 'output')

        self._gpio.set_pin_pwm('E1', True)
        self._gpio.set_pin_pwm('E2', True)

    def move_linear(self, linear_speed):
        

        if 0 <= linear_speed and linear_speed < self._range:
            linear_speed = self._map(linear_speed, 0.0, 1.0, 0.5, 1.0)
            self._gpio.write('M1', 1)
            self._gpio.write('M2', 0)
            self._gpio.write('E1', linear_speed)
            self._gpio.write('E2', linear_speed)
        elif 0 > linear_speed and linear_speed > -self._range:
            linear_speed = self._map(linear_speed, 0.0, -1.0, -0.5, -1.0)
            self._gpio.write('M1', 0)
            self._gpio.write('M2', 1)
            self._gpio.write('E1', -linear_speed)
            self._gpio.write('E2', -linear_speed)
           
    def move_angular(self, angular_speed):
        if 0 <= angular_speed and angular_speed < self._range:
            angular_speed = self._map(angular_speed, 0.0, 1.0, 0.5, 1.0)
            self._gpio.write('M1', 0)
            self._gpio.write('M2', 0)
            self._gpio.write('E1', angular_speed)
            self._gpio.write('E2', angular_speed)

        elif 0 > angular_speed and angular_speed > -self._range:
            angular_speed = self._map(angular_speed, 0.0, -1.0, -0.5, -1.0)
            self._gpio.write('M1', 1)
            self._gpio.write('M2', 1)
            self._gpio.write('E1', -angular_speed)
            self._gpio.write('E2', -angular_speed)

    def stop(self):
        self._gpio.write('E1', 0.0)
        self._gpio.write('E2', 0.0)
        self._gpio.write('M1', 0)
        self._gpio.write('M2', 0)

        self._gpio.set_pin_pwm('E1', False)
        self._gpio.set_pin_pwm('E2', False)

        self._gpio.close()

    
