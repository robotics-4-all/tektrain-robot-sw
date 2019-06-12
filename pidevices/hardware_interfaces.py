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
    """

    def __init__(self, number):
        """Constructor"""
        self._pin_num = number
        self._frequency = 0
        self._pwm = False
        self._duty_cycle = 0 
        self._edges = None

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

    def _set_bounce_time(self, bounce_time):
        self._bounce_time = bounce_time

    def _get_bounce_time(self):
        return self._bounce_time

    bounce_time = property(_get_bounce_time, _set_bounce_time)

    def _set_edges(self, edges):
        self._edges = edges

    def _get_edges(self):
        return self._edges

    edges = property(_get_edges, _set_edges)
    
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
    Methods:
    """
    
    def __init__(self, **kwargs):
        """Constructor

        Args:
            **kwargs: Keyword arguments pin_name: pin_number. For example 
                    echo=1, trigger=2
        """ 
        
        self._pins = {}
        self.add_pins(**kwargs)

    def add_pins(self, **kwargs):
        """Add new pins.
        
        Args:
            **kwargs: Keyword arguments pin_name: pin_number. For example 
                    echo=1, trigger=2
        """
        for key, value in kwargs.items():
            self._pins[key] = GPIOPin(value)
    
    # Not sure yet
    def remove_pin(self, pin):
        pass

    # Not sure yet
    def remove_pins(self, pins):
        pass

    def initialize(self, pin, function, pull="floating", value=None):
        """Initialize single pin.
        
        Args:
            pin: A string representing the pin as the user has name it.
            function: A string for the pin function.
            pull: Initialize pull up if it is an input pin.
            value: Initialize value if it is an output pin.
        """
        self.set_pin_function(pin, function)

        # Write if the function is output and we want value on start
        if function is 'output' and value is not None:
            self.write(pin, value)

        if function is 'input':
            self.set_pin_pull(pin, pull)

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

    def set_pin_pwm(self, pin, pwm):
        pass

    def get_pin_pwm(self, pin):
        return self._pins[pin].pwm

    def set_pin_duty_cycle(self, pin, duty_cycle):
        pass

    def get_pin_duty_cycle(self, pin):
        return self._pins[pin].duty_cycle

