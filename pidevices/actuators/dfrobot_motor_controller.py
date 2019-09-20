"""dfrobot_motor_controller.py"""

from collections import namedtuple
from math import pi
from .motor_controller import MotorController


# Channel
Channel = namedtuple("Channel", ["E", "M"])


class DfrobotMotorController(MotorController):
    """Dfrobot motor controller implementation using hwpm pins. Extends 
    :class:`MotorController`.
    
    Args:
        E1 (int): The pwm pin number of the first pwm channel.
        M1 (int): Pin number of first direction pin.
        E2 (int): The pwm pin number of the second pwm channel.
        M2 (int): Pin number of second direction pin.
        motor_1 : Optional instance of a motor object. Defaults to none.
        motor_2 : Optional instance of a motor object. Defaults to none.
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
        return self._frequency

    @frequency.setter
    def frequency(self, frequency):
        self._frequency = frequency

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

        self._gpio = self.init_interface("gpio", M1=self.M1, M2=self.M2)
        self._pwm_1 = self.init_interface("hpwm", pin=self.E1)
        self._pwm_2 = self.init_interface("hpwm", pin=self.E2)

        self._enable_side("M1", self._pwm_1)
        self._enable_side("M2", self._pwm_2)

        # Private namedtuples for handling each side.
        self._channel_1 = Channel(M="M1", E=self._pwm_1)
        self._channel_2 = Channel(M="M2", E=self._pwm_2)

        # Dictionary that maps each channel to a motor instance.
        self._motor_mapper = {self._channel_1: self.motor_1,
                              self._channel_2: self.motor_2}

    def _enable_side(self, gpio_pin, pwm):
        """Initialize direction and pwm pins.
        
        Args:
            gpio_pin (str): Name of the gpio direction pin.
            pwm (int): Index of hardware pwm hardware interface.
        """

        self.hardware_interfaces[self._gpio].set_pin_function(gpio_pin, "output")

        self.hardware_interfaces[pwm].frequency = self.frequency
        self.hardware_interfaces[pwm].duty_cycle = 0
        self.hardware_interfaces[pwm].enable = 1

    def _write_motor(self, channel, direction, speed, RPM):
        """Drive one motor writting to direction and pwm.
        
        Args:
            channel: Named tuple that has the direction pin name and the 
                hpwm index.
            direction: Direction value.
            speed: Speed value.
            RPM: Flag for choosing speed type.
        """
        self.hardware_interfaces[self._gpio].write(channel.M, direction)

        # Translate rpm to pwm duty cycle.
        if RPM:
            self._motor_mapper[channel].speed = speed
            speed = speed / self._motor_mapper[channel].rpm

        self.hardware_interfaces[channel.E].write(speed)
        
    def write(self, speed_1=None, speed_2=None, RPM=False):
        """Change motor's speed.
        
        Args:
            left_speed: Left motor speed. The value could be pwm duty cycle or
                rpm. Also for backward movement the value should be negative.
            right_speed: Right motor speed. The value could be pwm duty cycle or
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
        self.hardware_interfaces[self._gpio].close()
        self.hardware_interfaces[self._pwm_1].close()
        self.hardware_interfaces[self._pwm_2].close()


class Motor(object):
    """Abstract class for a motor.
    
    Args:
        v_spec: Voltage specification, at no load state
        rpm_spec: Rpm specification for v_spec at no load state
        voltage: The power suply voltage.
        
    """

    def __init__(self, v_spec, rpm_spec, voltage):
        """Contructor"""

        self.speed = 0
        self._k = self._compute_k(v_spec, rpm_spec)
        self._voltage = voltage
        self._rpm = (voltage/self._k * 60) / (2 * pi)

    @property
    def k(self):
        """Get k"""
        return self._k

    @property
    def voltage(self):
        """Voltage in use."""
        return self._voltage

    @property
    def rpm(self):
        """Max rpm value given the voltage in use."""
        return self._rpm

    def _compute_k(self, voltage, rpm):
        """Compute k from V and rpm at no-load state."""
        return voltage / (rpm * (1/60. * 2*pi))

    def set_parameters(self, voltage):
        """Set the voltage and compute the new max rpm value at no load-state.
        
        Args:
            voltage: The power suply voltage.
        """
        self._voltage = voltage
        self._rpm = (voltage/self._k * 60) / (2 * pi)
