# motor/tb6612.py  (driver for TB6612FNG)

import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

# Direction pins
AIN1 = 17
AIN2 = 27
BIN1 = 22
BIN2 = 23

# PWM pins
PWMA = 12  # Left motor
PWMB = 13  # Right motor

# Setup
for pin in [AIN1, AIN2, BIN1, BIN2, PWMA, PWMB]:
    GPIO.setup(pin, GPIO.OUT)

left_pwm = GPIO.PWM(PWMA, 1000)
right_pwm = GPIO.PWM(PWMB, 1000)

left_pwm.start(0)
right_pwm.start(0)

def set_left_motor(speed):
    if speed > 0:
        GPIO.output(AIN1, 1)
        GPIO.output(AIN2, 0)
    elif speed < 0:
        GPIO.output(AIN1, 0)
        GPIO.output(AIN2, 1)
    else:
        GPIO.output(AIN1, 0)
        GPIO.output(AIN2, 0)
    left_pwm.ChangeDutyCycle(abs(speed))

def set_right_motor(speed):
    if speed > 0:
        GPIO.output(BIN1, 1)
        GPIO.output(BIN2, 0)
    elif speed < 0:
        GPIO.output(BIN1, 0)
        GPIO.output(BIN2, 1)
    else:
        GPIO.output(BIN1, 0)
        GPIO.output(BIN2, 0)
    right_pwm.ChangeDutyCycle(abs(speed))

def forward(speed=60):
    set_left_motor(speed)
    set_right_motor(speed)

def backward(speed=60):
    set_left_motor(-speed)
    set_right_motor(-speed)

def stop():
    set_left_motor(0)
    set_right_motor(0)

def turn_left(speed=50, dur=0.4):
    set_left_motor(-speed)
    set_right_motor(speed)
    time.sleep(dur)
    stop()

def turn_right(speed=50, dur=0.4):
    set_left_motor(speed)
    set_right_motor(-speed)
    time.sleep(dur)
    stop()
