"""Configuration for the LLM Council."""

import os
from dotenv import load_dotenv

load_dotenv()

# PolzaAI API key
POLZAAI_API_KEY = os.getenv("POLZAAI_API_KEY")

# Council members - list of PolzaAI model identifiers
COUNCIL_MODELS = [
    "openai/gpt-5.1",
    "google/gemini-3-flash-preview",
    "anthropic/claude-sonnet-4.5",
    "x-ai/grok-4-fast",
]

# Chairman model - synthesizes final response
CHAIRMAN_MODEL = "google/gemini-3-flash-preview"

# PolzaAI API endpoint
POLZAAI_API_URL = "https://api.polza.ai/api/v1/chat/completions"

# Data directory for conversation storage
DATA_DIR = "data/conversations"
