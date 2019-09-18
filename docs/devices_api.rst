.. .devices_api

=======
Devices
=======

Overview
========

The main reason of this library is to have implementations of different sensors
and actuators that share the same common api. So it would be as easy as a pie
to use any implemented device(any sensor or effector is a device) without 
knowning the specific protocols.

A device is a sensor when it gets information from the environment and an 
actuator when it changes the environment. With that in mind every sensor 
should have a read function and every actuator a write function.

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
