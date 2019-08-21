"""The exceptions of the library."""

class PidevicesError(Exception):
    """Base class for all exceptions in pidevices."""

class NotSupportedInterface(PidevicesError):
    """Error when an invalid interface name is used."""
