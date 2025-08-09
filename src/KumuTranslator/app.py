from flask import Flask, request, jsonify, render_template
from openai import OpenAI
from flask_cors import CORS
import os
import pytz
from datetime import datetime

openai_client = OpenAI(api_key="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")

app = Flask(__name__, static_folder="static")
CORS(
    app,
    resources={
        r"/translate": {"origins": ["https://kumubot.com", "https://kumubot.com/kumutranslator"]},
    },
)


@app.route("/")
def index():
    return render_template("index.html")


def log_api_usage(endpoint_name, prompt, completion, total):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    logs_dir = os.path.join(dir_path, "logs")
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    log_file = os.path.join(logs_dir, f"{endpoint_name}.txt")
    with open(log_file, "a") as f:
        now_utc = datetime.now(pytz.timezone("UTC"))
        now_hst = now_utc.astimezone(pytz.timezone("Pacific/Honolulu"))
        formatted_time = now_hst.strftime("%m/%d/%Y %I:%M %p")
        f.write(
            f"{formatted_time}. Prompt: {prompt}. Completion: {completion}. Total: {total}.\n"
        )


def get_completion_from_messagesOpen(
    messages, model="gpt-5-nano", temperature=0, max_tokens=512
):
    response = openai_client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response


# KUMUTRANSLATE
@app.route("/translate", methods=["POST"])
def translate():
    data = request.get_json()
    text = data["text"].strip()
    language = data["language"]

    if "Hawaiian" in language:
        language = "Hawaiian"
    else:
        language = "English"

    prompt_tokens = 0
    completion_tokens = 0
    total_tokens = 0

    translated_text = ""

    if language == "Hawaiian":
        messages = [
            {
                "role": "user",
                "content": f"Translate the following text to English and output the translated English text. The original text should be in Hawaiian, so you should be translating Hawaiian to English. There should be no Hawaiian text in your output. Please do not output anything before or after the actual translated text. Text: {text}",
            },
        ]
        response = get_completion_from_messagesOpen(messages, temperature=0)
        translated_text = response.choices[0].message.content
        prompt_tokens += response.usage.prompt_tokens
        completion_tokens += response.usage.completion_tokens
        total_tokens += response.usage.total_tokens
    else:
        messages = [
            {
                "role": "user",
                "content": f"Translate the following text to Hawaiian and output the translated Hawaiian text. The original text should be in English, so you should be translating English to Hawaiian. There should be no English text in your output. Please do not output anything before or after the actual translated text. Text: {text}",
            },
        ]
        response = get_completion_from_messagesOpen(messages, temperature=0)
        translated_text = response.choices[0].message.content
        prompt_tokens += response.usage.prompt_tokens
        completion_tokens += response.usage.completion_tokens
        total_tokens += response.usage.total_tokens

    log_api_usage("translate", prompt_tokens, completion_tokens, total_tokens)

    return jsonify({"translated_text": translated_text})


if __name__ == "__main__":
    app.run(debug=True)
