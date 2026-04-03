# Backend - Makerspace Sign-In System

## What this backend does

The backend provides:
- student registration
- RFID access decision processing
- storage of access events in PostgreSQL
- centralized audit logging
- admin reporting endpoint

## Tech Stack

- Python 3.10+
- Flask
- Flask-SQLAlchemy
- PostgreSQL
- requests
- evdev

## Setup

### 1. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

Create a `.env` file in `backend/` using `.env.example`.

### 4. Create the database schema

```bash
psql -U postgres -d makerspace_db -f database/schema.sql
```

Or connect using your own database user and database name.

### 5. Start the backend

```bash
python run.py
```

The default development URL is:

```text
http://127.0.0.1:5000
```

## Important Files

- `app/__init__.py` - Flask application factory
- `app/routes.py` - API routes
- `app/models.py` - SQLAlchemy models
- `services/registration_service.py` - student registration logic
- `services/checkin_service.py` - access decision and DB logging
- `services/audit_service.py` - centralized audit logging
- `services/rfid_service.py` - RFID client for keyboard-style readers
- `database/schema.sql` - PostgreSQL schema
- `config/config.py` - environment-based configuration

## API Endpoints

### `POST /api/register`
Registers a student and stores a hashed RFID UID.

### `POST /api/access-events`
Processes an RFID tap and writes an access event.

### `GET /api/admin/access-events`
Returns access events with optional filters and pagination.

## RFID Reader Notes

If the card UID appears on screen when tapped, the reader is behaving like a keyboard HID scanner. That is fine.

You should:
1. Identify the correct input event device.
2. Put that device path in `RFID_DEVICE_PATH`.
3. Set `RFID_GRAB_DEVICE=true` if you want the script to capture the device exclusively and stop the digits from appearing in the terminal.

Example:

```env
RFID_DEVICE_PATH=/dev/input/event3
RFID_GRAB_DEVICE=true
RFID_API_URL=http://127.0.0.1:5000/api/access-events
RFID_DEVICE_ID=makerspace-reader-1
```
