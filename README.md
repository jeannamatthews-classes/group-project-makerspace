# Makerspace Sign-In Frontend

This frontend provides the user interface for the RFID-based Makerspace sign-in system.  
It works together with the Flask backend and an RFID scanner that behaves like a keyboard (HID device).

---

## Overview

The system follows a **scanner-first workflow**:

1. Student taps their RFID card
2. Frontend captures the card UID from keyboard input
3. Frontend sends UID to backend (`/api/access-events`)
4. Backend responds:
   - **GRANTED** → Access granted message displayed
   - **DENIED (not registered)** → Registration form appears
5. Student enters:
   - Name
   - Email
   - Student ID
6. Frontend sends registration data to `/api/register`
7. After successful registration:
   - Access is automatically granted

---

## Files

| File | Description |
|------|-------------|
| `index.html` | Main UI page |
| `script.js` | Handles scanner input, API calls, and form logic |
| `styles.css` | UI styling |
| `Montserrat-VariableFont_wght.ttf` | Custom font |

---

### How to Run

### 1. Start the backend

From the `backend/` directory:

```bash
python run.py