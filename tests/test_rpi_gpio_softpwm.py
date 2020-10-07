import RPi.GPIO as GPIO # always needed with RPi.GPIO  
from time import sleep  # pull in the sleep function from time module  
  

counter = 0


def counter_callback(channel):
    global counter
    counter = counter + 1


if __name__ == '__main__':
    GPIO.setmode(GPIO.BCM)  # choose BCM or BOARD numbering schemes. I use BCM  

    left_motor_pin = 20
    right_motor_pin = 12

    #left_encoder_pin = 23

    GPIO.setup(left_motor_pin, GPIO.OUT)# set GPIO 25 as output for white led  
    GPIO.setup(right_motor_pin, GPIO.OUT)# set GPIO 25 as output for white led  

    #GPIO.setup(left_encoder_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    #GPIO.add_event_detect(left_encoder_pin, GPIO.BOTH, callback=counter_callback)  # add rising edge detection on a channel

    left_motor = GPIO.PWM(left_motor_pin, 200)    # create object white for PWM on port 25 at 100 Hertz  
    right_motor = GPIO.PWM(right_motor_pin, 200)

    left_motor.start(0)              # start white led on 0 percent duty cycle (off)  
    right_motor.start(0)

    pause_time = 0.1           # you can change this to slow down/speed up  

    try:  
        while True:  
            for i in range(0,101):      # 101 because it stops when it finishes 100  
                left_motor.ChangeDutyCycle(i)  
                right_motor.ChangeDutyCycle(i)  
                sleep(pause_time)  
                #print(f"counter is: {counter}")
            for i in range(100,-1,-1):      # from 100 to zero in steps of -1  
                left_motor.ChangeDutyCycle(i) 
                right_motor.ChangeDutyCycle(i)  
                sleep(pause_time)  
                #print(f"counter is: {counter}")


    except KeyboardInterrupt:  
        left_motor.stop()            # stop the white PWM output
        right_motor.stop()  
        GPIO.cleanup()          # clean up GPIO on CTRL+C exit  