import evdev
from evdev import InputDevice, categorize, ecodes
import requests
import time

# This script reads RFID input from a connected device and sends the UID to a backend server.

DEVICE_PATH = '/dev/input/event3'

# Will change this to our backend URL once we have it set up
API_URL = ''

device = InputDevice(DEVICE_PATH)

print("RFID Client Started...")
rfid = ""

# Function to send the UID to the backend server
def send_to_backend(uid):
    try:
        response = requests.post(API_URL, json={"uid": uid}, timeout=5)

        if response.status_code == 200:
            data = response.json()
            message = data.get("message", "Unknown Response")
            print(message)

        elif response.status_code == 404:
            print("Not Registered")

        elif response.status_code == 403:
            print("Access Denied")
            
        else:
            print("Server Error:", response.status_code)

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
                    if digit.isdigit():
                        rfid += digit