# Energiespar-Assistent

Ein Telegram-Bot, der Benutzern hilft, Energie und Kosten zu sparen. Der Bot kann Text-, Audio- und Bildnachrichten verarbeiten und gibt personalisierte Energiespartipps.

## Funktionen

- Verarbeitung von Text-, Audio- und Bildnachrichten
- Transkription von Sprachnachrichten mit OpenAI Whisper
- Analyse von Bildern für Energiesparempfehlungen
- Speicherung von Konversationen für besseren Kontext
- Personalisierte Energiespartipps und Kosten-Nutzen-Analysen

## Voraussetzungen

- Python 3.7 oder höher
- Ein Telegram-Bot-Token (über BotFather erhältlich)
- Ein OpenAI API-Schlüssel

## Installation

1. Repository klonen:
```bash
git clone https://github.com/IhrUsername/energy_assistant.git
cd energy_assistant
```

2. Virtuelle Umgebung erstellen und aktivieren:
```bash
python3 -m venv venv
source venv/bin/activate  # Unter Windows: venv\Scripts\activate
```

3. Abhängigkeiten installieren:
```bash
pip install -r requirements.txt
```

4. Umgebungsvariablen konfigurieren:
```bash
cp .env.example .env
# Bearbeiten Sie .env und fügen Sie Ihre API-Schlüssel ein
```

## Konfiguration

Erstellen Sie eine `.env`-Datei mit folgenden Variablen:

```
TELEGRAM_BOT_TOKEN=Ihr_Telegram_Bot_Token
OPENAI_API_KEY=Ihr_OpenAI_API_Schlüssel
DATA_DIR=./data
```

## Verwendung

1. Bot starten:
```bash
python energy_assistant.py
```

2. Mit dem Bot über Telegram interagieren:
- `/start` - Startet den Bot
- `/help` - Zeigt Hilfe an
- `/reset` - Setzt die Konversation zurück
- Senden Sie Textnachrichten für Energiespartipps
- Senden Sie Fotos für spezifische Analysen
- Senden Sie Sprachnachrichten für bequeme Interaktion

## Entwicklung

Der Bot verwendet:
- `python-telegram-bot` für die Telegram-Integration
- `openai` für KI-Funktionen
- `python-dotenv` für Umgebungsvariablen

## Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert. 