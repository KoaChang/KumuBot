// This event listener watches for the "Enter" keydown event in the textarea
document.getElementById("noeauuserInput").addEventListener("keydown", function(event) {
  if (event.key === "Enter") {
    event.preventDefault();
    document.getElementById("oleloForm").dispatchEvent(new Event('submit'));
  }
});

document.getElementById("oleloForm").addEventListener("submit", function(event){
  event.preventDefault();

  // Disable the textarea input
  let userInputElement = document.getElementById("noeauuserInput");
  userInputElement.disabled = true;

  let userInput = userInputElement.value;
  // Get the checkbox's state
  let generateNew = document.getElementById("generateCheckbox").checked;
  let button = document.getElementById("noeausubmitButton");
  let originalButtonText = button.innerText;

  // Update loading state visually
  button.innerHTML = `Loading<span class="loading-dots"></span>`;
  button.disabled = true;

  // Show response area as active
  document.querySelector('.response-area').classList.remove('empty');

  fetch('https://kumubot.pythonanywhere.com/noeau', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ userInput, generateNew }),
  })
  .then(response => response.json())
  .then(data => {
    document.getElementById("noeauserverResponse").innerText = data.message;

    // Re-enable the textarea input and restore the button text
    userInputElement.disabled = false;
    button.innerHTML = originalButtonText;
    button.disabled = false;
  })
  .catch((error) => {
    console.error('Error:', error);

    // Re-enable the textarea input in case of error and restore the button text
    userInputElement.disabled = false;
    button.innerHTML = originalButtonText;
    button.disabled = false;
    document.getElementById("noeauserverResponse").innerText = "An error occurred. Please try again.";
  });
});

// Code to change the description text when checkbox is clicked
document.getElementById("generateCheckbox").addEventListener("change", function(){
  if(this.checked) {
    document.getElementById("checkboxDescription").innerText = "This makes KumuNoʻeau create its own new ʻŌlelo Noʻeau";
  } else {
    document.getElementById("checkboxDescription").innerText = "This makes KumuNoʻeau find existing 'Ōlelo Noʻeau";
  }
});

// Initialize the checkbox description when the page loads
window.onload = function() {
  document.getElementById("checkboxDescription").innerText = "This makes KumuNoʻeau find existing 'Ōlelo Noʻeau";
};

