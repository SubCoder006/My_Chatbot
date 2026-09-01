import re
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from app.config import GROQ_API_KEY, MAX_TOKENS, MODEL
from langchain_core.messages import HumanMessage, SystemMessage

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

def generate_title(first_message):
    try:
        response = llm.invoke([
            SystemMessage(content="Generate a short 3-6 word title summarizing this message. Reply with ONLY the title, no quotes."),
            HumanMessage(content=first_message),
        ])
        title = response.content.strip().strip('"')
        title = re.sub(r"<think>.*?</think>", "", title, flags=re.DOTALL).strip()
        return title[:60] if title else "New chat"
    except Exception:
        return "New chat"