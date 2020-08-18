"""uart_implementations.py"""

from .hardware_interfaces import UART

try:
    import serial
except ImportError:
    serial = None


class UartSerial(UART):
    """Wrapper for the serial library, extends :class:`UART`
    
    Args:
        devpath (str): Path to the serial device.
        baudrate (int): The baudrate of the communication.
    """

    def __init__(self, devpath, baudrate):
        """Constructor"""

        self.devpath = devpath
        self.baudrate = baudrate
        if serial is None:
            raise ImportError("Failed to import serial.")
        self._serial = serial.Serial(devpath=self.devpath, 
                                     baudrate=self.baudrate)

    def _set_devpath(self, devpath):
        self._devpath = devpath

    def _get_devpath(self):
        return self._devpath 

    def _set_baudrate(self, baudrate):
        self._baudrate = baudrate

    def _get_baudrate(self):
        return self._baudrate 

    def _set_parity(self, parity):
        self._parity = parity

    def _get_parity(self):
        return self._parity 

    def _set_stopbits(self, stopbits):
        self._stopbits = stopbits

    def _get_stopbits(self):
        return self._stopbits 

    def _set_bytesize(self, bytesize):
        self._bytesize = bytesize

    def _get_bytesize(self):
        return self._bytesize 
