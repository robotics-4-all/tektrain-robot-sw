"""df_robot_wheel_encoders.py"""
from .wheel_encoders import WheelEncoder
import atexit
import time
import math


class DfRobotWheelEncoder(WheelEncoder):
    """Class implementing df robot wheel encoders. Extends :class:`WheelEncoder`
    
    Args:
        pin_num: The pin number of encoder's signal.
    """
    RPM_PER_RPS = 9.5492

    def __init__(self, pin, resolution=10, name='', max_data_length=0):
        """Constructor."""

        # initialize base constructor
        super(DfRobotWheelEncoder, self).__init__(name, max_data_length)

        # track variables
        self._pin_num = pin
        self._res = resolution

        self._gpio = -1

        self._counter = 0
        self._timer = 0
        self._dt = 0
        self._started = False

        self.start()

        # register as cleanup function after execution .stop function
        atexit.register(self.stop)

    @property
    def pin_num(self):
        """The pin number of encoder's signal."""
        return self._pin_num

    @pin_num.setter
    def pin_num(self, value):
        self._pin_num = value

    @property
    def counts(self):
        """The number of encoder ticks since beginning"""

        return self._counter
    
    @counts.setter
    def counts(self, value):
        if value >= 0:
            self._counter = value

    def start(self):
        """Initialize hardware and os resources."""

        self._started = True

    def _cbf(self, gpio, level, tick, *args):
        """Callback function which records timestamps and tick between encoder pulses."""
        
        self._dt = time.time() - self._timer
        self._timer = time.time()
        self._counter += 1
        
    def state(self):
        """Get current state of encoder.
        
        Returns:
            An integer representing the state of the encoder.
        """

        return self.hardware_interfaces[self._gpio].read('signal')

    def read(self):
        """Return the last recorded value of the encoder.

        Returns:
            A dictionary with the rps and rps of the wheel attached to the encoder.
        """

        if self._dt is not 0:
            rps = 2 * math.pi / (self._res * self._dt)
        else:
            rps = 0.0

        return {"rps": rps, "rpm": self._rpsToRpm(rps)}     

    def _rpsToRpm(self, rps):
        """ Convert rps to rpm."""

        return (self.RPM_PER_RPS * rps)

    def stop(self):
        """Free hardware and os resources."""

        if self._started:
            self.hardware_interfaces[self._gpio].close()
            self._started = False
        


class DfRobotWheelEncoderPiGPIO(DfRobotWheelEncoder):
    """Class implementing df robot wheel encoders using pigpio library. 
    Extends :class:`DfRobotWheelEncoder`

    **UNTESTED**
    
    Args:
        pin_num (int): The pin number of encoder's signal.
    """

    def __init__(self, pin, resolution, name='', max_data_length=0):

        super(DfRobotWheelEncoderPiGPIO, self).__init__(pin, 
                                                        resolution,
                                                        name,
                                                        max_data_length)        
    def start(self):
        """Initialize hardware and os resources once."""

        if self._started:
            return
        else:
            self._started = True

        print("Starting")

        self._gpio = self.init_interface('gpio',
                                         impl='PiGPIO',
                                         signal=self.pin_num)

        # Init pin
        self.hardware_interfaces[self._gpio].set_pin_function('signal', 'input')
        self.hardware_interfaces[self._gpio].set_pin_bounce('signal', 25)
        self.hardware_interfaces[self._gpio].set_pin_edge('signal', 'rising')
        self.hardware_interfaces[self._gpio].set_pin_event('signal', self._cbf)


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
                                                           self._cbf)


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
                                                           self._cbf)
        self.hardware_interfaces[self._gpio].start_polling('signal')

