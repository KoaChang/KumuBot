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
        r"/art": {"origins": ["https://kumubot.com", "https://kumubot.com/kumuart"]},
    },
)

openai_client = OpenAI(api_key="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")


@app.route("/")
def home():
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
        if endpoint_name == "art":
            f.write(
                f"{formatted_time}. Prompt: {prompt}. Completion: {completion}. Total: {total}. Image Cost: 0.04\n"
            )
        else:
            f.write(
                f"{formatted_time}. Prompt: {prompt}. Completion: {completion}. Total: {total}.\n"
            )


def get_completion_from_messagesOpen(
    messages, model="gpt-4.1-mini", temperature=0, max_tokens=512
):
    response = openai_client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response


# KUMUART
@app.route("/art", methods=["POST"])
def generate_image():
    description = request.json["description"]

    prompt = (
        f"You are a expert artist in the Hawaiian culture and style. Generate an image of {description} in the style of Hawaiian culture and art."
    )

    response = openai_client.images.generate(
        model="dall-e-3", prompt=prompt, size="1024x1024", n=1
    )

    image_url = response.data[0].url

    system = "Your job is provide an interesting fun fact about a topic the user enters."

    messages = [
        {"role": "system", "content": f"{system}"},
        {
            "role": "user",
            "content": f"Write a fun fact about the following topic: {description}. Use complete sentences.",
        },
    ]

    fun_fact = get_completion_from_messagesOpen(messages, temperature=0.25, max_tokens=300)

    fun_fact_text = fun_fact.choices[0].message.content

    prompt_tokens = fun_fact.usage.prompt_tokens
    completion_tokens = fun_fact.usage.completion_tokens
    total_tokens = fun_fact.usage.total_tokens

    log_api_usage("art", prompt_tokens, completion_tokens, total_tokens)

    return jsonify({"image_url": image_url, "fun_fact": fun_fact_text})


if __name__ == "__main__":
    app.run(debug=True)
