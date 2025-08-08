from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import openai
from dotenv import load_dotenv, find_dotenv
import os

app = Flask(__name__, static_folder="static")
CORS(
    app,
    resources={
        r"/dictionary": {
            "origins": ["https://kumubot.com", "https://kumubot.com/kumudictionary"]
        }
    },
)

_ = load_dotenv(find_dotenv())
openai.api_key = os.getenv("OPENAI_API_KEY")


def log_api_usage(endpoint_name, prompt, completion, total):
    # Create a directory for the logs if it doesn't exist
    if not os.path.exists("logs"):
        os.makedirs("logs")

    # Open the log file for the endpoint
    with open(f"logs/{endpoint_name}.txt", "a") as f:
        # Write the current time and the number of tokens used to the log file
        if endpoint_name == "art":
            f.write(
                f"{datetime.datetime.now()}. Prompt: {prompt}. Completion: {completion}. Total: {total}. Image Cost: 0.016"
            )
        else:
            f.write(
                f"{datetime.datetime.now()}. Prompt: {prompt}. Completion: {completion}. Total: {total}."
            )


def get_completion(prompt, model="gpt-3.5-turbo", temperature=0, max_tokens=400):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message["content"]


def get_completion_from_messages(
    messages, model="gpt-3.5-turbo", temperature=0, max_tokens=400
):
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature,  # this is the degree of randomness of the model's output
        max_tokens=max_tokens,  # the maximum number of tokens the model can ouptut
    )
    return response.choices[0].message["content"]


@app.route("/")
def index():
    return render_template("index.html")


# KUMUDICTIONARY
@app.route("/dictionary", methods=["POST"])
def search():
    data = request.get_json()
    search_word = data["search"]

    # prompt = f"What is the language of the following text. Output one word for what language it is. Remember your output must be only one word. Text: {search_word}"
    # language = get_completion(prompt).lower()

    # print(language)
    # print(search_word)
    # response = ""

    # if "hawaiian" in language:
    system = "Your job is provide details about a inputted Hawaiian word or phrase. The user will input a Hawaiian word or phrase and you must return a description along with the word or phrase being used in a sentence in the Hawaiian language. If you are not familiar with the word or phrase just say you don't understand. If the user misspells the word, use the correct spelling for the word in your output."
    messages = [
        {"role": "system", "content": f"{system}"},
        {
            "role": "user",
            "content": f"What does this Hawaiian word mean: {search_word}.",
        },
    ]
    response = get_completion_from_messages(messages, temperature=0, max_tokens=150)
    prompt_tokens = response["usage"]["prompt_tokens"]
    completion_tokens = response["usage"]["completion_tokens"]
    total_tokens = response["usage"]["total_tokens"]

    response_text = response.choices[0].message["content"]
    # else:
    #     response = "Try again. Please input a Hawaiian word or phrase so I can tell you more about it."

    log_api_usage("dictionary", prompt_tokens, completion_tokens, total_tokens)

    return jsonify({"result": response_text})


if __name__ == "__main__":
    app.run(port=5000)
