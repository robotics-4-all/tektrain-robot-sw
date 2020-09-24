from ..devices import Sensor
import Adafruit_ADS1x15
from time import sleep
import threading
from collections import deque
import numpy



class ADS1X15(Sensor):
    _MAX_VALUE = 32767
    _CHANNELS = 4
    GAINS = numpy.array([[2/3, 6.144],
                         [1,   4.096],
                         [2,   2.048],
                         [4,   1.024],
                         [8,   0.512],
                         [16,  0.128]])

    def __init__(self, 
                 bus=1,
                 address=0x48,
                 v_ref=3.3,
                 averages=10,
                 max_data_length=100,
                 name=""):
        """Constructor"""

        self._bus = 1
        self._address = 0x48
        self.v_ref = v_ref
        self._gain = self._find_gain()
        self._averages = 10
        self._measurements = []
        self._results = [4000] * self._CHANNELS

        # threading stuff
        self._lock = threading.Lock()
        self._thread = None
        self._thread_alive = False
        
        for channel in range(0,4):
            self._measurements.append(deque(maxlen=self._averages))
        
        super(ADS1X15, self).__init__(name, max_data_length)
        
        self.start()


    def _find_gain(self):
        """Find the correct gain according to the given vref"""
        gain = 2/3
        for i in range(1, self.GAINS.shape[0]):
            if self.GAINS[-i][1] > self.v_ref:
                gain = int(self.GAINS[-i][0])
                self.v_ref = self.GAINS[-i][1]
                break
        return gain


    def start(self):
        """Initialize hardware and os resources."""
        self.adc = Adafruit_ADS1x15.ADS1115(address=self._address,busnum=self._bus)

        if not self._thread_alive:
            self._thread_alive = True
            self._thread = threading.Thread(target=self._update_channels, args=(), daemon=True)
            self._thread.start()


    def stop(self):
        """Free hardware and os resources."""
        self._thread_alive = False
        self._thread.join()

        self.adc.stop_adc()
        

    def _update_channels(self):
        """Periodically aquires the moving average of all adc channels"""
        while self._thread_alive:
            for channel in range(0, 4):
                self._measurements[channel].append(self._read_channel(channel))

                # to add lock
                if len(self._measurements[channel]) == self._averages:
                    with self._lock:
                        self._results[channel] = sum(self._measurements[channel]) / self._averages
            sleep(0.05)
        
        print("ADC thread terminating...")


    def _read_channel(self, channel): 
        """Read a sigle's channel value"""
        if 0 <= channel and channel < 4:
            return self.adc.read_adc(channel, gain=self._gain)


    def read(self, channel, SAVE=False):
        """Read result and transform it to voltage"""
        with self._lock:
            value = float(self._results[channel]) / self._MAX_VALUE * self.v_ref

        if SAVE:
            self.update_data(value)

        return value