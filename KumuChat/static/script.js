document.addEventListener("DOMContentLoaded", function() {
  const submitBtn = document.getElementById("kumuchat-submit-btn");
  const userInput = document.getElementById("kumuchat-user-input");
  const imageInput = document.getElementById("kumuchat-image-input");
  const fileNameDisplay = document.getElementById("kumuchat-file-name");
  const messageContainer = document.getElementById("kumuchat-message-container");
  const outputHawaiianCheckbox = document.getElementById("output-hawaiian");

  // Configure marked for Markdown
  marked.setOptions({
      breaks: true,
      gfm: true,
      headerIds: false,
      sanitize: false
  });

  let history = [];

  imageInput.addEventListener("change", function() {
      fileNameDisplay.textContent = imageInput.files.length > 0 ? imageInput.files[0].name : "";
  });

  submitBtn.addEventListener("click", sendMessage);
  userInput.addEventListener("keydown", function(event) {
      if (event.key === "Enter" && !event.shiftKey) {
          event.preventDefault();
          sendMessage();
      }
  });

  async function sendMessage() {
      const messageText = userInput.value.trim();
      const hawaiianOutput = outputHawaiianCheckbox.checked;
      const imageFile = imageInput.files[0];

      if (messageText !== "" || imageFile) {
          let messageContent = [];
          if (messageText) messageContent.push({ type: "text", text: messageText });

          if (imageFile) {
              try {
                  const dataURL = await readFileAsDataURL(imageFile);
                  messageContent.push({ type: "image_url", image_url: { url: dataURL } });
              } catch (error) {
                  console.error("Error processing image:", error);
                  return;
              }
          }

          addMessage("user", messageContent);
          userInput.value = "";
          imageInput.value = "";
          fileNameDisplay.textContent = "";

          try {
              const response = await fetch('https://kumubot.pythonanywhere.com/chat', {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify({ message: messageContent, history: history.slice(-9), hawaiian_output: hawaiianOutput }),
              });

              if (!response.ok) throw new Error("Network error");
              const data = await response.json();
              addMessage("assistant", data.message);
          } catch (error) {
              console.error("Error:", error);
          }
      }
  }

  function addMessage(role, content) {
      const messageElement = document.createElement("div");
      messageElement.classList.add("kumuchat-message", role === "user" ? "kumuchat-user-message" : "kumuchat-assistant-message");
      messageElement.innerHTML = role === "assistant" ? marked.parse(content) : `<p>${content[0].text}</p>`;
      messageContainer.appendChild(messageElement);
      messageContainer.scrollTop = messageContainer.scrollHeight;
  }

  function readFileAsDataURL(file) {
      return new Promise((resolve, reject) => {
          const reader = new FileReader();
          reader.onload = () => resolve(reader.result);
          reader.onerror = reject;
          reader.readAsDataURL(file);
      });
  }
});
