const nameInput = document.getElementById("name");
const emailInput = document.getElementById("email");
const studentIdInput = document.getElementById("studentid");
const registrationForm = document.getElementById("registrationForm");
const registrationSection = document.getElementById("registrationSection");
const statusMessage = document.getElementById("statusMessage");
const statusPanel = document.getElementById("statusPanel");
const cardUidDisplay = document.getElementById("cardUidDisplay");
const submitButton = document.getElementById("submitButton");

const ACCESS_EVENTS_URL = "http://127.0.0.1:5000/api/access-events";
const REGISTER_URL = "http://127.0.0.1:5000/api/register";
const DEVICE_ID = "frontend-scanner";

let pendingCardUid = null;
let scanBuffer = "";
let scanTimeout = null;

function setStatus(message, type = "info") {
    statusMessage.textContent = message;
    statusPanel.className = `status-panel status-${type}`;
}

function showRegistrationForm(uid) {
    pendingCardUid = uid;
    cardUidDisplay.textContent = uid;
    registrationSection.classList.remove("hidden");
}

function hideRegistrationForm() {
    registrationSection.classList.add("hidden");
    cardUidDisplay.textContent = "None";
    registrationForm.reset();
    pendingCardUid = null;
    resetErrors();
}

function resetErrors() {
    resetText("nameError");
    resetText("emailError");
    resetText("studentidError");
}

function resetText(fieldName) {
    document.getElementById(fieldName).textContent = "";
}

function isLikelyScannerKey(key) {
    return /^[0-9A-Fa-f]$/.test(key) || key === "Enter";
}

async function processCardScan(uid) {
    setStatus(`Card detected: ${uid}. Checking registration...`, "info");

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

        const data = await response.json();

        if (response.ok && data.decision === "GRANTED") {
            hideRegistrationForm();
            setStatus(`Access granted for student ${data.student_id || ""}.`, "success");
            return;
        }

        const reason = (data.reason || "").toLowerCase();

        if (data.decision === "DENIED" || response.status === 404) {
            if (
                reason.includes("not registered") ||
                reason.includes("unknown") ||
                reason.includes("not found") ||
                reason.includes("no student")
            ) {
                showRegistrationForm(uid);
                setStatus("Card not registered. Please complete the registration form.", "error");
                return;
            }

            setStatus(`Access denied. ${data.reason || "Unknown reason."}`, "error");
            return;
        }

        setStatus("Unexpected server response during card check.", "error");
    } catch (error) {
        setStatus("Could not connect to backend. Please try again.", "error");
    }
}

document.addEventListener("keydown", async (event) => {
    if (!isLikelyScannerKey(event.key)) {
        return;
    }

    if (scanTimeout) {
        clearTimeout(scanTimeout);
    }

    if (event.key === "Enter") {
        const uid = scanBuffer.trim();
        scanBuffer = "";

        if (!uid) {
            return;
        }

        await processCardScan(uid);
        return;
    }

    scanBuffer += event.key.toUpperCase();

    scanTimeout = setTimeout(() => {
        scanBuffer = "";
    }, 500);
});

registrationForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    resetErrors();

    let errors = 0;

    const nameValue = nameInput.value.trim();
    const emailValue = emailInput.value.trim().toLowerCase();
    const studentIdValue = studentIdInput.value.trim();

    if (!nameValue) {
        document.getElementById("nameError").textContent = "Enter your full name";
        errors++;
    }

    if (!emailValue.endsWith("@clarkson.edu")) {
        document.getElementById("emailError").textContent = "Enter a valid Clarkson email";
        errors++;
    }

    if (!/^\d{7}$/.test(studentIdValue)) {
        document.getElementById("studentidError").textContent = "Enter a valid 7-digit student ID";
        errors++;
    }

    if (!pendingCardUid) {
        setStatus("No scanned card was found. Please tap your card first.", "error");
        return;
    }

    if (errors > 0) {
        return;
    }

    submitButton.disabled = true;
    submitButton.textContent = "Submitting...";

    try {
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

        const registerData = await registerResponse.json();

        if (!registerResponse.ok) {
            setStatus(registerData.error || "Registration failed.", "error");
            submitButton.disabled = false;
            submitButton.textContent = "Submit Registration";
            return;
        }

        setStatus("Registration successful. Granting access...", "success");

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

        const accessData = await accessResponse.json();

        if (accessResponse.ok && accessData.decision === "GRANTED") {
            hideRegistrationForm();
            setStatus(`Registration successful. Access granted for student ${accessData.student_id || ""}.`, "success");
        } else {
            setStatus(
                `Registration succeeded, but automatic access check failed. ${accessData.reason || ""}`,
                "error"
            );
        }
    } catch (error) {
        setStatus("Could not connect to backend. Please try again later.", "error");
    } finally {
        submitButton.disabled = false;
        submitButton.textContent = "Submit Registration";
    }
});