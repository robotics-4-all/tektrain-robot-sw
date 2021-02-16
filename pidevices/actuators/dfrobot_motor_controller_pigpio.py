from .motor_controller import MotorController
from pidevices.hardware_interfaces.gpio_implementations import PiGPIO
from collections import namedtuple
from enum import Enum

Channel = namedtuple('Channel',['E', 'M'])  
Pin = namedtuple('Pin', ['name', 'number'])

class ChannelPos(Enum):
    LEFT = 0
    RIGHT = 1

class DfrobotMotorControllerPiGPIO(MotorController):
    """Dfrobot motor controller implementation using hwpm pins. Extends
    :class:`MotorController`.

    Args:
        E1 (int): The pwm pin number of the first pwm channel.
        M1 (int): Pin number of first direction pin.
        E2 (int): The pwm pin number of the second pwm channel.
        M2 (int): Pin number of second direction pin.
    """

    MotionDir = {
        'BACKWARD': 0,
        'FORWARD': 1
    }

    RESOLUTION = 1000
    FREQUENCY = 250
    MAX_PWM = 1.0

    def __init__(self,
                 E1, M1,
                 E2, M2,
                 resolution = None,
                 frequency = None,
                 name="", max_data_length=0):
        super(DfrobotMotorControllerPiGPIO, self).__init__(name, max_data_length)

        e1_pin = Pin('E1', E1)
        m1_pin = Pin('M1', M1)
        e2_pin = Pin('E2', E2)
        m2_pin = Pin('M2', M2)

        self._channel_left = Channel(e1_pin, m1_pin)
        self._channel_right = Channel(e2_pin, m2_pin)
        
        self._res = DfrobotMotorControllerPiGPIO.RESOLUTION if resolution == None else resolution
        self._freq = DfrobotMotorControllerPiGPIO.FREQUENCY if frequency == None else frequency

        self._gpio = PiGPIO()

        self._gpio.add_pins(E1=E1)
        self._gpio.add_pins(M1=M1)
        self._gpio.add_pins(E2=E2)
        self._gpio.add_pins(M2=M2)

        self._is_init = False

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

    def start(self):
        if not self._is_init:
            self._is_init = True

            self._init_channel(self._channel_left)
            self._init_channel(self._channel_right)

    def _init_channel(self, channel):
        self._gpio.set_pin_function(channel.E.name, 'output')
        self._gpio.set_pin_function(channel.M.name, 'output')

        self._gpio.set_pin_pwm(channel.E.name, True)
        self._gpio.set_pin_range(channel.E.name, self._res)
        self._gpio.set_pin_frequency(channel.E.name, self._freq)

    def write(self, pwm_left, pwm_right):
        if not self._is_init:
            return

        if pwm_left == 0.0 and pwm_right == 0.0:
            self._write_channel(self._channel_left, 0.0, self.MotionDir['FORWARD'])
            self._write_channel(self._channel_right, 0.0, self.MotionDir['BACKWARD'])
        else:
            # keep the sign
            sign_left = self.MotionDir['FORWARD'] if pwm_left >= 0 else self.MotionDir['BACKWARD']
            sign_right = self.MotionDir['BACKWARD'] if pwm_right >= 0 else self.MotionDir['FORWARD']

            pwm_left = abs(pwm_left)
            pwm_right = abs(pwm_right)

            # normalize if needed
            max_pwm = max(pwm_left, pwm_right)

            if max_pwm <= DfrobotMotorControllerPiGPIO.MAX_PWM:
                self._write_channel(self._channel_left, pwm_left, sign_left)
                self._write_channel(self._channel_right, pwm_right, sign_right)
            else:
                n = 1 / max_pwm

                pwm_left = n * pwm_left
                pwm_right = n * pwm_right

                self._write_channel(self._channel_left, pwm_left, sign_left)
                self._write_channel(self._channel_right, pwm_right, sign_right)

    def _write_channel(self, channel, pwm, sign):
        self._gpio.write(channel.M.name, sign)
        self._gpio.write(channel.E.name, pwm)
    
    def stop(self):
        if self._is_init:
            self._is_init = False
            
            self.write(0.0, 0.0)

            self._gpio.set_pin_pwm(self._channel_left.E.name, False)
            self._gpio.set_pin_pwm(self._channel_right.E.name, False)

            self._gpio.close()
        


