import evdev
from evdev import InputDevice, categorize, ecodes
import requests
import time
import os
from datetime import datetime, timezone
import json
import threading

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

# Offline Queue 
QUEUE_FILE = os.getenv("RFID_QUEUE_FILE", "rfid_queue.json") # use env var if set, otherwise fall back to local default file
RETRY_SECONDS = 10
queue_lock = threading.Lock()  # prevents two threads from reading/writing the queue file at the same time


def load_queue():
    with queue_lock:  # only one thread can read/write the queue file at a time
        if not os.path.exists(QUEUE_FILE):  # if the file does not exist yet, just start with an empty queue
            return []
        try:
            with open(QUEUE_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            print("Queue file read failed:", e)  # can be replaced with fuller logging later if another module handles device logs
            return []  # if something is wrong with the file, do not crash the scanner

def save_queue(queue):
    with queue_lock:  # lock while writing so another thread does not read/write at the same time
        with open(QUEUE_FILE, "w") as f:  # save the current queue back into the local JSON file
            json.dump(queue, f)


def add_event_to_queue(payload):
    with queue_lock:  # lock the full read-update-write sequence so it happens safely
        if not os.path.exists(QUEUE_FILE):
            queue = []
        else:
            try:
                with open(QUEUE_FILE, "r") as f:
                    queue = json.load(f)
            except Exception:
                queue = []  # if something is wrong with the file, do not crash the scanner

        queue.append(payload)  # add the new failed event to the end of the queue

        with open(QUEUE_FILE, "w") as f:
            json.dump(queue, f)

    print("Event saved locally for retry.")

# tries to send one RFID event to the backend

def try_send_payload(payload):
    try:
        # NOTE: possible duplicate-event edge case here.
        # The backend may have already received and processed this event,
        # but if the client fails while reading the response,
        # this function returns False and the payload may be queued again.
        # If deduplication is needed later, it will likely need to be handled
        # in the backend or by adding a unique client-generated event ID.
        response = requests.post(API_URL, json=payload, timeout=5)

        try:  # try converting the server response into JSON
            data = response.json()
        except ValueError:
            print("Invalid JSON response from server!!")
            return False

        decision = data.get("decision")
        reason = data.get("reason", "No reason provided")
        student = data.get("student_id")

        if response.status_code == 200: # backend successfully received and processed the event

            if decision == "GRANT":
                print(f"Access Granted ({student}) - {reason}")
            elif decision == "DENY":
                print(f"Access Denied - {reason}")
            else:
                print("Unexpected response:", data)

            return True

        print("Server Error:", response.status_code) # unsuccessful send 
        return False

    except requests.exceptions.RequestException as e: # catches addiitonal request failures
        print("Connection Failed:", e)
        return False


def retry_queued_events():
    queue = load_queue() # load any events that were previously saved because they could not be sent
    if len(queue) == 0: # if queue is empty, exit 
        return
    
    print(f"Retrying {len(queue)} queued event(s)...")
    new_queue = [] # holds any events that still fail after retrying

    for payload in queue: # try sending each queued event again
        success = try_send_payload(payload)
        if not success: #  if an event still cannot be sent, keep it in the queue
            new_queue.append(payload)

    save_queue(new_queue) # save only the failed events

    if len(new_queue) == 0: # queue is empty if all events were sent successfully 
        print("Queue cleared.")
    else:
        print(f"{len(new_queue)} event(s) still waiting in queue.")


# Redefined send_to_backend so I won't have to change the main loop
# NOTE: deduplication is not handled in this file yet.
# If the same event gets retried, duplicate prevention will likely need to be
# added in the backend access-events flow or by attaching a unique event ID later.
def send_to_backend(uid):
    payload = {
        "card_uid": uid,
        "device_id": DEVICE_ID,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    # First try to send anything older that was saved in the queue
    retry_queued_events()

    # Then try the current scan
    success = try_send_payload(payload)

    # NOTE: this may re-queue an event that was already processed by the backend
    # if the request succeeded but the client failed while handling the response.
    # Deduplication is not handled in this file yet.
    if not success:
        add_event_to_queue(payload)


def background_retry():
    while True: #  continuously retry queued events while the RFID script is running
        retry_queued_events()
        time.sleep(RETRY_SECONDS)

# start a background thread so retries happen automatically while the scanner is running
retry_thread = threading.Thread(target=background_retry, daemon=True)
retry_thread.start()


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