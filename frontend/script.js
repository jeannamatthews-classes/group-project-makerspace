const name = document.getElementById('name');
const email = document.getElementById('email');
const studentid = document.getElementById('studentid');
const registrationform = document.getElementById('registrationform');

registrationform.addEventListener('submit', (e) => {
    // e.preventDefault();
    document.getElementById("message").innerHTML = "The form has been submitted (but not yet uploaded).";
})

