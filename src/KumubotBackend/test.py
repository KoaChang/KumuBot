def get_completion(prompt):
    messages = [{"role": "user", "content": prompt}]

    return get_completion_from_messages(messages)


def get_completion_from_messages(messages):
    completion = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=messages,
        temperature=0,
        max_tokens=512,
        top_p=1,
        stream=False,
        stop=None,
    )
    return completion


import os
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq

load_dotenv(Path(__file__).resolve().with_name(".env"))

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

response = get_completion("Hello how are you")

text = response.choices[0].message.content
prompt_tokens = response.usage.prompt_tokens
completion_tokens = response.usage.completion_tokens
total_tokens = response.usage.total_tokens

print(text)
print(prompt_tokens)
print(completion_tokens)
print(total_tokens)
