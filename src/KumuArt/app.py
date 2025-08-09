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
    openai_client
)

app = Flask(__name__, static_folder="static")
CORS(
    app,
    resources={
        r"/art": {"origins": ["https://kumubot.com", "https://kumubot.com/kumuart"]},
    },
)


@app.route("/")
def home():
    return render_template("index.html")




# KUMUART
@app.route("/art", methods=["POST"])
def generate_image():
    description = request.json["description"]

    prompt = f"You are a expert artist in the Hawaiian culture and style. Generate an image of {description} in the style of Hawaiian culture and art."

    # DALL·E 3 (unchanged)
    response = openai_client.images.generate(
        model="dall-e-3", prompt=prompt, size="1024x1024", n=1
    )
    image_url = response.data[0].url

    system = "Your job is provide an interesting fun fact about a topic the user enters."

    messages = [
        {"role": "system", "content": f"{system}"},
        {"role": "user", "content": f"Write a fun fact about the following topic: {description}. Use complete sentences."},
    ]

    # Fun fact via Responses API (gpt-5-nano)
    fun_fact_resp = get_completion_from_messagesOpen(messages)
    fun_fact_text, prompt_tokens, completion_tokens, total_tokens = _extract_text_and_usage(fun_fact_resp)

    log_api_usage("art", prompt_tokens, completion_tokens, total_tokens)
    return jsonify({"image_url": image_url, "fun_fact": fun_fact_text})


if __name__ == "__main__":
    app.run(debug=True)
