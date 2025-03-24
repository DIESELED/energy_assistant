from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import TELEGRAM_BOT_TOKEN, OPENAI_API_KEY
from privacy_policy import get_privacy_policy
from openai import OpenAI
import logging
import sys

# Logging konfigurieren
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# OpenAI Client initialisieren
client = OpenAI(api_key=OPENAI_API_KEY)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Begrüßt den Benutzer und erklärt die Grundfunktionen.
    """
    welcome_text = """
👋 Willkommen beim Enerlytic Bot!

Ich bin dein persönlicher Energiespar-Assistent. Ich helfe dir dabei, Energie und Geld zu sparen.

📝 Verfügbare Befehle:
/start - Startet den Bot
/help - Zeigt die Hilfe-Nachricht
/privacy - Zeigt die Datenschutzerklärung

💡 Du kannst mir einfach Fragen zum Thema Energiesparen stellen, zum Beispiel:
- Wie kann ich beim Heizen Energie sparen?
- Was sind die besten Tipps für niedrigere Stromkosten?
- Welche Haushaltsgeräte verbrauchen am meisten Energie?
"""
    await update.message.reply_text(welcome_text)

async def privacy_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Sendet die Datenschutzerklärung an den Benutzer.
    """
    await update.message.reply_text(get_privacy_policy())

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Sendet eine Hilfe-Nachricht an den Benutzer.
    """
    help_text = """
🤖 Willkommen bei Enerlytic!

Verfügbare Befehle:
/start - Startet den Bot
/help - Zeigt diese Hilfe-Nachricht
/privacy - Zeigt die Datenschutzerklärung

Ich bin dein persönlicher Energiespar-Assistent. Du kannst mich alles zum Thema Energie sparen fragen, und ich werde dir passende Tipps geben.
"""
    await update.message.reply_text(help_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Verarbeitet eingehende Textnachrichten und verwendet OpenAI für die Antworten.
    """
    message_text = update.message.text
    logger.debug(f"Nachricht erhalten: {message_text}")
    
    try:
        logger.debug("Versuche OpenAI API aufzurufen...")
        # OpenAI API aufrufen
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": """Du bist ein Energiespar-Experte. Beantworte Fragen zum Thema Energiesparen 
                präzise und praktisch. Gib konkrete, umsetzbare Tipps. Verwende eine freundliche, verständliche Sprache 
                und formatiere deine Antworten mit Emojis für bessere Lesbarkeit. Antworte immer auf Deutsch."""},
                {"role": "user", "content": message_text}
            ],
            max_tokens=500,
            temperature=0.7
        )
        logger.debug("OpenAI API Antwort erhalten")
        
        # Antwort extrahieren und senden
        bot_response = response.choices[0].message.content
        logger.debug(f"Bot-Antwort: {bot_response[:100]}...")
        await update.message.reply_text(bot_response)
        
    except Exception as e:
        error_message = f"Entschuldigung, es gab ein technisches Problem: {str(e)}"
        logger.error(f"Fehler beim Verarbeiten der Nachricht: {str(e)}")
        logger.error(f"Fehlertyp: {type(e)}")
        await update.message.reply_text(error_message)

def main():
    """
    Startet den Bot.
    """
    try:
        logger.info("Starte Bot...")
        # Erstelle die Application
        application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

        # Füge Handler hinzu
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("privacy", privacy_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

        # Starte den Bot
        logger.info("Bot gestartet, beginne mit Polling...")
        application.run_polling()
    except Exception as e:
        logger.error(f"Fehler beim Starten des Bots: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 