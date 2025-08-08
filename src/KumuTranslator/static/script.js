document.addEventListener('DOMContentLoaded', function() {
    var inputText = document.getElementById('transinputText');
    var outputText = document.getElementById('transoutputText');
    var switchButton = document.getElementById('transswitch');
    var translateButton = document.getElementById('translate');
    
    // Handle Enter key press in input
    inputText.addEventListener('keyup', function(event) {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            translateButton.click();
        }
    });
    
    // Handle language switch
    switchButton.addEventListener('click', function() {
        // Swap both the placeholder text and values (if any)
        let tempInputPlaceholder = inputText.placeholder;
        let tempOutputPlaceholder = outputText.placeholder;
        let tempInputValue = inputText.value;
        let tempOutputValue = outputText.value;
        
        // Clear and swap placeholders
        if (inputText.placeholder === "Enter English text here...") {
            inputText.placeholder = "Enter Hawaiian text here...";
            outputText.placeholder = "Translated English text will appear here...";
        } else {
            inputText.placeholder = "Enter English text here...";
            outputText.placeholder = "Translated Hawaiian text will appear here...";
        }
        
        // If there was a translation in progress, swap the values too
        if (tempOutputValue) {
            inputText.value = tempOutputValue;
            outputText.value = "";
        } else {
            // Otherwise just clear both
            inputText.value = "";
            outputText.value = "";
        }
    });
    
    // Handle translation
    translateButton.addEventListener('click', function() {
        // Validate input
        if (!inputText.value.trim()) {
            outputText.value = "Please enter text to translate.";
            return;
        }
        
        // Disable button and show loading state
        translateButton.disabled = true;
        translateButton.innerHTML = `Loading<span class="loading-dots"></span>`;
        
        fetch("https://kumubot.pythonanywhere.com/translate", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                text: inputText.value,
                language: inputText.placeholder
            })
        })
        .then(response => response.json())
        .then(data => {
            // Reset button state
            translateButton.disabled = false;
            translateButton.textContent = 'Translate';
            
            // Display translated text
            outputText.value = data.translated_text;
        })
        .catch(error => {
            console.error('Error:', error);
            translateButton.disabled = false;
            translateButton.textContent = 'Translate';
            outputText.value = "An error occurred during translation. Please try again.";
        });
    });
});
