"""dfrobot_motor_controller_pca9685.py"""

from collections import namedtuple
from math import pi
from .motor_controller import MotorController
from .pca9685 import PCA9685
from .dfrobot_motor_controller import Motor


# Channel
Channel = namedtuple("Channel", ["E", "M"])


class DfrobotMotorControllerPCA(MotorController):
    """Dfrobot motor controller implementation using hwpm pins. Extends 
    :class:`MotorController`.
    
    Args:
        E1 (int): The pwm channel of the first pwm channel.
        M1 (int): The pwm channel of the first direction pin.
        E2 (int): The pwm channel of the second pwm channel.
        M2 (int): The pwm channle of second direction pin.
        motor_1 : Optional instance of a motor object. Defaults to none.
        motor_2 : Optional instance of a motor object. Defaults to none.
    """

    _FREQUENCY = 50

    def __init__(self, bus,
                 E1, M1,
                 E2, M2,
                 motor_1=None, motor_2=None,
                 name="", max_data_length=0):
        super(DfrobotMotorControllerPCA, self).__init__(name, max_data_length)

        self._bus = bus

        # Motor objects
        self._motor_1 = motor_1
        self._motor_2 = motor_2

        # Motor channels                     
        self._E1 = E1
        self._M1 = M1
        self._E2 = E2
        self._M2 = M2
                                  
        # PWM frequency                  
        self._frequency = self._FREQUENCY
        self._gpio = None
        self._pwm_1 = None
        self._pwm_2 = None

        self.start() 

    @property
    def bus(self):
        """Pin number of first pwm channel."""
        return self._bus

    @bus.setter
    def bus(self, value):
        self._bus = value

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

    @property
    def frequency(self):
        """Frequency of pwm channels."""
        return self._device.frequency

    @frequency.setter
    def frequency(self, frequency):
        self._device.frequency = frequency

    @property
    def motor_1(self):
        """Motor 1 instance."""
        return self._motor_1

    @motor_1.setter
    def motor_1(self, motor_1):
        self._motor_1 = motor_1

    @property
    def motor_2(self):
        """Motor 2 instance."""
        return self._motor_2

    @motor_2.setter
    def motor_2(self, motor_2):
        self._motor_2 = motor_2

    def start(self):
        """Initialize hardware and os resources."""

        # Initiate pca9685 object
        self._device = PCA9685(self._bus, self._frequency)

        # Private namedtuples for handling each side.
        self._channel_1 = Channel(M=self.M1, E=self.E1)
        self._channel_2 = Channel(M=self.M2, E=self.E2)

        # Dictionary that maps each channel to a motor instance.
        self._motor_mapper = {self._channel_1: self.motor_1,
                              self._channel_2: self.motor_2}

    def _write_motor(self, channel, direction, speed, RPM):
        """Drive one motor writting to direction and pwm.
        
        Args:
            channel: Named tuple that has the direction pin name and the 
                hpwm index.
            direction: Direction value.
            speed: Speed value.
            RPM: Flag for choosing speed type.
        """
        self._device.write(channel.M, direction)

        # Translate rpm to pwm duty cycle.
        if RPM:
            self._motor_mapper[channel].speed = speed
            speed = speed / self._motor_mapper[channel].rpm

        self._device.write(channel.E, speed)
        
    def write(self, speed_1=None, speed_2=None, RPM=False):
        """Change motor's speed.
        
        Args:
            speed_1: Channel 1 speed. The value could be pwm duty cycle or
                rpm. Also for backward movement the value should be negative.
            speed_2: Channel 2 speed. The value could be pwm duty cycle or
                rpm. Also for backward movement the value should be negative.
            RPM (boolean): Flag stating the mode of the speed values. Defaults
                to :data:`False`.
        """

        if speed_1 is not None:
            direction = int(speed_1 >= 0)
            self._write_motor(self._channel_1, direction, abs(speed_1), RPM)

        if speed_2 is not None:
            direction = int(speed_2 >= 0)
            self._write_motor(self._channel_2, direction, abs(speed_2), RPM)

    def stop(self):
        """Clear hardware and os resources."""
        self._device.stop()
