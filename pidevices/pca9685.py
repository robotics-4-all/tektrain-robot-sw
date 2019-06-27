from .devices import Actuator
import time


class PCA9685(Actuator):
    """Class for controlling pca9685 led/servo driver."""

    LED_OFFSET = 4
    PCA_ADDRESS = 0x40
    MODE_1 = 0x00
    MODE_2 = 0x01
    SUBADR_1 = 0x02
    SUBADR_2 = 0x03
    SUBADR_3 = 0x04
    ALLCALLADR = 0x05
    # Led on registers represent the value of the clock tick the on pulse 
    # must start. And Led of has the clock tick the pulse has to fall.
    # L-H are the registers
    # LED is led_on_l, +1 is led_on_h, +2 is led_off_l, +3 is led_off_h
    LED = 0x06      
    ALL_LED_ON_L = 0xfa
    ALL_LED_ON_H = 0xfb
    ALL_LED_OFF_L = 0xfc
    ALL_LED_OFF_H = 0xfd
    PRESCALE = 0xfe
    TestMode = 0xff

    # Values for mode_1
    ALLCALL = 0x01
    SLEEP = 0x10

    # Values for mode_2
    OUTDRV = 0x04

    # PWM counter max clock cycles
    TICKS = 4096
    OSC_CLOCK = 25e6

    # Values for leds
    LED_FULL = 0x1000

    def __init__(self, bus, frequency=None, oe=None, name="", max_data_lenght=1):
        """Constructor"""

        super(PCA9685, self).__init__(name, max_data_lenght)
        self._frequency = frequency
        self._oe = oe
        self._bus = bus
        self.start()

    def start(self):
        """Init hardware and os resources."""

        # Init hardware interfaces
        self._i2c = self.init_interface("i2c", bus=self.bus)
        if self.oe:
            self._gpio = self.init_interface("gpio", oe=self.oe)

        # Init modes of pca
        self.hardware_interfaces[self._i2c].write(self.PCA_ADDRESS, 
                                                  self.MODE_2,
                                                  self.OUTDRV)
        self.hardware_interfaces[self._i2c].write(self.PCA_ADDRESS, 
                                                  self.MODE_1,
                                                  self.ALLCALL)
        self._settle_osc()
        
        # Change frequency
        if self._frequency:
            self.frequency = self._frequency

        # Write 0 to sleep bit
        mode = self.hardware_interfaces[self._i2c].read(self.PCA_ADDRESS,
                                                        self.MODE_1)
        mode = mode & (self.SLEEP ^ 0xFF)
        self.hardware_interfaces[self._i2c].write(self.PCA_ADDRESS,
                                                  self.MODE_1,
                                                  mode)

    # TODO: different values per channel
    def write(self, channels, duty_cycle, delay=0):
        """Write
        
        Channel list of channels or a single value

        delay is in %

        The value should be a duty cycle. Start at on_ = delay -1
        off = delay + int(duty_cycle*self.TICKS) - 1. Have in mind overflow 
        if off starts after end

        Fully on just make one bit 4 of high byte
        """
        
        # TODO: make computations for delay different of zero. Check led off 
        # overflowing self.TICKS
        led_on, led_off = self._compute_on_off(duty_cycle, delay)

        # Make it a list if is a single value
        channels = channels if isinstance(channels, list) else [channels]

        for channel in channels:
            self._set_register(self.LED + 4*channel, led_on)
            self._set_register(self.LED + 4*channel + 2, led_off)

    def _compute_on_off(self, duty_cycle, delay):
        """Compute the value in registers.
        
        Setting bit 4 of led_on_h makes the led always on and the same bit
        of led_on_l makes them always off. When both are set the off wins.
        """
        
        if not duty_cycle:
            led_off = self.LED_FULL
            led_on = 0
        elif int(duty_cycle) is 1:
            led_on = self.LED_FULL
            led_off = 0
        else:
            led_on = max(round(delay*self.TICKS) - 1, 0)
            led_off = (led_on + int(duty_cycle*self.TICKS)) % (self.TICKS+1)

        return led_on, led_off

    def _set_register(self, register, value):
        """Write to a 2 bytes register a 10bit value. The registers are 
           first low and then high bytes.
        """

        l = value & 0xFF 
        h = value >> 8
        self.hardware_interfaces[self._i2c].write(self.PCA_ADDRESS,
                                                  register,
                                                  l)
        self.hardware_interfaces[self._i2c].write(self.PCA_ADDRESS,
                                                  register + 1,
                                                  h)

    def write_all(self, value):
        """Privete function for writting to all registers
        
        Write to register ALLCALLADDR
        """
        #if int(value) is 1:
        #    all_led_on_h = self.LED_FULL
        #elif !value:
        #    all_led_off_h = self.LED_FULL

        self.hardware_interfaces[self._i2c].write(self.PCA_ADDRESS,
                                                  self.ALL_LED_ON_H,
                                                  all_led_on_h)
        self.hardware_interfaces[self._i2c].write(self.PCA_ADDRESS,
                                                  self.ALL_LED_ON_L,
                                                  all_led_on_l)

        self.hardware_interfaces[self._i2c].write(self.PCA_ADDRESS,
                                                  self.ALL_LED_OFF_H,
                                                  all_led_off_h)
        self.hardware_interfaces[self._i2c].write(self.PCA_ADDRESS,
                                                  self.ALL_LED_OFF_L,
                                                  all_led_off_l)
    def restart(self):
        """Set bit 7 at 1 of mode 1 register."""
        pass

    def _settle_osc(self):
        time.sleep(0.005)

    def _set_frequency(self, freq):
        """Set the prescale value. 
        
        The value is given from prescale = (osc_clock / 4096*update_rate) - 1
        osc_clock = 25MHz
        max_freq = 1526 Hz
        min_freq = 24Hz
        The prescaler can be set if sleep bit is set to mode register
        """
        prescaler = int(round(self.OSC_CLOCK/(self.TICKS*freq) - 1))

        # Save previous mode 1 value and then activate sleep bit
        old_mode = self.hardware_interfaces[self._i2c].read(self.PCA_ADDRESS,
                                                            self.MODE_1)
        self.hardware_interfaces[self._i2c].write(self.PCA_ADDRESS,
                                                  self.MODE_1,
                                                  old_mode & 0x7F | self.SLEEP)

        # Write prescaler value
        self.hardware_interfaces[self._i2c].write(self.PCA_ADDRESS,
                                                  self.PRESCALE,
                                                  prescaler)

        # Restore mode_1
        self.hardware_interfaces[self._i2c].write(self.PCA_ADDRESS,
                                                  self.MODE_1,
                                                  old_mode)
        self._settle_osc()
        self.hardware_interfaces[self._i2c].write(self.PCA_ADDRESS,
                                                  self.MODE_1,
                                                  old_mode | 0x80)
        

    def _get_frequency(self):
        """Maybe read prescaler value than having an extra variable."""
        pass

    frequency  = property(_get_frequency, _set_frequency)

    @property
    def bus(self):
        return self._bus

    @property
    def oe(self):
        return self._oe
