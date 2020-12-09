"""button_array.py"""

from ..devices import Sensor


class ButtonArray(Sensor):
    """An array of buttons, extends :class:`Sensor`.
    
    Args:
        pin_nums (list): List with the gpio numbers for buttons.
        direction (list|str): Could be a list with different values per pin_num
            or single value.
        bounce (list|int): Could be a list with different value per pin_num or 
            a single value.
    """

    def __init__(self, pin_nums, direction, bounce, name='', max_data_length=0):
        """Constructor"""

        super(ButtonArray, self).__init__(name, max_data_length)
        self._pin_nums = pin_nums

        self._dir = direction if isinstance(direction, list) else [direction]
        self._bounce = bounce if isinstance(bounce, list) else [bounce]
        self._b_names = []     # Order of button names
        self._directions = []
        self._debounce = []

        self.start()

    @property
    def pin_nums(self):
        """A list with the pin nums of the buttons"""
        return self._pin_nums

    @pin_nums.setter
    def pin_nums(self, value):
        self._pin_nums = value

    @property
    def directions(self):
        """A list with the direction of every button."""
        return self._directions

    @directions.setter
    def directions(self, value):
        self._directions = value

    @property
    def debounce(self):
        """A list with the debounce time of every button."""
        return self._debounce

    @debounce.setter
    def debounce(self, value):
        self._debounce = value

    def start(self):
        """Init hardware and os resources."""

        buttons = {}
        for pin in self._pin_nums:
            buttons["button_" + str(pin)] = pin

        self._gpio = self.init_interface("gpio",
                                         impl=self._impl, 
                                         **buttons)

        d_len = len(self._dir)
        b_len = len(self._bounce)
        for i, button in enumerate(buttons):
            # Initiliaze every button
            dire = self._dir[i % d_len]
            self._directions.append(dire)

            boun = self._bounce[i % b_len]
            self._debounce.append(boun)

            self._button_init(button, dire, boun)

    def read(self, button):
        """Read current state of button.
        
        Args:
            button (int): The number of the button.

        Returns:
            int: Int with the button's current state.
        """

        return self.hardware_interfaces[self._gpio].read(self._b_names[button])

    def when_pressed(self, button, func, *args):
        """Set a function for asynchronous call when the button is pressed.

        Args:
            button (int): The number of the button.
            func (function): The function.
            *args: Arguments for the function.
        """

        self.hardware_interfaces[self._gpio].set_pin_event(self._b_names[button],
                                                           func,
                                                           *args)

    def wait_for_press(self, b):
        """Wait to be pressed
        
        Args:
            b (int): The number of the button.
        """
        
        self.hardware_interfaces[self._gpio].wait_pin_for_edge(self._b_names[b])

    def stop(self):
        """Free hardware and os resources."""

        self._bounce.clear()
        self._dir.clear()
        self._b_names.clear()

        self.hardware_interfaces[self._gpio].close()
    
    def add_button(self, pin_num, direction, bounce):
        """Add a button to the array.
        
        Args:
            pin_num (int): BCM number of the pin.
        """

        button_key = "button_" + str(pin_num)
        self._debounce.append(bounce)
        self._directions.append(direction)

        self.hardware_interfaces[self._gpio].add_pins(**{button_key: pin_num})
        self._button_init(button_key, direction, bounce)

    def _button_init(self, button, direction, bounce):
        """Initialize a button"""

        # Make the list with the names
        self._b_names.append(button)

        self.hardware_interfaces[self._gpio].init_input(button, direction)
        self.hardware_interfaces[self._gpio].set_pin_bounce(button, bounce)

        #edge = "falling" if direction is 'up' else "rising"
        self._hardware_interfaces[self._gpio].set_pin_edge(button, "both")

    def remove_button(self, button):
        """Remove a button from the array.
        
        Args:
            button (int): The button index.
        """

        self.hardware_interfaces[self._gpio].remove_pins(self._b_names[button])
        del self._b_names[button]
        del self._directions[button]
        del self._debounce[button]


class ButtonArrayRPiGPIO(ButtonArray):
    """An array of buttons, extends :class:`ButtonArray`.
    
    Args:
        pin_nums (list): List with the gpio numbers for buttons.
        direction (list|str): Could be a list with different values per pin_num
            or single value.
        bounce (list|int): Could be a list with different value per pin_num or 
            a single value.
    """

    def __init__(self, pin_nums, direction, bounce, name='', max_data_length=0):
        """Constructor"""

        self._impl = "RPiGPIO"
        super(ButtonArrayRPiGPIO, self).__init__(pin_nums, direction,
                                                 bounce, name, max_data_length)


class ButtonArrayMcp23017(ButtonArray):
    """An array of buttons, extends :class:`ButtonArray`.
    
    Args:
        pin_nums (list): List with the gpio numbers for buttons.
        direction (list|str): Could be a list with different values per pin_num
            or single value.
        bounce (list|int): Could be a list with different value per pin_num or 
            a single value.
    """

    def __init__(self, pin_nums, direction, bounce, name='', max_data_length=0):
        """Constructor"""

        self._impl = "Mcp23017GPIO"
        super(ButtonArrayMcp23017, self).__init__(pin_nums, direction,
                                                  bounce, name, max_data_length)

    def enable_pressed(self, buttons):
        """Enable when pressed interrupts for all button"""

        names = []
        for button in buttons:
            names.append(self._b_names[button])

        self.hardware_interfaces[self._gpio].start_polling(names)
