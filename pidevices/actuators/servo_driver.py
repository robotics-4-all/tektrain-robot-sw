"""servo_driver.py"""

from ..devices import Actuator

class ServoDriver(Actuator):
    """Class representing a servo driver. Extends :class:`Actuator`."""

    def _angle_to_dc(self, angle):
        """Frequency if how many overflows per sec. 1/f is the period or the 
        the overall time of duty cycle.

        1ms is equal to 0 degrees and 2ms is equal to 180 degrees
        Because pulse is not ideal we start from 0.75ms and finish at 2.25ms.
        TODO: Plot rump function.

        Args:
            angle: The angle in degrees.
        """

        min_pulse = 0.75
        max_pulse = 2.25
        pulse_range = max_pulse - min_pulse
        period = 1 / self.frequency
        pulse_time = (min_pulse + angle*(pulse_range/180)) * 10**-3 

        return pulse_time / period
