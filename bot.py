from flask import Flask
from telegram import Update
from telegram.ext import Application, ChatJoinRequestHandler, MessageHandler, filters
import logging
from threading import Thread

# Enable logging
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Replace with your actual bot token
BOT_TOKEN = "7804254832:AAG98eY4lt2fp3z9ruETnmHGx7xKJMxTaG8"

# Flask app to keep the bot alive
app = Flask(__name__)

async def approve_request(update: Update, context):
    user = update.chat_join_request.from_user
    chat_id = update.chat_join_request.chat.id

    try:
        # Approve the user
        await context.bot.approve_chat_join_request(chat_id=chat_id, user_id=user.id)

        # Send a welcome message
        await context.bot.send_message(
            chat_id=user.id,
            text=f"Hi {user.first_name}, welcome to our channel! Feel free to reach out anytime.",
        )
        logger.info(f"Approved join request for {user.first_name} ({user.id}).")
    except Exception as e:
        logger.error(f"Error while approving request: {e}")

async def handle_user_message(update: Update, context):
    user_message = update.message.text
    await update.message.reply_text(
        "Thanks for your message! I'll get back to you soon."
    )

@app.route('/')
def home():
    return "Bot is running!"  # Keeps Render from timing out

def start_flask():
    app.run(host="0.0.0.0", port=8080)

def start_bot():
    # Ensure polling only has one instance
    application = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(ChatJoinRequestHandler(approve_request))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_message))

    logger.info("Bot is starting...")
    application.run_polling()

if __name__ == "__main__":
    # Run Flask in a background thread
    flask_thread = Thread(target=start_flask)
    flask_thread.start()

    # Start the bot
    start_bot()
