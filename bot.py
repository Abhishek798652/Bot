from telegram import Update
from telegram.ext import Application, ChatJoinRequestHandler, MessageHandler, filters
import logging

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Replace with your actual bot token
BOT_TOKEN = "7318436729:AAGeg3R-cLsC_-l3-I6XKn0tacTpW7V47X0"

# Approve chat join requests and send a welcome message
async def approve_request(update: Update, context):
    user = update.chat_join_request.from_user
    chat_id = update.chat_join_request.chat.id

    try:
        # Approve the user's join request
        await context.bot.approve_chat_join_request(chat_id=chat_id, user_id=user.id)

        # Send a welcome message to the new member
        await context.bot.send_message(
            chat_id=user.id,
            text=f"Hi {user.first_name}, welcome to our channel! Feel free to reach out anytime.",
        )
        logger.info(f"Approved join request for {user.first_name} ({user.id}).")
    except Exception as e:
        logger.error(f"Error while approving request: {e}")

# Handle user messages
async def handle_user_message(update: Update, context):
    user_message = update.message.text  # The user's message
    user = update.message.from_user    # User details
    try:
        # Reply to the user's message
        await update.message.reply_text(
            f"Hi {user.first_name}, I received your message: '{user_message}'."
        )
        logger.info(f"Message from {user.first_name} ({user.id}): {user_message}")
    except Exception as e:
        logger.error(f"Error while handling user message: {e}")

# Main function to start the bot
def main():
    # Create an application instance
    application = Application.builder().token(BOT_TOKEN).build()

    # Add a handler for approving chat join requests
    application.add_handler(ChatJoinRequestHandler(approve_request))

    # Add a handler for all text messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_message))

    # Log that the bot is starting and run polling
    logger.info("Bot is starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)  # Ensure all updates are received

# Start the bot
if __name__ == "__main__":
    main()
