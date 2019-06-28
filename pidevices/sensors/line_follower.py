from ..devices import Sensor

class LineFollower(Sensor):
    """Base class representing line following sensors."""

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

    def _get_max_dist(self):
        return self._max_dist

    def _set_max_dist(self, max_dist):
        self._max_dist = max_dist

    max_dist = property(_get_max_dist, _set_max_dist)
