from ..devices import Sensor


class Button(Sensor):
    """A single button"""

    def __init__(self, pin_num, name='', max_data_length=0):
        """Constructor"""

        super(Button, self).__init__(name, max_data_length)
        self._pin_num = pin_num

        self.start()

    def start(self):
        """Init hardware and os resources."""

        self._gpio = self.init_interface('gpio', button=self.pin_num)
        self.hardware_interfaces[self._gpio].init_input('button', 'up')
        self.hardware_interfaces[self._gpio].set_pin_bounce('button', 200)
        self.hardware_interfaces[self._gpio].set_pin_edge('button', 'falling')
    
    def read(self):
        """Read current state of button."""

        return self.hardware_interfaces[self._gpio].read('button')

    def when_pressed(self, func, *args):
        """Function to be called when the button is pressed."""

        self.hardware_interfaces[self._gpio].set_pin_event('button', func, *args)

    def wait_for_press(self):
        """Wait to be pressed"""

        self.hardware_interfaces[self._gpio].wait_pin_for_edge('button')

    def stop(self):
        """Free hardware and os resources."""

        self.hardware_interfaces[self._gpio].close()

    @property
    def pin_num(self):
        return self._pin_num

    @pin_num.setter
    def pin_num(self, value):
        self._pin_num = value
