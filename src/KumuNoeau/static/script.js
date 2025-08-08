document.getElementById("noeauuserInput").addEventListener("keydown", function(event) {
  if (event.key === "Enter") {
      event.preventDefault();
      document.getElementById("oleloForm").dispatchEvent(new Event('submit'));
  }
});

document.getElementById("oleloForm").addEventListener("submit", function(event){
  event.preventDefault();
  
  let userInputElement = document.getElementById("noeauuserInput");
  userInputElement.disabled = true;

  let userInput = userInputElement.value;
  let generateNew = document.getElementById("generateCheckbox").checked;
  let button = document.getElementById("noeausubmitButton");
  let originalButtonText = button.innerText;

  button.innerHTML = `Loading<span class="loading-dots"></span>`;
  button.disabled = true;

  fetch('https://kumubot.pythonanywhere.com/noeau', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ userInput, generateNew }),
  })
  .then(response => response.json())
  .then(data => {
      document.getElementById("noeauserverResponse").innerText = data.message;
      userInputElement.disabled = false;
      button.innerHTML = originalButtonText;
      button.disabled = false;
  })
  .catch(() => {
      document.getElementById("noeauserverResponse").innerText = "An error occurred.";
      userInputElement.disabled = false;
      button.innerHTML = originalButtonText;
      button.disabled = false;
  });
});
