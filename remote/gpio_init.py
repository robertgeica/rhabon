# gpio_init.py
import RPi.GPIO as GPIO

# List of GPIO pins used to control the relays (update with your pins)
PINS = [17, 27, 22, 05, 06, 13, 19, 26]

# Disable GPIO warnings to avoid warnings if pins are already in use
GPIO.setwarnings(False)

# Set GPIO numbering mode to BCM (Broadcom SoC channel numbers)
GPIO.setmode(GPIO.BCM)

# Setup each pin as output and set it HIGH to deactivate the relay (active-low)
for pin in PINS:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.HIGH)  # HIGH means relay is off (inactive)

# Do NOT call GPIO.cleanup() here because:
# cleanup() resets all GPIO channels which might immediately
# turn pins to input and cause undesired relay state changes.
# Instead, leave GPIO initialized so the pins stay in desired state.
# Call cleanup() only when your program terminates completely.

# If you want to clean up (reset pins) on exit, do it explicitly in your main application.
