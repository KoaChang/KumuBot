import openai
from dotenv import load_dotenv, find_dotenv
import os

_ = load_dotenv(find_dotenv())
openai.api_key = "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"

prompt = "Dog"
response = openai.Image.create(prompt=prompt,size="256x256")

print(response)





