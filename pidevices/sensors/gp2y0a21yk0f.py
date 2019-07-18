from ..devices import Sensor
from .mcp3002 import Mcp3002
from scipy import interpolate
import numpy
import time


# TODO: Initiliazation of adc inside the class or outside.
class GP2Y0A21YK0F_mcp3002(Sensor):
    """Shaprt gp2y0a21yk0f ir distance sensor."""

    # Distance measuring characteristics from datasheet. (voltage, cm)
    INTER_DATA = numpy.array([[3.3, 7],
                              [2.4, 10],
                              [1.4, 20],
                              [0.95, 30],
                              [0.8, 40],
                              [0.6, 50],
                              [0.52, 60],
                              [0.475, 70],
                              [0.46, 80]])

    _MIN_VOLT = INTER_DATA[len(INTER_DATA) - 1, 0]
    _MAX_VOLT = INTER_DATA[0, 0]

    _AVERAGES = 1
    _INTERVAL = 0.040

    def __init__(self, port, device, channel, name='', max_data_length=0):
        """Constructor."""

        super(GP2Y0A21YK0F_mcp3002, self).__init__(name, max_data_length)
        self._port = port
        self._device = device
        self._channel = channel
        self._interpol()

        self.start()

    def _interpol(self):
        self.f_int = interpolate.interp1d(self.INTER_DATA[:, 0],
                                          self.INTER_DATA[:, 1])

    def start(self):
        """Init hardware and os resources."""

        self.adc = Mcp3002(port=self._port, device=self._device)

    def read(self):
        """Read a measurment."""

        adc_val = 0
        for _ in range(self._AVERAGES):
            adc_val += self.adc.read(channel=self._channel)
            time.sleep(self._INTERVAL)
        adc_val /= self._AVERAGES

        # Check thresholds
        if adc_val < self._MIN_VOLT:
            # Raise out of max distance
            pass
        if adc_val > self._MAX_VOLT:
            # Raise out of min distance
            pass

        adc_val = max(adc_val, self._MIN_VOLT)
        adc_val = min(adc_val, self._MAX_VOLT)

        return round(self.f_int(adc_val).item(0), 4)

    def stop(self):
        """Free hardware and os resources."""

        self.adc.stop()

    @property
    def adc(self):
        return self._adc

    @adc.setter
    def adc(self, value):
        self._adc = value

    @property
    def f_int(self):
        return self._f_int

    @f_int.setter
    def f_int(self, value):
        self._f_int = value
