from .hardware_interfaces import HPWM

try:
    from periphery import PWM
except ImportError:
    PWM = None


class HPWMPeriphery(HPWM):
    """Wrapper around python periphery pwm implementation."""

    _chip = 0  # PWM chip

    def __init__(self, pin):
        # Check if the pin is valid
        try:
            super(HPWMPeriphery, self).__init__(pin)
        except:
            pass
        
        if PWM is None:
            raise ImportError("Failed to import PWM from periphery.")

        self._pwm = PWM(self._chip, self._SELECTED_COMB.index(pin))

    def read(self):
        return self.duty_cycle

    def write(self, value):
        self.duty_cycle = value
    
    def close(self):
        pass

    def _get_frequency(self):
        return self.pwm.frequency

    def _set_frequency(self, frequency):
        self.pwm.frequency = frequency

    def _get_duty_cycle(self):
        return self.pwm.duty_cycle

    def _set_duty_cycle(self, duty_cycle):
        self.pwm.duty_cycle = duty_cycle

    def _get_enable(self):
        return self._enable

    def _set_enable(self, enable):
        #self.pwm.enable = enable
        self._enable = enable
        if self._enable:
            self.pwm.enable()
        else:
            self.pwm.disable()

    def _get_polarity(self):
        pass

    def _set_polarity(self, polarity):
        pass

    @property
    def pwm(self):
        return self._pwm
