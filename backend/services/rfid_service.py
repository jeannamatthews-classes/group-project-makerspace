import evdev
from evdev import InputDevice, categorize, ecodes
import requests
import time
import os
from datetime import datetime, timezone

# This script reads RFID input from a connected device and sends the UID to a backend server.

DEVICE_PATH = os.getenv("RFID_DEVICE_PATH", "/dev/input/event3")

# Will change this to our backend URL once we have it set up
API_URL = os.getenv("RFID_API_URL", "")
DEVICE_ID = os.getenv("RFID_DEVICE_ID", "")

try:
    device = InputDevice(DEVICE_PATH)
except FileNotFoundError:
    print(f"RFID Device not found at {DEVICE_PATH}")
    exit(1)

print("RFID Client Started...")
rfid = ""

# Function to send the UID to the backend server
def send_to_backend(uid):
    payload = {
        "card_uid": uid,
        "device_id": DEVICE_ID,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    try:
        response = requests.post(API_URL, json=payload, timeout=5)
        try:
                data = response.json()
        except ValueError:
                print("Invalid JSON response from server")
                return
        
        decision = data.get("decision")
        reason = data.get("reason", "No reason provided")
        student = data.get("student_id")

        if decision == "GRANT":
            print(f"Access Granted ({student}) - {reason}")

        # Access Denied - Card is registered but access is denied (e.g., expired, blacklisted)
        elif decision == "DENY":
            print(f"Access Denied - {reason}")
  
        else:
            print("Unexpected response:", data)

    except requests.exceptions.RequestException as e:
        print("Connection Failed:", e)

# Main loop to read RFID input
for event in device.read_loop():
    if event.type == ecodes.EV_KEY:
        key = categorize(event)

        if key.keystate == 1:  # Key Down
            if key.keycode == 'KEY_ENTER':
                if rfid:
                    print("Card Detected:", rfid)
                    send_to_backend(rfid)
                    rfid = ""

            else:
                if isinstance(key.keycode, list):
                    k = key.keycode[0]
                else:
                    k = key.keycode

                if k.startswith("KEY_"):
                    digit = k.replace("KEY_", "")
                    if digit.upper() in "0123456789ABCDEF":
                        rfid += digit.upper()