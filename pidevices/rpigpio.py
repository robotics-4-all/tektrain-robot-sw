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

        # Set RPi.GPIO mode
        if RPIGPIO.getmode() is None:
            RPIGPIO.setmode(RPIGPIO.BCM)

    # TODO: Initialize for custom key args, for example function="input",
    #                                                   pull="up")
    def initialize(self, pin, function):
        #self.set_pin_function(pin, function)
        #self.set_pin_pull(pin, pull)
        #self.set_pin_frequency(pin, frequency)
        #self.set_pin_pwm(pin, pwm)
        pass

    def read(self, pin):
        pin = self.pins[pin]
        if pin.function is 'input':
            return RPIGPIO.input(pin.pin_num)
        else:
            # Cant read from output pin
            pass

    def write(self, pin):
        pass

    def close(self, pin):
        pass

    # TODO: Add keyword arguments for initial values as pull if is input
    # or state if it is output.
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
        # This is software pwm
        pin = self.pins[pin]
        if pin.function is 'output':
            # TODO: Checks for frequency as gpiozero.
            RPIGPIO.PWM(pin.number, pin.frequency)
            pin.pwm = True
        else:
            # Raise expeption for hardware pwm
            pass

    def set_pin_frequency(self, pin, frequency):
        #pin = self.pins[pin]
        pass
