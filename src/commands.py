# commands.py
from telegram import Update
from telegram.ext import ContextTypes
from logger import Logger
from database import Database
from datetime import datetime

class Commands:
    def __init__(self, db: Database, logger: Logger):
        self.db = db
        self.logger = logger

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            user = update.message.from_user
            log_msg = (
                f"Nuovo utente: ID={user.id}, "
                f"Username=@{user.username}, "
                f"Nome={user.first_name} {user.last_name or ''}, "
                f"Data={datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            self.logger.log_bot_info(log_msg)
            await update.message.reply_text("Welcome in the official bot of PoliTo Paths!")
        except Exception as e:
            self.logger.log_app_error(f"COMMAND ERROR: {str(e)}")

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            commands = [
                "/start - Start the bot",
                "/help - Commands help"
            ]
            await update.message.reply_text("\n".join(commands))
        except Exception as e:
            self.logger.log_app_error(f"COMMAND ERROR: {str(e)}")

    async def unknown(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            await update.message.reply_text("This command does not exist!")
        except Exception as e:
            self.logger.log_app_error(f"COMMAND ERROR: {str(e)}")