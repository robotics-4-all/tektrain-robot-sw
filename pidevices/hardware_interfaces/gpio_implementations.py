"""gpio_implementations.py"""

from .hardware_interfaces import GPIO, GPIOPin
from ..exceptions import NotInputPin, NotOutputPin, NotPwmPin
import threading 
import time
from collections import namedtuple

try:
    import RPi.GPIO as RPIGPIO
except ImportError:
    RPIGPIO = None

try:
    from ..mcp23017 import MCP23017
except ImportError:
    MCP23017 = None

try:
    import pigpio as PIGPIO
except ImportError:
    PIGPIO = None



class PiGPIO(GPIO):
    PIGPIO_FUNCTIONS = {
        'input': PIGPIO.INPUT,
        'output': PIGPIO.OUTPUT,
        'alt_0': PIGPIO.ALT0,
        'alt_1': PIGPIO.ALT1,
        'alt_2': PIGPIO.ALT2,
        'alt_3': PIGPIO.ALT3,
        'alt_4': PIGPIO.ALT4,
        'alt_5': PIGPIO.ALT5
    }

    PIGPIO_PULLS = {
        'up': PIGPIO.PUD_UP,
        'dowm': PIGPIO.PUD_DOWN,
        'floating': PIGPIO.PUD_OFF
    }

    PIGPIO_EDGES = {
        'rising': PIGPIO.RISING_EDGE,
        'falling': PIGPIO.FALLING_EDGE,
        'both': PIGPIO.EITHER_EDGE
    }

    PWM_FREQUENCY = 10000
    PWM_RANGE = 1000

    def __init__(self, **kwargs):
        """Contstructor"""
        if PIGPIO is None:
            raise ImportError("pigpio not found.")

        super(PiGPIO, self).__init__(**kwargs)
        self.initialize()

    def initialize(self):
        self.gpio = PIGPIO.pi()
        if not self.gpio.connected:
            raise ImportError("pigpio not found.")
        
    def set_pin_function(self, pin, function):
        if function not in self.PIGPIO_FUNCTIONS:
            raise TypeError("Invalid function name should be input or output or alt_func.")

        pin = self.pins[pin]    #get pins object thorw its name
        self.gpio.set_mode(pin.pin_num, self.PIGPIO_FUNCTIONS[function])
        pin.function = function


    def set_pin_pull(self, pin, pull):
        if pull not in self.PIGPIO_PULLS:
            raise TypeError("Invalid pull name, should be up, dowm or floating.")

        pin = self.pins[pin]
        if pin.function is 'input':
            self.gpio.set_pull_up_down(pin.pin_num, self.PIGPIO_PULLS[pull])
            pin.pull = pull
        else:
            raise NotInputPin("Can't set pull up resistor to a non input pin.")

    def read(self, pin):
        pin = self.pins[pin]
        if pin.function is not "input":
            raise NotInputPin("Can't read from non input pin.")

        return self.gpio.read(pin.pin_num)

    def write(self, pin, value):
        if isinstance(value, int):
            value = float(value)

        if not isinstance(value, float):
            raise TypeError("Invalid value type, should be float or int.")

        # get pin object throw its name
        pin = self.pins[pin]

        # Check if it is pwm or simple output
        if pin.function is 'output':
            if pin.pwm:
                pin.duty_cycle = value
                range_value = pin.duty_cycle * self.PWM_RANGE

                if value < 0:
                    raise TypeError("The value should be positive.")

                if value > range_value:
                    raise TypeError("The value should be less or equal than 1.")
                
                self.gpio.set_PWM_dutycycle(pin.pin_num, range_value)
            else:
                if value !=0 and value != 1:
                    raise TypeError("The value should be equal to 0 or 1.")

                value = int(round(value))
                self.gpio.write(pin.pin_num, value)
        else:
            raise NotOutputPin("Can't write to a non output pin.")


    def set_pin_pwm(self, pin, pwm):
        if not isinstance(pwm, bool):
            raise TypeError("Invalid pwm type, should be boolean.")

        # get pin object throw its name
        pin = self.pins[pin]
        
        # throw error if it is not of type output
        if pin.function is not 'output':
            raise NotOutputPin("Can't set pwm to a non output pin.")

        if not pin.pwm and pwm:
            # if it is not already a pwm, initialize it as one
            pin.frequency = self.PWM_FREQUENCY
            pin.duty_cycle = 0

            self.gpio.set_PWM_frequency(pin.pin_num, pin.frequency)
            self.gpio.set_PWM_range(pin.pin_num, self.PWM_RANGE)
            self.gpio.set_PWM_dutycycle(pin.pin_num, 0)

        elif pin.pwm and not pwm:
            # The pwm is activated and will be deactivated.
            pin.frequency = None
            pin.duty_cycle = None
            
            # write 0 to the pin to deactivate the PWM functionality
            self.gpio.write(pin.pin_num, 0)

        pin.pwm = pwm

    def set_pin_frequency(self, pin, frequency):
        # get pin object throw its name
        pin = self.pins[pin]

        if pin.pwm:
            pin.frequency = frequency
            self.gpio.set_PWM_frequency(pin.pin_num, pin.frequency)
        else:
            raise NotPwmPin("Can't set frequency to a non pwm pin.")

    def set_pin_range(self, pin, range):
        pin = self.pins[pin]
        
        if pin.pwm:
            self.gpio.set_PWM_range(pin.pin_num, self.PWM_RANGE)
        else:
            raise NotPwmPin("Can't set range to a non pwm pin.")

    def get_pin_range(self, pin):
        pin = self.pins[pin]

        if pin.pwm:
            return self.gpio.get_PWM_range(pin.pin_num)
        else:
            raise NotPwmPin("Can't set range to a non pwm pin.")

    def set_pin_edge(self, pin, edge):
        pin = self.pins[pin]
        if edge not in self.PIGPIO_EDGES:
            raise TypeError("Wrong edge name, should be rising, falling or both")
        if pin.function is 'input':
            pin.edge = self.PIGPIO_EDGES[edge]
        else:
            raise NotInputPin("Can't set edge to a non input pin.")

    def set_pin_bounce(self, pin, bounce):
        self.pins[pin].bounce = bounce
    
    def set_pin_event(self, pin, event, *args):
        # The function which needs the arguments
        pin = self.pins[pin]

        def callback(gpio, level, tick):
            global callback_timer
            if pin.bounce is None:
                event(gpio, level, tick, *args)
            else:
                print(pin.bounce)
                if (tick - callback_timer) >= pin.bounce * 1000:
                    callback_timer = tick
                    event(gpio, level, tick, *args)
        
        global callback_timer
        callback_timer = 0

        if pin.function is 'input':
            self.gpio.callback(pin.pin_num, pin.edge, callback)
            pin.event = event
        else:
            # Raise exception output pin
            raise NotInputPin("Can's set event to a non input pin.")

    def remove_pins(self, *args):
        for pin in args:
            if self.pins[pin].pwm:
                self.set_pin_pwm(pin, False)
            
            del self.pins[pin]

    def close(self):
        """Close interface.input"""

        self.remove_pins(*self.pins.keys())
        self.gpio.stop()


    



class RPiGPIO(GPIO):
    """GPIO hardware interface implementation using RPi.GPIO library extends
    :class:`GPIO`.

    Raises:
        ImportError: If the rpigpio library is not installed.
    """

    # Maybe make them class attributes and with inheritance change the values
    RPIGPIO_FUNCTIONS = {
        'input': RPIGPIO.IN,
        'output': RPIGPIO.OUT
    }

    RPIGPIO_PULLS = {
        'up': RPIGPIO.PUD_UP,
        'down': RPIGPIO.PUD_DOWN,
        'floating': RPIGPIO.PUD_OFF
    }

    RPIGPIO_EDGES = {
        'rising': RPIGPIO.RISING,
        'falling': RPIGPIO.FALLING,
        'both': RPIGPIO.BOTH
    }

    def __init__(self, **kwargs):
        """Contstructor"""
        if RPIGPIO is None:
            raise ImportError("rpigpio not found.")

        super(RPiGPIO, self).__init__(**kwargs)
        self.initialize()

        # Specific pwm pin instances of RPi.GPIO library.
        self._pwm_pins = {}

    @property
    def pwm_pins(self):
        """A dictionary that contains instances of RPi.GPIO's pwm class.""" 
        return self._pwm_pins

    def initialize(self):
        """Initialize RPi.GPIO mode. By default it inializes to RPi.GPIO.BCM"""

        if RPIGPIO.getmode() is None:
            RPIGPIO.setmode(RPIGPIO.BCM)

    def read(self, pin):
        pin = self.pins[pin]
        if pin.function is not "input":
            raise NotInputPin("Can't read from non input pin.")

        return RPIGPIO.input(pin.pin_num)

    def write(self, pin, value):
        if isinstance(value, int):
            value = float(value)

        if not isinstance(value, float):
            raise TypeError("Invalid value type, should be float or int.")

        if value < 0:
            raise TypeError("The value should be positive.")

        if value > 1:
            raise TypeError("The value should be less or equal than 1.")

        pin_name = pin
        pin = self.pins[pin]

        # Check if it is pwm or simple output
        if pin.function is 'output':
            if pin.pwm:
                self.pwm_pins[pin_name].ChangeDutyCycle(value*100)
                pin.duty_cycle = value
            else:
                value = int(round(value))
                RPIGPIO.output(pin.pin_num, value)
        else:
            raise NotOutputPin("Can't write to a non output pin.")

    def remove_pins(self, *args):
        for pin in args:
            if self.pins[pin].pwm:
                self.set_pin_pwm(pin, False)
            RPIGPIO.cleanup(self.pins[pin].pin_num)
            del self.pins[pin]

    def set_pin_function(self, pin, function):
        if function not in self.RPIGPIO_FUNCTIONS:
            raise TypeError("Invalid function name should be input or output.")

        pin = self.pins[pin]
        RPIGPIO.setup(pin.pin_num, self.RPIGPIO_FUNCTIONS[function]) 
        pin.function = function

    def set_pin_pull(self, pin, pull):
        if pull not in self.RPIGPIO_PULLS:
            raise TypeError("Invalid pull name, should be up, dowm or floating.")

        pin = self.pins[pin]
        if pin.function is 'input':
            RPIGPIO.setup(pin.pin_num,
                          self.RPIGPIO_FUNCTIONS['input'],
                          self.RPIGPIO_PULLS[pull])
            pin.pull = pull
        else:
            raise NotInputPin("Can't set pull up resistor to a non input pin.")

    def set_pin_pwm(self, pin, pwm):
        if not isinstance(pwm, bool):
            raise TypeError("Invalid pwm type, should be boolean.")

        pin_name = pin
        pin = self.pins[pin]
        
        if pin.function is not 'output':
            raise NotOutputPin("Can't set pwm to a non output pin.")

        if not pin.pwm and pwm:
            # The pwm is deactivated and it will be activated.
            pin.frequency = 1
            pin.duty_cycle = 0
            self.pwm_pins[pin_name] = RPIGPIO.PWM(pin.pin_num, pin.frequency)
            self.pwm_pins[pin_name].start(pin.duty_cycle)
        elif pin.pwm and not pwm:
            # The pwm is activated and will be deactivated.
            pin.frequency = None
            pin.duty_cycle = None
            self.pwm_pins[pin_name].stop()
            del self.pwm_pins[pin_name]

        pin.pwm = pwm

    def set_pin_frequency(self, pin, frequency):
        pin_name = pin
        pin = self.pins[pin]
        if pin.pwm:
            pin.frequency = frequency
            self.pwm_pins[pin_name].ChangeFrequency(frequency)
        else:
            raise NotPwmPin("Can't set frequency to a non pwm pin.")
    
    def set_pin_edge(self, pin, edge):
        pin = self.pins[pin]
        if edge not in self.RPIGPIO_EDGES:
            raise TypeError("Wrong edge name, should be rising, falling or both")
        if pin.function is 'input':
            pin.edge = self.RPIGPIO_EDGES[edge]
        else:
            raise NotInputPin("Can't set edge to a non input pin.")

    def set_pin_bounce(self, pin, bounce):
        self.pins[pin].bounce = bounce

    def set_pin_event(self, pin, event, *args):
        # The function which needs the arguments
        def callback(channel):
            event(*args)

        pin = self.pins[pin]

        if pin.function is 'input':
            if pin.bounce is None:
                RPIGPIO.add_event_detect(pin.pin_num, pin.edge)
            else:
                RPIGPIO.add_event_detect(pin.pin_num,
                                         pin.edge,
                                         bouncetime=pin.bounce)

            pin.event = event
            RPIGPIO.add_event_callback(pin.pin_num, callback)
        else:
            # Raise exception output pin
            raise NotInputPin("Can's set event to a non input pin.")

    def wait_pin_for_edge(self, pin, timeout=None):
        """Wait pin for an edge detection.

        Args:
            pin (str): Pin name.
            timeout (int): The time until it stops waiting for an edge signal.
        """
        
        pin = self.pins[pin]
        if pin.function is'input':
            if timeout is None:
                RPIGPIO.wait_for_edge(pin.pin_num, pin.edge)
            else:
                RPIGPIO.wait_for_edge(pin.pin_num, pin.edge, timeout=timeout)
        else:
            raise NotInputPin("Can's wait for an event to a non input pin.")

    def close(self):
        """Close interface.input"""

        self.remove_pins(*self.pins.keys())


Timers = namedtuple("Timers", ["t_on", "t_off"])


class Mcp23x17GPIO(GPIO):
    """GPIO class implementation using mcp23x17 family chips. Extends :class:`GPIO`
    
    Args:
        **kwargs: Could be multiple keyword arguments in the form of
            pin_name = pin_number(pin number is A_x or B_x, because the 
            implementation use the mcp23x17 devices.) For example for the 
            hc-sr04 sonar, it would be echo="A_1", trigger="B_2".
    """
    class _edges:
        """A private class for storing values for bits that define an interrupt
        
        For the mcp modules these values are intcon bit and defval. If intcon
        bit is set then the interrupt happens to the specified pin when the 
        value is different than the value that is stored in the defval bit
        (usefull for interrupts that occur only on rising or falling edges). 
        Else if the intcon is cleared then the interrupt occur when the pin 
        value is different than the previous value.

        Args:
            intcon (int): Representing the int con value
            defval (int): Representing the defval
        """
        def __init__(self, intcon, defval):
            """Constructor"""
            self.intcon = intcon
            self.defval = defval

    MCP_FUNCTION = {'input': 1, 'output': 0}

    MCP_POLARITY = {'reverse': 1, 'same': 0}

    MCP_PULL = {'up': 1, 'down': 0}

    MCP_EDGES = {
        'rising': _edges(intcon=1, defval=0),
        'falling': _edges(intcon=1, defval=1),    
        'both': _edges(intcon=0, defval=0),
    }

    PIN_NUMBER_MAP = {
        'A_0': 0, 
        'A_1': 1, 
        'A_2': 2, 
        'A_3': 3, 
        'A_4': 4, 
        'A_5': 5, 
        'A_6': 6, 
        'A_7': 7, 
        'B_0': 8, 
        'B_1': 9, 
        'B_2': 10,
        'B_3': 11,
        'B_4': 12,
        'B_5': 13,
        'B_6': 14,
        'B_7': 15,
        0: 'A_0', 
        1: 'A_1', 
        2: 'A_2', 
        3: 'A_3', 
        4: 'A_4', 
        5: 'A_5', 
        6: 'A_6', 
        7: 'A_7', 
        8: 'B_0', 
        9: 'B_1', 
        10: 'B_2', 
        11: 'B_3', 
        12: 'B_4', 
        13: 'B_5', 
        14: 'B_6', 
        15: 'B_7', 
    }
    

    def __init__(self, **kwargs):
        """Contructor"""

        self._pins = {}
        self._int_pins = []
        self.add_pins(**kwargs)

        # Pwm timers
        self._pwm_timers = {}
        self._spwm_mutex = threading.Lock()

        self.initialize()

    def initialize(self):
        """Initialize hardware and os resources."""
        pass

    def add_pins(self, **kwargs):
        """Add new pins to the pins dictionary.

        Args:
            **kwargs: Keyword arguments pin_name=pin_number.
                For example echo="A_1", trigger="B_2".
        """

        for key, value in kwargs.items():
            self._pins[key] = GPIOPin(self.PIN_NUMBER_MAP[value])

    def read(self, pin):
        pin = self.pins[pin]
        if pin.function is not "input":
            raise NotInputPin("Can't read from non input pin.")

        return self._device.read(self.PIN_NUMBER_MAP[pin.pin_num])

    def write(self, pin, value):
        if isinstance(value, int):
            value = float(value)

        if not isinstance(value, float):
            raise TypeError("Invalid value type, should be float or int.")

        if value < 0:
            raise ValueError("The value should be positive.")

        if value > 1:
            raise ValueError("The value should be less or equal than 1.")

        pin_name = pin
        pin = self.pins[pin]

        # Check if it is pwm or simple output
        if pin.function is 'output':
            if pin.pwm:
                self._pwm_timers[pin.pin_num][0] = value * 1/pin.frequency
                self._pwm_timers[pin.pin_num][1] = (1 - value)* 1/pin.frequency
                pin.duty_cycle = value
            else:
                value = int(round(value))
                self._device.write(self.PIN_NUMBER_MAP[pin.pin_num], value)
        else:
            raise NotOutputPin("Can't write to a non output pin.")

    def remove_pins(self, *args):
        for pin in args:
            del self.pins[pin]

    def set_pin_function(self, pin, function):
        if function not in self.MCP_FUNCTION:
            raise TypeError("Invalid function name should be input or output.")

        pin = self.pins[pin]
        self._device.set_pin_dir(self.PIN_NUMBER_MAP[pin.pin_num],
                                 self.MCP_FUNCTION[function])
        pin.function = function 

    def set_pin_pull(self, pin, pull):
        if pull not in self.MCP_PULL:
            raise TypeError("Invalid pull name, should be up or dowm.")

        pin = self.pins[pin]
        if pin.function is 'input':
            self._device.set_pin_pull_up(self.PIN_NUMBER_MAP[pin.pin_num],
                                         self.MCP_PULL[pull])
            pin.pull = pull
        else:
            raise NotInputPin("Can't set pull up resistor to a non input pin.")

    def set_pin_pwm(self, pin, pwm):
        if not isinstance(pwm, bool):
            raise TypeError("Invalid pwm type, should be boolean.")

        pin_name = pin
        pin = self.pins[pin]
        if pin.function is not 'output':
            raise NotOutputPin("Can't set pwm to a non output pin.")
        
        prev_pwm = pin.pwm
        pin.pwm = pwm
        if not prev_pwm and pwm:
            # The pwm is deactivated and it will be activated.
            pin.frequency = 1
            pin.duty_cycle = 0
            # Start thread
            self._pwm_timers[pin.pin_num] = [0, 1/pin.frequency]
            thread = threading.Thread(target=self._spwm, args=(pin,), daemon=True)
            thread.start()
        elif prev_pwm and not pwm:
            # The pwm is activated and will be deactivated.
            pin.frequency = None
            pin.duty_cycle = None

    def set_pin_frequency(self, pin, frequency):
        pin_name = pin
        pin = self.pins[pin]
        if pin.pwm:
            pin.frequency = frequency
        else:
            raise NotPwmPin("Can't set frequency to a non pwm pin.")
 
    def _spwm(self, pin):
        """Gen spwm."""
        while pin.pwm:
            with self._spwm_mutex:
                self._device.write(self.PIN_NUMBER_MAP[pin.pin_num], 1)
            time.sleep(self._pwm_timers[pin.pin_num][0])
            with self._spwm_mutex:
                self._device.write(self.PIN_NUMBER_MAP[pin.pin_num], 0)
            time.sleep(self._pwm_timers[pin.pin_num][1])

        del self._pwm_timers[pin.pin_num]

    def set_pin_edge(self, pin, edge):
        pin = self.pins[pin]
        if edge not in self.MCP_EDGES:
            raise TypeError("Wrong edge name, should be rising, falling or both")
        if pin.function is 'input':
            pin.edge = edge
            self._device.set_pin_intcon(self.PIN_NUMBER_MAP[pin.pin_num],
                                        self.MCP_EDGES[pin.edge].intcon)
            self._device.set_pin_def_val(self.PIN_NUMBER_MAP[pin.pin_num],
                                         self.MCP_EDGES[pin.edge].defval)
        else:
            raise NotInputPin("Can't set edge to a non input pin.")

    def set_pin_bounce(self, pin, bounce):
        pin = self.pins[pin]

        if pin.function is 'input':
            self._device.set_pin_debounce(self.PIN_NUMBER_MAP[pin.pin_num],
                                          bounce)
            pin.bounce = bounce
        else:
            raise NotInputPin("Can't set edge to a non input pin.")

    def set_pin_event(self, pin, event, *args):
        """Set the function that will be called with a new edge.
        
        In RPi.GPIO calling this function enables interrupt handling. In this
        implementation the :meth:`start_polling` function need to be called 
        in order to catch interrupts.

        Args:
            pin (str): Pin name
            event (function): Function pointer to the target function.
            *args: The arguments of the target function.

        Raises:
            NotInputPin: Try to set event to a non input pin.
        """
        pass

        pin_name = pin
        pin = self.pins[pin]

        if pin.function is 'input':
            if pin.bounce is None:
                self.set_pin_bounce(pin_name, 0)

            # Enable interrupts on pin
            self._device.set_pin_int(self.PIN_NUMBER_MAP[pin.pin_num], 1)
            self._int_pins.append(pin)  # Append to list with intrpt enable pins

            # Set event
            pin.event = event
            self._device.set_int_handl_func(self.PIN_NUMBER_MAP[pin.pin_num],
                                            event,
                                            *args)
        else:
            # Raise exception output pin
            raise NotInputPin("Can's set event to a non input pin.")

    def start_polling(self, pins):
        """Start polling for interrupts the specified pins.
        
        Args:
            pins (list): List with the names of the target pins to be polled.
        """
        pins = pins if isinstance(pins, list) else [pins]

        pins = [self.PIN_NUMBER_MAP[self.pins[pin].pin_num] for pin in pins]
        self._device.poll_int_async(pins)

    def stop_polling(self):
        """Stop polling for interrupts"""

        self._device.stop_poll_int_async()

    def wait_pin_for_edge(self, pin, timeout=None):
        """Wait pin for an edge detection.

        Args:
            pin (str): Pin name.
            timeout (int): The time until it stops waiting for an edge signal.

        Returns:
            int: Indicating if the interrupt occured.

        Raise:
            NotInputPin: Can't wait for edge to a non input pin.
        """

        pin = self.pins[pin]
        if pin.function is'input':
            ret = self._device.wait_pin_for_edge(self.PIN_NUMBER_MAP[pin.pin_num],
                                                 timeout)
        else:
            raise NotInputPin("Can's wait for an event to a non input pin.")
        
        return ret

    def close(self):
        """Close interface.input"""

        # Clear interrupts from pins that have them enabled.
        for i in range(len(self._int_pins)):
            pin = self._int_pins[0]
            self._device.set_pin_int(self.PIN_NUMBER_MAP[pin.pin_num], 0)
            del self._int_pins[0]

        self.remove_pins(*self.pins.keys())
        self._device.stop()


class Mcp23017GPIO(Mcp23x17GPIO):
    """GPIO class implementation using mcp23017 chip. Extends :class:`Mcp23x17GPIO`
    
    Args:
        bus (int): Optional argument for specifying the i2c bus of the mcp23017
            module. Defaults to :data:`1`.
        address (int): Optional argument for specifying the i2c address of the 
            mcp23017 module. Defaults to :data:`0x20`.
        **kwargs: Could be multiple keyword arguments in the form of
            pin_name = pin_number(pin number is A_x or B_x, because the 
            implementation use the mcp23x17 devices.) For example for the 
            hc-sr04 sonar, it would be echo="A_1", trigger="B_2".
    """

    def __init__(self, bus=1, address=0x20, **kwargs):
        """Contructor"""

        self._bus = bus
        self._address = address
        super(Mcp23017GPIO, self).__init__(**kwargs)

    def initialize(self):
        """Initialize hardware and os resources."""
        self._device = MCP23017(bus=self._bus, address=self._address)

        # Configuration for interrupts
        self._device.set_mirror(0)  # Clear the mirror bit for separate interrupts
        self._device.set_intpol(1)  # Set int output to active high.
