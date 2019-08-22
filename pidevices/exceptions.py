"""The exceptions of the library."""


class PidevicesError(Exception):
    """Base class for all exceptions in pidevices."""


class NotSupportedInterface(PidevicesError):
    """Error when an invalid interface name is used."""


class NotInstalledInterface(PidevicesError):
    """Error when there isn't any supported library installed for the 
       currrent interface."""


class InvalidHPWMPin(PidevicesError):
    """Error with invalid hardware pwm pin."""
    pass
