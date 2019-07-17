from .hardware_interfaces import SPI

try:
    from spidev import SpiDev
except ImportError:
    SpiDev = None


# Got gpiozero's spi implementation
class SPIimplementation(SPI):
    def __init__(self, port, device):
        self._port = port
        self._device = device
        self._interface = None
        if SpiDev is None:
            raise ImportError('failed to import spidev')
        self._interface = SpiDev()
        self._interface.open(port, device)
        self._interface.max_speed_hz = 1000000

    def close(self):
        if self._interface is not None:
            self._interface.close()
        self._interface = None

    def read(self, n):
        """Read n words from spi"""
        return self._interface.readbytes(n)

    # TODO: Check writebytes2 for large lists
    def write(self, data):
        """Write data to spi"""
        self._interface.writebytes2(data)

    def read_write(self, data):
        """
        Writes data (a list of integer words where each word is assumed to have
        :attr:`bits_per_word` bits or less) to the SPI interface, and reads an
        equivalent number of words, returning them as a list of integers.
        """
        return self._interface.xfer2(data)

    def _get_clock_mode(self):
        return self._interface.mode

    def _set_clock_mode(self, value):
        self._interface.mode = value

    def _get_lsb_first(self):
        return self._interface.lsbfirst

    def _set_lsb_first(self, value):
        self._interface.lsbfirst = bool(value)

    def _get_select_high(self):
        return self._interface.cshigh

    def _set_select_high(self, value):
        self._interface.cshigh = bool(value)

    def _get_bits_per_word(self):
        return self._interface.bits_per_word

    def _set_bits_per_word(self, value):
        self._interface.bits_per_word = value

