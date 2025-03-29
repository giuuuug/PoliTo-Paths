# app.py
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters
)
from database import execute_query

# Logging configuration
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.WARNING
)
logging.getLogger('telegram').setLevel(logging.WARNING)
logging.getLogger('httpx').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.warning(f"User {update.effective_user.id} started the bot")
    await update.message.reply_text(
        "Welcome! Use /query to get data from the database"
    )

async def handle_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.warning(f"User {update.effective_user.id} requested a query")
    
    # Execute query through database module
    result = execute_query("SELECT * FROM grafi_clean LIMIT 10;")
    
    # Handle results/errors
    if isinstance(result, str):  # If it's a string, it's an error
        response = result
    else:
        response = "📋 Query results:\n\n" + "\n".join(
            [str(row) for row in result]
        ) if result else "⚠️ No data found"
    
    await update.message.reply_text(response)

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(update.message.text)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show available commands list"""
    commands_list = [
        "/start - Start the bot",
        "/query - Execute database query",
        "/help - Show this help guide"
    ]
    
    await update.message.reply_text(
        "📜 Available commands:\n\n" + "\n".join(commands_list)
    )

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle unknown commands"""
    await update.message.reply_text(
        "⚠️ Unrecognized command. Use one of these:\n\n"
        "/start - Start the bot\n"
        "/query - Execute query\n"
        "/help - Show commands"
    )

if __name__ == '__main__':
    application = ApplicationBuilder().token('7944271446:AAFbzzLSgiN5VwDOnaY_T_x6UX7RPeYFl6U').build()
    
    # Add handlers
    handlers = [
        CommandHandler('start', start),
        CommandHandler('query', handle_query),
        CommandHandler('help', help_command),
        MessageHandler(filters.TEXT & ~filters.COMMAND, echo),
        MessageHandler(filters.COMMAND, unknown)
    ]
    
    for handler in handlers:
        application.add_handler(handler)
    
    logger.warning("Bot starting...")
    application.run_polling()