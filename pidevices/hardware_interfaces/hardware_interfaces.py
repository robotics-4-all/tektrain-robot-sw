"""hardware_interfaces.py"""

from pidevices.exceptions import InvalidHPWMPin
# TODO: Check pins global pins availability


class HardwareInterface():
    """Abstract class representing a hardware interface."""

    def initialize():
        """Initialize hardware resources."""
        pass

    def read():
        """Read data from hardware."""
        raise NotImplementedError("This method has not been implemented.")

    def write():
        """Write data to hardware."""
        raise NotImplementedError("This method has not been implemented.")

    def close():
        """Free hardware resources."""
        pass


class GPIOPin(HardwareInterface):
    """Class representing a gpio pin by defining it's attributes.

    Args:
        number: The bcm number of the pin.
    """

    def __init__(self, number):
        """Constructor"""

        self._pin_num = number
        self._function = None
        self._pull = None
        self._frequency = None
        self._pwm = None
        self._duty_cycle = None
        self._event = None
        self._edge = None
        self._bounce = None

    def _set_pin_num(self, pin_num):
        self._pin_num = pin_num

    def _get_pin_num(self):
        return self._pin_num

    pin_num = property(_get_pin_num, _set_pin_num, doc="""
            An integer representing the bcm number of the pin.
            """)

    def _set_function(self, function):
        self._function = function

    def _get_function(self):
        return self._function

    function = property(_get_function, _set_function, doc="""
            This attribute represents the function of the pin, it could be
            :data:`input` for reading from the gpio pin or :data:`output` for
            writting to the pin.
            """)

    def _set_pull(self, pull):
        self._pull = pull

    def _get_pull(self):
        return self._pull

    pull = property(_get_pull, _set_pull, doc="""
            A str for the pull resistor of the pin, it could be 
            :data:`up`, :data:`down` or :data:`floating`. If the pin's function
            is output this attribute can't be set.
            """)

    def _set_frequency(self, frequency):
        self._frequency = frequency

    def _get_frequency(self):
        return self._frequency

    frequency = property(_get_frequency, _set_frequency, doc="""
            Integer value representing the frequency of the pwm pulse.
            """)

    def _set_pwm(self, pwm):
        self._pwm = pwm

    def _get_pwm(self):
        return self._pwm

    pwm = property(_get_pwm, _set_pwm, doc="""
            Boolean that indicates if the pin has pwm output. If the pin's
            function is input this attribute can't be set.
            """)

    def _set_duty_cycle(self, duty_cycle):
        self._duty_cycle = duty_cycle

    def _get_duty_cycle(self):
        return self._duty_cycle

    duty_cycle = property(_get_duty_cycle, _set_duty_cycle, doc="""
            Float value between [0, 1] representing the pwm's duty cycle.
            """)

    def _set_edge(self, edge):
        self._edge = edge

    def _get_edge(self):
        return self._edge

    edge = property(_get_edge, _set_edge, doc="""
            String that represents on which edge signal the pin whould trigger
            a function call or a specific action. The value should be 
            :data:`rising`, :data:`falling` or :data:`both`.
            """)

    def _set_event(self, event):
        self._event = event

    def _get_event(self):
        return self._event

    event = property(_get_event, _set_event, doc="""
            The event is a function that whould be called when an edge signal 
            have occured.
            """)

    def _set_bounce(self, bounce):
        self._bounce = bounce

    def _get_bounce(self):
        return self._bounce

    bounce = property(_get_bounce, _set_bounce, doc="""
            Integer representing the time intervel in miliseconds after an 
            edge signal that the event function doesn't get called with the 
            occurence of a new edge signal.
            """)


# TODO: catch exceptions if the pin for get functions if the pins has not that
# attribute
class GPIO(HardwareInterface):
    """Abstract class representing the GPIO hardware interface.

    The pupropse of this class is to handle every pin from the gpio pins set
    that a device needs to use. The implementations of this class 
    wrap the specific library functions for handling the gpio pins.

    Args:
        **kwargs: Could be multiple keyword arguments in the form of 
            pin_name=pin_number(pin_number is the bcm number of the board).
            For example for the hc-sr04 sonar, it would be echo=14, trigger=25.
    """

    def __init__(self, **kwargs):
        """Constructor"""

        self._pins = {}
        self.add_pins(**kwargs)

    def _set_pins(self, pins):
        self._pins = pins

    def _get_pins(self):
        return self._pins

    pins = property(lambda self: self._get_pins(),
                    lambda self, value: self._set_pins(value),
                    doc="""
                    A dictionary that has attributes of type 
                    :class:`GPIOPin` that represent
                    each pin. Keys are the pin names and values the objects.""")

    def write(self, pin, value):
        """Write a value to an output pin.

        Args:
            pin (str): The pin's name.
            value (int): The output value. The value should be 0 or 1 for a simple
                output pin and if it is pwm should be between [0, 1].

        Raises:
            TypeError: Try to write non arithmetic value or use value greater
                than 1 or use negative value.
            NotOutputPin: Try to write to an input pin.
        """
        pass

    def read(self, pin):
        """Read the value of an input pin.

        Args:
            pin (str): The pin's name.

        Returns:
            int: that is 1 for high voltage, 0 for low voltage.

        Raises:
            NotInputPin: Try to read from non input pin.
        """
        pass

    def add_pins(self, **kwargs):
        """Add new pins to the pins dictionary.

        Args:
            **kwargs: Keyword arguments pin_name=pin_number. For example echo=1,
                trigger=2.
        """
        for key, value in kwargs.items():
            self._pins[key] = GPIOPin(value)

    def remove_pins(self, *args):
        """Remove a pin/pins from the dictionary and free the resources.

        Args:
            *args: String with the pin's name, it could be more than one.
        """
        pass

    def init_input(self, pin, pull):
        """Initialize a pin to input with initial pull up value.

        Args:
            pin (str): The pin name.
            pull (str): The pull up value.
        """

        self.set_pin_function(pin, "input")
        self.set_pin_pull(pin, pull)

    def init_output(self, pin, value):
        """Initialize a pin to output with an output value.

        Args:
            pin (str): The pin name.
            value (int): The output value.
        """

        self.set_pin_function(pin, "output")
        self.write(pin, value)

    def init_pwm(self, pin, frequency, duty_cycle=0):
        """Initialize a pin to pwm with frequency and duty cycle.

        Args:
            pin (str): The pin name.
            frequency (int): The pwm frequency.
            duty_cycle (int): Optional parameter for initializing duty_cycle.
                Defaults to 0.
        """

        self.set_pin_function(pin, "output")
        self.set_pin_pwm(pin, True)
        self.set_pin_frequency(pin, frequency)
        self.write(pin, duty_cycle)

    def set_pin_function(self, pin, function):
        """Set a pin's function.

        Args:
            pin (str): The pin name.
            function (str): The function value.

        Raises:
            TypeError: Error occured using invalid function name.
        """
        pass

    def get_pin_function(self, pin):
        """Get the pin's function.

        Args:
            pin (str): The pin name.

        Returns:
            A string containing the pin's function.
        """

        return self._pins[pin].function

    def set_pin_pull(self, pin, pull):
        """Set a pin's pull up.

        Args:
            pin (str): The pin name.
            pull (str): The pull up value.

        Raises:
            TypeError: Error occured using invalid pull name.
            NotInputPin: Try to set pull up resistor to a non input pin.
        """
        pass

    def get_pin_pull(self, pin):
        """Get a pin's pull up.

        Args:
            pin (str): The pin's name.

        Returns:
            str: containing the pin's pull value.
        """

        return self._pins[pin].pull

    def set_pin_pwm(self, pin, pwm):
        """Set a pwm pin.

        Args:
            pin (str): The pin's name.
            pwm (int): The pwm value.

        Raises:
            TypeError: Invalid pwm type.
            NotOutputPin: Error occured trying to drive a non output pin.
        """
        pass

    def get_pin_pwm(self, pin):
        """Get a pin's pwm value.

        Args:
            pin (str): The pin's name.

        Returns:
            bool: that represents if the pin is pwm.
        """

        return self._pins[pin].pwm

    def set_pin_frequency(self, pin, frequency):
        """Set a pwm pin's frequency.

        Args:
            pin (str): The pin's name.
            frequency (int): The frequency value.

        Raises:
            NotPwmPin: Error occured trying to set pwm frequency to a non pwm
                pin.
        """
        pass

    def get_pin_frequency(self, pin):
        """Get a pin's frequency.

        Args:
            pin (str): The pin's name.

        Returns:
            int: with the pin's pwm frequency.
        """

        return self._pins[pin].frequency

    def set_pin_duty_cycle(self, pin, duty_cycle):
        """Set a pwm pin's duty_cycle.
        
        Maybe it is unnecessary.

        Args:
            pin (str): The pin's name.
            duty_cycle (int): The duty_cycle value.
        """
        pass

    def get_pin_duty_cycle(self, pin):
        """Get a pin's duty_cycle value.

        Args:
            pin (str): The pin's name.

        Returns:
            float: Representing the duty cycle.
        """

        return self._pins[pin].duty_cycle

    def set_pin_edge(self, pin, edge):
        """Set a pin's edge value.

        Args:
            pin (str): The pin's name.
            edge (str): The edge value.

        Raises:
            NotInputPin: Try to set edge to a non input pin.
        """
        pass

    def get_pin_edge(self, pin):
        """Get a pin's edge value.

        Args:
            pin (str): The pin's name.

        Returns:
            A str with the pin's edge.
        """

        return self._pins[pin].edge

    def set_pin_event(self, pin, event, *args):
        """Set the function that will be called with a new edge.

        Args:
            pin (str): Pin name
            event (function): Function pointer to the target function.
            *args: The arguments of the target function.

        Raises:
            NotInputPin: Try to set event to a non input pin.
        """
        pass

    def get_pin_event(self, pin):
        """Get a pin's event function.

        Args:
            pin (str): The pin's name.

        Returns:
            The function that is called when an edge signal occurs.
        """

        return self._pins[pin].event

    def set_pin_bounce(self, pin, bounce):
        """Set a pin's bounce time.

        Args:
            pin (str): The pin's name.
            bounce (int): The bounce value.
        """
        pass

    def get_pin_bounce(self, pin):
        """Get a pin's bounce value.

        Args:
            pin (str): The pin's name.

        Returns:
            int: Representing the pin's bounce time.
        """

        return self._pins[pin].bounce


class SPI(HardwareInterface):
    """Abstract class representing spi hardware interface. It is higly inspired 
    from `gpiozero <https://gpiozero.readthedocs.io/en/stable/api_spi.html>`
    SPI abstract class.
    """

    def _get_clock_polarity(self):
        pass

    def _set_clock_polarity(self, clock_polarity):
        pass

    clock_polarity = property(lambda self: self._get_clock_polarity(),
                              lambda self, value: self._set_clock_polarity(value),
                              doc="""Boolean representing the polarity of the
                                     SPI clock. If it is :data:`False` the clock
                                     will idle low and pulse high. Otherwise it
                                     will idle high and pulse low.""")

    def _get_clock_phase(self):
        pass

    def _set_clock_phase(self, clock_phase):
        pass

    clock_phase = property(lambda self: self._get_clock_phase(),
                           lambda self, value: self._set_clock_phase(value),
                           doc="""Boolean representing the phase of the SPI
                                  clock. If it is :data:`False` the data will be
                                  read from the MISO pin when the clock pin 
                                  activates. Else it the data will be read from
                                  the MISO pin when the clock pin deactivates.""")

    def _get_clock_mode(self):
        pass

    def _set_clock_mode(self, clock_phase):
        pass

    clock_mode = property(lambda self: self._get_clock_mode(),
                          lambda self, value: self._set_clock_mode(value),
                          doc="""Integer representing the four combinations of
                                 clock_polarity and clock_phase.""")

    def _get_lsb_first(self):
        pass

    def _set_lsb_first(self, lsb_first):
        pass

    lsb_first = property(lambda self: self._get_lsb_first(),
                         lambda self, value: self._set_lsb_first(value),
                         doc="""Boolean that controls if the data are read and
                                written in LSB.""")

    def _get_select_high(self):
        pass

    def _set_select_high(self, select_high):
        pass

    select_high = property(lambda self: self._get_select_high(),
                           lambda self, value: self._set_select_high(value),
                           doc="""
                                  Boolean that indicates if the chip select line
                                  is considered active when it is pulled down.""")

    def _get_bit_per_word(self):
        pass

    def _set_bit_per_word(self, bit_per_word):
        pass

    bit_per_word = property(lambda self: self._get_bit_per_word(),
                            lambda self, value: self._set_bit_per_word(value),
                            doc="""An integer representing the number of bits
                                   that make up a word.""")

    def _get_max_speed_hz(self):
        pass

    def _set_max_speed_hz(self, max_speed_hz):
        pass

    max_speed_hz = property(lambda self: self._get_max_speed_hz(),
                            lambda self, value: self._set_max_speed_hz(value),
                            doc="""Integer that sets the maximum bus speed
                                   in Hz.""")


class HPWM(HardwareInterface):
    """Abstract class representing hardware pwm.

    The raspberry pi has two channels of hardware pwm. This channels comes
    in pairs that only one could be activated. This pairs are pins (12, 13),
    (18, 19), (40, 41), (52, 53).

    Args:
        pin (int): The pin number.

    Raises:
        InvalidHPWMPin: Error with invalid pwm pin.
    """

    _VALID_COMBS = [(12, 13), (18, 19), (40, 41), (52, 53)]
    _SELECTED_COMB = None

    def __init__(self, pin):
        """Constructor"""

        if not self._check_valid(pin):
            raise InvalidHPWMPin("Invalid hardware pwm pin.")

    def _check_valid(self, pin):
        """Check if the pin is pwm"""

        ret_val = False
        if not HPWM._SELECTED_COMB:
            for comb in self._VALID_COMBS:
                if pin in comb:
                    HPWM._SELECTED_COMB = comb
                    ret_val = True
        else:
            if pin in HPWM._SELECTED_COMB:
                ret_val = True

        return ret_val

    def _get_frequency(self):
        pass

    def _set_frequency(self, frequency):
        pass

    frequency = property(lambda self: self._get_frequency(),
                         lambda self, value: self._set_frequency(value),
                         doc="""Frequency of the pwm pulse.""")

    def _get_duty_cycle(self):
        pass

    def _set_duty_cycle(self, duty_cycle):
        pass

    duty_cycle = property(lambda self: self._get_duty_cycle(),
                          lambda self, value: self._set_duty_cycle(value),
                          doc="""Duty cycle of the pwm pulse.""")

    def _get_enable(self):
        pass

    def _set_enable(self, enable):
        pass

    enable = property(lambda self: self._get_enable(),
                      lambda self, value: self._set_enable(value),
                      doc="""Enable hardware pwm.""")

    def _get_polarity(self):
        pass

    def _set_polarity(self, polarity):
        pass

    polarity = property(lambda self: self._get_polarity(),
                        lambda self, value: self._set_polarity(value),
                        doc="""Polarity of the pulse.""")


class I2C(HardwareInterface):
    """Abstract base class representing i2c hardware interface."""

    def _set_bus(self, bus):
        pass

    def _get_bus(self):
        pass

    bus = property(lambda self: self._get_bus(),
                   lambda self, value: self._set_bus(value),
                   doc="""Hardware bus of the i2c interface.""")


class UART(HardwareInterface):
    """Abstract base class representing uart hardware inteface."""

    def _get_devpath(self):
        pass

    def _set_devpath(self, devpath):
        pass

    devpath = property(lambda self: self._get_devpath(),
                       lambda self, value: self._set_devpath(value),
                       doc="""Device for the serial communication.""")

    def _get_baudrate(self):
        pass

    def _set_baudrate(self, baudrate):
        pass

    baudrate = property(lambda self: self._get_baudrate(),
                       lambda self, value: self._set_baudrate(value),
                       doc="""Baudrate of the serial communication.""")

    def _get_parity(self):
        pass

    def _set_parity(self, parity):
        pass

    parity = property(lambda self: self._get_parity(),
                       lambda self, value: self._set_parity(value),
                       doc="""Flag for parity check.""")

    def _get_stopbits(self):
        pass

    def _set_stopbits(self, stopbits):
        pass

    stopbits = property(lambda self: self._get_stopbits(),
                       lambda self, value: self._set_stopbits(value),
                       doc="""Pattern indicating the stopbits.""")

    def _get_bytesize(self):
        pass

    def _set_bytesize(self, bytesize):
        pass

    bytesize = property(lambda self: self._get_bytesize(),
                       lambda self, value: self._set_bytesize(value),
                       doc="""The number of data bits.""")
