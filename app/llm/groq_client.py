import re
from groq import Groq
from app.config import GROQ_API_KEY, MAX_TOKENS, MODEL

client = Groq(api_key=GROQ_API_KEY)

def get_reply(messages):
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        max_tokens=MAX_TOKENS,
        reasoning_effort="none",
        include_reasoning=False
    )
    content = response.choices[0].message.content
    content = re.sub(r"<think>.*?</think>","",content, flags=re.DOTALL).strip()
    return content
