"""servo_kit.py"""

from ..devices import Actuator
from .pca9685 import PCA9685


class ServoKit(Actuator):
    """Class representing multiple servos. Will be deprecated."""

    # TODO: Importing driver and not hardcoded
    def __init__(self, frequency, channels, name="", max_data_length=1):
        """Constructor
        
        Args:
            driver: Is a class representing the pwm driver.
        """

        super(ServoKit, self).__init__(name, max_data_length)
        self._channels = channels
        self._frequency = frequency
        self._driver = PCA9685(1, self._frequency)
        self.start()

    @property
    def driver(self):
        return self._driver

    @driver.setter
    def driver(self, driver):
        self._driver = driver

    @property
    def channels(self):
        return self._channels

    @channels.setter
    def channels(self, channels):
        self._channels = channels

    @property
    def frequency(self):
        return self._frequency

    @frequency.setter
    def frequency(self, frequency):
        self._frequency = frequency

    def start(self):
        """Init hardware and os resources."""
        self.driver.start()

    def stop(self):
        self.driver.stop()

    def write(self, channel, angle):
        self.driver.write(channel, self._angle_to_dc(angle))

    def _angle_to_dc(self, angle):
        """Frequency if how many overflows per sec. 1/f is the period or the 
           the overall time of duty cycle.

           1ms is equal to 0 degrees and 2ms is equal to 180 degrees
           Because pulse is not ideal we start from 0.75ms and finish at 2.25ms.
           Plot rump function.
        """

        min_pulse = 0.75
        max_pulse = 2.25
        pulse_range = max_pulse - min_pulse
        period = 1 / self.frequency
        pulse_time = (min_pulse + angle*(pulse_range/180)) * 10**-3 

        return pulse_time / period
