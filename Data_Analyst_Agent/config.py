# config.py
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY not found. Please check your .env file.")

# Use smaller faster model during testing to save tokens
if os.getenv("TEST_MODE") == "true":
    MODEL = "llama-3.1-8b-instant"   # 5x cheaper, separate rate limit
else:
    MODEL = "llama-3.3-70b-versatile"  # full model for production

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=GROQ_API_KEY,
)

print(f"✅ Using model: {MODEL}")