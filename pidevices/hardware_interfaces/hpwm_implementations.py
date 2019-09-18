from .hardware_interfaces import HPWM
from ..exceptions import InvalidHPWMPin

try:
    from periphery import PWM
except ImportError:
    PWM = None


class HPWMPeriphery(HPWM):
    """Wrapper around python periphery pwm implementation extends :class:`HPWM`.
    
    Args:
        pin (int): The pin number in bcm mode.

    Raises:
        ImportError: Error if the periphery library is not installed.
    """

    _chip = 0  # PWM chip

    def __init__(self, pin):
        # Check if the pin is valid
        super(HPWMPeriphery, self).__init__(pin)
        
        if PWM is None:
            raise ImportError("Failed to import PWM from periphery.")

        self._pwm = PWM(self._chip, self._SELECTED_COMB.index(pin))

    @property
    def pwm(self):
        """Periphery pwm object."""
        return self._pwm

    def read(self):
        """Read from hardware pwm pin.
        
        Returns:
            The duty cycle of the pwm pin.
        """

        return self.duty_cycle

    def write(self, value):
        """Write to the pwm pin.
        
        Args:
            value (float): The new duty cycle value.
        """

        self.duty_cycle = value
    
    def close(self):
        self.enable = 0

    def _get_frequency(self):
        return self.pwm.frequency

    def _set_frequency(self, frequency):
        "Ugly solution to sysf permission error"
        try:
            self.pwm.frequency = frequency
        except PermissionError:
            sleep(0.1)
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
