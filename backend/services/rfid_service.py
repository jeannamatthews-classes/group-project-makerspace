import json
import os
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

<<<<<<< HEAD
import requests
from evdev import InputDevice, categorize, ecodes


BASE_DIR = Path(__file__).resolve().parent
=======
# Device configuration
>>>>>>> 2be73f6af9b7843775f301664e7cc2b2203c397d
DEVICE_PATH = os.getenv("RFID_DEVICE_PATH", "/dev/input/event3")
API_URL = os.getenv("RFID_API_URL", "")
DEVICE_ID = os.getenv("RFID_DEVICE_ID", "")
QUEUE_FILE = os.getenv("RFID_QUEUE_FILE", str(BASE_DIR / "rfid_queue.json"))
RETRY_SECONDS = int(os.getenv("RFID_RETRY_SECONDS", "10"))
REQUEST_TIMEOUT = int(os.getenv("RFID_REQUEST_TIMEOUT", "5"))
GRAB_DEVICE = os.getenv("RFID_GRAB_DEVICE", "true").lower() == "true"

<<<<<<< HEAD
queue_lock = threading.Lock()


KEY_MAP = {
    "KEY_0": "0",
    "KEY_1": "1",
    "KEY_2": "2",
    "KEY_3": "3",
    "KEY_4": "4",
    "KEY_5": "5",
    "KEY_6": "6",
    "KEY_7": "7",
    "KEY_8": "8",
    "KEY_9": "9",
    "KEY_A": "A",
    "KEY_B": "B",
    "KEY_C": "C",
    "KEY_D": "D",
    "KEY_E": "E",
    "KEY_F": "F",
}


def log(message: str):
    print(f"[RFID] {message}")
=======
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
>>>>>>> 2be73f6af9b7843775f301664e7cc2b2203c397d


def load_queue():
    with queue_lock:
        if not os.path.exists(QUEUE_FILE):
            return []
        try:
<<<<<<< HEAD
            with open(QUEUE_FILE, "r", encoding="utf-8") as handle:
                return json.load(handle)
        except Exception as exc:
            log(f"Queue file read failed: {exc}")
=======
            with open(QUEUE_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            print("Queue file read failed:", e)
>>>>>>> 2be73f6af9b7843775f301664e7cc2b2203c397d
            return []


def save_queue(queue):
    with queue_lock:
<<<<<<< HEAD
        Path(QUEUE_FILE).parent.mkdir(parents=True, exist_ok=True)
        with open(QUEUE_FILE, "w", encoding="utf-8") as handle:
            json.dump(queue, handle)


def add_event_to_queue(payload):
    queue = load_queue()
    queue.append(payload)
    save_queue(queue)
    log("Event saved locally for retry.")
=======
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
>>>>>>> 2be73f6af9b7843775f301664e7cc2b2203c397d


def try_send_payload(payload):
    try:
<<<<<<< HEAD
        response = requests.post(API_URL, json=payload, timeout=REQUEST_TIMEOUT)
=======
        response = requests.post(API_URL, json=payload, timeout=5)
>>>>>>> 2be73f6af9b7843775f301664e7cc2b2203c397d

        try:
            data = response.json()
        except ValueError:
<<<<<<< HEAD
            log(f"Invalid JSON response from server. Status={response.status_code}")
=======
            print("Invalid JSON response from server")
>>>>>>> 2be73f6af9b7843775f301664e7cc2b2203c397d
            return False

        decision = data.get("decision")
        reason = data.get("reason", "No reason provided")
        student = data.get("student_id")

        if response.status_code == 200:
            if decision == "GRANTED":
<<<<<<< HEAD
                log(f"Access Granted ({student}) - {reason}")
            elif decision == "DENIED":
                log(f"Access Denied - {reason}")
=======
                print(f"Access Granted ({student}) - {reason}")
            elif decision == "DENIED":
                print(f"Access Denied - {reason}")
>>>>>>> 2be73f6af9b7843775f301664e7cc2b2203c397d
            else:
                log(f"Unexpected successful response: {data}")
            return True

<<<<<<< HEAD
        log(f"Server error {response.status_code}: {data}")
        return False

    except requests.exceptions.RequestException as exc:
        log(f"Connection failed: {exc}")
=======
        print("Server Error:", response.status_code)
        return False

    except requests.exceptions.RequestException as e:
        print("Connection Failed:", e)
>>>>>>> 2be73f6af9b7843775f301664e7cc2b2203c397d
        return False


def retry_queued_events():
    queue = load_queue()
<<<<<<< HEAD
    if not queue:
        return

    log(f"Retrying {len(queue)} queued event(s)...")
=======

    if len(queue) == 0:
        return

    print(f"Retrying {len(queue)} queued event(s)...")
>>>>>>> 2be73f6af9b7843775f301664e7cc2b2203c397d
    new_queue = []

    for payload in queue:
        success = try_send_payload(payload)
        if not success:
            new_queue.append(payload)

    save_queue(new_queue)

<<<<<<< HEAD
    if not new_queue:
        log("Queue cleared.")
=======
    if len(new_queue) == 0:
        print("Queue cleared.")
>>>>>>> 2be73f6af9b7843775f301664e7cc2b2203c397d
    else:
        log(f"{len(new_queue)} event(s) still waiting in queue.")


def send_to_backend(uid):
    payload = {
        "card_uid": uid,
        "device_id": DEVICE_ID,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

<<<<<<< HEAD
    retry_queued_events()
    success = try_send_payload(payload)
=======
    # Retry old events first
    retry_queued_events()

    # Send current event
    success = try_send_payload(payload)

>>>>>>> 2be73f6af9b7843775f301664e7cc2b2203c397d
    if not success:
        add_event_to_queue(payload)


def background_retry():
    while True:
        retry_queued_events()
        time.sleep(RETRY_SECONDS)


<<<<<<< HEAD
def extract_keycode_name(keycode):
    if isinstance(keycode, list):
        return keycode[0]
    return keycode


def build_uid_from_device(device):
    current_uid = ""

    for event in device.read_loop():
        if event.type != ecodes.EV_KEY:
            continue

        key_event = categorize(event)
        if key_event.keystate != key_event.key_down:
            continue

        key_name = extract_keycode_name(key_event.keycode)
=======
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
>>>>>>> 2be73f6af9b7843775f301664e7cc2b2203c397d

        if key_name in {"KEY_ENTER", "KEY_KPENTER"}:
            if current_uid:
                yield current_uid
                current_uid = ""
            continue

        if key_name in KEY_MAP:
            current_uid += KEY_MAP[key_name]


def create_device():
    device = InputDevice(DEVICE_PATH)
    log(f"Using device: {device.path} ({device.name})")

    if GRAB_DEVICE:
        try:
            device.grab()
            log("Device grabbed exclusively. Card digits should stop appearing on screen.")
        except OSError as exc:
            log(f"Could not grab device exclusively: {exc}")

    return device


def main():
    if not API_URL:
        raise RuntimeError("RFID_API_URL is not set")

    device = create_device()
    retry_thread = threading.Thread(target=background_retry, daemon=True)
    retry_thread.start()

    log("RFID client started.")
    log("If tapping a card types digits into the screen, the reader is acting like a keyboard HID device. This script supports that mode.")

    for uid in build_uid_from_device(device):
        log(f"Card detected: {uid}")
        send_to_backend(uid)


if __name__ == "__main__":
    try:
        main()
    except FileNotFoundError:
        log(f"RFID device not found at {DEVICE_PATH}")
        raise SystemExit(1)
    except KeyboardInterrupt:
        log("RFID client stopped by user.")
        raise SystemExit(0)
    except Exception as exc:
        log(f"Fatal error: {exc}")
        raise SystemExit(1)
