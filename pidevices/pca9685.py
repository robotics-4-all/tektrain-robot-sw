from .devices import Actuator


class PCA9685(Actuator):
    """Class for controlling pca9685 led/servo driver."""

    self.LED_OFFSET = 4
    self.PCA_ADDRESS = 0x40
    self.MODE_1 = 0x00
    self.MODE_2 = 0x01
    self.SUBADR_1 = 0x02
    self.SUBADR_2 = 0x03
    self.SUBADR_3 = 0x04
    self.ALLCALLADR = 0x05
    self.LED_ON_L = 0x06      
    # Led on registers represent the value of the clock tick the on pulse 
    # must start. And Led of has the clock tick the pulse has to fall.
    self.LED_ON_H = 0x07
    self.LED_OFF_L = 0x08
    self.LED_OFF_H = 0x09
    self.ALL_LED_ON_L = 0xfa
    self.ALL_LED_ON_H = 0xfb
    self.ALL_LED_OFF_L = 0xfc
    self.ALL_LED_OFF_H = 0xfd
    self.PRESCALE = 0xfe
    self.TestMode = 0xff

    # Values for mode_1
    self.ALLCALL = 0x01
    self.SLEEP = 0x10

    # Values for mode_2
    self.OUTDRV = 0x04

    # PWM counter max clock cycles
    self.TICKS = 4096

    def write(self, channel, duty_cycle):
        """Write
        
        The value should be a duty cycle. Start at on_ = delay -1
        off = delay + int(duty_cycle*self.TICKS) - 1. Have in mind overflow 
        if off starts after end

        Fully on just make one bit 4 of high byte
        """
        pass

    def change_frequency(self, freq):
        """Set the prescale value. 
        
        The value is given from prescale = (osc_clock / 4096*update_rate) - 1
        osc_clock = 25MHz
        max_freq = 1526 Hz
        min_freq = 24Hz
        The prescaler can be set if sleep bit is set to mode register
        """
        pass

    def _write_all(self, value):
        """Privete function for writting to all registers
        
        Write to register ALLCALLADDR
        """
