# TODO: Check pins global pins availability


class HardwareInterface(object):
    """Abstract class representing a hardware interface

    Methods:
        initilize: Initialize hardware resources.
        read: Read from the hardware. Descendants should ovevwrite this method.
        write: Write to rhe hardware. Descendants should overwrite this method.
        close: Free hardware resources.
    """

    def initialize():
        """Initialize hardware resources."""
        pass

    def read():
        """Read data from hardware"""
        raise NotImplementedError("This method has not been implemented.")

    def write():
        """Write data to hardware"""
        raise NotImplementedError("This method has not been implemented.")

    def close():
        """Free hardware resources."""
        pass


class GPIOPin(HardwareInterface):
    """Class representing a gpio pin.

    Attributes:
        pin_num: An integer indicating the bcm pin number.
        function: A string that could be input or output.
        pull: A string indicating the pull up state of the pin. It could be
            up, down or floating.
        frequency: An integer indicating the frequency of the pin, if it is 
                 a pwm pin. 
        pwm: A boolean that indicates if the pin is pwm or not.
        duty_cycle: Float for the percentage of the pwm cycle.
    """

    def __init__(self, number):
        """Constructor"""
        self._pin_num = number
        self._function = None
        self._pull = None
        self._frequency = None
        self._pwm = None
        self._duty_cycle = None

    def _set_pin_num(self, pin_num):
        self._pin_num = pin_num
    
    def _get_pin_num(self):
        return self._pin_num

    pin_num = property(_get_pin_num, _set_pin_num)

    def _set_function(self, function):
        self._function = function

    def _get_function(self):
        return self._function

    function = property(_get_function, _set_function)

    def _set_pull(self, pull):
        self._pull = pull

    def _get_pull(self):
        return self._pull

    pull = property(_get_pull, _set_pull)

    def _set_frequency(self, frequency):
        self._frequency = frequency

    def _get_frequency(self):
        return self._frequency

    frequency = property(_get_frequency, _set_frequency)

    def _set_pwm(self, pwm):
        self._pwm = pwm

    def _get_pwm(self):
        return self._pwm

    pwm = property(_get_pwm, _set_pwm)

    def _set_duty_cycle(self, duty_cycle):
        self._duty_cycle = duty_cycle

    def _get_duty_cycle(self):
        return self._duty_cycle

    duty_cycle = property(_get_duty_cycle, _set_duty_cycle)


# TODO: catch exceptions if the pin for get functions if the pins has not that
# attribute
class GPIO(HardwareInterface):
    """GPIO

    Attributes:
        pins: A dictionary that has as keys the pin's name and as value the 
            GPIOPin instance.
    """
    
    def __init__(self, **kwargs):
        """Constructor

        Args:
            **kwargs: Keyword arguments pin_name=pin_number. For example 
                    echo=1, trigger=2
        """ 
        
        self._pins = {}
        self.add_pins(**kwargs)

    def add_pins(self, **kwargs):
        """Add new pins.
        
        Args:
            **kwargs: Keyword arguments pin_name=pin_number. For example 
                    echo=1, trigger=2
        """
        for key, value in kwargs.items():
            self._pins[key] = GPIOPin(value)
    
    def remove_pins(self, *args):
        """Remove a pin/pins from the dictionary and free the resources."""
        pass

    def initialize_input(self, pin, pull):
        """Initialize a pin to input with initial pull up value."""
        self.set_pin_function(pin, "input")
        self.set_pin_pull(pin, pull)
    
    def initialize_output(self, pin, value):
        """Initialize a pin to output with an output value."""
        self.set_pin_function(pin, "output")
        self.write(pin, value)

    def initialize_pwm(self, pin, frequency, duty_cycle=0):
        """Initialize a pin to pwm with frequency and duty cycle."""
        self.set_pin_function(pin, "output")
        self.set_pin_pwm(pin, True)
        self.set_pin_frequency(pin, frequency)
        self.write(pin, duty_cycle)

    def write(self, pin, value):
        """Write a value to the specific pin
        
        Args:
            pin: An integer indicating the pin number
            value: A float that should be between [0, 1]
        """
        pass

    def _set_pins(self, pins):
        self._pins = pins

    def _get_pins(self):
        return self._pins

    pins = property(_get_pins, _set_pins)

    def set_pin_function(self, pin, function):
        pass

    def get_pin_function(self, pin):
        return self._pins[pin].function

    def set_pin_pull(self, pin, pull):
        pass

    def get_pin_pull(self, pin):
        return self._pins[pin].pull

    def set_pin_frequency(self, pin, frequency):
        pass

    def get_pin_frequency(self, pin):
        return self._pins[pin].frequency

    def set_pin_pwm(self, pin, frequency):
        pass

    def get_pin_pwm(self, pin):
        return self._pins[pin].pwm

    def set_pin_duty_cycle(self, pin, duty_cycle):
        pass

    def get_pin_duty_cycle(self, pin):
        return self._pins[pin].duty_cycle
