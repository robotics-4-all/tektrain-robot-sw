from ..pidevices import Sensor
from .mcp3002 import Mcp3002


# Distance measuring characteristics from datasheet. (voltage, cm)
data = [(3.3, 7),
        (2.4, 10),
        (1.4, 20),
        (0.95, 30),
        (0.8, 40),
        (0.6, 50),
        (0.52, 60),
        (0.475, 70),
        (0.46, 80)]


# TODO: Initiliazation of adc inside the class or outside.
class GP2Y0A21YK0f_mcp3002(Sensor):
    """Shaprt gp2y0a21yk0f ir distance sensor."""

    def __init__(self, port, device, channel, name='', max_data_length=0):
        """Constructor."""

        super(GP2Y0A21YK0f, self).__init__(name, max_data_length)
        self._port = port
        self._device = device
        self._channel = channel

        self.start()

    def start(self):
        """Init hardware and os resources."""

        self.adc = Mcp3002(port=port, device=device)

    def read(self):
        """Read a measurment."""

        adc_val = self.adc.read(channel=self._channel)

    def stop(self):
        """Free hardware and os resources."""

        self.adc.stop()

    @property
    def adc(self):
        return self._adc

    @adc.setter
    def adc(self, value):
        self._adc = value
