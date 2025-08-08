import openai
from dotenv import load_dotenv, find_dotenv
import os

_ = load_dotenv(find_dotenv())
openai.api_key = os.getenv("OPENAI_API_KEY")

prompt = "Dog"
response = openai.Image.create(prompt=prompt,size="256x256")

print(response)





