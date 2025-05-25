import logging
import threading
import time
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import responses
from scrapper import scrape_user_tables
import subprocess

API_KEY = "7641931043:AAHPflgEiQSIQLkjavkriNj8grfFFEOcLjc"

credentials = [
{"username": "pnb052", "password": "s5623h"},
{"username": "pnb144", "password": "m8519e"},
{"username": "pnb044", "password": "t87368r67"},
{"username": "pnb157", "password": "y8502h"},
{"username": "pnb151", "password": "m4555d"},
{"username": "pnb097", "password": "v2198a"},
{"username": "pnb109", "password": "g1341x"},
{"username": "pnb150", "password": "d6337c"},
{"username": "pnb169", "password": "f3336s"},
{"username": "pnb170", "password": "h7037z"},
{"username": "pnb172", "password": "p7630g"},
{"username": "pnb173", "password": "v2897m"},
{"username": "pnb158", "password": "n7678r"},
{"username": "pnb159", "password": "z4855v"},
{"username": "pnb163", "password": "Z5239x"},
{"username": "pnb166", "password": "h2106h"},
]


# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logging.info('Starting bot...')

# Global variable to store the bot application
bot_app = None

# The user chat_id for sending messages
CHAT_ID = None  # Will be set in the first /start command

# Reusable function to do the scraping and return the message
def run_scraping():
    print("scrapping new data !!!")
    data = scrape_user_tables(credentials)
    return data

# Async Telegram command handlers
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global CHAT_ID
    CHAT_ID = update.effective_chat.id  # Capture chat_id
    logging.info(f"Set CHAT_ID to {CHAT_ID}")
    await update.message.reply_text("Scraping new data from the website, please wait....")
    data = run_scraping()
    await update.message.reply_text(data)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Choose a command: /start - Get latest scraped data\n/help - Show this help message\n/custom - Custom command")

async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("This is a custom command.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = str(update.message.text).lower()
    logging.info(f"User ({update.message.chat.id}) says: {text}")
    response = responses.get_response(text)
    await update.message.reply_text(response)

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.error(msg="Exception while handling an update:", exc_info=context.error)

if __name__ == '__main__':
    app = ApplicationBuilder().token(API_KEY).build()
    bot_app = app  # Store application instance globally

    # Handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("custom", custom_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error_handler)

    # Run the bot
    app.run_polling()