document.addEventListener('DOMContentLoaded', function() {
    var loadingInterval;
    var submitButton = document.getElementById('artsubmit-btn');
    var descriptionInput = document.getElementById('artdescription');
    var imageContainer = document.getElementById('artimage-container');
    var imageElement = document.getElementById('artimage');
    var outputContainer = document.getElementById('artoutput');
    var factContainer = document.getElementById('artfact');
    var imagePlaceholder = document.getElementById('image-placeholder');
    var factPlaceholder = document.getElementById('fact-placeholder');

    function startLoadingAnimation() {
        submitButton.innerHTML = `Loading<span class="loading-dots"></span>`;
        submitButton.disabled = true;
    }

    function stopLoadingAnimation() {
        submitButton.innerHTML = 'Submit';
        submitButton.disabled = false;
    }

    function submitDescription() {
        var description = descriptionInput.value.trim();
        
        if(!description) {
            outputContainer.innerText = "Please enter a description!";
            return;
        }
        
        // Clear previous error messages
        outputContainer.innerText = "";
        
        // Disable input during processing
        descriptionInput.disabled = true;
        
        // Start loading animation
        startLoadingAnimation();
        
        // Hide previous results and show placeholders
        factContainer.innerText = "";
        imageElement.style.display = "none";
        factContainer.style.display = "none";
        imagePlaceholder.style.display = "block";
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
            
            var funFact = data.fun_fact;
            factContainer.innerText = funFact;

            // Show results and hide placeholders
            imageElement.style.display = "block";
            factContainer.style.display = "block";
            imagePlaceholder.style.display = "none";
            factPlaceholder.style.display = "none";
            
            // Re-enable input
            descriptionInput.disabled = false;
            stopLoadingAnimation();
        })
        .catch(error => {
            console.error('Error:', error);
            outputContainer.innerText = "Error occurred while generating image.";
            descriptionInput.disabled = false;
            stopLoadingAnimation();
        });
    }

    // Attach click event to the submit button
    submitButton.addEventListener('click', submitDescription);

    // Add event listener for return key in textarea
    descriptionInput.addEventListener('keydown', function(event) {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault(); // This prevents the new line from being added
            submitDescription();
        }
    });
});
