from .hardware_interfaces import HPMW

try:
    from periphery import PWM
except ImportError:
    PWM = None


class HPWMPeriphery(HPMW):
    """Wrapper around python periphery pwm implementation."""

    def __init__(self, chip, channel):

        if PWM is None:
            raise ImportError("Failed to import PWM from periphery.")
        self._pwm = PWM(chip, channel)

    def read(self):
        return self.duty_cycle

    def write(self, value):
        self.duty_cycle = value

    def _get_frequency(self):
        return self.pwm.frequency

    def _set_frequency(self, frequency):
        self.pwm.frequency = frequency

    def _get_duty_cycle(self):
        return self.pwm.duty_cycle

    def _set_duty_cycle(self, duty_cycle):
        self.pwm.duty_cycle = duty_cycle

    def _get_enable(self):
        return self.pwm.enable

    def _set_enable(self, enable):
        self.pwm.enable = enable

    def _get_polarity(self):
        pass

    def _set_polarity(self, polarity):
        pass

    @property
    def pwm(self):
        return self._pwm
