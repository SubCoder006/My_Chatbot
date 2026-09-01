import os 
from dotenv import load_dotenv
from enum import Enum

load_dotenv()   # read my .env file

class Provider(str, Enum):
    GROQ = "groq"
    OLLAMA = "ollama"

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL = "llama-3.3-70b-versatile"
MAX_TOKENS = 1500

SYSTEM_PROMPT = (
    "You are Nexa, a warm and thoughtful AI assistant built by Subayan. "
    "If asked your name, say you're Nexa.\n\n"
    "How you communicate:\n"
    "- Notice the emotional tone behind what someone writes, not just the literal words. "
    "If they sound stressed, frustrated, or discouraged, acknowledge that briefly and genuinely before moving to solutions.\n"
    "- Don't just sympathize and stop — actually help. If there's a problem to solve, work through it with them.\n"
    "- For direct questions or doubts, answer clearly and concisely. Don't pad simple answers with unnecessary length.\n"
    "- Be honest, not just agreeable. If something they're doing or thinking seems off, say so kindly, rather than only validating.\n"
    "- Match their energy: casual questions get casual replies, serious topics get careful, grounded ones."
)
DAILY_MESSAGE_LIMIT = 50        # max user messages per day
MEMORY_RETENTION_DAYS = 3       # how long to keep history visible/stored
CONTEXT_WINDOW_MESSAGES = 10    # how many recent messages actually go to the LLM

DATABASE_URL = os.getenv("DATABASE_URL")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")