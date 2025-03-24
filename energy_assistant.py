#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Energiespar-Assistent

Ein Telegram-Bot, der Benutzern hilft, Energieeinsparungsvorschläge zu erhalten.
Kann Text-, Audio- und Bildnachrichten verarbeiten und mit GPT-4 interagieren.
"""

import os
import json
import base64
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union
import asyncio

from openai import OpenAI
from dotenv import load_dotenv
from telegram import Update, Message
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Setze die Standard-Kodierung auf UTF-8
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# Konfiguration des Loggings
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    encoding='utf-8'
)
logger = logging.getLogger(__name__)

# Laden der Umgebungsvariablen
load_dotenv()

# API-Schlüssel
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")

# OpenAI Client initialisieren
client = OpenAI(
    api_key=OPENAI_API_KEY,
    base_url="https://api.openai.com/v1",  # Standard OpenAI API URL
    timeout=60.0,
    max_retries=3
)

# Konfiguration
DATA_DIR = Path(os.getenv("DATA_DIR", "./data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)

# System-Prompt für den Energiespar-Assistenten
SYSTEM_PROMPT = """
Du bist ein hilfreicher Assistent, der Benutzer bei der Energieeinsparung unterstützt. Deine Aufgabe ist es:

1. Dich auf energietechnische Fragen zu konzentrieren und andere Themen höflich abzulehnen oder auf energierelevante Aspekte zu lenken
2. Den Benutzer durch strukturierte Abfragen zu führen, um personalisierte Energiespartipps zu geben
3. Konkrete und umsetzbare Empfehlungen für Energieeffizienz in der Wohnung durch Produkte und Maßnahmen zu geben
4. Verständliche und prägnante Erklärungen zu liefern, ohne zu technisch zu werden
5. Potenzielle Kosteneinsparungen durch empfohlene Maßnahmen zu berechnen und dem Nutzer zu präsentieren

Stelle dem Benutzer Fragen zu seiner Wohnsituation, seinen Geräten und seinem Verhalten, um möglichst detaillierte Informationen für personalisierte Empfehlungen zu erhalten.
Konzentriere dich auf Maßnahmen wie energieeffiziente Beleuchtung, wassersparende Duschköpfe, smarte Thermostate, Abdichtungen und optimierte Stromverträge.
Vermeide zu technische Erklärungen und fokussiere dich stattdessen auf die Vorteile und die Umsetzbarkeit der Empfehlungen.
"""

class ConversationManager:
    def __init__(self):
        self.conversation_dir = DATA_DIR

    def save_conversation(self, user_id: int, message: dict):
        """Speichert eine Nachricht in der Konversationshistorie"""
        file_path = os.path.join(self.conversation_dir, f"{user_id}.json")
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            else:
                history = []
            
            history.append(message)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Fehler beim Speichern der Konversation: {e}")

    def get_conversation_history(self, user_id: int, limit: int = 20) -> list:
        """Lädt die letzten N Nachrichten aus der Konversationshistorie"""
        file_path = os.path.join(self.conversation_dir, f"{user_id}.json")
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    history = json.load(f)
                return history[-limit:]
            return []
        except Exception as e:
            logger.error(f"Fehler beim Laden der Konversation: {e}")
            return []

class EnergyAssistant:
    """Hauptklasse für den Energiespar-Assistenten."""

    def __init__(self, api_key: str):
        """Initialisiert den Energiespar-Assistenten."""
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.openai.com/v1",  # Standard OpenAI API URL
            timeout=60.0,
            max_retries=3
        )
        self.conversation_manager = ConversationManager()
        self.conversations = {}
        self.load_conversations()

    def load_conversations(self):
        """Lädt gespeicherte Konversationen aus dem Datenverzeichnis."""
        try:
            for file_path in DATA_DIR.glob("*.json"):
                with open(file_path, "r", encoding="utf-8") as file:
                    user_id = file_path.stem
                    self.conversations[user_id] = json.load(file)
            logger.info(f"Konversationen für {len(self.conversations)} Benutzer geladen.")
        except Exception as e:
            logger.error(f"Fehler beim Laden der Konversationen: {e}")

    def save_conversation(self, user_id: str):
        """Speichert die Konversation eines Benutzers."""
        try:
            file_path = DATA_DIR / f"{user_id}.json"
            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(self.conversations[user_id], file, ensure_ascii=False, indent=2)
            logger.info(f"Konversation für Benutzer {user_id} gespeichert.")
        except Exception as e:
            logger.error(f"Fehler beim Speichern der Konversation für Benutzer {user_id}: {e}")

    def get_user_conversation(self, user_id: str) -> List[Dict]:
        """Holt die Konversation eines Benutzers oder erstellt eine neue."""
        if user_id not in self.conversations:
            self.conversations[user_id] = [
                {"role": "system", "content": SYSTEM_PROMPT}
            ]
        return self.conversations[user_id]

    def add_message_to_conversation(
        self, user_id: str, role: str, content: str, image_url: Optional[str] = None
    ):
        """Fügt eine Nachricht zur Konversation eines Benutzers hinzu."""
        conversation = self.get_user_conversation(user_id)
        
        message = {"role": role, "content": content}
        
        # Wenn ein Bild vorhanden ist, fügen wir es dem Nachrichteninhalt hinzu
        if image_url:
            message = {
                "role": role, 
                "content": [
                    {"type": "text", "text": content},
                    {"type": "image_url", "image_url": {"url": image_url}}
                ]
            }
            
        conversation.append(message)
        self.save_conversation(user_id)

    async def process_message(self, message: str, user_id: int) -> str:
        """Verarbeitet eine Nachricht und generiert eine Antwort"""
        try:
            # Lade Konversationsverlauf
            conversation_history = self.conversation_manager.get_conversation_history(user_id, limit=20)
            
            # Erstelle die Nachrichtenliste für die API
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            
            # Füge den Konversationsverlauf hinzu
            for msg in conversation_history:
                if msg.get('type') == 'text':  # Nur Textnachrichten verarbeiten
                    role = "assistant" if msg.get('is_bot', False) else "user"
                    content = msg.get('content', '')
                    if content:  # Nur hinzufügen, wenn Inhalt vorhanden
                        messages.append({"role": role, "content": content})
            
            # Füge die aktuelle Nachricht hinzu
            messages.append({"role": "user", "content": message})
            
            # Erstelle Chat-Completion mit await
            try:
                completion = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self.client.chat.completions.create(
                        model="gpt-4o-2024-08-06",
                        messages=messages,
                        temperature=0.7,
                        max_tokens=800
                    )
                )
                
                response = completion.choices[0].message.content
                
                # Füge Kostenberechnungen hinzu, wenn relevant
                if "kosten" in message.lower() or "einsparung" in message.lower() or "sparen" in message.lower():
                    # Hier Code für die Integration von Kostenberechnungen basierend auf externen Daten
                    # Beispiel: response += "\n\nDurch die empfohlenen Maßnahmen könntest du bis zu 100€ pro Jahr einsparen."
                    pass
                
                return response
            
            except Exception as api_error:
                logger.error(f"API-Fehler: {str(api_error)}")
                raise
            
        except Exception as e:
            logger.error(f"Fehler bei der Verarbeitung der Nachricht: {str(e)}")
            if "insufficient_quota" in str(e):
                return "Entschuldigung, aber ich habe momentan keine verfügbaren API-Credits mehr. Bitte kontaktieren Sie den Administrator."
            elif "invalid_api_key" in str(e):
                return "Es gibt ein Problem mit dem API-Schlüssel. Bitte kontaktieren Sie den Administrator."
            elif "connection" in str(e).lower():
                return "Entschuldigung, aber es gibt momentan Verbindungsprobleme. Bitte versuchen Sie es in ein paar Minuten erneut."
            else:
                return "Entschuldigung, es gab ein Problem bei der Verarbeitung Ihrer Anfrage. Bitte versuchen Sie es später erneut."

    async def process_audio(self, file_path: str) -> str:
        """Verarbeitet eine Audiodatei mit OpenAI's Whisper API."""
        try:
            with open(file_path, "rb") as audio_file:
                response = await client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file
                )
            return response.text
        except Exception as e:
            logger.error(f"Fehler bei der Transkription der Audiodatei: {e}")
            return "Es tut mir leid, ich konnte die Audiodatei nicht verarbeiten."

    def encode_image_to_base64(self, file_path: str) -> str:
        """Konvertiert ein Bild in Base64-Format."""
        try:
            with open(file_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode("utf-8")
        except Exception as e:
            logger.error(f"Fehler bei der Kodierung des Bildes: {e}")
            return ""


# Telegram Bot Funktionen
assistant = EnergyAssistant(OPENAI_API_KEY)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sendet eine Begrüßungsnachricht, wenn der Befehl /start verwendet wird."""
    user_id = str(update.effective_user.id)
    welcome_message = (
        "Willkommen beim Energiespar-Assistenten! 👋\n\n"
        "Ich bin hier, um dir zu helfen, Energie und damit Geld zu sparen. "
        "Du kannst mir Textnachrichten, Sprachnachrichten oder Bilder schicken, "
        "und ich werde versuchen, dir nützliche Tipps zu geben.\n\n"
        "Wie kann ich dir heute helfen?"
    )
    await update.message.reply_text(welcome_message)
    assistant.add_message_to_conversation(user_id, "assistant", welcome_message)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sendet eine Hilfenachricht, wenn der Befehl /help verwendet wird."""
    help_message = (
        "Hier sind einige Möglichkeiten, wie du mit mir interagieren kannst:\n\n"
        "- Sende mir eine Textnachricht mit Fragen zu Energiespartipps\n"
        "- Sende mir ein Foto deines Raumes oder deiner Geräte für spezifische Empfehlungen\n"
        "- Sende mir eine Sprachnachricht, wenn du nicht tippen möchtest\n"
        "- Verwende /reset, um unsere Unterhaltung neu zu starten\n\n"
        "Ich bin hier, um zu helfen!"
    )
    await update.message.reply_text(help_message)


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Setzt die Konversation zurück, wenn der Befehl /reset verwendet wird."""
    user_id = str(update.effective_user.id)
    assistant.conversations[user_id] = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]
    assistant.save_conversation(user_id)
    await update.message.reply_text(
        "Unsere Unterhaltung wurde zurückgesetzt. Wie kann ich dir jetzt helfen?"
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Verarbeitet eingehende Nachrichten."""
    try:
        user_id = update.effective_user.id
        message = update.effective_message
        
        # Lade die Konversation des Benutzers
        conversation = assistant.get_user_conversation(str(user_id))
        
        # Zeige Tippindikator
        await message.chat.send_chat_action(action="typing")
        
        # Verarbeite die Nachricht basierend auf ihrem Typ
        if message.text:
            user_input = message.text
        elif message.voice:
            # Verarbeitung von Sprachnachrichten...
            pass
        elif message.photo:
            # Verarbeitung von Bildern...
            pass
        else:
            await message.reply_text("Entschuldigung, aber ich kann nur Text-, Sprach- und Bildnachrichten verarbeiten.")
            return

        # Aktualisiere die Konversation
        conversation.append({"role": "user", "content": user_input})
        
        try:
            # Generiere Antwort
            response = await assistant.process_message(user_input, user_id)
            
            # Füge die Antwort zur Konversation hinzu
            conversation.append({"role": "assistant", "content": response})
            
            # Speichere die aktualisierte Konversation
            assistant.save_conversation(str(user_id))
            
            # Sende die Antwort
            await message.reply_text(response)
            
        except Exception as e:
            logger.error(f"Fehler bei der Verarbeitung: {str(e)}")
            error_message = "Es tut mir leid, aber es gab einen Fehler bei der Verarbeitung Ihrer Anfrage. Bitte versuchen Sie es später noch einmal."
            await message.reply_text(error_message)
            
    except Exception as e:
        logger.error(f"Unerwarteter Fehler: {str(e)}")
        await update.effective_message.reply_text(
            "Es ist ein unerwarteter Fehler aufgetreten. Bitte versuchen Sie es später noch einmal."
        )


async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Verarbeitet eingehende Audiodateien."""
    user_id = str(update.effective_user.id)
    
    # Informieren Sie den Benutzer, dass die Audiodatei verarbeitet wird
    await update.message.reply_text("Ich verarbeite deine Audiodatei...")
    
    # Audio-Datei herunterladen
    audio_file = await update.message.voice.get_file()
    file_path = f"temp_audio_{user_id}.ogg"
    await audio_file.download_to_drive(file_path)
    
    # Audio transkribieren
    transcript = await assistant.process_audio(file_path)
    
    # Aufräumen der temporären Datei
    os.remove(file_path)
    
    # Informieren Sie den Benutzer über die Transkription
    await update.message.reply_text(f"Ich habe folgendes verstanden: {transcript}")
    
    # Hinzufügen der transkribierten Nachricht zur Konversation
    assistant.add_message_to_conversation(user_id, "user", transcript)
    
    # Generieren einer Antwort
    await update.message.reply_chat_action("typing")
    response = await assistant.process_message(transcript, user_id)
    
    # Hinzufügen der Assistentenantwort zur Konversation
    assistant.add_message_to_conversation(user_id, "assistant", response)
    
    # Senden der Antwort an den Benutzer
    await update.message.reply_text(response)


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Verarbeitet eingehende Fotos."""
    user_id = str(update.effective_user.id)
    
    # Informieren Sie den Benutzer, dass das Foto verarbeitet wird
    await update.message.reply_text("Ich analysiere dein Foto...")
    
    # Foto herunterladen
    photo_file = await update.message.photo[-1].get_file()
    file_path = f"temp_photo_{user_id}.jpg"
    await photo_file.download_to_drive(file_path)
    
    # Bild in Base64 konvertieren für die GPT-4 Vision API
    image_base64 = assistant.encode_image_to_base64(file_path)
    image_url = f"data:image/jpeg;base64,{image_base64}"
    
    # Begleittext zum Bild abrufen oder Default verwenden
    caption = update.message.caption or "Hier ist ein Bild. Kannst du mir Energiespartipps basierend auf diesem Bild geben?"
    
    # Hinzufügen der Bildnachricht zur Konversation
    assistant.add_message_to_conversation(user_id, "user", caption, image_url)
    
    # Aufräumen der temporären Datei
    os.remove(file_path)
    
    # Generieren einer Antwort
    await update.message.reply_chat_action("typing")
    response = await assistant.process_message(caption, user_id)
    
    # Hinzufügen der Assistentenantwort zur Konversation
    assistant.add_message_to_conversation(user_id, "assistant", response)
    
    # Senden der Antwort an den Benutzer
    await update.message.reply_text(response)


def main():
    """Startet den Bot."""
    # Überprüfen, ob API-Schlüssel gesetzt sind
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN ist nicht gesetzt")
        return
    if not OPENAI_API_KEY:
        logger.error("OPENAI_API_KEY ist nicht gesetzt")
        return

    # Erstellen der Anwendung und Hinzufügen von Handlern
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Befehle
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("reset", reset))

    # Nachrichtentypen
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.VOICE, handle_audio))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    # Bot starten
    logger.info("Bot gestartet")
    application.run_polling()


if __name__ == "__main__":
    main() 