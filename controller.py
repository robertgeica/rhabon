import RPi.GPIO as GPIO
import sys
import json
import asyncio
import signal

# Default duration in minutes if not specified for a pin
DEFAULT_DURATION_MINUTES = 10


# Prints usage instructions and exits.
def print_usage():
    print(
        'Usage: python3 controller.py \'[{"pin": 17, "state": true, "duration": 5}, {"pin": 18, "state": false}]\''
    )
    print("Duration is optional and in minutes; default is 10 minutes.")
    sys.exit(1)


# Validates the JSON input data for correct format and types.
# Returns a list of pin dicts with pin, state, and duration.
def validate_pins_data(data):
    if not isinstance(data, list):
        print("Error: JSON input must be a list of pin objects.")
        sys.exit(1)
    pins = []
    for item in data:
        if not isinstance(item, dict):
            print("Error: Each pin object must be a dictionary.")
            sys.exit(1)
        if "pin" not in item or "state" not in item:
            print("Error: Each pin object must have 'pin' and 'state'.")
            sys.exit(1)
        pin = item["pin"]
        state = item["state"]
        duration = item.get("duration", DEFAULT_DURATION_MINUTES)

        # Validate pin is integer
        try:
            pin = int(pin)
        except:
            print(f"Error: Pin must be integer, got {pin}")
            sys.exit(1)

        # Validate state is boolean
        if not isinstance(state, bool):
            print(f"Error: State must be boolean for pin {pin}.")
            sys.exit(1)

        # Validate duration is a number
        try:
            duration = float(duration)
        except:
            print(f"Error: Duration must be a number for pin {pin}.")
            sys.exit(1)
        pins.append({"pin": pin, "state": state, "duration": duration})
    return pins


# Coroutine to control a single GPIO pin.
# Sets the pin to the requested state, waits for the duration, then resets the pin to LOW.
# Handles cancellation gracefully.
async def control_pin(pin, state, duration):
    gpio_state = GPIO.HIGH if state else GPIO.LOW
    GPIO.output(pin, gpio_state)
    print(
        f"GPIO pin {pin} set to {'HIGH' if gpio_state == GPIO.HIGH else 'LOW'}. Duration: {duration} minutes."
    )

    # Sleep asynchronously for the specified duration (converted to seconds)
    try:
        await asyncio.sleep(duration * 60)

    # Handle task cancellation (e.g., user pressed Ctrl+C)
    except asyncio.CancelledError:
        print(f"Timer for pin {pin} cancelled.")

    # Always reset the pin to LOW on completion or cancellation
    finally:
        GPIO.output(pin, GPIO.LOW)
        print(f"GPIO pin {pin} reset to LOW.")


# Main coroutine to parse input, setup GPIO,
# create and run pin control tasks concurrently,
# and handle graceful shutdown on signals.
async def main():
    if len(sys.argv) < 2:
        print_usage()

    # Parse JSON argument with pin configurations
    try:
        pins_data = json.loads(sys.argv[1])
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        print_usage()

    # Validate and normalize pin data
    pins = validate_pins_data(pins_data)

    # Setup GPIO mode and pins
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    for p in pins:
        GPIO.setup(p["pin"], GPIO.OUT)

    # Create asyncio tasks for each pin control coroutine
    tasks = [
        asyncio.create_task(control_pin(p["pin"], p["state"], p["duration"]))
        for p in pins
    ]

    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()

    # Signal handler to catch SIGINT and SIGTERM for graceful exit
    def stop_signal_handler():
        print("\nReceived exit signal. Cleaning up GPIO...")
        stop_event.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop_signal_handler)

    # Gather all pin tasks
    pin_tasks = asyncio.gather(*tasks)
    # Create a task that waits for stop_event to be set
    stop_task = asyncio.create_task(stop_event.wait())

    # Wait until either all pin tasks finish or stop_event is set (user interrupt)
    done, pending = await asyncio.wait(
        {pin_tasks, stop_task}, return_when=asyncio.FIRST_COMPLETED
    )

    if stop_event.is_set():
        # User requested exit; cancel all pin tasks
        for task in tasks:
            task.cancel()
        # Wait for all cancellations to complete
        await asyncio.gather(*tasks, return_exceptions=True)
    else:
        # All pin tasks completed normally; cancel the stop_task
        stop_task.cancel()
        await asyncio.gather(stop_task, return_exceptions=True)

    # Now just clean up GPIO; pins are already LOW individually
    GPIO.cleanup()
    print("GPIO cleaned up. Exiting.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Unexpected error: {e}")
        GPIO.cleanup()
        sys.exit(1)
