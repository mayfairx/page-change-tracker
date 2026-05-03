import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"), base_url="https://openrouter.ai/api/v1"
)


def summarize(text):
    try:
        response = client.chat.completions.create(
            model="google/gemini-2.0-flash-001",
            messages=[
                {
                    "role": "user",
                    "content": f"Summarize the following news headline in one short sentence in English: '{text}'",
                }
            ],
            max_tokens=100,
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return text
