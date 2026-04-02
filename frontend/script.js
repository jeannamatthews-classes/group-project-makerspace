const name = document.getElementById('name');
const email = document.getElementById('email');
const studentid = document.getElementById('studentid');
const registrationForm = document.getElementById('registrationForm');

// controls the submit button
registrationForm.addEventListener('submit', (e) => {

    // reset the errors
    resetText("nameError");
    resetText("emailError");
    resetText("studentidError");

    errors = 0;

    tempEmail = email.value;
    if (tempEmail.substring(tempEmail.length - 13, tempEmail.length) != "@clarkson.edu") {
        document.getElementById("emailError").textContent = "Enter a valid Clarkson email";
        errors++;
    }

    // check that the student id has the correct length
    if (studentid.value.length != 7) {
        document.getElementById("studentidError").textContent = "Enter a valid student ID";
        errors++;
    }



    //check for successful response. If inputs are valid AND response is successful:
    // TODO: add succesful response condition
    if (errors === 0) {
        alert("The form has been submitted (but not yet uploaded).");

        // reset the form
        document.getElementById("registrationForm").reset();

    }

    // check for successful response. If response is unsuccessful:
    // TODO: add unsuccessful response condition
    if (false) {
        alert("The form was not uploaded. Please try again later.");
    }

})

// function to reset the errors
function resetText(fieldName) {
    document.getElementById(fieldName).textContent = "";
}