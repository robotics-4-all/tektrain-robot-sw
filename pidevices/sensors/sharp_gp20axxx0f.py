from ..exceptions import OutOfRange
from .distance_sensor import DistanceSensor
from scipy import interpolate
import numpy
import time


class GP2Y0AxxxK0F(DistanceSensor):
    """Sharp gp2y0axxxk0f family of ir distance sensors extends 
    :class:`DistanceSensor`.
    
    Args:
        datasheet_data: A 2d numpy array with the measurements from the 
            datasheet. The array goes from max voltage to min voltage and 
            every entry is of type voltage, cm.
        adc: Instance of any adc class. 
        interval (float): Interval between consecutive read.
    """

    def __init__(self, datasheet_data, 
                 adc, interval, 
                 name='', max_data_length=0):
        """Constructor"""

        super(GP2Y0AxxxK0F, self).__init__(name, max_data_length)
        self._min_volt = datasheet_data[len(datasheet_data) - 1, 0]
        self._max_volt = datasheet_data[0, 0]
        self.adc = adc
        self._interpol(datasheet_data)
        self._interval = interval

        self.start()

    @property
    def adc(self):
        """Adc instance of any adc class."""
        return self._adc

    @adc.setter
    def adc(self, value):
        """Set adc"""
        self._adc = value

    def set_channel(self, channel):
        """Set the adc channel"""
        if 0 <= channel and channel < 4:
            self._channel = channel
        else:
            self._channel = 0

    def _interpol(self, data):
        self._f_int = interpolate.interp1d(data[:, 0],
                                           data[:, 1])

    def start(self):
        """Init hardware and os resources."""

        if not len(self.adc.hardware_interfaces):
            self.adc.start()

    def read(self, n=1):
        """Read a measurment.
        
        The result comes from the average of n measurments

        Args:
            n (int): The number of consecutive measurments. Defaults to 1.

        Returns:
            The measured distance.

        Raises:
            OutOfRange: If the measurment is out of min or max distance.
        """

        adc_val = self.adc.read(channel=self._channel)

        # Check thresholds
        if adc_val < self._min_volt:
            adc_val = self._min_volt
        if adc_val > self._max_volt:
            adc_val = self._max_volt

        adc_val = max(adc_val, self._min_volt)
        adc_val = min(adc_val, self._max_volt)

        raw_distance = round(self._f_int(adc_val).item(0), 4)
        distance = raw_distance / self._units

        return distance

    def stop(self):
        """Free hardware and os resources."""

        self.adc.stop()


class GP2Y0A21YK0F(GP2Y0AxxxK0F):
    """Sharp gp2y0a21yk0f ir distance sensor extends :class:`GP2Y0AxxxK0F`
    
    Args:
        adc: Instance of any adc class. 
    """

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

    _INTERVAL = 0.040

    def __init__(self, adc, name='', max_data_length=0):
        """Constructor."""

        super(GP2Y0A21YK0F, self).__init__(self.INTER_DATA, adc,
                                           self._INTERVAL, name,
                                           max_data_length)


class GP2Y0A41SK0F(GP2Y0AxxxK0F):
    """Shaprt gp2y0a21yk0f ir distance sensor extends :class:`GP2Y0AxxxK0F`

    Args:
        adc: Instance of any adc class. 
    """

    # Distance measuring characteristics from datasheet. (voltage, cm)
    INTER_DATA = numpy.array([[3.00, 3],
                              [2.70, 4],
                              [2.35, 5],
                              [2.02, 6],
                              [1.78, 7],
                              [1.58, 8],
                              [1.40, 9],
                              [1.28, 10],
                              [1.09, 12],
                              [0.75, 14],
                              [0.80, 16],
                              [0.75, 18],
                              [0.66, 20],
                              [0.55, 25],
                              [0.42, 30],
                              [0.38, 35],
                              [0.31, 40]])

    _INTERVAL = 0.018

    def __init__(self, adc, name='', max_data_length=0):
        """Constructor."""

        super(GP2Y0A41SK0F, self).__init__(self.INTER_DATA, adc,
                                           self._INTERVAL, name,
                                           max_data_length)
