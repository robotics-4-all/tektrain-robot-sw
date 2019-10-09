"""cytron_line_sensor_lss05.py"""

from .line_follower import LineFollower
from time import sleep
from collections import namedtuple
from ..exceptions import InvalidMode


cytron_res = namedtuple('cytron_res', ['so_1', 'so_2', 'so_3', 'so_4', 'so_5'])


class CytronLfLSS05(LineFollower):
    """Class representing cytron line sensor.
    
    Args:
        so_1 (int): BCM pin number for first ir sensor.
        so_2 (int): BCM pin number for second ir sensor.
        so_3 (int): BCM pin number for third ir sensor.
        so_4 (int): BCM pin number for fourth ir sensor.
        so_5 (int): BCM pin number for fifth ir sensor.
        mode (str): Working mode of the sensor. Valid values dark(the
            sensor returns one for dark line) and bright(the sesnor returns
            one for bright line). Defaults to dark.
        cal: Calibration pin BCM number. Defaults to None for disconnected 
            calibration pin.
    """
    
    _MODES = {"dark": 2, "bright": 3}
    _PULSE_TIME = 200
    _SLEEP_TIME = 0.001

    def __init__(self, so_1, so_2, 
                 so_3, so_4, so_5, 
                 mode="dark", cal=None,
                 max_data_length=100, name=""):
        # Frequency in hz, min/max_dist in meters
        super(CytronLfLSS05, self).__init__(name, max_data_length)
        self.max_frequency = 100
        self.max_dist = 4
        self.min_dist = 1

        # Init pin numbers
        self._so_1 = so_1
        self._so_2 = so_2
        self._so_3 = so_3
        self._so_4 = so_4
        self._so_5 = so_5
        self._cal = cal

        # Working mode
        if mode not in self._MODES.keys():
            # Print warning that the default dark mode will be used
            print("Invalid mode, dark mode will be used.")
            mode = "dark"
        self._mode = mode

        self.start()

    @property
    def so_1(self):
        """BCM number of 1st ir sensor."""
        return self._so_1

    @so_1.setter
    def so_1(self, so_1):
        self._so_1 = so_1

    @property
    def so_2(self):
        """BCM number of 2nd ir sensor."""
        return self._so_2

    @so_2.setter
    def so_2(self, so_2):
        self._so_2 = so_2

    @property
    def so_3(self):
        """BCM number of 3rd ir sensor."""
        return self._so_3

    @so_3.setter
    def so_3(self, so_3):
        self._so_3 = so_3

    @property
    def so_4(self):
        """BCM number of 4th ir sensor."""
        return self._so_4

    @so_4.setter
    def so_4(self, so_4):
        self._so_4 = so_4

    @property
    def so_5(self):
        """BCM number of 5th ir sensor."""
        return self._so_5

    @so_5.setter
    def so_5(self, so_5):
        self._so_5 = so_5

    @property
    def cal(self):
        """BCM number of calibration pin."""
        return self._cal

    @cal.setter
    def cal(self, cal):
        self._cal = cal

    @property
    def mode(self):
        """Working mode of sensor. Valid value dark and bright."""
        return self._mode

    @mode.setter
    def mode(self, mode):
        if mode not in self._MODES:
            raise InvalidMode("Invalid sensor mode.")

        self._mode = mode
        self._control_cal(self._MODES[mode])

    @property
    def gpio(self):
        return self._gpio

    @gpio.setter
    def gpio(self, value):
        self._gpio = value

    def start(self):
        """Init hardware and os resources.
        
        Will be overloaded from specific implementations.
        """
        pass

    def stop(self):
        """Free hardware and os resources."""
        self.hardware_interfaces[self.gpio].close()

    def read(self, SAVE=False):
        """Read a measurment from sensor.
        
        Args:
            SAVE: Flag for saving measurments to the data list.

        Returns:
            An named tuple with every sensor measurment.
            The format is (so_1, so_2, so_3, so_4, so_5).
        """

        so_1_res = self.hardware_interfaces[self.gpio].read("so_1")
        so_2_res = self.hardware_interfaces[self.gpio].read("so_2")
        so_3_res = self.hardware_interfaces[self.gpio].read("so_3")
        so_4_res = self.hardware_interfaces[self.gpio].read("so_4")
        so_5_res = self.hardware_interfaces[self.gpio].read("so_5")

        res = cytron_res(so_1=so_1_res,
                         so_2=so_2_res,
                         so_3=so_3_res,
                         so_4=so_4_res,
                         so_5=so_5_res,
                         )
        if SAVE:
            self.update_data(res)

        return res

    def calibrate(self):
        """Calibrate sensor."""

        self._control_cal(1)
        print("Calibration starts. Move the sensor over a line.")

    def _control_cal(self, pulses):
        """Control cal pin.
        
        The time between to falling edges need to be in range of 1.5 seconds

        Args:
            pulses: The number of pulses to send.
        """

        for i in range(pulses):
            self.hardware_interfaces[self.gpio].write("cal", 0)
            c = 0
            while c < self._PULSE_TIME:
                sleep(self._SLEEP_TIME)
                c += 1

            self.hardware_interfaces[self.gpio].write("cal", 1)
            c = 0
            while c < self._PULSE_TIME:
                sleep(self._SLEEP_TIME)
                c += 1
