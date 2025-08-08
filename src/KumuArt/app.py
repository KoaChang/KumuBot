from flask import Flask, request, jsonify, render_template
from openai import OpenAI
from flask_cors import CORS
import os

app = Flask(__name__, static_folder="static")
CORS(
    app,
    resources={
        r"/art": {"origins": ["https://kumubot.com", "https://kumubot.com/kumuart"]}
    },
)

client = OpenAI(api_key="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")


@app.route("/")
def home():
    return render_template("index.html")


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


# KUMUART
@app.route("/art", methods=["POST"])
def generate_image():
    description = request.json["description"]

    prompt = f"You are a expert artist in the Hawaiian culture and style. Generate an image of {description} in the style of Hawaiian culture and art."
    response = client.images.generate(
        model="dall-e-3", prompt=prompt, size="1024x1024", n=1
    )

    image_url = response.data[0].url

    system = (
        "Your job is provide an interesting fun fact about a topic the user enters."
    )

    messages = [
        {"role": "system", "content": f"{system}"},
        {
            "role": "user",
            "content": f"Write a fun fact about the following topic: {description}. Use complete sentences.",
        },
    ]

    fun_fact = get_completion_from_messages(messages, temperature=0.25, max_tokens=100)

    fun_fact_text = fun_fact.choices[0].message.content

    return jsonify({"image_url": image_url, "fun_fact": fun_fact_text})

    # # For now, simply return a static image
    # return send_file('output.jpeg', mimetype='image/jpeg')


if __name__ == "__main__":
    app.run(debug=True)
