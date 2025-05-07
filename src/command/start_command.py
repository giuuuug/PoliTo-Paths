from telegram import Update
from telegram.ext import ContextTypes, CallbackContext
from command.command_handler import CommandHandler
from utils.log import Log

class StartCommand(CommandHandler):
    def __init__(self):
        super().__init__(log=Log(self.__class__.__name__))
    
    async def command_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        # Send the welcome image
        with open('img/polito_bot_logo.jpg', 'rb') as photo:
            await update.message.reply_photo(
                photo=photo,
                caption="Welcome to PoliTo Mapping Bot! 🎓"
            )
        
        # Send welcome message
        welcome_text = """
🏛️ *Welcome to PoliTo Mapping Bot!*

I'm here to help you navigate through the Politecnico di Torino buildings. With my help, you can:
• Find the shortest path between any two points
• Get step-by-step navigation instructions
• See nearby landmarks and reference points

To start navigating, use the /navigate command.
Type /help to see all available commands.

Happy exploring! 🗺️
"""
        await update.message.reply_text(welcome_text, parse_mode='Markdown')
    
    async def handle_question(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Not used in this command."""
        pass
    
    async def command_cancel(self, update: Update, context: CallbackContext):
        """Not used in this command."""
        pass