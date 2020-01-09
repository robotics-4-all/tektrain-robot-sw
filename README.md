# pidevices

## Overview

Pidevices is a python library whose main goal is the easy deployment of devices for the raspberry pi. A device could be anything that get’s connected to the pi(also the pi could be a device, but we don’t see it from that prespective). Pidevices distinct the devices in two categories sensors, which are devices that get any information from the environment and actuators that change the environment.

To make things easier for the maker/developer pidevices use a common interface consisting of three functions start(), stop() and restart(). The distinction between sensors and actuators is a read() function that belongs to sensors and a write() function that belongs only to actuatos.

With that in mind a developer can contribute a new sensor or effector by just implementing these four functions and then any user could use it without having to know the specific implementation.

In order to accomplish that pidevices abstracts all hardware interfaces by a common api that has 4 main functions initialize(), read(), write() and close(). So when it comes to the development of a new driver the programmer can focus on the device protocol and not get distracted by the underling protocol library.

This abstraction is done using inheritance of abstract protocol classes. For example the SPI class defines the attributes and the abstract functions of the spi interface in general and then an SPI_Implementation class inherits it and fills the functions and the setters/getters of the parent class using a specific protocol library e.x. spidev2. Basically the implementations are wrappers of the specific library but they follow a common interface so the programmer doesn’t have to know how to use the specific protocol libraries.

## Installation

From the project's top level directory type 
```bash
pip install .
```

### Hardware Interfaces Libraries

### Configuration

## Usage

## Docs

## Roadmap

## License
