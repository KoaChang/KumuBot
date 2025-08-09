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
        r"/chat": {"origins": ["https://kumubot.com", "https://kumubot.com/kumuchat", "http://127.0.0.1:5500"]},
    },
)


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


@app.route("/")
def home():
    return render_template("index.html")


# KUMUCHAT
@app.route("/chat", methods=["POST"])
def message():
    data = request.get_json()

    message_history = data["history"]
    is_hawaiian_enabled = data.get("hawaiian_output")
    current_message = data["message"]

    if (
        message_history
        and message_history[-1]["role"] == "user"
        and message_history[-1]["content"] == current_message
    ):
        message_history = message_history[:-1]

    system_message_content = (
        """You are KumuChat, an automated assistant made by Koa Chang and trained on Hawaiian data.
You are an expert on questions related to anything Hawaiʻi and its language and culture.
Your purpose is to answer questions and be helpful to the user.
You must respond in {}.
Only output complete sentences.""".format(
            "the Hawaiian language" if is_hawaiian_enabled else "English"
        )
    )

    messages = []
    messages.append({"role": "system", "content": system_message_content})
    messages.extend(message_history)
    messages.append({"role": "user", "content": current_message})

    response = get_completion_from_messagesOpen(messages)
    text = response.choices[0].message.content

    return jsonify({"message": text})


if __name__ == "__main__":
    app.run(debug=True)
