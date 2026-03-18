import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Add the shared directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

load_dotenv(Path(__file__).resolve().with_name(".env"))

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from utils import (
    DEFAULT_CHAT_MODEL,
    log_api_usage,
    get_completion_from_messagesOpen,
    _extract_text_and_usage
)

app = Flask(__name__, static_folder="static")
CORS(
    app,
    resources={
        r"/dictionary": {"origins": ["https://kumubot.com", "https://kumubot.com/kumudictionary"]}
    },
)

CHAT_MODEL = DEFAULT_CHAT_MODEL


@app.route("/")
def home():
    return render_template("index.html")




# KUMUDICTIONARY
@app.route("/dictionary", methods=["POST"])
def search():
    data = request.get_json()
    search_word = data["search"]

    system = "Your job is provide details about a inputted Hawaiian word or phrase. The user will input a Hawaiian word or phrase and you must return a description along with the word or phrase being used in a sentence in the Hawaiian language. If you are not familiar with the word or phrase just say you don't understand. If the user misspells the word, use the correct spelling for the word in your output."
    messages = [
        {"role": "system", "content": f"{system}"},
        {"role": "user", "content": f"What does this Hawaiian word mean: {search_word}."},
    ]
    resp = get_completion_from_messagesOpen(messages, model=CHAT_MODEL)
    response_text, prompt_tokens, completion_tokens, total_tokens = _extract_text_and_usage(resp)

    log_api_usage("dictionary", prompt_tokens, completion_tokens, total_tokens)
    return jsonify({"result": response_text})


if __name__ == "__main__":
    app.run(debug=True)
