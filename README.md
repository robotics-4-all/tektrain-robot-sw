# pidevices

## Overview

Pidevices is a python library whose main goal is the easy deployment of devices for the raspberry pi. A device could be anything that get’s connected to the pi(also the pi could be a device, but we don’t see it from that prespective). Pidevices distinct the devices in two categories sensors, which are devices that get any information from the environment and actuators that change the environment.

To make things easier for the maker/developer pidevices use a common interface consisting of three functions start(), stop() and restart(). The distinction between sensors and actuators is a read() function that belongs to sensors and a write() function that belongs only to actuatos.

With that in mind a developer can contribute a new sensor or effector by just implementing these four functions and then any user could use it without having to know the specific implementation.

In order to accomplish that pidevices abstracts all hardware interfaces by a common api that has 4 main functions initialize(), read(), write() and close(). So when it comes to the development of a new driver the programmer can focus on the device protocol and not get distracted by the underling protocol library.

This abstraction is done using inheritance of abstract protocol classes. For example the SPI class defines the attributes and the abstract functions of the spi interface in general and then an SPI_Implementation class inherits it and fills the functions and the setters/getters of the parent class using a specific protocol library e.x. spidev2. Basically the implementations are wrappers of the specific library but they follow a common interface so the programmer doesn’t have to know how to use the specific protocol libraries.

### Hardware Interfaces Support

The library support gpio, i2c, spi and hpwm(hardware pwm) hardware interfaces. Also in tbe future it will support UART.

For those interfaces the follow wrappers have been implemented for existing libraries:
- GPIO: RPiGPIO([RPi.GPIO](https://pypi.org/project/RPi.GPIO/))
- I2C: SMBus2([smbus2](https://pypi.org/project/smbus2/))
- SPI: SPIimplementation([spidev](https://pypi.org/project/spidev/))
- HPWM: HPWMPeriphery([python-periphery](https://pypi.org/project/python-periphery/))

Also for the GPIO interface has been implemented a wrapper using the mcp23017 chip.

### Drivers Implementation

Pidevices support multiple implementations of device drivers using different underlying libraries and hardware interfaces.
For example there is an implementation for a single button using RPi.GPIO library and one using the custom mcp23017 gpio expander. These two implementations go by the names ButtonRpiGPIO and ButtonMcp23017.

## Installation

First type

```bash
sudo apt install numpy
sudo apt install scipy
```

and then from the project's top level directory type 

```bash
pip install .
```

## Configuration

For using some of the device drivers additional configuration steps should be done.

#### HPWMPeriphery interface

* Enable kernel support for hardware PWM. For kernel 4.9 edit file /boot/config.txt and add

    ```
    dtoverlay=pwm-2chan
    ```
   For earlier kernels more information [here](https://jumpnowtek.com/rpi/Using-the-Raspberry-Pi-Hardware-PWM-timers.html).
* Add udev rule for adding /sys/class/pwm folder and it's files in the gpio group. Append the following lines in the /etc/udev/rules.d/99-com.rules file or make a new one with custom udev rules.
   ```
   SUBSYSTEM=="pwm*", PROGRAM="/bin/sh -c '\
        chown -R root:gpio /sys/class/pwm && chmod -R 770 /sys/class/pwm;\
        chown -R root:gpio /sys/devices/platform/soc/*.pwm/pwm/pwmchip* && chmod -R 770 /sys/devices/platform/soc/*.pwm/pwm/pwmchip*\
   '"
   ```
   An example of that file can be found in the [conf_files](conf_files) folder with the name 97-pwm.rules.

#### Speaker and Microphone
The speaker's and microphone drivers need the [pyalsaaudio](https://pypi.org/project/pyalsaaudio/) module to work.
Also because the module use the underlying alsa interface a consistent name should be given to the devices.
For the currently implemented devices the following two extra steps need to be done.

* Give the name "Speaker" to the speaker device in the asoundrc configuration file. Or use the example file from the 
[config_files](config_files) folder with the following command.
  ```bash
  cp conf_files/asoundrc ~/.asoundrc
  ```
* Make an udev rule for consistent naming of the same devices across different boots. Or copy the example from the [config_file](config_files) folder.
  ```bash
  cp conf_files/98-alsa.rules /etc/udev/rules.d/
  ```
**Attension** This udev rule work only for [this](https://gr.mouser.com/ProductDetail/Adafruit/3367?qs=%2Fha2pyFadugRA3aNmodCvBjn4f6vAekNsFsMZrN8apA6SGrKPmkiozE4dX7pFIV0) microphone and [this](https://www.digikey.com/products/en?keywords=Mini%20External%20USB%20Stereo%20Speaker) speaker. The library for the time doesn't support other devices.

#### Touch Screen
The touch screen driver is written on top of [pygame](https://pypi.org/project/pygame/) module. The only screen that is currently supported is [this](https://www.waveshare.com/wiki/4inch_HDMI_LCD_(H)). 

In order to work the instructions from the above link have to be followed for configuring the raspberry to support the hardware.

## Usage
Example:

```python
from pidevices import ButtonRPiGPIO
```

## Docs

## License
