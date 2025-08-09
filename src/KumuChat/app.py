import sys
import os

# Add the shared directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from utils import (
    log_api_usage,
    get_completion_from_messagesOpen,
    _extract_text_and_usage,
    _last_five_pairs
)

app = Flask(__name__, static_folder="static")
CORS(
    app,
    resources={
        r"/chat": {"origins": ["https://kumubot.com", "https://kumubot.com/kumuchat", "http://127.0.0.1:5500"]},
    },
)


@app.route("/")
def home():
    return render_template("index.html")


# KUMUCHAT
@app.route("/chat", methods=["POST"])
def message():
    data = request.get_json()

    message_history = data.get("history", [])  # List[{"role","content"}]
    is_hawaiian_enabled = data.get("hawaiian_output")
    current_message = data.get("message")      # string OR list of parts (may include images)

    # Avoid doubling the final user message if frontend echoes it
    if message_history and message_history[-1].get('role') == 'user' and message_history[-1].get('content') == current_message:
        message_history = message_history[:-1]

    # Server-side enforce last 5 pairs
    message_history = _last_five_pairs(message_history)

    # System prompt
    system_message_content = (
        "You are KumuChat, an automated assistant made by Koa Chang and trained on Hawaiian data.\n"
        "You are an expert on questions related to anything Hawaiʻi and its language and culture.\n"
        "Your purpose is to answer questions and be helpful to the user.\n"
        f"You must respond in {'the Hawaiian language' if is_hawaiian_enabled else 'English'}.\n"
        "Only output complete sentences."
    )

    # Build the 'messages' list for Responses API
    messages = []
    messages.append({'role': 'system', 'content': system_message_content})
    messages.extend(message_history)
    messages.append({'role': 'user', 'content': current_message})

    # Call model
    response = get_completion_from_messagesOpen(messages)

    # Extract text + usage
    text, prompt_tokens, completion_tokens, total_tokens = _extract_text_and_usage(response)

    log_api_usage("chat", prompt_tokens, completion_tokens, total_tokens)

    return jsonify({"message": text})


if __name__ == "__main__":
    app.run(debug=True)
