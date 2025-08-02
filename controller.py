# Import required modules
import RPi.GPIO as GPIO  # For controlling Raspberry Pi GPIO pins
import sys  # For command-line argument handling
import json  # For decoding JSON
import asyncio  # For async task management
import signal  # For handling termination signals
import base64  # For decoding the base64-encoded input
from collections import defaultdict  # For grouping pins by execution order

# Default pin activation duration in minutes
DEFAULT_DURATION_MINUTES = 10


def print_usage():
    # Print usage instructions and exit the program.
    # python3 controller.py '[{"pin": 17, "state": true, "duration": 5, "order": 1}]'
    print(
        "Usage: python3 controller.py '[{\"pin\": 17, \"state\": true, \"duration\": 5, \"order\": 1}]'",
        flush=True,
    )
    print("Duration is optional and in minutes; default is 10 minutes.", flush=True)
    sys.exit(1)


def validate_pins_data(data):
    # Validate the decoded JSON pin data. Each item must be a dictionary
    # with required keys: 'pin' (int), 'state' (bool), optional 'duration' (float) and 'order' (int).
    # Returns a list of validated pin configurations.
    if not isinstance(data, list):
        print("Error: JSON input must be a list of pin objects.", flush=True)
        sys.exit(1)

    pins = []
    for item in data:
        if not isinstance(item, dict):
            print("Error: Each pin object must be a dictionary.", flush=True)
            sys.exit(1)
        if "pin" not in item or "state" not in item:
            print("Error: Each pin object must have 'pin' and 'state'.", flush=True)
            sys.exit(1)

        try:
            pin = int(item["pin"])
        except:
            print(f"Error: Pin must be integer, got {item['pin']}", flush=True)
            sys.exit(1)

        state = item["state"]
        if not isinstance(state, bool):
            print(f"Error: State must be boolean for pin {pin}.", flush=True)
            sys.exit(1)

        try:
            duration = float(item.get("duration", DEFAULT_DURATION_MINUTES))
        except:
            print(f"Error: Duration must be a number for pin {pin}.", flush=True)
            sys.exit(1)

        try:
            order = int(item.get("order", 0))
        except:
            print(f"Error: Order must be an integer for pin {pin}.", flush=True)
            sys.exit(1)

        pins.append(
            {
                "pin": pin,
                "state": state,
                "duration": duration,
                "order": order,
            }
        )

    return pins


async def control_pin(pin, state, duration):
    # Control a single GPIO pin for a specified duration.
    # Sets the pin to LOW if state is True (active), else HIGH (inactive).
    gpio_state = GPIO.LOW if state else GPIO.HIGH
    GPIO.output(pin, gpio_state)
    print(
        f"GPIO pin {pin} set to {'LOW (activated)' if gpio_state == GPIO.LOW else 'HIGH (deactivated)'}. Duration: {duration} minutes.",
        flush=True,
    )

    try:
        # Keep pin active for the specified duration
        await asyncio.sleep(duration * 60)
    except asyncio.CancelledError:
        # Handle cancellation (e.g., on termination signal)
        print(f"Timer for pin {pin} cancelled.", flush=True)
    finally:
        # Always deactivate the pin afterward
        GPIO.output(pin, GPIO.HIGH)
        print(f"GPIO pin {pin} reset to HIGH (deactivated).", flush=True)


async def main():
    # Main entry point: decode input, validate, group, and control GPIO pins asynchronously.
    # Handles signals for graceful shutdown.
    if len(sys.argv) < 2:
        print_usage()

    try:
        # Decode base64-encoded JSON string
        decoded = base64.b64decode(sys.argv[1]).decode("utf-8")
        pins_data = json.loads(decoded)
    except Exception as e:
        print(f"Error decoding or parsing JSON: {e}", flush=True)
        print_usage()

    # Validate pin configuration
    pins = validate_pins_data(pins_data)

    # Initialize GPIO mode and disable warnings
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    for p in pins:
        GPIO.setup(p["pin"], GPIO.OUT)

    # Group pins by execution order
    grouped_pins = defaultdict(list)
    for p in pins:
        grouped_pins[p["order"]].append(p)

    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()

    # Signal handler to allow clean GPIO shutdown
    def stop_signal_handler():
        print("\nReceived exit signal. Cleaning up GPIO...", flush=True)
        stop_event.set()

    # Register signal handlers for termination (e.g., Ctrl+C)
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop_signal_handler)

    try:
        # Process pin groups sequentially based on order
        for order in sorted(grouped_pins):
            current_group = grouped_pins[order]
            print(f"\nStarting group with order {order}...", flush=True)

            # Start pin control tasks for the current group
            tasks = [
                asyncio.create_task(control_pin(p["pin"], p["state"], p["duration"]))
                for p in current_group
            ]

            # Create task for detecting stop event
            group_tasks = asyncio.gather(*tasks)
            stop_task = asyncio.create_task(stop_event.wait())

            # Wait until either pin tasks complete or stop event is triggered
            done, pending = await asyncio.wait(
                {group_tasks, stop_task}, return_when=asyncio.FIRST_COMPLETED
            )

            # If stop was requested, cancel all pin tasks
            if stop_event.is_set():
                for task in tasks:
                    task.cancel()
                await asyncio.gather(*tasks, return_exceptions=True)
                break  # Exit processing loop

            # Cancel stop task if it wasn’t triggered
            stop_task.cancel()
            await asyncio.gather(stop_task, return_exceptions=True)

    finally:
        # Cleanup GPIO before exiting
        GPIO.cleanup()
        print("GPIO cleaned up. Exiting.", flush=True)


# Entry point when script is executed directly
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Unexpected error: {e}", flush=True)
        GPIO.cleanup()
        sys.exit(1)
