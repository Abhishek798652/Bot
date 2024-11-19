from telegram import Update, Message
from telegram.ext import Application, CommandHandler, MessageHandler, ChatJoinRequestHandler, filters, ContextTypes
import logging

# Enable logging
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Replace with your bot token
BOT_TOKEN = "7318436729:AAGeg3R-cLsC_-l3-I6XKn0tacTpW7V47X0"

# Replace with your Telegram user ID
ADMIN_USER_ID = 6490744056  # Your Telegram user ID (get it from @userinfobot)

# To store the mapping of users and messages
user_context = {}


async def approve_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle join requests, approve, and send a greeting message."""
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


async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle messages sent by members and forward them to the admin."""
    user = update.message.from_user
    chat_id = update.message.chat.id
    user_message = update.message.text

    # Store the chat_id for two-way communication
    user_context[update.message.message_id] = chat_id

    # Forward the member's message to the admin
    forwarded_message = await context.bot.send_message(
        chat_id=ADMIN_USER_ID,
        text=f"Message from {user.first_name} (UserID: {user.id}):\n\n{user_message}",
    )

    # Map admin's reply to the user's chat
    user_context[forwarded_message.message_id] = chat_id
    logger.info(f"Forwarded message from {user.first_name} ({user.id}) to admin.")


async def handle_admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle admin's reply and send it back to the member."""
    reply_message = update.message
    original_chat_id = user_context.get(reply_message.reply_to_message.message_id)

    if original_chat_id:
        await context.bot.send_message(
            chat_id=original_chat_id,
            text=f"Admin replied:\n\n{reply_message.text}",
        )
        logger.info(f"Sent admin's reply to user with chat_id: {original_chat_id}")
    else:
        await update.message.reply_text("Unable to determine the original user for this reply.")


def main():
    """Start the bot."""
    application = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(ChatJoinRequestHandler(approve_request))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.REPLY, handle_user_message))
    application.add_handler(MessageHandler(filters.TEXT & filters.REPLY, handle_admin_reply))

    logger.info("Bot is starting...")
    application.run_polling()


if __name__ == "__main__":
    main()
