#!/bin/bash

# Erstellen einer virtuellen Umgebung
python3 -m venv venv

# Aktivieren der virtuellen Umgebung
source venv/bin/activate

# Installation der benötigten Pakete
pip install python-telegram-bot openai python-dotenv

# Erstellen einer .env-Vorlage
cat > .env.example << EOL
# API-Schlüssel
TELEGRAM_BOT_TOKEN=dein_telegram_bot_token
OPENAI_API_KEY=dein_openai_api_key

# Konfiguration
DATA_DIR=./data
EOL

# Erstellen des Datenverzeichnisses
mkdir -p data

echo "Setup abgeschlossen. Bitte kopiere .env.example zu .env und aktualisiere die API-Schlüssel." 