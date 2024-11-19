from telegram import Update, Message, ReplyKeyboardMarkup, KeyboardButton
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

# Track which users have clicked "How to start"
user_started = set()

async def approve_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle join requests, approve, and send a greeting message."""
    user = update.chat_join_request.from_user
    chat_id = update.chat_join_request.chat.id

    try:
        # Approve the user
        await context.bot.approve_chat_join_request(chat_id=chat_id, user_id=user.id)

        # Send a greeting message with a "How to Start" button
        keyboard = [[KeyboardButton("How to start")]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        await context.bot.send_message(
            chat_id=user.id,
            text=f"Hi {user.first_name}, welcome to our channel! Please click the button below to get started.",
            reply_markup=reply_markup
        )

        logger.info(f"Approved join request for {user.first_name} ({user.id}).")

    except Exception as e:
        logger.error(f"Error while approving request: {e}")

async def handle_how_to_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the 'How to start' button click."""
    user = update.message.from_user
    chat_id = update.message.chat.id

    # Mark user as having started interaction
    user_started.add(user.id)

    # Send a message explaining how to interact with the bot
    await context.bot.send_message(
        chat_id=chat_id,
        text="You can now start typing freely. Your messages will be sent to the admin for review. 😊",
    )

    logger.info(f"User {user.first_name} ({user.id}) clicked the 'How to start' button.")

async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle messages sent by members and forward them to the admin."""
    user = update.message.from_user
    chat_id = update.message.chat.id
    user_message = update.message.text

    # Check if the user has clicked the 'How to start' button
    if user.id in user_started:
        # Forward the member's message to the admin
        forwarded_message = await context.bot.send_message(
            chat_id=ADMIN_USER_ID,
            text=f"Message from {user.first_name} (UserID: {user.id}):\n\n{user_message}",
        )

        # Map admin's reply to the user's chat
        user_context[forwarded_message.message_id] = chat_id
        logger.info(f"Forwarded message from {user.first_name} ({user.id}) to admin.")
    else:
        # Inform the user they need to click "How to start" first
        await update.message.reply_text("Please click the 'How to start' button to begin interacting.")

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
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex("How to start"), handle_how_to_start))  # Handle button click

    logger.info("Bot is starting...")
    application.run_polling()

if __name__ == "__main__":
    main()
