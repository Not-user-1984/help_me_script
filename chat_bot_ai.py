from openai import OpenAI
from core.settings import DEEPSEEK_API_KEY, BASE_URL, MODEL

client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=BASE_URL)

response = client.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Hello"},
    ],
    stream=False
)

print(response.choices[0].message.content)