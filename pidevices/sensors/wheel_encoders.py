"""wheel_encoders.py"""

from ..devices import Sensor


class WheelEncoder(Sensor):
    """Abstract class for a wheel encoders. Extends :class:`Sensor`"""

    def _set_res(self, value):
        """Resolution of the encoder."""
        if value > 0:
            self._res = value

    def _get_res(self):
        return self._res

    res = property(lambda self: self._get_res(),
                   lambda self, value: self._set_res(value),
                   doc="""Resolution of the encoder.""")
