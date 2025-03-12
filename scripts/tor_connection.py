import os
import subprocess
import time


def is_tor_running():
    """Check if the Tor service is running."""
    try:
        output = subprocess.check_output(["systemctl", "is-active", "tor"], text=True).strip()
        return output == "active"
    except subprocess.CalledProcessError:
        return False


def start_tor():
    """Start the Tor service if it's not running."""
    print("[Info] Checking Tor connection...")

    if is_tor_running():
        print("[Success] Tor is already running.")
    else:
        print("[Warning] Tor is not running. Attempting to start Tor service...")
        os.system("sudo systemctl start tor")
        time.sleep(3)  # Give it some time to start

        if is_tor_running():
            print("[Success] Tor service started successfully.")
        else:
            print("[Error] Failed to start Tor. Please start it manually using 'sudo systemctl start tor'.")


if __name__ == "__main__":
    start_tor()
