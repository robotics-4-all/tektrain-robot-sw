import time
from .distance_sensor import DistanceSensor


# TODO find max pulse width from testing
class HcSr04(DistanceSensor):
    """HcSr04 class extends :class:`DistanceSensor`

    Implementation of the HC-SR04 sensor class speed of sound is 
    33100 + 0.6*temperature(cm/s) considering temperature = 20, speed of sound 
    at sea level.
    
    Hardware specs:
        - Operating voltage: 5V
        - Min distance: 2cm
        - Max distance: 4m

    Args:
        trigger_pin (int): BCM number of the trigger pin.
        echo_pin (int): BCM number of the echo pin.
        name (str): The optional name of the device.
        max_data_length (int): The max data of the data list.
    """
    _SPEED_OF_SOUND = 33100

    def __init__(self, trigger_pin,
                 echo_pin, name="",
                 max_data_length=100):
        "Constructor"

        # Set id and max data length.
        super(HcSr04, self).__init__(name, max_data_length)
        self.max_distance = 4
        self.min_distance = 0.02

        # Set the pins names
        self._trigger_pin = trigger_pin
        self._echo_pin = echo_pin

        # Initialize hardware resources
        self.start()

    @property
    def trigger_pin(self):
        """Get trigger pin."""
        return self._trigger_pin

    @trigger_pin.setter
    def trigger_pin(self, pin):
        """Set trigger pin."""
        self._trigger_pin = pin

    @property
    def echo_pin(self):
        """Get echo pin."""
        return self._echo_pin

    @echo_pin.setter
    def echo_pin(self, pin):
        """Set echo pin."""
        self._echo_pin = pin

    def start(self):
        """Initialize hardware and os resources."""

        self._gpio = self.init_interface('gpio',
                                         trigger=self.trigger_pin,
                                         echo=self.echo_pin)
        self.hardware_interfaces[self._gpio].set_pin_function('echo', 'input')
        self.hardware_interfaces[self._gpio].set_pin_edge('echo', 'both')
        self.hardware_interfaces[self._gpio].set_pin_event('echo',
                                                           self._async_measure)
        self.hardware_interfaces[self._gpio].set_pin_function('trigger', 'output')

        # Allow module to settle
        time.sleep(0.25)

    def stop(self):
        """Free hardware and os resources."""
        # Set output to low
        self.hardware_interfaces[self._gpio].write('trigger', 0)

        # Close pins
        self.hardware_interfaces[self._gpio].close()

    def read(self, SAVE=False):
        """Get a distance measurment
        
        Args:
            SAVE (boolean): Flag for saving the measurment to the data list.

        Returns:
            The distance in centimeters.

        Raises:
            OutOfRange: Error when a measurment takes too long.
        """

        # Send 10us pulse to trigger
        self.hardware_interfaces[self._gpio].write('trigger', 1)
        time.sleep(0.000015)
        self.hardware_interfaces[self._gpio].write('trigger', 0)

        self.out = False
        # If wait time is more than max echo signal = 0.024s
        count = 0
        while not self.out:
            if count == 10:
                raise OutOfRange("Out of range.")
            time.sleep(0.003)
            count += 1

        # Distance is the time that the pulse travelled
        # multiplied by the speed of sound
        distance_of_pulse = self.duration * self._SPEED_OF_SOUND

        # Half the distance
        distance = round(distance_of_pulse / 2., ndigits=4)

        # Add measurment to data deque
        if SAVE:
            self.update_data(distance)

        return distance

    def _async_measure(self):
        """Function to be called with edge signals.
        
        With rising signal start measure time and with falling signal stop
        save signal duration.
        """

        if self.hardware_interfaces[self._gpio].read('echo'):
            self.t_start = time.time()
        else:
            self.duration = time.time() - self.t_start
            self.out = True
