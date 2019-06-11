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
    """Abstract class representing a gpio pin.

    Attributes:
        pin_num: An integer indicating the bcm pin number.
        function: A string that could be input or output.
        pull: A string indicating the pull up state of the pin. It could be
              up, down or floating.
        frequency: An integer indicating the frequency of the pin, if it is 
                   a pwm pin. 
        pwm: A boolean that indicates if the pin is pwm or not.
    """

    def _set_pin_num(self, pin_num):
        pass
    
    def _get_pin_num(self):
        pass

    pin_num = property(_get_pin_num, _set_pin_num)

    def _set_function(self, function):
        pass

    def _get_function(self):
        pass

    function = property(_get_function, _set_function)

    def _set_pull(self, pull):
        pass

    def _get_pull(self):
        pass

    pull = property(_get_pull, _set_pull)

    def _set_frequency(self, frequency):
        pass

    def _get_frequency(self):
        pass

    frequency = property(_get_frequency, _set_frequency)

    def _set_bounce_time(self, bounce_time):
        pass

    def _get_bounce_time(self):
        pass

    bounce_time = property(_get_bounce_time, _set_bounce_time)

    def _set_edges(self, edges):
        pass

    def _get_edges(self):
        pass

    edges = property(_get_edges, _set_edges)
    
    def _set_pwm(self, pwm):
        pass

    def _get_pwm(self):
        pass

    pwm = property(_get_pwm, _set_pwm)
