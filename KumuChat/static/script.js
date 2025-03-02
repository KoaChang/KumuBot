
document.addEventListener("DOMContentLoaded", function() {
var submitBtn = document.getElementById("chatsubmit-btn");
var userInput = document.getElementById("chatuser-input");
var messageContainer = document.getElementById("chatmessage-container");
var enableEnglishOutput = document.getElementById("chatenable-english-output");

var history = [];

submitBtn.addEventListener("click", sendMessage);
userInput.addEventListener("keydown", function(event) {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    sendMessage();
  }
});
userInput.addEventListener("input", adjustInputHeight);

async function sendMessage() {
  var messageText = userInput.value;
  var isEnglishEnabled = enableEnglishOutput.checked;

  console.log(isEnglishEnabled)

  if (messageText.trim() !== "") {
    addMessage("user", messageText, true);
    userInput.value = "";
    userInput.disabled = true;
    submitBtn.disabled = true;

    // Create a loading animation
    let i = 0;
    let loadingInterval = setInterval(() => {
      submitBtn.textContent = 'Loading' + '.'.repeat(i);
      i = (i + 1) % 4;
    }, 500);

    var lastMessages = history.slice(Math.max(history.length - 9, 0));

    console.log(lastMessages)

    const response = await fetch('https://kumubot.pythonanywhere.com/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message: messageText, history: lastMessages, english_output: isEnglishEnabled }),
    });

    const data = await response.json();
    const systemMessage = data.message;

    addMessage("assistant", systemMessage, false);

    // Reset the input and button
    userInput.disabled = false;
    submitBtn.disabled = false;
    submitBtn.textContent = 'Submit';

    // Stop the loading animation
    clearInterval(loadingInterval);

    userInput.scrollTop = userInput.scrollHeight;
    messageContainer.scrollTop = messageContainer.scrollHeight;
  }
}

function addMessage(role, content, userTriggered) {
  var messageElement = document.createElement("div");
  messageElement.classList.add("chatmessage");
  messageElement.classList.add(role === "user" ? "user-message" : "assistant-message");
  messageElement.textContent = content;

  if(userTriggered){
    let deleteIcon = document.createElement("span");
    deleteIcon.classList.add("delete-icon");
    deleteIcon.textContent = "❌"; /* Change the icon to a red X */
    deleteIcon.onclick = function() {
      deleteMessagePair(messageElement);
    }
    messageElement.appendChild(deleteIcon);
  }

  messageContainer.appendChild(messageElement);

  history.push({ role: role, content: content });
}

function deleteMessagePair(messageElement) {
  if (messageElement.classList.contains("user-message")) {
    let nextElement = messageElement.nextElementSibling;

    // Check if the next element is an assistant message before deleting it
    if (nextElement && nextElement.classList.contains("assistant-message")) {
      messageContainer.removeChild(nextElement);
    }
  }

  messageContainer.removeChild(messageElement);

  // Update history
  history = Array.from(messageContainer.getElementsByClassName("chatmessage")).map(element => {
      return {
          role: element.classList.contains("user-message") ? "user" : "assistant",
          content: element.textContent.replace("❌", "") // Make sure to exclude the delete icon's text
      };
  });
}

function adjustInputHeight() {
  userInput.style.height = "auto";
  userInput.style.height = userInput.scrollHeight + "px";
}
});

