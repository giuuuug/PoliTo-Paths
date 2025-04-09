from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from commands import Commands
from database.database_postgreSQL_pgrouting_sample import DatabasePostgreSQLPgRoutingSample
from database.database_postgreSQL_polito_paths import DatabasePostgreSQLPolitoPaths

class TelegramBot:
    def __init__(self, token: str):
        self.token = token
        self.app = ApplicationBuilder().token(token).build()
        self.db_pg_routing_sample = DatabasePostgreSQLPgRoutingSample()
        self.db_polito_paths = DatabasePostgreSQLPolitoPaths()
        self.commands = Commands(self.db_pg_routing_sample, self.db_polito_paths)

        self._register_handlers()

    def _register_handlers(self):
        handlers = [
            CommandHandler("sample", self.commands.sample),
            CallbackQueryHandler(self.commands.handle_callback),
            MessageHandler(filters.COMMAND, self.commands.unknown),
        ]
        for handler in handlers:
            self.app.add_handler(handler)

    def run(self):
        try:
            self.app.run_polling()
        except Exception as e:
            raise