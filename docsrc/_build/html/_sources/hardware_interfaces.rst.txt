.. .hardware_interfaces.rst

===================
Hardware Interfaces
===================

Overview
========

A hardware interface is an architecture used to interconnect two devices 
together. The main hardware interfaces that are supported by the raspberry 
pi are i2c, spi, uart, hardware pwm(there is also software pwm but
this belongs to the gpio interface) and gpio.

Pidevices abstracts all hardware interfaces by a common api that has 4 main 
functions initialize(), read(), write() and close(). So when it comes to the
development of a new driver the programmer can focus on the device protocol and
not get distracted by the underling protocol library. 

This abstraction is done using inheritance of abstract protocol classes. For 
example the SPI class defines the attributes and the abstract functions of the
spi interface in general and then an SPI_Implementation class inherits it and 
fills the functions and the setters/getters of the parent class using a specific
protocol library e.x. spidev2. Basically the implementations are wrappers of the
specific library but they follow a common interface so the programmer doesn't 
have to know how to use the specific protocol libraries.

Classes
=======

HardwareInterface
-----------------

.. autoclass:: pidevices.HardwareInterface
   :members:

GPIOPin 
-------

.. autoclass:: pidevices.GPIOPin
   :members:

GPIO
----

.. autoclass:: pidevices.GPIO
   :members:
   :inherited-members:

SPI
---

.. autoclass:: pidevices.SPI
   :members:
   :inherited-members:

HPWM
----

.. autoclass:: pidevices.HPWM
   :members:
   :inherited-members:

I2C
---

.. autoclass:: pidevices.I2C
   :members:
   :inherited-members:
