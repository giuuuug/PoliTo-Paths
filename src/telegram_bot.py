from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ConversationHandler
from command.sample_command import SampleCommand
from command.navigate_command import NavigateCommand
from command.start_command import StartCommand
from command.help_command import HelpCommand
from database.database_postgreSQL_pgrouting_sample import DatabasePostgreSQLPgRoutingSample
from database.database_postgreSQL_polito_paths import DatabasePostgreSQLPolitoPaths

QUESTION_1, QUESTION_2 = range(2)

class TelegramBot:
    def __init__(self, token: str):
        self.token = token
        self.app = ApplicationBuilder().token(token).build()
        self.db_pg_routing_sample = DatabasePostgreSQLPgRoutingSample()
        self.db_polito_paths = DatabasePostgreSQLPolitoPaths()
        
        # Initialize all commands
        self.sample_command = SampleCommand(self.db_pg_routing_sample)
        self.navigate_command = NavigateCommand(self.db_polito_paths)
        self.start_command = StartCommand()
        self.help_command = HelpCommand()
    
        self._register_handlers()

    def _register_handlers(self):
        # Regular command handlers
        self.app.add_handler(CommandHandler("start", self.start_command.command_start))
        self.app.add_handler(CommandHandler("help", self.help_command.command_start))
        
        # Conversation handlers
        sample_command_handler = ConversationHandler(
            entry_points=[CommandHandler("sample", self.sample_command.command_start)],
            states={
                QUESTION_1: [CallbackQueryHandler(self.sample_command.handle_question)],
                QUESTION_2: [CallbackQueryHandler(self.sample_command.handle_question)],
            },
            fallbacks=[CommandHandler("cancel", self.sample_command.command_cancel)],
        )
        
        navigate_command_handler = ConversationHandler(
            entry_points=[CommandHandler("navigate", self.navigate_command.command_start)],
            states={
                QUESTION_1: [CallbackQueryHandler(self.navigate_command.handle_question)],
                QUESTION_2: [CallbackQueryHandler(self.navigate_command.handle_question)],
            },
            fallbacks=[CommandHandler("cancel", self.navigate_command.command_cancel)],
        )
        
        self.app.add_handler(sample_command_handler)
        self.app.add_handler(navigate_command_handler)

    def run(self):
        try:
            self.app.run_polling()
        except Exception as e:
            raise