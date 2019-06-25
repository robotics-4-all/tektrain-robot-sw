from .line_follower import LineFollower
from time import sleep
from collections import namedtuple


cytron_res = namedtuple('cytron_res', ['so_1', 'so_2', 'so_3', 'so_4', 'so_5'])


class CytronLfLSS05(LineFollower):
    """Class representing cytron line sensor.
    
    Attributes:
    """
    
    _MODES = {"dark": 2, "bright": 3}
    _PULSE_TIME = 200
    _SLEEP_TIME = 0.001

    def __init__(self, so_1, so_2, 
                 so_3, so_4, so_5, 
                 cal=None, max_data_length=100, mode="dark", name=""):
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

        self._gpio = None

        self.start()

    def start(self):
        """Initializa hardware and os resources."""

        self._gpio = self.init_interface("gpio",
                                         so_1=self.so_1,
                                         so_2=self.so_2,
                                         so_3=self.so_3,
                                         so_4=self.so_4,
                                         so_5=self.so_5)

        # Init pins as input and pull down the resistors.
        self.hardware_interfaces[self._gpio].init_input("so_1", pull="down")
        self.hardware_interfaces[self._gpio].init_input("so_2", pull="down")
        self.hardware_interfaces[self._gpio].init_input("so_3", pull="down")
        self.hardware_interfaces[self._gpio].init_input("so_4", pull="down")
        self.hardware_interfaces[self._gpio].init_input("so_5", pull="down")

        # If calibration line pin is connected initialize it to high.
        if self.cal is not None:
            self.hardware_interfaces[self._gpio].add_pins(cal=self.cal)
            self.hardware_interfaces[self._gpio].init_output("cal", 1)

        # Settle hardware resources
        sleep(1)

        # Set mode
        self._control_cal(self._MODES[self.mode])

    def stop(self):
        self.hardware_interfaces[self._gpio].close()

    def read(self, SAVE=False):
        so_1_res = self.hardware_interfaces[self._gpio].read("so_1")
        so_2_res = self.hardware_interfaces[self._gpio].read("so_2")
        so_3_res = self.hardware_interfaces[self._gpio].read("so_3")
        so_4_res = self.hardware_interfaces[self._gpio].read("so_4")
        so_5_res = self.hardware_interfaces[self._gpio].read("so_5")

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
        self._control_cal(1)
        print("Calibration starts. Move the sensor over a line.")

    def _control_cal(self, pulses):
        """Control cal pin.
        
        The time between to falling edges need to be in range of 1.5 seconds

        Args:
            pulses: The number of pulses to send.
        """

        for i in range(pulses):
            self.hardware_interfaces[self._gpio].write("cal", 0)
            c = 0
            while c < self._PULSE_TIME:
                sleep(self._SLEEP_TIME)
                c += 1

            self.hardware_interfaces[self._gpio].write("cal", 1)
            c = 0
            while c < self._PULSE_TIME:
                sleep(self._SLEEP_TIME)
                c += 1

    # Setters and getters
    @property
    def so_1(self):
        return self._so_1

    @so_1.setter
    def so_1(self, so_1):
        self._so_1 = so_1

    @property
    def so_2(self):
        return self._so_2

    @so_2.setter
    def so_2(self, so_2):
        self._so_2 = so_2

    @property
    def so_3(self):
        return self._so_3

    @so_3.setter
    def so_3(self, so_3):
        self._so_3 = so_3

    @property
    def so_4(self):
        return self._so_4

    @so_4.setter
    def so_4(self, so_4):
        self._so_4 = so_4

    @property
    def so_5(self):
        return self._so_5

    @so_5.setter
    def so_5(self, so_5):
        self._so_5 = so_5

    @property
    def cal(self):
        return self._cal

    @cal.setter
    def cal(self, cal):
        self._cal = cal

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, mode):
        self._mode = mode
        self._control_cal(self._MODES[mode])
