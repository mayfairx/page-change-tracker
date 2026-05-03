import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"), base_url="https://openrouter.ai/api/v1"
)

response = client.chat.completions.create(
    model="google/gemini-2.0-flash-001",
    messages=[
        {
            "role": "user",
            "content": "Summarize this in one short sentence: 'OpenAI announced a new model that can generate videos from text descriptions.'",
        }
    ],
)

print(response.choices[0].message.content)
