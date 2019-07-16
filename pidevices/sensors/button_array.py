from ..devices import Sensor
from .button import Button


class ButtonArray(Sensor):
    """Multiple button"""

    def __init__(self, pin_nums, name='', max_data_length=0):
        """Constructor
        
        Args:
            pin_numss: List with the gpio numbers for buttons.
        """

        super(ButtonArray, self).__init__(name, max_data_length)
        self._pin_nums = pin_nums
        self._buttons = []

        self.start()

    def start(self):
        """Init hardware and os resources."""

        for pin_num in self.pin_nums:
            self.buttons.append(Button(pin_num))
    
    def read(self, button):
        """Read current state of button."""

        return self.buttons[button].read()

    def when_pressed(self, button, func, *args):
        """Function to be called when the button is pressed."""

        self.buttons[button].when_pressed(func, *args)

    def wait_for_press(self, button):
        """Wait to be pressed"""
        
        self.buttons[button].wait_for_press()

    def stop(self):
        """Free hardware and os resources."""

        for button in self.buttons:
            button.stop()
            del button
    
    def add_button(self, pin_num):
        self.buttons.append(Button(pin_num))

    def remove_button(self, button):
        del self.buttons[button]

    @property
    def pin_nums(self):
        return self._pin_nums

    @pin_nums.setter
    def pin_nums(self, value):
        self._pin_nums = value

    @property
    def buttons(self):
        return self._buttons
