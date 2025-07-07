import os
import logging
from threading import Thread
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

# Logging setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- आपके चैनल की जानकारी ---
CHANNEL_DATA = {
    "danime": {
        "text": "Here is your link! Click below to proceed:",
        "button_text": "🔔 Request to Join",
        "url": "https://t.me/+mUBQJuyB5FNlMTVl"
    },
    "parody": {
        "text": "Here is your link! Click below to proceed:",
        "button_text": "🔔 Request to Join",
        "url": "https://t.me/+G_BZgtePcARkN2M1"
    },
    "hentai": {
        "text": "Here is your link! Click below to proceed:",
        "button_text": "🔔 Request to Join",
        "url": "https://t.me/+ypMzwwRrx1I1NGZl"
    },
    # आप और भी चैनल ऐसे ही जोड़ सकते हैं
}

# --- Keep-Alive सर्वर ---
app = Flask('')
@app.route('/')
def home():
    return "Bot is alive and running!"

def run():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- बॉट के फंक्शन्स ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    # अगर /start के साथ कोई key है (जैसे ?start=danime)
    if context.args:
        channel_key = context.args[0]
        
        if channel_key in CHANNEL_DATA:
            data = CHANNEL_DATA[channel_key]
            
            keyboard = [[InlineKeyboardButton(data["button_text"], url=data["url"])]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(data["text"], reply_markup=reply_markup)
            logger.info(f"Link for '{channel_key}' sent to {user.first_name}")
        else:
            await update.message.reply_text(f"Hello {user.first_name}! Sorry, yeh link valid nahi hai.")
    # अगर सिर्फ /start भेजा गया है
    else:
        await update.message.reply_text(f"Hello {user.first_name}! Please hamare main channel se link use karein.")


def main():
    # --- महत्वपूर्ण: एनवायरनमेंट वेरिएबल का नाम BOT_TOKEN है ---
    TOKEN = os.environ.get("BOT_TOKEN")
    if not TOKEN:
        logger.critical("Error: BOT_TOKEN not set in environment variables! Bot cannot start.")
        return

    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))

    keep_alive()
    logger.info("Keep-alive server started.")
    
    logger.info("Bot is starting...")
    application.run_polling()


if __name__ == '__main__':
    main()
