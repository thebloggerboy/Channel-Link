import os
import logging
import threading
import asyncio
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

# Logging को कॉन्फ़िगर करें
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- चैनल कॉन्फ़िगरेशन (आपके दिए गए लिंक्स के साथ) ---
CHANNELS = {
    "danime": {
        "message": "Ye raha aapka Danime channel ka link! Join karne ke liye neeche button par click karein:",
        "button_text": "🔔 Request to Join",
        "link": "https://t.me/+mUBQJuyB5FNlMTVl"
    },
    "parody": {
        "message": "Ye raha aapka Parody channel ka link! Join karne ke liye neeche button par click karein:",
        "button_text": "🔔 Request to Join",
        "link": "https://t.me/+G_BZgtePcARkN2M1"
    },
    "hentai": {
        "message": "Ye raha aapka Hentai channel ka link! Join karne ke liye neeche button par click karein:",
        "button_text": "🔔 Request to Join",
        "link": "https://t.me/+ypMzwwRrx1I1NGZl"
    },
    # आप यहाँ और चैनल जोड़ सकते हैं...
}

# --- बॉट के फंक्शन (Hinglish में) ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    args = context.args

    if args:
        channel_key = args[0]
        channel_data = CHANNELS.get(channel_key)

        if channel_data:
            # अगर key सही है तो यह मैसेज भेजें
            keyboard = [[InlineKeyboardButton(channel_data["button_text"], url=channel_data["link"])]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(channel_data["message"], reply_markup=reply_markup)
        else:
            # अगर key गलत है तो यह मैसेज भेजें
            await update.message.reply_text(f"Hey {user.mention_html()}!\n\nLagta hai ye link kaam nahi kar raha hai ya purana ho gaya hai. Kripya hamare main channel se dobara try karein.", parse_mode='HTML')
    else:
        # अगर कोई सिर्फ /start भेजता है
        await update.message.reply_text(f"Hey {user.mention_html()}!\n\nYeh ek gateway bot hai. Link paane ke liye, kripya hamare main channel par kisi button par click karein.", parse_mode='HTML')

# --- Render.com के लिए वेब सर्वर ---
app = Flask(__name__)

@app.route('/')
def index():
    return "Bot is running!"

# --- बॉट को चलाने के लिए सही तरीका (एरर फिक्स के साथ) ---
def run_bot_polling(application):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        # stop_signals=None जोड़ने से RuntimeError फिक्स हो जाएगा
        loop.run_until_complete(application.run_polling(stop_signals=None))
    finally:
        loop.close()

# --- मुख्य प्रोग्राम ---
if __name__ == "__main__":
    BOT_TOKEN = os.environ.get("BOT_TOKEN")
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN एनवायरनमेंट वेरिएबल सेट नहीं है!")

    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))

    bot_thread = threading.Thread(target=run_bot_polling, args=(application,), daemon=True)
    bot_thread.start()
    
    logger.info("बॉट का थ्रेड शुरू हो गया है। Gunicorn अब मुख्य थ्रेड को संभालेगा।")
