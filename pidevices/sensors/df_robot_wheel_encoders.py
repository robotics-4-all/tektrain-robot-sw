"""df_robot_wheel_encoders.py"""

import atexit
import time
import math
from .wheel_encoders import WheelEncoder


class DfRobotWheelEncoder(WheelEncoder):
    """Class implementing df robot wheel encoders. Extends :class:`WheelEncoder`
    
    Args:
        pin_num: The pin number of encoder's signal.
    """

    # RESOLUTION = 20     # PPR value.
    # DIVISOR = 1         # Divisor of the resolution for faster measurment.
    # SLEEP_TIME = 0.001  # The sleep time in s

    def __init__(self, pin, name='', max_data_length=0):
        """Constructor."""
        atexit.register(self.stop)

        super(DfRobotWheelEncoder, self).__init__(name, max_data_length)

        self._pin_num = pin
        self._counter = 0
        self._gpio = -1

        self._res = 10
        self._timer = 0
        self._dt = 0

        self.start()

    @property
    def pin_num(self):
        """The pin number of encoder's signal."""
        return self._pin_num

    @pin_num.setter
    def pin_num(self, value):
        self._pin_num = value

    def start(self):
        """Initialize hardware and os resources."""
        pass

    def _handler(self, gpio, level, tick, *args):
        """Function for handling edge signals."""
        self._counter += 1

        self._dt = time.time() - self._timer
        self._timer = time.time()
    
    def read_state(self):
        """Get current state of encoder.
        
        Returns:
            An integer representing the state of the encoder.
        """

        return self.hardware_interfaces[self._gpio].read('signal')

    def read_counts(self):
        return self._counter

    def read(self):
        now = time.time()

        if (now - self._timer) > 0.5:
            rps = 0.0
        else:
            rps = 2 * math.pi / (self._res * self._dt)

        return {"rps": rps, "rpm": rps * 9.5492}        

    def stop(self):
        """Free hardware and os resources."""

        self.hardware_interfaces[self._gpio].close()



class DfRobotWheelEncoderPiGPIO(DfRobotWheelEncoder):
    def __init__(self, pin, name='', max_data_length=0):

        super(DfRobotWheelEncoderPiGPIO, self).__init__(pin, 
                                                         name,
                                                         max_data_length)

    def start(self):
        self._gpio = self.init_interface('gpio',
                                         impl='PiGPIO',
                                         signal=self._pin_num)

        self.hardware_interfaces[self._gpio].set_pin_function('signal', 'input')
        self.hardware_interfaces[self._gpio].set_pin_bounce('signal', 5)
        self.hardware_interfaces[self._gpio].set_pin_edge('signal', 'rising')
        self.hardware_interfaces[self._gpio].set_pin_event('signal', self._handler)





class DfRobotWheelEncoderRpiGPIO(DfRobotWheelEncoder):
    """Class implementing df robot wheel encoders using rpigpio library. 
    Extends :class:`DfRobotWheelEncoder`

    **UNTESTED**
    
    Args:
        pin_num (int): The pin number of encoder's signal.
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
                                                           self._handler)


class DfRobotWheelEncoderMcp23017(DfRobotWheelEncoder):
    """Class implementing df robot wheel encoders using mcp23017 gpio extender.
    Extends :class:`DfRobotWheelEncoder`
    
    Args:
        pin_num: The pin number of encoder's signal.
    """

    def __init__(self, pin, bus=1, address=0x20, name='', max_data_length=0):
        """Constructor."""

        self._bus = bus
        self._address = address

        print(f"starting with bus {bus} and address {address}")
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
                                                           self._handler)
        self.hardware_interfaces[self._gpio].start_polling('signal')

