import os
import signal
import sys

# Path to the file storing the PID of the running valve controller script
PID_FILE = "/tmp/valve_controller.pid"

def read_pid(pid_file):
    # Reads the PID from the given file and returns it as an integer.
    if not os.path.exists(pid_file):
        raise FileNotFoundError(f"PID file not found: {pid_file}")

    with open(pid_file, "r") as f:
        pid_str = f.read().strip()

    if not pid_str.isdigit():
        raise ValueError(f"Invalid PID content: '{pid_str}'")

    return int(pid_str)

def is_process_running(pid):
    # Checks if a process with the given PID exists.
    try:
        os.kill(pid, 0)  # Signal 0 checks existence without killing
        return True
    except OSError:
        return False

def terminate_process(pid):
    # Attempts to terminate the process with SIGTERM.
    os.kill(pid, signal.SIGTERM)

def main():
    try:
        pid = read_pid(PID_FILE)

        if not is_process_running(pid):
            raise ProcessLookupError(f"No running process with PID {pid}.")

        terminate_process(pid)
        print(f"Process {pid} terminated.", flush=True)

        # Remove the PID file
        os.remove(PID_FILE)

    except Exception as e:
        print(f"Failed to stop process: {e}", file=sys.stderr, flush=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
