function chooseFile() {
    document.getElementById('fileInput').click();
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// Handle file selection
document.getElementById('fileInput').addEventListener('change', function () {
    var selectedFile = this.files[0];
    document.getElementById('submit').click();
});


// Add event listener for keyup on the search input
$('#searchInput').on('keyup', function () {
    // Get the search query
    var searchQuery = $(this).val().toLowerCase();

    // Filter and show/hide rows based on the search query
    $('#fileTableBody tr').each(function () {
        var fileName = $(this).find('td:first-child a').text().toLowerCase();
        if (fileName.includes(searchQuery)) {
            $(this).show();
        } else {
            $(this).hide();
        }
    });
});

// Optional: Add event listener for click on the search button
$('#searchButton').on('click', function () {
    // Trigger keyup event to perform filtering
    $('#searchInput').trigger('keyup');
});


// progress bar loading animation
document.addEventListener('DOMContentLoaded', function () {
    var progressBar = document.querySelectorAll('.fill-up-animation');
    progressBar.forEach(function (progressBar) {
        progressBar.style.width = progressBar.getAttribute('aria-valuenow') + '%';
    });
});

// file download
// Use getElementsByClassName instead of getElementById
var downloadLinks = document.getElementsByClassName('download-link');

// Iterate through all elements with the specified class
for (var i = 0; i < downloadLinks.length; i++) {
    downloadLinks[i].addEventListener('click', function () {
        var fileId = this.getAttribute('file_id');
        var fileName = this.getAttribute('file_name');

        var xhr = new XMLHttpRequest();
        xhr.open('GET', '/download/' + fileId, true);
        xhr.responseType = 'blob';

        xhr.onload = function () {
            var blob = new Blob([this.response], { type: 'application/octet-stream' });

            var url = URL.createObjectURL(blob);

            var a = document.createElement('a');
            a.href = url;
            a.download = fileName; // Set the desired filename

            document.body.appendChild(a);
            a.click();

            // Remove the anchor element and revoke the URL to free up resources
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        };

        xhr.send();
    });
}

// file delete
// Use getElementsByClassName instead of getElementById
var deleteFiles = document.getElementsByClassName('delete-link');

// Iterate through all elements with the specified class
for (var i = 0; i < deleteFiles.length; i++) {
    deleteFiles[i].addEventListener('click', function () {
        var fileId = this.getAttribute('file_id');

        var xhr = new XMLHttpRequest();
        xhr.open('GET', '/delete/' + fileId, true);
        xhr.send();
        sleep(500).then(() => { location.reload(); });
    });
}