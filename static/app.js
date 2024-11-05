document.addEventListener("DOMContentLoaded", function() {
    const form = document.getElementById("steg-form");
    const responseDiv = document.getElementById("response");
    const downloadButton = document.getElementById("download-stego");
    const extractButton = document.getElementById("extract-data");
    const extractedDataDiv = document.getElementById("extracted-data");
    let stegoFilePath = "";

    form.addEventListener("submit", function(event) {
        event.preventDefault();

        const formData = new FormData(form);
        const actionUrl = event.submitter.getAttribute("formaction");

        // Send the AJAX request
        fetch(actionUrl, {
            method: "POST",
            body: formData
        })
        .then(response => {
            const contentType = response.headers.get("content-type");
            if (!contentType || !contentType.includes("application/json")) {
                throw new Error("Received non-JSON response");
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                responseDiv.textContent = data.message;
                responseDiv.style.color = "green";
                stegoFilePath = data.path; // Save the path for downloading
                downloadButton.style.display = "inline"; // Show download button
                extractButton.style.display = "inline"; // Show extract button
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

    downloadButton.addEventListener("click", function() {
        window.location.href = '/download/' + stegoFilePath; // Change to the correct URL for downloading
    });

    extractButton.addEventListener("click", function() {
        const formData = new FormData();
        const audioInput = document.getElementById("audio_file");
        const keyInput = document.getElementById("key");

        formData.append('audio_file', audioInput.files[0]);
        formData.append('key', keyInput.value);

        fetch('/extract', {
            method: "POST",
            body: formData
        })
        .then(response => {
            const contentType = response.headers.get("content-type");
            if (!contentType || !contentType.includes("application/json")) {
                throw new Error("Received non-JSON response");
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                extractedDataDiv.textContent = "Extracted Data: " + atob(data.data);
                extractedDataDiv.style.color = "green";
                extractedDataDiv.style.display = "block"; // Show the extracted data
            } else {
                extractedDataDiv.textContent = data.message;
                extractedDataDiv.style.color = "red";
                extractedDataDiv.style.display = "block"; // Show the error
            }
        })
        .catch(error => {
            extractedDataDiv.textContent = "An error occurred: " + error.message;
            extractedDataDiv.style.color = "red";
            extractedDataDiv.style.display = "block"; // Show the error
        });
    });
});
