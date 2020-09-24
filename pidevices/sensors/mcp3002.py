"""mcp3002.py"""

from ..devices import Sensor
from time import sleep


class Mcp3002(Sensor):
    """Mcp3002 adc implementation extends :class:`Sensor`
    
    Args:
        port: spi port.
        device: spi device.
        v_ref: The reference voltage. Defaults to 3.3V.
    """
    
    _AVERAGES = 100
    _VALUE_REF = 1024

    def __init__(self, 
                 port=0,
                 device=1,
                 v_ref=3.3,
                 max_data_length=100,
                 name=""):
        """Constructor"""
        self._port = port
        self._device = device
        self.v_ref = v_ref
        super(Mcp3002, self).__init__(name, max_data_length)

        self.start()

    @property
    def port(self):
        """Spi chip"""
        return self._port

    @port.setter
    def port(self, chip):
        """Set spi chip"""
        self._port = chip

    @property
    def device(self):
        """Spi device"""
        return self._device

    @device.setter
    def device(self, chip):
        """Set spi chip"""
        self._device = chip
    
    def start(self):
        """Initialize hardware and os resources."""

        self._spi = self.init_interface('spi', port=self.port, device=self.device)

    def stop(self):
        """Free hardware and os resources."""

        self.hardware_interfaces[self._spi].close()

    def _read_channel(self, channel):
        """
        Protocol start bit (S), sql/diff (D), odd/sign (C), MSBF (M)
        Use leading zero for more stable clock cycle
        0000 000S DCM0 0000 0000 0000
        Sending 3 8bit packages so xpi.xfer2 will return the same amount.
        start bit = 1
        sql/diff = 1 SINGLE ENDED MODE  (2 channel mode)
        odd/sign = channel 0/1
        MSBF = 0
        """
        command = [1, (2 + channel) << 6, 0]
        #2 + channel shifted 6 to left
        #10 or 11 << 6 = 1000 0000 or 1100 0000
        reply = self.hardware_interfaces[self._spi].read_write(command)
        """
        Parse right bits from 24 bit package (3*8bit)
        We need only data from last 2 bytes.
        And there we can discard last two bits to get 10 bit value
        as MCP3002 resolution is 10bits
        Discard reply[0] byte and start from reply[1] where our data starts
        """
        value = reply[1] & 31
        """
        31 = 0001 1111 with & operation makes sure that we have all data
        from XXXX DDDD and nothing more. 0001 is for signed in next operation.
        """
        value = value << 6  # Move to left to make room for next piece of data.
        #000D DDDD << 6 = 0DDD DD00 0000
        #Now we get the last of data from reply[2]
        value = value + (reply[2] >> 2)
        #Here we discard last to bits
        #DDDD DDXX >> 2 = 00DD DDDD
        #0DDD DD00 0000 + 00DD DDDD = 0DDD DDDD DDDD
        return value

    def read(self, channel, SAVE=False):
        """Read adc value.
        
        Args:
            channel: The adc channel. Valid values 0 and 1.
            SAVE: Flag for saving to data list.

        Returns:
            The digital value.
        """

        value = 0
        for _ in range(self._AVERAGES):
            value += self._read_channel(channel)
            sleep(0.001)

        value /= self._AVERAGES
        value = float(value) / self._VALUE_REF * self.v_ref

        if SAVE:
            self.update_data(value)

        return value

