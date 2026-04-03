import evdev
from evdev import InputDevice, categorize, ecodes
import requests
import time
import os
from datetime import datetime, timezone
import json
import threading

# Device configuration
DEVICE_PATH = os.getenv("RFID_DEVICE_PATH", "/dev/input/event3")
API_URL = os.getenv("RFID_API_URL", "")
DEVICE_ID = os.getenv("RFID_DEVICE_ID", "")

# Initialize RFID device
try:
    device = InputDevice(DEVICE_PATH)
except FileNotFoundError:
    print(f"RFID Device not found at {DEVICE_PATH}")
    exit(1)

# Ensure API URL is set
if not API_URL:
    print("ERROR: RFID_API_URL is not set")
    exit(1)

print("RFID Client Started...")
rfid = ""

# Offline queue configuration
QUEUE_FILE = os.getenv("RFID_QUEUE_FILE", "rfid_queue.json")
RETRY_SECONDS = 10
queue_lock = threading.Lock()


def load_queue():
    with queue_lock:
        if not os.path.exists(QUEUE_FILE):
            return []
        try:
            with open(QUEUE_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            print("Queue file read failed:", e)
            return []


def save_queue(queue):
    with queue_lock:
        with open(QUEUE_FILE, "w") as f:
            json.dump(queue, f)


def add_event_to_queue(payload):
    with queue_lock:
        if not os.path.exists(QUEUE_FILE):
            queue = []
        else:
            try:
                with open(QUEUE_FILE, "r") as f:
                    queue = json.load(f)
            except Exception:
                queue = []

        queue.append(payload)

        with open(QUEUE_FILE, "w") as f:
            json.dump(queue, f)

    print("Event saved locally for retry.")


def try_send_payload(payload):
    try:
        response = requests.post(API_URL, json=payload, timeout=5)

        try:
            data = response.json()
        except ValueError:
            print("Invalid JSON response from server")
            return False

        decision = data.get("decision")
        reason = data.get("reason", "No reason provided")
        student = data.get("student_id")

        if response.status_code == 200:
            if decision == "GRANTED":
                print(f"Access Granted ({student}) - {reason}")
            elif decision == "DENIED":
                print(f"Access Denied - {reason}")
            else:
                print("Unexpected response:", data)

            return True

        print("Server Error:", response.status_code)
        return False

    except requests.exceptions.RequestException as e:
        print("Connection Failed:", e)
        return False


def retry_queued_events():
    queue = load_queue()

    if len(queue) == 0:
        return

    print(f"Retrying {len(queue)} queued event(s)...")
    new_queue = []

    for payload in queue:
        success = try_send_payload(payload)
        if not success:
            new_queue.append(payload)

    save_queue(new_queue)

    if len(new_queue) == 0:
        print("Queue cleared.")
    else:
        print(f"{len(new_queue)} event(s) still waiting in queue.")


def send_to_backend(uid):
    payload = {
        "card_uid": uid,
        "device_id": DEVICE_ID,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    # Retry old events first
    retry_queued_events()

    # Send current event
    success = try_send_payload(payload)

    if not success:
        add_event_to_queue(payload)


def background_retry():
    while True:
        retry_queued_events()
        time.sleep(RETRY_SECONDS)


# Start background retry thread
retry_thread = threading.Thread(target=background_retry, daemon=True)
retry_thread.start()


# Main RFID reading loop
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