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
            {"role": "user", "content": f"""Your name is KumuTranslate and your job is to translate the following Hawaiian text to English.
                                         The text I will give you should be in Hawaiian. If the text does not seem to be in Hawaiian,
                                         please explain that your job is to translate Hawaiian text to English so please input Hawaiian text.
                                         There should be no Hawaiian text in your output.
                                         Please do not output anything before or after the actual translated text if you are translating. Text: {text}"""},
        ]
        resp = get_completion_from_messagesOpen(messages)
        translated_text, prompt_tokens, completion_tokens, total_tokens = _extract_text_and_usage(resp)
    else:
        messages = [
            {
                "role": "user",
                "content": f"""Your name is KumuTranslate and your job is to translate the following English text to Hawaiian.
                The text I will give you should be in English.
                If the text does not seem to be in English, please explain that your job is to translate English text to Hawaiian so please input English text.
                There should be no English text in your output unless you are explaining your job is to translate English to Hawaiian. If you actually preform a translation to Hawaiian, then the output text should only be Hawaiian.
                Please do not output anything before or after the actual translated text if you are translating.
                Text: {text}"""},
        ]
        resp = get_completion_from_messagesOpen(messages)
        translated_text, prompt_tokens, completion_tokens, total_tokens = _extract_text_and_usage(resp)

    log_api_usage("translate", prompt_tokens, completion_tokens, total_tokens)
    return jsonify({"translated_text": translated_text})


if __name__ == "__main__":
    app.run(debug=True)
