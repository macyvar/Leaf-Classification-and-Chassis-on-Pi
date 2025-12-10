import RPi.GPIO as GPIO
import time

TRIG = 5
ECHO = 6

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

def get_distance():
    # Send trigger pulse
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    # Wait for echo start with timeout
    start_time = time.time()
    timeout = start_time + 0.02
    while GPIO.input(ECHO) == 0:
        start_time = time.time()
        if time.time() > timeout:
            return 999  # no reading

    # Wait for echo end with timeout
    stop_time = time.time()
    timeout = stop_time + 0.02
    while GPIO.input(ECHO) == 1:
        stop_time = time.time()
        if time.time() > timeout:
            return 999

    # Calculate distance
    distance = (stop_time - start_time) * 17150  # cm

    # Clamp weird values
    if distance < 2 or distance > 400:
        return 999

    return distance
