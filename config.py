"""
Konfigurationsdatei für den Enerlytic Bot
"""

import os
from dotenv import load_dotenv

# Lade Umgebungsvariablen aus .env
load_dotenv()

# Hole den Bot-Token aus den Umgebungsvariablen
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Stelle sicher, dass die erforderlichen Tokens vorhanden sind
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN muss in der .env Datei definiert sein")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY muss in der .env Datei definiert sein")

# DeepSeek API Key
DEEPSEEK_API_KEY = "YOUR_DEEPSEEK_API_KEY_HERE"  # Ersetzen Sie dies mit Ihrem tatsächlichen DeepSeek API Key 