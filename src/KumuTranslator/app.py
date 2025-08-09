import sys
import os

# Add the shared directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from utils import (
    log_api_usage,
    get_completion_from_messagesOpen,
    _extract_text_and_usage
)

app = Flask(__name__, static_folder="static")
CORS(
    app,
    resources={
        r"/translate": {"origins": ["https://kumubot.com", "https://kumubot.com/kumutranslator"]},
    },
)


@app.route("/")
def home():
    return render_template("index.html")




# KUMUTRANSLATE
@app.route("/translate", methods=["POST"])
def translate():
    data = request.get_json()
    text = data["text"].strip()
    language = data["language"]
    language = "Hawaiian" if "Hawaiian" in language else "English"

    prompt_tokens = completion_tokens = total_tokens = 0
    translated_text = ""

    if language == "Hawaiian":
        messages = [
            {"role": "user", "content": f"Translate the following text to English and output the translated English text. "
                                         f"The original text should be in Hawaiian, so you should be translating Hawaiian to English. "
                                         f"There should be no Hawaiian text in your output. "
                                         f"Please do not output anything before or after the actual translated text. Text: {text}"},
        ]
        resp = get_completion_from_messagesOpen(messages)
        translated_text, prompt_tokens, completion_tokens, total_tokens = _extract_text_and_usage(resp)
    else:
        messages = [
            {"role": "user", "content": f"Translate the following text to Hawaiian and output the translated Hawaiian text. "
                                         f"The original text should be in English, so you should be translating English to Hawaiian. "
                                         f"There should be no English text in your output. "
                                         f"Please do not output anything before or after the actual translated text. Text: {text}"},
        ]
        resp = get_completion_from_messagesOpen(messages)
        translated_text, prompt_tokens, completion_tokens, total_tokens = _extract_text_and_usage(resp)

    log_api_usage("translate", prompt_tokens, completion_tokens, total_tokens)
    return jsonify({"translated_text": translated_text})


if __name__ == "__main__":
    app.run(debug=True)
