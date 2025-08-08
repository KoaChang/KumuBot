from flask import Flask, request, jsonify, render_template
from openai import OpenAI
from flask_cors import CORS
import os
import pytz
from datetime import datetime

app = Flask(__name__, static_folder="static")
CORS(
    app,
    resources={
        r"/dictionary": {"origins": ["https://kumubot.com", "https://kumubot.com/kumudictionary"]}
    },
)

openai_client = OpenAI(api_key="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")


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
    messages, model="gpt-4.1-mini", temperature=0, max_tokens=200
):
    response = openai_client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response


# KUMUDICTIONARY
@app.route("/dictionary", methods=["POST"])
def search():
    data = request.get_json()
    search_word = data["search"]

    system = "Your job is provide details about a inputted Hawaiian word or phrase. The user will input a Hawaiian word or phrase and you must return a description along with the word or phrase being used in a sentence in the Hawaiian language. If you are not familiar with the word or phrase just say you don't understand. If the user misspells the word, use the correct spelling for the word in your output."
    messages = [
        {"role": "system", "content": f"{system}"},
        {
            "role": "user",
            "content": f"What does this Hawaiian word mean: {search_word}.",
        },
    ]
    response = get_completion_from_messagesOpen(messages, temperature=0, max_tokens=200)
    prompt_tokens = response.usage.prompt_tokens
    completion_tokens = response.usage.completion_tokens
    total_tokens = response.usage.total_tokens

    response_text = response.choices[0].message.content

    log_api_usage("dictionary", prompt_tokens, completion_tokens, total_tokens)

    return jsonify({"result": response_text})


if __name__ == "__main__":
    app.run(debug=True)
