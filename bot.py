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

# --- चैनल कॉन्फ़िगरेशन ---
# यहीं पर आप अपने सभी चैनलों को मैनेज करेंगे।
CHANNELS = {
    "hentai": {
        "message": "Here is your link! Click below to proceed:",
        "button_text": "🔔 Request to Join",
        "link": "https://t.me/+ypMzwwRrx1I1NGZl"  # <<--- यहाँ अपना असली ज्वाइन लिंक डालें
    },
    "parody": {
        "message": "Here is your link! Click below to proceed:",
        "button_text": "🔔 Request to Join",
        "link": "https://t.me/+G_BZgtePcARkN2M1" # <<--- यहाँ अपना असली ज्वाइन लिंक डालें
    },
    # आप यहाँ और चैनल जोड़ सकते हैं...
}

# --- बॉट के फंक्शन ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """यह फंक्शन तब चलता है जब कोई यूजर /start कमांड भेजता है।"""
    user = update.effective_user
    args = context.args

    if args:
        channel_key = args[0]
        channel_data = CHANNELS.get(channel_key)

        if channel_data:
            keyboard = [[InlineKeyboardButton(channel_data["button_text"], url=channel_data["link"])]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(channel_data["message"], reply_markup=reply_markup)
        else:
            await update.message.reply_text(f"नमस्ते {user.mention_html()}!\n\nयह लिंक शायद काम नहीं कर रहा है। कृपया हमारे मुख्य चैनल से दोबारा प्रयास करें।", parse_mode='HTML')
    else:
        await update.message.reply_text(f"नमस्ते {user.mention_html()}!\n\nयह एक गेटवे बॉट है। कृपया हमारे मुख्य चैनल पर जाकर किसी बटन पर क्लिक करें।", parse_mode='HTML')

# --- Render.com के लिए वेब सर्वर ---
app = Flask(__name__)

@app.route('/')
def index():
    return "Bot is running!"

# --- बॉट को चलाने के लिए सही तरीका ---
def run_bot_polling(application):
    """यह फंक्शन एक नए थ्रेड में बॉट को सही तरीके से चलाता है।"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(application.run_polling())
    finally:
        loop.close()

# --- मुख्य प्रोग्राम ---
if __name__ == "__main__":
    BOT_TOKEN = os.environ.get("BOT_TOKEN")
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN एनवायरनमेंट वेरिएबल सेट नहीं है!")

    # Telegram एप्लीकेशन सेट करें
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))

    # एक अलग थ्रेड में बॉट को चलाएं
    bot_thread = threading.Thread(target=run_bot_polling, args=(application,), daemon=True)
    bot_thread.start()
    
    logger.info("बॉट का थ्रेड शुरू हो गया है। Gunicorn अब मुख्य थ्रेड को संभालेगा।")
    
    # Gunicorn इस 'app' ऑब्जेक्ट को ढूंढेगा और चलाएगा।
