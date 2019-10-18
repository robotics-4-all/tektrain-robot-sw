"""button.py"""

from ..devices import Sensor


class Button(Sensor):
    """A single button extends :class:`Sensor`.
    
    Args:
        pin_num (int): BCM number of the pin.
        direction (str): Indicating the it will use pull up or pull down resistor
            . Could be :data:`up` or data:`down`.
        bounce (int): The bounce time of the button. Defaults to 200ms
    """

    def __init__(self, pin_num,
                 direction, bounce=200,
                 name='', max_data_length=0):
        """Constructor"""

        super(Button, self).__init__(name, max_data_length)
        self._pin_num = pin_num
        self._dir = direction
        self._bounce = bounce

        self.start()

    @property
    def pin_num(self):
        """The bcm pin number."""
        return self._pin_num

    @pin_num.setter
    def pin_num(self, value):
        self._pin_num = value

    @property
    def dir(self):
        """The direction of the pull resistor."""
        return self._dir

    @dir.setter
    def dir(self, value):
        self._dir = value

    @property
    def bounce(self):
        """The bounceection of the pull resistor."""
        return self._bounce

    @bounce.setter
    def bounce(self, value):
        self._bounce = value

    def start(self):
        """Init hardware and os resources."""

        self._gpio = self.init_interface('gpio',
                                         impl=self._impl,
                                         button=self.pin_num)

        self.hardware_interfaces[self._gpio].init_input('button', self._dir)

        self.hardware_interfaces[self._gpio].set_pin_bounce('button', 
                                                            self._bounce)
        edge = "falling" if self._dir is 'up' else "rising"
        self._hardware_interfaces[self._gpio].set_pin_edge('button', edge)
    
    def read(self):
        """Read current state of button.
        
        Returns:
            An int that represents the state of the button. 0 for not pressed
            1 for pressed.
        """

        return self.hardware_interfaces[self._gpio].read('button')

    def when_pressed(self, func, *args):
        """Set the function to be called when the button is pressed.
        
        Set a function for asynchronous call when the button is pressed.

        Args:
            func (function): The function.
            *args: Arguments for the function.
        """

        self.hardware_interfaces[self._gpio].set_pin_event('button', func, *args)

    def wait_for_press(self):
        """Wait to be pressed"""

        self.hardware_interfaces[self._gpio].wait_pin_for_edge('button')

    def stop(self):
        """Free hardware and os resources."""

        self.hardware_interfaces[self._gpio].close()


class ButtonRPiGPIO(Button):
    """A single button with rpigpio implementation extends :class:`Button`.
    
    Args:
        pin_num (int): BCM number of the pin.
        direction (str): Indicating the it will use pull up or pull down resistor
            . Could be :data:`up` or data:`down`.
        bounce (int): The bounce time of the button. Defaults to 200ms
    """
    
    def __init__(self, pin_num,
                 direction, bounce=200,
                 name='', max_data_length=0):
        """Constructor"""

        self._impl = "RPiGPIO"
        super(ButtonRPiGPIO, self).__init__(pin_num, direction, bounce, 
                                            name, max_data_length)


class ButtonMcp23017(Button):
    """A single button with mcp23017 implementation extends :class:`Button`.
    
    Args:
        pin_num (int): The module's pin number.
        direction (str): Indicating the it will use pull up or pull down resistor
            . Could be :data:`up` or data:`down`.
        bounce (int): The bounce time of the button. Defaults to 200ms
    """
    
    def __init__(self, pin_num,
                 direction, bounce=200,
                 name='', max_data_length=0):
        """Constructor"""

        self._impl = "Mcp23017GPIO"
        super(ButtonMcp23017, self).__init__(pin_num, direction, bounce,
                                             name, max_data_length)

    def when_pressed(self, func, *args):
        """Set the function to be called when the button is pressed.
        
        Set a function for asynchronous call when the button is pressed.

        Args:
            func (function): The function.
            *args: Arguments for the function.
        """

        self.hardware_interfaces[self._gpio].set_pin_event('button', func, *args)
        self.hardware_interfaces[self._gpio].start_polling('button')
