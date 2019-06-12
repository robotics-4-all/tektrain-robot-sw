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

        pin = self.pins[pin]

        # Check if it is pwm or simple output
        if pin.function is 'output':
            if pin.pwm:
                pin.pwm.ChangeDutyCycle(value*100)
                pin.duty_cycle = value
            else:
                value = int(round(value))
                RPIGPIO.output(pin.pin_num, value)
        else:
            # Can't drive an input pin.

    def close(self):
        RPIGPIO.cleanup()

    def close_pin(self, pin):
        RPIGPIO.cleanup(self.pins[pin])

    def remove_pins(self):
        pass

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

    def set_pin_pwm(self, pin, frequency):
        """Starts the pwm with duty cycle 0."""

        # This is software pwm
        pin = self.pins[pin]
        if pin.function is 'output':
            pin.pwm = RPIGPIO.PWM(pin.pin_num, frequency)
            pin.frequency = frequency
            pin.duty_cycle = 0.
            pin.pwm.start(pin.duty_cycle)
        else:
            # Raise expeption for hardware pwm
            pass

    def set_pin_frequency(self, pin, frequency):
        pin = self.pins[pin]
        if pin.pwm:
            pin.frequency = frequency
            pin.pwm.ChangeFrequency(frequency)
        else:
            # Raise exception that this pin isn't pwm
            pass

    def set_pin_duty_cycle(self, pin, duty_cycle):
        pin = self.pins[pin].duty_cycle = duty_cycle
