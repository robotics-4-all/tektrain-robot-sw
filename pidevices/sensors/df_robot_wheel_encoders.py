"""df_robot_wheel_encoders.py"""

from .wheel_encoders import WheelEncoder


class DfRobotWheelEncoder(WheelEncoder):
    """Class implementing df robot wheel encoders. Extends :class:WheelEncoder
    
    Args:
        pin_num: The pin number of encoder's signal.
    """

    RESOLUTION = 20

    def __init__(self, pin, name='', max_data_length=0):
        """Constructor."""

        super(DfRobotWheelEncoder, self).__init__(name, max_data_length)
        self._pin_num = pin
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

        self._gpio = self.init_interface('gpio',
                                         impl='RPiGPIO',
                                         signal=self.pin_num)

        # Init pin
        self.hardware_interfaces[self._gpio].init_input('signal', 'down')
        #self.hardware_interfaces[self._gpio].set_pin_edge('signal', 'both')
        #self.hardware_interfaces[self._gpio].set_pin_event('signal', )

    def read(self):
        """Get current state of encoder.
        
        Returns:
            An integer representing the state of the encoder.
        """

        return self.hardware_interfaces[self._gpio].read('signal')

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
        self.hardware_interfaces[self._gpio].init_input('signal', 'down')
        #self.hardware_interfaces[self._gpio].set_pin_edge('signal', 'both')
        #self.hardware_interfaces[self._gpio].set_pin_event('signal', )


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
        #self.hardware_interfaces[self._gpio].init_input('signal', 'down')
        #self.hardware_interfaces[self._gpio].set_pin_edge('signal', 'both')
        #self.hardware_interfaces[self._gpio].set_pin_event('signal', )
