import os 
from dotenv import load_dotenv

load_dotenv()   # read my .env file

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL = "qwen/qwen3.6-27b"
MAX_TOKENS = 1500
MAX_HISTORY_MESSAGES = 10
SYSTEM_PROMPT = "You are a helpful, friendly assistant. Keep answers concise and short. Always think before answering."
