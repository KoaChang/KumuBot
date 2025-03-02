
document.getElementById('transinputText').addEventListener('keyup', function(event) {
if (event.keyCode === 13) {
    event.preventDefault();
    document.getElementById('translate').click();
}
});

document.getElementById('transswitch').addEventListener('click', function() {
var inputText = document.getElementById('transinputText');
var outputText = document.getElementById('transoutputText');

if (inputText.placeholder === "Enter English text here...") {
    inputText.placeholder = "Enter Hawaiian text here...";
    outputText.placeholder = "Translated English text will appear here...";
} else {
    inputText.placeholder = "Enter English text here...";
    outputText.placeholder = "Translated Hawaiian text will appear here...";
}

inputText.value = "";
outputText.value = "";
});

document.getElementById('translate').addEventListener('click', function() {
var inputText = document.getElementById('transinputText');
var outputText = document.getElementById('transoutputText');
var translateButton = document.getElementById('translate');

var loadingText = 'Loading';
var counter = 0;

// Change the button text to "Loading..."
var loadingInterval = setInterval(function() {
    translateButton.textContent = loadingText + '.'.repeat(counter);
    counter = (counter + 1) % 4;
}, 500);

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
    // Stop the loading animation and reset the button text
    clearInterval(loadingInterval);
    translateButton.textContent = 'Translate';

    outputText.style.color = 'black';
    outputText.value = data.translated_text;
});
});

