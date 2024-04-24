document.addEventListener("DOMContentLoaded", function (event) {
    var video = document.querySelector('#video');

    if (navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({ video: true })
            .then(function (stream) {
                video.srcObject = stream;
            })
            .catch(function (err) {
                console.log("Something went wrong!", err);
            });
    }
});
