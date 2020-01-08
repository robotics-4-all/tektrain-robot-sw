.. .devices_api

=======
Devices
=======

Overview
========

Pidevices's main goal is the easy deployment of devices. A device could be anything
that get's connected to the pi(also the pi could be a device, but we don't see it
from that prespective). Pidevices distinct the devices in two categories sensors
which are devices that get any information from the environment and actuators
that change the environment.

To make things easier for the maker/developer pidevices use a common interface
consisting of three functions start(), stop() and restart(). The distinction
between sensors and actuators is a read() function that belongs to sensors and 
a write function that belongs only to actuatos.

With that in mind a developer can contribute a new sensor or effector by 
just implementing these four functions and then any user could use it without 
having to know the specific implementation.

Device
------

.. autoclass:: pidevices.devices.Device
   :members:

Sensor
------

.. autoclass:: pidevices.Sensor
   :members:

Actuator
--------

.. autoclass:: pidevices.Actuator
   :members:
