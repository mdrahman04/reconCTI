import os
import subprocess
import time
import requests

TOR_PROXY = "socks5h://127.0.0.1:9050"  # def Tor SOCKS5 proxy

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
        time.sleep(3)

        if is_tor_running():
            print("[Success] Tor service started successfully.")
        else:
            print("[Error] Failed to start Tor. Please start it manually using 'sudo systemctl start tor'.")

def get_tor_session():
    """Return a requests session that routes traffic through Tor."""
    session = requests.Session()
    session.proxies = {
        "http": TOR_PROXY,
        "https": TOR_PROXY
    }
    return session

def check_tor_status():
    """Check if Tor is working by making a request through the Tor network."""
    session = get_tor_session()
    test_url = "http://check.torproject.org"

    try:
        response = session.get(test_url, timeout=10)
        if "Congratulations" in response.text:
            print("[Success] Tor is working! You are using the Tor network.")
            return True
        else:
            print("[Warning] Tor is running, but the connection is not through Tor.")
            return False
    except requests.RequestException:
        print("[Error] Unable to reach Tor check site. Ensure Tor is properly configured.")
        return False
