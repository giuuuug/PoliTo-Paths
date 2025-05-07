from telegram import Update
from telegram.ext import ContextTypes, CallbackContext
from command.command_handler import CommandHandler
from utils.log import Log

class HelpCommand(CommandHandler):
    def __init__(self):
        super().__init__(log=Log(self.__class__.__name__))
    
    async def command_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command."""
        help_text = """
🔍 *Available Commands*:

/start - Start the bot and see welcome message
/navigate - Start navigation between two points
/sample - Try a sample navigation
/help - Show this help message

For navigation assistance, use /navigate command.
"""
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def handle_question(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Not used in this command."""
        pass
    
    async def command_cancel(self, update: Update, context: CallbackContext):
        """Not used in this command."""
        pass