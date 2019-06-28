from .motor_controller import MotorController
from collections import namedtuple


# Channel
Channel = namedtuple("Channel", ["E", "M"])


class DfrobotMotorController(MotorController):
    """Dfrobot motor controller implmenentation.
    
    Attributes:
    """

    _FREQUENCY = 20

    def __init__(self,
                 E1, M1,
                 E2, M2,
                 motor_1=None, motor_2=None,
                 name="", max_data_length=0):
        super(DfrobotMotorController, self).__init__(name, max_data_length)

        # Motor objects
        self._motor_1 = motor_1
        self._motor_2 = motor_2

        # Motor pins                     
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

    def _enable_side(self, gpio_pin, pwm):
        self.hardware_interfaces[self._gpio].set_pin_function(gpio_pin, "output")

        self.hardware_interfaces[pwm].frequency = self.frequency
        self.hardware_interfaces[pwm].duty_cycle = 0
        self.hardware_interfaces[pwm].enable = 1

    def start(self):
        # Initialize hardware interfaces
        self._gpio = self.init_interface("gpio", M1=self.M1, M2=self.M2)
        self._pwm_1 = self.init_interface("hpwm", pin=self.E1)
        self._pwm_2 = self.init_interface("hpwm", pin=self.E2)

        self._enable_side("M1", self._pwm_1)
        self._enable_side("M2", self._pwm_2)

        self._channel_1 = Channel(M="M1", E=self._pwm_1)
        self._channel_2 = Channel(M="M2", E=self._pwm_2)

        self._motor_mapper = {self.channel_1: self.motor_1,
                              self.channel_2: self.motor_2}

    def _write_motor(self, channel, direction, speed, RPM):
        self.hardware_interfaces[self._gpio].write(channel.M, direction)

        if RPM:
            self.motor_mapper[channel].speed = speed
            speed = speed / self.motor_mapper[channel].rpm

        self.hardware_interfaces[channel.E].write(speed)
        
    def write(self, speed_1=None, speed_2=None, RPM=False):
        """Drive left and right motor.
        
        Args:
            left_speed:
            right_speed:
            RPM:
        """

        if speed_1 is not None:
            direction = int(speed_1 >= 0)
            self._write_motor(self.channel_1, direction, abs(speed_1), RPM)

        if speed_2 is not None:
            direction = int(speed_2 >= 0)
            self._write_motor(self.channel_2, direction, abs(speed_2), RPM)

    def stop(self):
        self.hardware_interfaces[self._gpio].close()
        self.hardware_interfaces[self._pwm_1].close()
        self.hardware_interfaces[self._pwm_2].close()

    @property
    def E1(self):
        return self._E1

    @E1.setter
    def E1(self, E1):
        self._E1 = E1

    @property
    def E2(self):
        return self._E2

    @E2.setter
    def E2(self, E2):
        self._E2 = E2

    @property
    def M1(self):
        return self._M1

    @M1.setter
    def M1(self, M1):
        self._M1 = M1

    @property
    def M2(self):
        return self._M2

    @M2.setter
    def M2(self, M2):
        self._M2 = M2

    @property
    def frequency(self):
        return self._frequency

    @frequency.setter
    def frequency(self, frequency):
        self._frequency = frequency

    @property
    def motor_1(self):
        return self._motor_1

    @motor_1.setter
    def motor_1(self, motor_1):
        self._motor_1 = motor_1

    @property
    def motor_2(self):
        return self._motor_2

    @motor_2.setter
    def motor_2(self, motor_2):
        self._motor_2 = motor_2

    @property
    def channel_1(self):
        return self._channel_1

    @channel_1.setter
    def channel_1(self, channel_1):
        self._channel_1 = channel_1
        
    @property
    def channel_2(self):
        return self._channel_2

    @channel_2.setter
    def channel_2(self, channel_2):
        self._channel_2 = channel_2

    @property
    def motor_mapper(self):
        return self._motor_mapper

    @motor_mapper.setter
    def motor_mapper(self, motor_mapper):
        self._motor_mapper = motor_mapper
