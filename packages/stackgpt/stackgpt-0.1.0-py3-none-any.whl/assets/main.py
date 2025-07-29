# ============================================================
# 🧠 StackGPT - Terminal-based StackOverflow-style AI Assistant
# Created by Ayub Farxaan under Buuya Studious Lab (2025)
# GitHub: https://github.com/cptbuuya
# ============================================================

# stackgpt/main.py
import os
from cli import run_cli
from dotenv import load_dotenv

# Load API key from .env
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    print("\n[❌] Missing OpenAI API Key in .env file.\n")
    exit(1)

if __name__ == '__main__':
    run_cli(api_key=OPENAI_API_KEY)
