document.addEventListener('DOMContentLoaded', function() {
    var inputText = document.getElementById('transinputText');
    var outputText = document.getElementById('transoutputText');
    var switchButton = document.getElementById('transswitch');
    var translateButton = document.getElementById('translate');

    inputText.addEventListener('keyup', function(event) {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            translateButton.click();
        }
    });

    switchButton.addEventListener('click', function() {
        let temp = inputText.placeholder;
        inputText.placeholder = outputText.placeholder;
        outputText.placeholder = temp;
        [inputText.value, outputText.value] = [outputText.value, ""];
    });

    translateButton.addEventListener('click', function() {
        if (!inputText.value.trim()) {
            outputText.value = "Please enter text to translate.";
            return;
        }

        translateButton.disabled = true;
        translateButton.innerHTML = `Loading<span class="loading-dots"></span>`;

        fetch("https://kumubot.pythonanywhere.com/translate", {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: inputText.value, language: inputText.placeholder })
        })
        .then(response => response.json())
        .then(data => {
            translateButton.disabled = false;
            translateButton.textContent = 'Translate';
            outputText.value = data.translated_text;
        })
        .catch(() => {
            translateButton.disabled = false;
            outputText.value = "Translation error. Try again.";
        });
    });
});
