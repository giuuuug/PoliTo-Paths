from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from commands import Commands
from database import Database
from logger import Logger

class TelegramBot:
    def __init__(self, token: str):
        self.token = token
        self.app = ApplicationBuilder().token(token).build()
        
        # Inizializza logging e dipendenze
        self.logger = Logger()
        self.db = Database(self.logger)
        self.commands = Commands(self.db, self.logger)

        self._register_handlers()

    def _register_handlers(self):
        handlers = [
            CommandHandler('start', self.commands.start),
            CommandHandler('help', self.commands.help),
            MessageHandler(filters.COMMAND, self.commands.unknown)
        ]
        for handler in handlers:
            self.app.add_handler(handler)
    
    def run(self):
        try:
            self.logger.log_bot_info("BOT STARTED")
            self.app.run_polling()
        except Exception as e:
            self.logger.log_bot_critical(f"BOT CRASHED: {str(e)}")
            raise