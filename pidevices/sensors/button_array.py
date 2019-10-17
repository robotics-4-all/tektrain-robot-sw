"""button_array.py"""

from ..devices import Sensor
from .button import ButtonRPiGPIO, ButtonMcp23017


class ButtonArray(Sensor):
    """An array of buttons, extends :class:`Sensor`.
    
    Args:
        pin_nums: List with the gpio numbers for buttons.
    """

    def __init__(self, pin_nums, name='', max_data_length=0):
        """Constructor"""

        super(ButtonArray, self).__init__(name, max_data_length)
        self._pin_nums = pin_nums
        self._buttons = {}

        self.start()

    @property
    def pin_nums(self):
        """List with the gpio numbers for buttons."""
        return self._pin_nums

    @pin_nums.setter
    def pin_nums(self, value):
        self._pin_nums = value

    @property
    def buttons(self):
        """List with the instances of :class:`Button`."""
        return self._buttons

    def start(self):
        """Init hardware and os resources."""
        
        for pin_num in self.pin_nums:
            self.buttons[pin_num] = self._button_class(pin_num)
    
    def read(self, button):
        """Read current state of button.
        
        Args:
            button (int): The number of the button.

        Returns:
            An int with the button's current state.
        """

        return self.buttons[button].read()

    def when_pressed(self, button, func, *args):
        """Set the function to be called when a button is pressed.
        
        Set a function for asynchronous call when the button is pressed.

        Args:
            button (int): The number of the button.
            func (function): The function.
            *args: Arguments for the function.
        """

        self.buttons[button].when_pressed(func, *args)

    def wait_for_press(self, button):
        """Wait to be pressed
        
        Args:
            button (int): The number of the button.
        """
        
        self.buttons[button].wait_for_press()

    def stop(self):
        """Free hardware and os resources."""

        for button in self.buttons:
            button.stop()
            del button
    
    def add_button(self, pin_num):
        """Add a button to the array.
        
        Args:
            pin_num (int): BCM number of the pin.
        """

        self.buttons[pin_num] = self._button_class(pin_num)

    def remove_button(self, button):
        """Remove a button from the array.
        
        Args:
            button (int): The button index.
        """

        del self.buttons[button]


class ButtonArrayRPiGPIO(ButtonArray):
    """An array of buttons, extends :class:`ButtonArray`.
    
    Args:
        pin_nums: List with the gpio numbers for buttons.
    """

    def __init__(self, pin_nums, name='', max_data_length=0):
        """Constructor"""

        self._button_class = ButtonRPiGPIO
        super(ButtonArrayRPiGPIO, self).__init__(pin_nums, name, max_data_length)


class ButtonArrayMcp23017(ButtonArray):
    """An array of buttons, extends :class:`ButtonArray`.
    
    Args:
        pin_nums: List with the module's numbers for buttons.
    """

    def __init__(self, pin_nums, name='', max_data_length=0):
        """Constructor"""

        self._button_class = ButtonMcp23017
        super(ButtonArrayMcp23017, self).__init__(pin_nums, name, max_data_length)
