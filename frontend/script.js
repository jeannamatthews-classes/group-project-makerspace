const nameInput = document.getElementById("name");
const emailInput = document.getElementById("email");
const studentIdInput = document.getElementById("studentid");
const registrationForm = document.getElementById("registrationForm");
const registrationSection = document.getElementById("registrationSection");
const statusMessage = document.getElementById("statusMessage");
const statusPanel = document.getElementById("statusPanel");
const cardUidDisplay = document.getElementById("cardUidDisplay");
const submitButton = document.getElementById("submitButton");

// Backend endpoints
const ACCESS_EVENTS_URL = "http://127.0.0.1:5000/api/access-events";
const REGISTER_URL = "http://127.0.0.1:5000/api/register";

// Identifier for where the scan came from
const DEVICE_ID = "frontend-scanner";

// Stores the last scanned UID while registration is pending
let pendingCardUid = null;

// Buffer for scanner keyboard input
let scanBuffer = "";
let scanTimeout = null;

/**
 * Update the status message shown to the user.
 * type can be: info, success, error
 */
function setStatus(message, type = "info") {
    statusMessage.textContent = message;
    statusPanel.className = `status-panel status-${type}`;
}

/**
 * Show the registration section and remember the UID being registered.
 */
function showRegistrationForm(uid) {
    pendingCardUid = uid;
    cardUidDisplay.textContent = uid;
    registrationSection.classList.remove("hidden");
}

/**
 * Hide the registration section and clear form/UI state.
 */
function hideRegistrationForm() {
    registrationSection.classList.add("hidden");
    cardUidDisplay.textContent = "None";
    registrationForm.reset();
    pendingCardUid = null;
    resetErrors();
}

/**
 * Clear all validation error messages.
 */
function resetErrors() {
    resetText("nameError");
    resetText("emailError");
    resetText("studentidError");
}

/**
 * Clear one validation message by element id.
 */
function resetText(fieldName) {
    document.getElementById(fieldName).textContent = "";
}

/**
 * Only accept keys that are likely to come from the scanner.
 * Most scanners type characters quickly and then press Enter.
 */
function isLikelyScannerKey(key) {
    return /^[0-9A-Fa-f]$/.test(key) || key === "Enter";
}

/**
 * Process one completed card scan.
 *
 * This version is "bulletproof" because it does NOT rely on matching
 * human-readable reason text from the backend.
 *
 * Instead it uses the explicit machine-readable backend code:
 * - NOT_REGISTERED
 * - ACCESS_GRANTED
 * - INVALID_UID
 * - POLICY_FAILED
 */
async function processCardScan(uid) {
    setStatus(`Card detected: ${uid}. Checking registration...`, "info");
    console.log("Processing scanned card:", uid);

    try {
        const response = await fetch(ACCESS_EVENTS_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                card_uid: uid,
                device_id: DEVICE_ID
            })
        });

        let data = {};

        // Parse backend JSON safely
        try {
            data = await response.json();
        } catch (jsonError) {
            console.error("Failed to parse backend response JSON:", jsonError);
            setStatus("Backend returned an invalid response.", "error");
            return;
        }

        console.log("Access check HTTP status:", response.status);
        console.log("Access check response:", data);

        // Case 1: backend explicitly says the card is not registered
        if (data.code === "NOT_REGISTERED") {
            console.log("Card not registered. Showing registration form.");
            showRegistrationForm(uid);
            setStatus("Card not registered. Please complete the registration form.", "error");
            return;
        }

        // Case 2: backend explicitly grants access
        if (response.ok && data.decision === "GRANTED" && data.code === "ACCESS_GRANTED") {
            hideRegistrationForm();
            setStatus(`Access granted for student ${data.student_id || ""}.`, "success");
            return;
        }

        // Case 3: backend explicitly says UID format is invalid
        if (data.code === "INVALID_UID") {
            hideRegistrationForm();
            setStatus("Invalid card UID. Please try again.", "error");
            return;
        }

        // Case 4: any other DENIED response means the card/student was recognized
        // but access is denied for another rule or policy reason
        if (data.decision === "DENIED") {
            hideRegistrationForm();
            setStatus(`Access denied. ${data.reason || "Unknown reason."}`, "error");
            return;
        }

        // Fallback if backend returns something unexpected
        setStatus("Unexpected server response during card check.", "error");
    } catch (error) {
        console.error("Could not connect to backend:", error);
        setStatus("Could not connect to backend. Please try again.", "error");
    }
}

/**
 * Listen for scanner keyboard input.
 * Scanner usually sends the UID followed by Enter.
 */
document.addEventListener("keydown", async (event) => {
    console.log("Key detected:", event.key);

    // Ignore unrelated keyboard input
    if (!isLikelyScannerKey(event.key)) {
        return;
    }

    // Reset inactivity timer every time a scanner key arrives
    if (scanTimeout) {
        clearTimeout(scanTimeout);
    }

    // Enter means scanner finished sending the UID
    if (event.key === "Enter") {
        const uid = scanBuffer.trim();
        scanBuffer = "";

        if (!uid) {
            return;
        }

        console.log("Completed card scan:", uid);
        await processCardScan(uid);
        return;
    }

    // Add scanner character to the current buffer
    scanBuffer += event.key.toUpperCase();

    // If too much time passes, clear incomplete scanner input
    scanTimeout = setTimeout(() => {
        scanBuffer = "";
    }, 500);
});

/**
 * Handle registration form submission.
 */
registrationForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    resetErrors();

    let errors = 0;

    const nameValue = nameInput.value.trim();
    const emailValue = emailInput.value.trim().toLowerCase();
    const studentIdValue = studentIdInput.value.trim();

    // Validate full name
    if (!nameValue) {
        document.getElementById("nameError").textContent = "Enter your full name";
        errors++;
    }

    // Validate Clarkson email
    if (!emailValue.endsWith("@clarkson.edu")) {
        document.getElementById("emailError").textContent = "Enter a valid Clarkson email";
        errors++;
    }

    // Validate 7-digit student ID
    if (!/^\d{7}$/.test(studentIdValue)) {
        document.getElementById("studentidError").textContent = "Enter a valid 7-digit student ID";
        errors++;
    }

    // Make sure a card was scanned before registering
    if (!pendingCardUid) {
        setStatus("No scanned card was found. Please tap your card first.", "error");
        return;
    }

    // If there are errors, do not submit and scroll to the form
    if (errors > 0) {
        registrationSection.scrollIntoView({ behavior: 'smooth', block: 'start' })
        return;
    }

    submitButton.disabled = true;
    submitButton.textContent = "Submitting...";

    try {
        // Step 1: register the student/card
        const registerResponse = await fetch(REGISTER_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                card_uid: pendingCardUid,
                student_id: studentIdValue,
                name: nameValue,
                email: emailValue
            })
        });

        let registerData = {};

        try {
            registerData = await registerResponse.json();
        } catch (jsonError) {
            console.error("Failed to parse register response JSON:", jsonError);
            setStatus("Registration response was invalid.", "error");
            return;
        }

        if (!registerResponse.ok) {
            setStatus(registerData.error || "Registration failed.", "error");
            return;
        }

        setStatus("Registration successful. Granting access...", "success");

        // Step 2: immediately re-check access after successful registration
        const accessResponse = await fetch(ACCESS_EVENTS_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                card_uid: pendingCardUid,
                device_id: DEVICE_ID
            })
        });

        let accessData = {};

        try {
            accessData = await accessResponse.json();
        } catch (jsonError) {
            console.error("Failed to parse access response JSON:", jsonError);
            setStatus("Registration succeeded, but access response was invalid.", "error");
            return;
        }

        // If backend confirms access was granted, close the form
        if (
            accessResponse.ok &&
            accessData.decision === "GRANTED" &&
            accessData.code === "ACCESS_GRANTED"
        ) {
            hideRegistrationForm();
            setStatus(
                `Registration successful. Access granted for student ${accessData.student_id || ""}.`,
                "success"
            );
        } else {
            setStatus(
                `Registration succeeded, but automatic access check failed. ${accessData.reason || ""}`,
                "error"
            );
        }
    } catch (error) {
        console.error("Registration flow failed:", error);
        setStatus("Could not connect to backend. Please try again later.", "error");
    } finally {
        submitButton.disabled = false;
        submitButton.textContent = "Submit Registration";
    }
});