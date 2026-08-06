import re
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from app.config import GROQ_API_KEY, MAX_TOKENS, MODEL

llm = ChatGroq(
    model=MODEL,
    api_key=GROQ_API_KEY,
    max_retries=MAX_TOKENS,
    reasoning_effort="none",
)

prompt = ChatPromptTemplate.from_messages([
    ("placeholder","{message}"),
])

chain = prompt | llm

def get_reply(messages):
    response = llm.invoke(messages)
    content = response.content
    content = re.sub(r"<think>.*?</think>","",content, flags=re.DOTALL).strip()
    return content
