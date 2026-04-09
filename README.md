# Makerspace Sign-In System

An RFID-based Makerspace sign-in system that allows students to tap their card, automatically log access, and register if they are new.

---

## Contributors

* Kahlan Chapman
* Justin Bourchard
* Tinaishe Tapera
* Essence Raymo
* Gilbert Ncube

---

## Overview

This system is designed for Clarkson University IGNITE Makerspace where:

* Students tap RFID cards to sign in
* New users register on first use
* Access events are logged in a database
* Admins can retrieve logs for reporting

---

## System Workflow

```
RFID Card Tap
      ↓
Frontend captures UID
      ↓
POST /api/access-events
      ↓
Backend decision:
   ├── ACCESS_GRANTED → Show success
   └── NOT_REGISTERED → Show registration form
                             ↓
                      POST /api/register
                             ↓
                      Access granted
```

---

## Architecture

```
[ RFID Scanner ]
        ↓ (keyboard input)
[ Frontend (HTML/JS) ]
        ↓ HTTP
[ Flask Backend API ]
        ↓
[ PostgreSQL Database ]
```

---

## Tech Stack

* Frontend: HTML, CSS, JavaScript
* Backend: Python, Flask
* Database: PostgreSQL
* Hardware: RFID Scanner (HID / evdev)

---

## Project Structure

```
group-project-makerspace/
│
├── backend/
│   ├── app/
│   ├── services/
│   ├── database/
│   ├── config/
│   └── run.py
│
├── frontend/
│   ├── index.html
│   ├── script.js
│   ├── styles.css
```

---

## Setup Guide

### 1. Clone the Repository

```
git clone https://github.com/jeannamatthews-classes/group-project-makerspace.git
cd group-project-makerspace
```

---

### 2. Backend Setup

```
cd backend
python -m venv .venv
```

#### Activate Virtual Environment

Mac/Linux:

```
source .venv/bin/activate
```

---

#### Install Dependencies

```
pip install -r requirements.txt
```

---

#### Configure Environment

Create a `.env` file inside `backend/`:

```
DATABASE_URL=postgresql://postgres:password@localhost:5432/makerspace_db

RFID_DEVICE_PATH=/dev/input/event3
RFID_API_URL=http://127.0.0.1:5000/api/access-events
RFID_DEVICE_ID=makerspace-reader-1
RFID_GRAB_DEVICE=true
```

---

### 3. Database Setup (PostgreSQL)

Start PostgreSQL:

```
psql -U postgres
```

Create database:

```sql
CREATE DATABASE makerspace_db;
\q
```

Run schema:

```
psql -U postgres -d makerspace_db -f database/schema.sql
```

---

### 4. Run Backend

```
python run.py
```

Backend runs at:

```
http://127.0.0.1:5000
```

---

### 5. Run Frontend

Open a new terminal:

```
cd frontend
python3 -m http.server 5500
```

Frontend runs at:

```
http://127.0.0.1:5500
```

---

### 6. Open the Web Application

```
http://127.0.0.1:5500
```

---

## API Endpoints

### Register Student

```
POST /api/register
```

```
{
  "card_uid": "123456",
  "student_id": "1234567",
  "name": "John Doe",
  "email": "john@clarkson.edu"
}
```

---

### Process RFID Tap

```
POST /api/access-events
```

Example response:

```
{
  "decision": "DENIED",
  "code": "NOT_REGISTERED",
  "reason": "Card is not registered",
  "student_id": null
}
```

---

### Admin Access Logs

```
GET /api/admin/access-events
```

Supports filters:

* student_id
* decision
* from
* to

---

## Database Access

### CLI (psql)

```
psql -U postgres -d makerspace_db
```

```
\dt
SELECT * FROM students;
SELECT * FROM audit_logs;
SELECT * FROM access_events ORDER BY timestamp DESC;
```

---

### GUI Tools

* pgAdmin 4

---

## Testing Without RFID

```
curl -X POST http://127.0.0.1:5000/api/access-events \
  -H "Content-Type: application/json" \
  -d '{"card_uid": "123456"}'
```

---

## Design Principle

The system uses machine-readable response codes:

| Code           | Meaning                |
| -------------- | ---------------------- |
| NOT_REGISTERED | Show registration form |
| ACCESS_GRANTED | Allow entry            |
| INVALID_UID    | Reject scan            |
| POLICY_FAILED  | Deny access            |

This avoids fragile string matching and improves reliability.

---

## Troubleshooting

### Registration form not showing

Ensure backend returns:

```
"code": "NOT_REGISTERED"
```

---

### Frontend cannot reach backend

Check URL in `script.js`:

```
http://127.0.0.1:5000
```

If using Raspberry Pi:

```
http://<PI_IP>:5000
```

---

### Scanner not working

* Ensure it outputs characters followed by Enter
* Test in a text editor

---

## Future Improvements

* Google Sheets export integration
* Admin dashboard UI
* Role-based access control
* Training validation policies

---

## Quick Start Checklist

* PostgreSQL running
* Database created
* `.env` configured
* Backend running
* Frontend running
* Scanner connected