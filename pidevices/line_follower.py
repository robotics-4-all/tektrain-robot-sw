from .devices import Sensor

class LineFollower(Sensor):
    """Base class representing line following sensors."""

    def __init__(self, max_frequency, min_dist, max_dist):
        self._max_frequency = max_frequency
        self._min_dist = min_dist
        self._max_dist = max_dist

    def _get_max_freq(self):
        return self._max_frequency 

    def _set_max_freq(self, freq):
        self._max_frequency = freq

    max_frequency = property(_get_max_freq, _set_max_freq)

    def _get_min_dist(self):
        return self._min_dist

    def _set_min_dist(self, max_dist):
        self._min_dist = max_dist

    min_dist = property(_get_min_dist, _set_min_dist)

    def _get_min_dist(self):
        return self._min_dist

    def _set_min_dist(self, min_dist):
        self._min_dist = min_dist

    max_dist = property(_get_max_dist, _set_max_dist)
