document.addEventListener("DOMContentLoaded", function() {
    const form = document.getElementById("steg-form");
    const responseDiv = document.getElementById("response");

    form.addEventListener("submit", function(event) {
        event.preventDefault();

        const formData = new FormData(form);
        const actionUrl = event.submitter.getAttribute("formaction");

        // Send the AJAX request
        fetch(actionUrl, {
            method: "POST",
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                responseDiv.textContent = data.message + " File saved at: " + data.path;
                responseDiv.style.color = "green";
            } else {
                responseDiv.textContent = data.message;
                responseDiv.style.color = "red";
            }
        })
        .catch(error => {
            responseDiv.textContent = "An error occurred: " + error.message;
            responseDiv.style.color = "red";
        });
    });
});
