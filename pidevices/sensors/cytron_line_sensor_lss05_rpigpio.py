"""cytron_line_sensor_lss05_rpigpio.py"""

from time import sleep
from .cytron_line_sensor_lss05 import CytronLfLSS05


class CytronLfLSS05Rpi(CytronLfLSS05):
    """Class implementing the driver of cytron line sensor using rpi.gpio 
    implementation. Extends :class:`CytronLfLSS05`
    
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

    def __init__(self, so_1, so_2, 
                 so_3, so_4, so_5, 
                 mode="dark", cal=None,
                 max_data_length=100, name=""):
        "Constructor"

        super(CytronLfLSS05Rpi, self).__init__(so_1, so_2, so_3,
                                               so_4, so_5, mode,
                                               cal, max_data_length, name)

    def start(self):
        """Init hardware and os resources."""

        self.gpio = self.init_interface("gpio",
                                        so_1=self.so_1,
                                        so_2=self.so_2,
                                        so_3=self.so_3,
                                        so_4=self.so_4,
                                        so_5=self.so_5)

        # Init pins as input and pull down the resistors.
        self.hardware_interfaces[self.gpio].init_input("so_1", pull="down")
        self.hardware_interfaces[self.gpio].init_input("so_2", pull="down")
        self.hardware_interfaces[self.gpio].init_input("so_3", pull="down")
        self.hardware_interfaces[self.gpio].init_input("so_4", pull="down")
        self.hardware_interfaces[self.gpio].init_input("so_5", pull="down")

        # If calibration line pin is connected initialize it to high.
        if self.cal is not None:
            self.hardware_interfaces[self.gpio].add_pins(cal=self.cal)
            self.hardware_interfaces[self.gpio].init_output("cal", 1)

            # Set mode
            self._control_cal(self._MODES[self.mode])

        # Settle hardware resources
        sleep(1)
