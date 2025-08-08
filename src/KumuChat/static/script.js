document.addEventListener("DOMContentLoaded", function() {
    const submitBtn = document.getElementById("kumuchat-submit-btn");
    const userInput = document.getElementById("kumuchat-user-input");
    const imageInput = document.getElementById("kumuchat-image-input");
    const fileNameDisplay = document.getElementById("kumuchat-file-name");
    const messageContainer = document.getElementById("kumuchat-message-container");
    const outputHawaiianCheckbox = document.getElementById("output-hawaiian");

    // Configure marked for safe rendering
    marked.setOptions({
        breaks: true,         // Add line breaks when rendered
        gfm: true,            // GitHub flavored markdown
        headerIds: false,     // Don't add ids to headers
        sanitize: false,      // Don't sanitize, we'll use DOMPurify later if needed
    });

    let history = [];

    // Update file name display when a file is selected
    imageInput.addEventListener("change", function() {
        if (imageInput.files.length > 0) {
            fileNameDisplay.textContent = imageInput.files[0].name;
        } else {
            fileNameDisplay.textContent = "";
        }
    });

    submitBtn.addEventListener("click", sendMessage);
    userInput.addEventListener("keydown", function(event) {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            sendMessage();
        }
    });
    userInput.addEventListener("input", adjustInputHeight);

    async function sendMessage() {
        const messageText = userInput.value.trim();
        const hawaiianOutput = outputHawaiianCheckbox.checked;
        const imageFile = imageInput.files[0];

        if (messageText !== "" || imageFile) {
            let messageContent = [];
            if (messageText !== "") {
                messageContent.push({ type: "text", text: messageText });
            }
            if (imageFile) {
                try {
                    const dataURL = await readFileAsDataURL(imageFile);
                    messageContent.push({
                        type: "image_url",
                        image_url: { url: dataURL }
                    });
                } catch (error) {
                    console.error("Error reading image file:", error);
                    addMessage("assistant", "Error processing the image. Please try again.", false);
                    return;
                }
            }

            addMessage("user", messageContent, true);
            userInput.value = "";
            imageInput.value = "";
            fileNameDisplay.textContent = "";
            adjustInputHeight();
            userInput.disabled = true;
            imageInput.disabled = true;
            submitBtn.disabled = true;

            // Loading animation
            submitBtn.innerHTML = `Loading<span class="loading-dots"></span>`;

            // Prepare and send the request
            const lastMessages = history.slice(-9);
            try {
                const response = await fetch('https://kumubot.pythonanywhere.com/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        message: messageContent, 
                        history: lastMessages,
                        hawaiian_output: hawaiianOutput 
                    }),
                });
                if (!response.ok) throw new Error(`Error: ${response.statusText}`);
                const data = await response.json();
                addMessage("assistant", data.message, false);
            } catch (error) {
                console.error("Error sending message:", error);
                addMessage("assistant", "Sorry, something went wrong. Please try again.", false);
            } finally {
                // Reset input and button
                submitBtn.innerHTML = 'Submit';
                userInput.disabled = false;
                imageInput.disabled = false;
                submitBtn.disabled = false;
                userInput.focus();
                messageContainer.scrollTop = messageContainer.scrollHeight;
            }
        }
    }

    function readFileAsDataURL(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => resolve(reader.result);
            reader.onerror = reject;
            reader.readAsDataURL(file);
        });
    }

    function addMessage(role, content, userTriggered) {
        const messageElement = document.createElement("div");
        messageElement.classList.add("kumuchat-message");
        messageElement.classList.add(role === "user" ? "kumuchat-user-message" : "kumuchat-assistant-message");

        if (Array.isArray(content)) {
            content.forEach(part => {
                if (part.type === "text") {
                    const textNode = document.createElement("p");
                    textNode.textContent = part.text;
                    messageElement.appendChild(textNode);
                } else if (part.type === "image_url") {
                    const imgNode = document.createElement("img");
                    imgNode.src = part.image_url.url;
                    imgNode.alt = "Uploaded image";
                    imgNode.classList.add("kumuchat-image");
                    messageElement.appendChild(imgNode);
                }
            });
        } else {
            // For assistant messages, render markdown
            if (role === "assistant") {
                messageElement.innerHTML = marked.parse(content);
            } else {
                // For user messages, just use text
                const textNode = document.createElement("p");
                textNode.textContent = content;
                messageElement.appendChild(textNode);
            }
        }

        if(userTriggered) {
            const deleteIcon = document.createElement("span");
            deleteIcon.classList.add("kumuchat-delete-icon");
            deleteIcon.textContent = "✕";
            deleteIcon.onclick = function() {
                deleteMessagePair(messageElement);
            };
            messageElement.appendChild(deleteIcon);
        }

        messageContainer.appendChild(messageElement);
        history.push({ role: role, content: content });

        // Auto-scroll to the bottom
        messageContainer.scrollTop = messageContainer.scrollHeight;
    }

    function deleteMessagePair(messageElement) {
        if (messageElement.classList.contains("kumuchat-user-message")) {
            const nextElement = messageElement.nextElementSibling;

            // Remove assistant message if it exists
            if (nextElement && nextElement.classList.contains("kumuchat-assistant-message")) {
                messageContainer.removeChild(nextElement);
                // Remove from history
                history.pop(); // assistant message
            }

            // Remove user message
            messageContainer.removeChild(messageElement);
            // Remove from history
            history.pop(); // user message
        }

        // Reconstruct history from remaining messages
        history = [];
        const remainingMessages = messageContainer.getElementsByClassName("kumuchat-message");
        Array.from(remainingMessages).forEach(element => {
            const role = element.classList.contains("kumuchat-user-message") ? "user" : "assistant";

            // This part is tricky since we now have markdown content
            // For simplicity, we'll just store the innerHTML for assistant messages
            if (role === "assistant") {
                history.push({ role: role, content: element.innerHTML });
            } else {
                let content = [];
                element.childNodes.forEach(child => {
                    if (child.tagName === "P") {
                        content.push({ type: "text", text: child.textContent });
                    } else if (child.tagName === "IMG") {
                        content.push({ type: "image_url", image_url: { url: child.src } });
                    }
                });
                history.push({ role: role, content: content });
            }
        });
    }

    function adjustInputHeight() {
        userInput.style.height = "auto";
        userInput.style.height = (userInput.scrollHeight) + "px";

        // If the input exceeds max height, enable scrollbar
        if (userInput.scrollHeight > 150) { // 150px matches the CSS max-height
            userInput.style.overflowY = "auto";
            userInput.style.height = "150px";
        } else {
            userInput.style.overflowY = "hidden";
        }
    }
});

