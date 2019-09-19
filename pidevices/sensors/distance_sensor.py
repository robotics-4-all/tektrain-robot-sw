from ..devices import Sensor


class DistanceSensor(Sensor):
    """Abstract class for distance sensors.
    
    Describes a using some common attributes like max distance and fov.
    """

    def _set_max_distance(self, max_distance):
        self._max_distance = max_distance

    def _get_max_distance(self):
        return self._max_distance

    max_distance = property(lambda self: self._get_max_distance(),
                            lambda self, value: self._set_max_distance(value),
                            doc="""The max distance that can be measured.""")

    def _set_min_distance(self, min_distance):
        self._min_distance = min_distance

    def _get_min_distance(self):
        return self._min_distance

    min_distance = property(lambda self: self._get_min_distance(),
                            lambda self, value: self._set_min_distance(value),
                            doc="""The min distance that can be measured.""")
