## MOTOR.PY

import RPi.GPIO as GPIO
import time

IN1, IN2, IN3, IN4 = 17, 27, 22, 23
ENA, ENB = 12, 13  # PWM

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

GPIO.setup([IN1, IN2, IN3, IN4], GPIO.OUT)
GPIO.setup(ENA, GPIO.OUT)
GPIO.setup(ENB, GPIO.OUT)

pwm_left = GPIO.PWM(ENA, 1000)
pwm_right = GPIO.PWM(ENB, 1000)
pwm_left.start(0)
pwm_right.start(0)

def set_speed(d):
    pwm_left.ChangeDutyCycle(d)
    pwm_right.ChangeDutyCycle(d)

def forward(speed=60):
    set_speed(speed)
    GPIO.output(IN1,1); GPIO.output(IN2,0)
    GPIO.output(IN3,1); GPIO.output(IN4,0)

def backward(dur=0.3, speed=60):
    set_speed(speed)
    GPIO.output(IN1,0); GPIO.output(IN2,1)
    GPIO.output(IN3,0); GPIO.output(IN4,1)
    time.sleep(dur)
    stop()

def stop():
    GPIO.output(IN1,0); GPIO.output(IN2,0)
    GPIO.output(IN3,0); GPIO.output(IN4,0)
    set_speed(0)

def turn_left(dur=0.4, speed=50):
    pwm_left.ChangeDutyCycle(0)
    pwm_right.ChangeDutyCycle(speed)
    GPIO.output(IN1,0); GPIO.output(IN2,1)
    GPIO.output(IN3,1); GPIO.output(IN4,0)
    time.sleep(dur); stop()

def turn_right(dur=0.4, speed=50):
    pwm_left.ChangeDutyCycle(speed)
    pwm_right.ChangeDutyCycle(0)
    GPIO.output(IN1,1); GPIO.output(IN2,0)
    GPIO.output(IN3,0); GPIO.output(IN4,1)
    time.sleep(dur); stop()
