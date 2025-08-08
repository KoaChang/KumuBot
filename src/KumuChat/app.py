from flask import Flask, request, jsonify, render_template
from openai import OpenAI
import os
from flask_cors import CORS

client = OpenAI(api_key="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")

app = Flask(__name__, static_folder="static")
CORS(
    app,
    resources={
        r"/chat": {"origins": ["https://kumubot.com", "https://kumubot.com/kumuchat"]}
    },
)


def get_completion(prompt, model="gpt-3.5-turbo", temperature=0, max_tokens=400):
    messages = [{"role": "user", "content": prompt}]
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response


def get_completion_from_messages(
    messages, model="gpt-3.5-turbo", temperature=0, max_tokens=250
):
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,  # this is the degree of randomness of the model's output
        max_tokens=max_tokens,  # the maximum number of tokens the model can ouptut
    )

    return response


@app.route("/")
def home():
    return render_template("index.html")


# KUMUCHAT
# cheaper alternative
@app.route("/chat", methods=["POST"])
def message():
    data = request.get_json()
    message_history = data["history"]
    is_english_enabled = data.get("english_output")
    current_message = data["message"]

    text = ""

    if is_english_enabled == True:
        system_message = """You are KumuBot, an automated assistant made by Koa Chang and trained on Hawaiian data.\
        You are an expert on questions related to anything Hawaiʻi and its language and culture.\
        Your purpose is to answer questions and be helpful to the user.\
        Your must respond in English.\
        Only output complete sentences.\
        """

        current_message += " (Remember to respond in English)"

        messages = (
            [{"role": "system", "content": f"{system_message}"}]
            + message_history[:-1]
            + [{"role": "user", "content": f"{current_message}"}]
        )

        response = get_completion_from_messages(messages, max_tokens=250)

        text = response.choices[0].message.content

    else:
        system_message = """You are KumuBot, an automated assistant made by Koa Chang and trained on Hawaiian data.\
        You are an expert on questions related to anything Hawaiʻi and its language and culture.\
        Your purpose is to answer questions and be helpful to the user.\
        Your must respond in Hawaiian.\
        Only output complete sentences.\
        """

        current_message += " (Remember to respond in Hawaiian)"

        messages = (
            [{"role": "system", "content": f"{system_message}"}]
            + message_history[:-1]
            + [{"role": "user", "content": f"{current_message}"}]
        )

        response = get_completion_from_messages(messages, max_tokens=250)

        text = response.choices[0].message.content

        # Here you can process the user message and generate a system message
        # For now, we'll just echo back the user message
        # response =

    return jsonify({"message": text})


if __name__ == "__main__":
    app.run(debug=True)
