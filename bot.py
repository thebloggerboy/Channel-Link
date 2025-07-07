import os
import logging
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

# Logging सेटअप, ताकि हमें सर्वर पर पता चले कि बॉट चल रहा है
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- चैनल लिंक कॉन्फ़िगरेशन ---
# यह सबसे ज़रूरी हिस्सा है।
# 'key': यह वो यूनिक आईडी है जो आप /start लिंक में इस्तेमाल करेंगे (जैसे ?start=hanime)
# 'link': यह उस चैनल का असली प्राइवेट ज्वाइन लिंक है।

CHANNEL_LINKS = {
    "danime": "https://t.me/+mUBQJuyB5FNlMTVl",   # यहाँ hanime चैनल का ज्वाइन लिंक डालें
    "hentai": "https://t.me/+ypMzwwRrx1I1NGZl",   # यहाँ parody चैनल का ज्वाइन लिंक डालें
    "parody": "https://t.me/+G_BZgtePcARkN2M1",  # यहाँ manga18+ चैनल का ज्वाइन लिंक डालें
    
    # --- नए चैनल ऐसे जोड़ें ---
    # "new_channel_key": "https://t.me/your_new_channel_join_link",
    # "another_key": "https://t.me/another_join_link",
}

# --- बॉट का मुख्य फंक्शन ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """यह फंक्शन /start कमांड पर चलता है।"""
    args = context.args

    if args:
        # अगर /start के साथ कोई की (key) भेजी गई है (जैसे ?start=hanime)
        channel_key = args[0]
        join_link = CHANNEL_LINKS.get(channel_key)

        if join_link:
            # अगर key हमारी डिक्शनरी में मौजूद है, तो बटन बनाएँ
            message_text = "Here is your link! Click below to proceed:"
            button_text = "🔔 Request to Join"
            
            keyboard = [[InlineKeyboardButton(button_text, url=join_link)]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(message_text, reply_markup=reply_markup)
        else:
            # अगर key मौजूद नहीं है
            await update.message.reply_text("This link seems to be invalid or expired. Please try again from our main channel.")
    else:
        # अगर किसी ने सीधे बॉट को /start किया है
        await update.message.reply_text("Welcome! Please use a link from one of our channels to get access.")

# --- Render.com के लिए वेब सर्वर (इसे 24/7 जगाए रखने के लिए) ---
app = Flask(__name__)

@app.route('/')
def index():
    return "Bot is alive and running!"

# --- बॉट और वेब सर्वर को चलाने का कोड ---

def main():
    # एनवायरनमेंट से बॉट टोकन लें
    BOT_TOKEN = os.environ.get("BOT_TOKEN")
    if not BOT_TOKEN:
        logger.error("FATAL: BOT_TOKEN environment variable not set.")
        return

    # Telegram एप्लीकेशन सेट करें
    application = Application.builder().token(BOT_TOKEN).build()

    # /start कमांड के लिए हैंडलर जोड़ें
    application.add_handler(CommandHandler("start", start))

    # बॉट को एक अलग थ्रेड में चलाएं ताकि वेब सर्वर ब्लॉक न हो
    threading.Thread(target=application.run_polling, daemon=True).start()
    
    logger.info("Telegram Bot has started polling...")
    
    # यह 'app' ऑब्जेक्ट Gunicorn द्वारा Render पर चलाया जाएगा।
    # लोकल टेस्टिंग के लिए, आप app.run() का उपयोग कर सकते हैं।

# Gunicorn को 'app' ऑब्जेक्ट की जरूरत होती है, इसलिए इसे ग्लोबल स्कोप में रखते हैं
main()