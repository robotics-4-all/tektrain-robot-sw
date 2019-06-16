from .hardware_interfaces import GPIO

try:
    import RPi.GPIO as RPIGPIO
except ModuleNotFoundError:
    print("RPi.GPIO is not installed.")


class RPiGPIO(GPIO):
    """GPIO class implementation using RPi.GPIO library

    Attributes:
    Methods:
    """

    # Maybe make them class attributes and with inheritance change the values
    RPIGPIO_FUNCTIONS = {
        'input': RPIGPIO.IN,
        'output': RPIGPIO.OUT
    }

    RPIGPIO_PULLS = {
        'up': RPIGPIO.PUD_UP,
        'down': RPIGPIO.PUD_DOWN,
        'floating': RPIGPIO.PUD_OFF
    }

    def __init__(self, **kwargs):
        """Contstructor"""

        super(RPiGPIO, self).__init__(**kwargs)
        self.initialize()

        # Specific pwm pin instances of RPi.GPIO library.
        self._pwm_pins = {}

    def initialize(self):
        # Set RPi.GPIO mode
        if RPIGPIO.getmode() is None:
            RPIGPIO.setmode(RPIGPIO.BCM)

    def read(self, pin):
        return RPIGPIO.input(self.pins[pin].pin_num)

    def write(self, pin, value):
        # Check for value type
        if isinstance(value, int):
            value = float(value)

        if not isinstance(value, float):
            raise TypeError("Invalid value type, should be float or int.")

        value = abs(value)    # Make it positive
        # Move it in range [0, 1], it may be with no reason
        try:
            value = (value - int(value)) if value % 1 != 0 else value/value
        except ZeroDivisionError:
            value = 0

        pin_name = pin
        pin = self.pins[pin]

        # Check if it is pwm or simple output
        if pin.function is 'output':
            if pin.pwm:
                self.pwm_pins[pin_name].ChangeDutyCycle(value*100)
                pin.duty_cycle = value
            else:
                value = int(round(value))
                RPIGPIO.output(pin.pin_num, value)
        else:
            # Can't drive an input pin.
            pass

    def close(self):
        self.remove_pins(*self.pins.keys())

    def remove_pins(self, *args):
        """Remove a pin/pins
        
        Args:
            *args: String with the pin's name, it could be more than one.
        """
        for pin in args:
            if self.pins[pin].pwm:
                self.set_pin_pwm(pin, False)
            RPIGPIO.cleanup(self.pins[pin].pin_num)
            del self.pins[pin]


    def set_pin_function(self, pin, function):
        pin = self.pins[pin]
        RPIGPIO.setup(pin.pin_num, self.RPIGPIO_FUNCTIONS[function]) 
        pin.function = function

    def set_pin_pull(self, pin, pull):
        pin = self.pins[pin]
        if pin.function is 'input':
            RPIGPIO.setup(pin.pin_num,
                          self.RPIGPIO_FUNCTIONS['input'],
                          self.RPIGPIO_PULLS[pull])
            pin.pull = pull
        else:
            # Raise exception for invalid function for pin
            pass

    def set_pin_pwm(self, pin, pwm):
        """Sets the pwm attribute and initialize pwm with frequency 0 and 
           duty cycle 0.
            
            Args:
                pwm: A boolean indicating the state of the pin.
        """
        if not isinstance(pwm, bool):
            raise TypeError("Invalid pwm type, should be boolean.")

        pin_name = pin
        pin = self.pins[pin]

        if not pin.pwm and pwm:
            # The pwm is deactivated and it will be activated.
            pin.frequency = 1
            pin.duty_cycle = 0
            self.pwm_pins[pin_name] = RPIGPIO.PWM(pin.pin_num, pin.frequency)
            self.pwm_pins[pin_name].start(pin.duty_cycle)
        elif pin.pwm and not pwm:
            # The pwm is activated and will be deactivated.
            pin.frequency = None
            pin.duty_cycle = None
            self.pwm_pins[pin_name].stop()
            del self.pwm_pins[pin_name]

        pin.pwm = pwm

    def set_pin_frequency(self, pin, frequency):
        pin_name = pin
        pin = self.pins[pin]
        if pin.pwm:
            pin.frequency = frequency
            self.pwm_pins[pin_name].ChangeFrequency(frequency)
        else:
            # Raise exception that this pin isn't pwm
            pass

    @property
    def pwm_pins(self):
        return self._pwm_pins
