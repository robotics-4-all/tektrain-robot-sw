"""df_robot_wheel_encoders.py"""

import atexit
import time
from .wheel_encoders import WheelEncoder


class DfRobotWheelEncoder(WheelEncoder):
    """Class implementing df robot wheel encoders. Extends :class:WheelEncoder
    
    Args:
        pin_num: The pin number of encoder's signal.
    """

    RESOLUTION = 20     # PPR value.
    DIVISOR = 1         # Divisor of the resolution for faster measurment.
    SLEEP_TIME = 0.001  # The sleep time in s

    def __init__(self, pin, name='', max_data_length=0):
        """Constructor."""

        atexit.register(self.stop)
        super(DfRobotWheelEncoder, self).__init__(name, max_data_length)
        self._pin_num = pin
        self._counter = 0  # Counter that counts the edge signals
        self.res = self.RESOLUTION

        self.start()

    @property
    def pin_num(self):
        """The pin number of encoder's signal."""
        return self._pin_num

    @pin_num.setter
    def pin_num(self, value):
        self._pin_num = pin_num

    def start(self):
        """Initialize hardware and os resources."""
        pass

    def _int_handler(self):
        """Function for handling edge signals."""
        self._counter += 1

    def read(self):
        """Get current state of encoder.
        
        Returns:
            An integer representing the state of the encoder.
        """

        return self.hardware_interfaces[self._gpio].read('signal')

    def read_rpm(self, save=False):
        """Get rpm value of wheel.
        
        Count until res/divisor pulses and then use the interval to compute
        the rounds per minute.

        Args:
            save: Flag for saving the measurment to device data deque.

        Returns:
            A number indicating the rpm value of the wheel.
        """

        # Initial value of counter
        init_count = self._counter
        count = 0
        it = 0

        # Measure time after limit pulses
        rpm = -1
        limit = self.res / self.DIVISOR
        t_s = time.time()
        while count < limit:
            count = self._counter - init_count

            # Use it to break in case of too slow speed value
            it += 1
            if(it > 100) and not count:
                rpm = 0
                break
            time.sleep(self.SLEEP_TIME)

        if rpm is -1:
            interval = time.time() - t_s
            rpm = (60 / (interval*self.DIVISOR))
        
        if save:
            self.update_data(rpm)

        return rpm

    def stop(self):
        """Free hardware and os resources."""

        self.hardware_interfaces[self._gpio].close()


class DfRobotWheelEncoderRpiGPIO(DfRobotWheelEncoder):
    """Class implementing df robot wheel encoders using rpigpio library. 
    Extends :class:DfRobotWheelEncoder
    
    Args:
        pin_num: The pin number of encoder's signal.
    """

    def __init__(self, pin, name='', max_data_length=0):
        """Constructor."""

        super(DfRobotWheelEncoderRpiGPIO, self).__init__(pin, 
                                                         name,
                                                         max_data_length)

    def start(self):
        """Initialize hardware and os resources."""

        self._gpio = self.init_interface('gpio',
                                         impl='RPiGPIO',
                                         signal=self.pin_num)

        # Init pin
        self.hardware_interfaces[self._gpio].set_pin_function('signal', 'input')
        self.hardware_interfaces[self._gpio].init_input('signal', 'down')
        self.hardware_interfaces[self._gpio].set_pin_edge('signal', 'rising')
        self.hardware_interfaces[self._gpio].set_pin_event('signal', 
                                                           self._int_handler)


class DfRobotWheelEncoderMcp23017(DfRobotWheelEncoder):
    """Class implementing df robot wheel encoders using mcp23017 gpio extender.
    Extends :class:DfRobotWheelEncoder
    
    Args:
        pin_num: The pin number of encoder's signal.
    """

    def __init__(self, pin, bus=1, address=0x20, name='', max_data_length=0):
        """Constructor."""

        self._bus = bus
        self._address = address

        super(DfRobotWheelEncoderMcp23017, self).__init__(pin, 
                                                          name,
                                                          max_data_length)

    def start(self):
        """Initialize hardware and os resources."""

        self._gpio = self.init_interface('gpio',
                                         impl='Mcp23017GPIO',
                                         bus=self._bus,
                                         address=self._address,
                                         signal=self.pin_num)

        # Init pin
        self.hardware_interfaces[self._gpio].set_pin_function('signal', 'input')
        self.hardware_interfaces[self._gpio].init_input('signal', 'down')
        self.hardware_interfaces[self._gpio].set_pin_edge('signal', 'both')
        self.hardware_interfaces[self._gpio].set_pin_event('signal', 
                                                           self._int_handler)
        self.hardware_interfaces[self._gpio].start_polling('signal')

