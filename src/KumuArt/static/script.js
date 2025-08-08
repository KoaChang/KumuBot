var loadingInterval;

function startLoadingAnimation() {
var loadingTexts = ["Loading", "Loading.", "Loading..", "Loading..."];
var i = 0;
loadingInterval = setInterval(() => {
    document.getElementById('artsubmit-btn').innerText = loadingTexts[i];
    i = (i + 1) % loadingTexts.length; // This makes the animation loop
}, 500); // Change the number to make the animation faster or slower
}

function stopLoadingAnimation() {
clearInterval(loadingInterval);
document.getElementById('artsubmit-btn').innerText = 'Submit';
}

function submitDescription() {
var description = document.getElementById('artdescription').value;
var descriptionBox = document.getElementById('artdescription');
var imageContainer = document.getElementById('artimage-container');
var imageElement = document.getElementById('artimage');
var outputContainer = document.getElementById('artoutput');
var factContainer = document.getElementById('artfact');

var imagePlaceholder = document.getElementById('image-placeholder');
var factPlaceholder = document.getElementById('fact-placeholder');

if(description) {
    descriptionBox.disabled = true;
    startLoadingAnimation(); // Start the loading animation
    factContainer.innerText = "";
    imageElement.style.display = "none";  // Hide the image
    factContainer.style.display = "none";  // Hide the fun fact
    imagePlaceholder.style.display = "block"; // Show the placeholders
    factPlaceholder.style.display = "block";

    fetch('https://kumubot.pythonanywhere.com/art', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({description: description})
    })
    .then(response => response.json())
    .then(data => {
        var imgURL = data.image_url;
        imageElement.src = imgURL;
        descriptionBox.disabled = false;
        outputContainer.innerText = "";
        
        var funFact = data.fun_fact;
        factContainer.innerText = funFact;

        imageElement.style.display = "block";  // Show the image and the fun fact
        factContainer.style.display = "block";
        imagePlaceholder.style.display = "none"; // Hide the placeholders
        factPlaceholder.style.display = "none";
        stopLoadingAnimation(); // Stop the loading animation
    })
    .catch(error => {
        console.error('Error:', error);
        outputContainer.innerText = "Error occurred while generating image.";
        descriptionBox.disabled = false;
        stopLoadingAnimation(); // Stop the loading animation
    });
} else {
    alert('Please enter a description!');
}
}

// attach click event to the submit button
document.getElementById('artsubmit-btn').addEventListener('click', submitDescription);

// Add event listener for return key in textarea
document.getElementById('artdescription').addEventListener('keyup', function(event) {
if (event.keyCode === 13) {
    event.preventDefault();
    submitDescription();
}
});