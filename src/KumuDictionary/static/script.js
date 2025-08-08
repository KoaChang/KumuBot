document.addEventListener('DOMContentLoaded', function() {
    var submitButton = document.getElementById("dicsubmitButton");
    var searchInput = document.getElementById("dicsearchInput");
    var responseContainer = document.getElementById("dicresponse");
    var responseArea = document.querySelector(".response-area");
    
    function startLoadingAnimation() {
        submitButton.innerHTML = `Loading<span class="loading-dots"></span>`;
        submitButton.disabled = true;
    }
    
    function stopLoadingAnimation() {
        submitButton.innerHTML = 'Submit';
        submitButton.disabled = false;
    }
    
    function processInput() {
        var userInput = searchInput.value;
        if (!userInput.trim()) {
            return; // Don't process empty inputs
        }
        
        searchInput.disabled = true;
        startLoadingAnimation();
        
        // Remove empty class to show response area is active
        responseArea.classList.remove('empty');
        
        fetch('https://kumubot.pythonanywhere.com/dictionary', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                search: userInput
            }),
        })
        .then(response => response.json())
        .then(data => {
            responseContainer.textContent = data.result;
            searchInput.disabled = false;
            stopLoadingAnimation();
        })
        .catch((error) => {
            console.error('Error:', error);
            responseContainer.textContent = 'An error occurred. Please try again.';
            searchInput.disabled = false;
            stopLoadingAnimation();
        });
    }
    
    submitButton.addEventListener('click', processInput);
    
    searchInput.addEventListener('keyup', function(e) {
        if (e.key === 'Enter') {
            processInput();
        }
    });
});
