from ..devices import Sensor


class DistanceSensor(Sensor):
    """Abstract class for distance sensors extends :class:`Sensor` and 
    a distance sensor using some common attributes.
    """
    UNITS = {
        "m": 100,
        "cm": 1,
        "mm": 0.1
    }

    def __init__(self, name="", max_data_length=100):
        super(DistanceSensor, self).__init__(name, max_data_length)
        self._units = self.UNITS.get("m")

    def set_units(self, units):
        if isinstance(units, str):
            if units in self.UNITS:
                self._units = self.UNITS.get(units)
            else:
                raise KeyError("Units should be one of these types {m, cm, mm}")
        else:
            raise ValueError("Units should be a string")

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

    

