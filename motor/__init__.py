# motor/__init__.py

from config import USE_DRIVER

if USE_DRIVER.upper() == "L298N":
    from .l298n import forward, backward, stop, turn_left, turn_right
elif USE_DRIVER.upper() == "TB6612":
    from .tb6612 import forward, backward, stop, turn_left, turn_right
else:
    raise ValueError(f"Unknown motor driver: {USE_DRIVER}")
