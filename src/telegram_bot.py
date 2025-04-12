from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ConversationHandler
from command.sample_command import SampleCommand
from database.database_postgreSQL_pgrouting_sample import DatabasePostgreSQLPgRoutingSample
from database.database_postgreSQL_polito_paths import DatabasePostgreSQLPolitoPaths

QUESTION_1, QUESTION_2 = range(2)

class TelegramBot:
    def __init__(self, token: str):
        self.token = token
        self.app = ApplicationBuilder().token(token).build()
        self.db_pg_routing_sample = DatabasePostgreSQLPgRoutingSample()
        self.db_polito_paths = DatabasePostgreSQLPolitoPaths()
        
        self.sample_command = SampleCommand(self.db_pg_routing_sample)
    
        self._register_handlers()

    def _register_handlers(self):
        sample_command_handler = ConversationHandler(
            entry_points=[CommandHandler("start", self.sample_command.command_start),
                        CommandHandler("sample", self.sample_command.command_start)],
            states={
                QUESTION_1: [CallbackQueryHandler(self.sample_command.handle_question)],
                QUESTION_2: [CallbackQueryHandler(self.sample_command.handle_question)],
            },
            fallbacks=[CommandHandler("cancel", self.sample_command.command_cancel)],
        )
        
    
        self.app.add_handler(sample_command_handler)
        

    def run(self):
        try:
            self.app.run_polling()
        except Exception as e:
            raise