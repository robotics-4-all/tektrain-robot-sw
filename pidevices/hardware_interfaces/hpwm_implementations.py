from .hardware_interfaces import HPWM
from ..exceptions import InvalidHPWMPin
from time import sleep

try:
    from periphery import PWM
except ImportError:
    PWM = None


class HPWMPeriphery(HPWM):
    """Wrapper around python periphery pwm implementation extends :class:`HPWM`.
    
    This class need the periphery module to be installed. Also some configuration
    files need to be added to the system. More info in the repo's README.

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

    def read(self):
        """Read from hardware pwm pin.
        
        Returns:
            float: The duty cycle of the pwm pin.
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
        return self._pwm.frequency

    def _set_frequency(self, frequency):
        "Ugly solution to sysf permission error"
        try:
            self._pwm.frequency = frequency
        except PermissionError:
            sleep(0.1)
            self._pwm.frequency = frequency

    def _get_duty_cycle(self):
        return self._pwm.duty_cycle

    def _set_duty_cycle(self, duty_cycle):
        self._pwm.duty_cycle = duty_cycle

    def _get_enable(self):
        return self._enable

    def _set_enable(self, enable):
        #self._pwm.enable = enable
        self._enable = enable
        if self._enable:
            self._pwm.enable()
        else:
            self._pwm.disable()

    def _get_polarity(self):
        pass

    def _set_polarity(self, polarity):
        pass
