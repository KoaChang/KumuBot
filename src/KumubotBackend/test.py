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


from groq import Groq

client = Groq(api_key="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")

response = get_completion("Hello how are you")

text = response.choices[0].message.content
prompt_tokens = response.usage.prompt_tokens
completion_tokens = response.usage.completion_tokens
total_tokens = response.usage.total_tokens

print(text)
print(prompt_tokens)
print(completion_tokens)
print(total_tokens)
