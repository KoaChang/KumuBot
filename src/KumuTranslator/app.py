from flask import Flask, request, jsonify, render_template
import openai
from dotenv import load_dotenv, find_dotenv
import os
from flask_cors import CORS

_ = load_dotenv(find_dotenv())
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__, static_folder='static')
CORS(app, resources={r"/translate": {"origins": ["https://kumubot.com", "https://kumubot.com/kumutranslator"]}})


# if only want requests from word press website, add line CORS(app, origins="https://your-wordpress-site.com")

def get_completion(prompt, model="gpt-3.5-turbo",max_tokens=400,temperature=0):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature, 
        max_tokens=max_tokens,
    )
    return response.choices[0].message["content"]

def get_completion_from_messages(messages, 
                                 model="gpt-3.5-turbo", 
                                 temperature=0, 
                                 max_tokens=400):
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message["content"]

def log_api_usage(endpoint_name,prompt,completion,total):
    # Create a directory for the logs if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Open the log file for the endpoint
    with open(f'logs/{endpoint_name}.txt', 'a') as f:
        # Write the current time and the number of tokens used to the log file
        if endpoint_name == 'art':
            f.write(f'{datetime.datetime.now()}. Prompt: {prompt}. Completion: {completion}. Total: {total}. Image Cost: 0.016')
        else:
            f.write(f'{datetime.datetime.now()}. Prompt: {prompt}. Completion: {completion}. Total: {total}.')

# KUMUTRANSLATE
@app.route('/translate', methods=['POST'])
def translate():
    data = request.get_json()
    text = data['text']
    text = text.strip()
    language = data['language']

    if "Hawaiian" in language:
        language = "Hawaiian"
    else:
        language = "English"

    # TODO: Implement your translation code here
    # For now, we'll just return the same text

    prompt_tokens = 0
    completion_tokens = 0
    total_tokens = 0

    translated_text = ""

    if language == "Hawaiian":
        prompt = f"What is the language of the following text? Output one word for what language it is. Remember your output must be only one word. Text: {text}"
        response = get_completion(prompt)

        predicted_language = response.choices[0].message["content"].lower()

        prompt_tokens += response['usage']['prompt_tokens']
        completion_tokens += response['usage']['completion_tokens']
        total_tokens += response['usage']['total_tokens']

        if "hawaiian" in predicted_language:
            messages =  [{'role':'user','content':f'Translate the following text to English and output the translated English text. There should be no Hawaiian text in your output. Please do not output anything before or after the actual translated text. Text: {text}'},]
            
            response = get_completion_from_messages(messages, temperature=0)
            translated_text = response.choices[0].message["content"]
            prompt_tokens += response['usage']['prompt_tokens']
            completion_tokens += response['usage']['completion_tokens']
            total_tokens += response['usage']['total_tokens']

        else:
            translated_text = "I only accept Hawaiian text, try again."

    else:
        prompt = f"What is the language of the following text? Output one word for what language it is. Remember your output must be only one word. Text: {text}"
        response = get_completion(prompt)
        predicted_language = response.choices[0].message["content"].lower()
        prompt_tokens += response['usage']['prompt_tokens']
        completion_tokens += response['usage']['completion_tokens']
        total_tokens += response['usage']['total_tokens']

        if "english" in predicted_language:
            messages =  [{'role':'user','content':f'Translate the following text to Hawaiian and output the translated Hawaiian text. There should be no English text in your output. Please do not output anything before or after the actual translated text. Text: {text}'},]
            response = get_completion_from_messages(messages, temperature=0)
            translated_text = response.choices[0].message["content"]
            prompt_tokens += response['usage']['prompt_tokens']
            completion_tokens += response['usage']['completion_tokens']
            total_tokens += response['usage']['total_tokens']

        else:
            translated_text = "I only accept English text, try again."

    log_api_usage('translate',prompt_tokens,completion_tokens,total_tokens)

    return jsonify({'translated_text': translated_text})

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=False)
